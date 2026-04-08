from pathlib import Path
from datetime import datetime, timezone
from importlib.metadata import version
import secrets
import tempfile

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.models import TailorRequest, TailorResponse, PositionGroup, PositionBullet
from app.services.gemini_service import GeminiService
from app.services.pdf_service import PdfService
from app.services.template_service import TemplateService
from app.services.resume_parser import ResumeParser

app = FastAPI(title=settings.app_name)

# CORS configuration to allow requests from Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


def rate_limit_handler(request: Request, exc: Exception):
    return _rate_limit_exceeded_handler(request, exc)  # type: ignore[arg-type]


app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


template_service = TemplateService(settings.master_template)
gemini_service = GeminiService(settings.google_api_key)
pdf_service = PdfService(settings.libreoffice_bin)
resume_parser = ResumeParser()


@app.exception_handler(FileNotFoundError)
async def handle_file_not_found(_: Request, exc: FileNotFoundError):
    return JSONResponse(
        status_code=500,
        content={"detail": f"File not found: {exc}"},
    )


@app.exception_handler(TimeoutError)
async def handle_timeout(_: Request, exc: TimeoutError):
    return JSONResponse(
        status_code=500,
        content={"detail": f"API timeout: {exc}"},
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/admin/security-summary")
@limiter.limit(f"{settings.admin_rate_limit_per_minute}/minute")
def security_summary(request: Request):
    provided_token = request.headers.get("x-admin-token", "")
    expected_token = settings.admin_audit_token

    if not expected_token or not secrets.compare_digest(provided_token, expected_token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "service": settings.app_name,
        "security": {
            "rate_limit_per_minute": settings.rate_limit_per_minute,
            "cors_origins_count": len(settings.allowed_origins),
            "master_template_exists": settings.master_template.exists(),
            "output_dir_exists": Path(settings.output_dir).exists(),
            "admin_token_configured": bool(settings.admin_audit_token),
        },
        "versions": {
            "fastapi": version("fastapi"),
            "starlette": version("starlette"),
            "python-multipart": version("python-multipart"),
            "uvicorn": version("uvicorn"),
        },
    }


@app.post("/api/tailor", response_model=TailorResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def tailor_resume(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(...),
) -> TailorResponse:
    """Tailor a user-provided resume DOCX against a job description."""
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only DOCX files are supported.")

    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # Parse resume to extract positions and bullets
        parsed_resume = resume_parser.parse_docx(tmp_path)
        flat_bullets = resume_parser.extract_bullets_by_tag(tmp_path)

        # Validate that we found bullets
        if not flat_bullets:
            raise HTTPException(
                status_code=400,
                detail="No bullet points found in resume. Ensure bullets are marked with bullet_N tags or bullet markers.",
            )

        # Rewrite bullets using Gemini
        try:
            rewritten_bullets = gemini_service.rewrite_bullets(job_description, flat_bullets)
        except RuntimeError as exc:
            message = str(exc).lower()
            if "api_key_invalid" in message or "api key expired" in message or "api key" in message:
                raise HTTPException(
                    status_code=502,
                    detail="Gemini API key is invalid or expired. Update GOOGLE_API_KEY in backend environment.",
                ) from exc
            raise HTTPException(
                status_code=502,
                detail="Gemini service request failed. Please try again shortly.",
            ) from exc

        # Prepare context for template rendering (merge rewritten bullets)
        safe_context = flat_bullets.copy()
        safe_context.update({k: rewritten_bullets.get(k, flat_bullets[k]) for k in flat_bullets.keys()})

        # Render DOCX
        rendered_docx = template_service.render_docx(
            safe_context,
            settings.rendered_docx_output,
        )

        # Try PDF conversion and standardize filename
        rendered_pdf: Path | None = None
        message = "Resume tailored successfully."
        try:
            pdf_temp = pdf_service.convert_docx_to_pdf(rendered_docx, Path(settings.output_dir))
            # Rename to standard name so download endpoint can find it
            rendered_pdf = Path(settings.output_dir) / "tailored_resume.pdf"
            if pdf_temp != rendered_pdf:
                pdf_temp.rename(rendered_pdf)
        except RuntimeError:
            message = (
                "Resume tailored successfully. PDF conversion unavailable on this host; "
                "DOCX output is ready."
            )

        # Build position-grouped response
        positions = []
        for position in parsed_resume["positions"]:
            position_bullets = []
            for bullet in position["bullets"]:
                tag = bullet["tag"]
                original = flat_bullets.get(tag, "")
                tailored = rewritten_bullets.get(tag, original)
                position_bullets.append(
                    PositionBullet(tag=tag, original=original, tailored=tailored)
                )

            if position_bullets:
                positions.append(
                    PositionGroup(title=position["title"], bullets=position_bullets)
                )

        return TailorResponse(
            message=message,
            output_docx_path=str(rendered_docx),
            output_pdf_path=str(rendered_pdf) if rendered_pdf else None,
            original_bullets=flat_bullets,
            tailored_bullets=safe_context,
            positions=positions,
        )
    finally:
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink()


@app.get("/api/download/{file_format}")
@limiter.limit(f"{settings.download_rate_limit_per_minute}/minute")
def download_tailored_resume(request: Request, file_format: str):
    if file_format == "docx":
        file_path = settings.rendered_docx_output
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = "tailored_resume.docx"
    elif file_format == "pdf":
        file_path = settings.rendered_pdf_output
        media_type = "application/pdf"
        filename = "tailored_resume.pdf"
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'docx' or 'pdf'.")

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Requested {file_format.upper()} file is not available yet.",
        )

    return FileResponse(path=file_path, media_type=media_type, filename=filename)
