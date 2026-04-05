from pathlib import Path
from datetime import datetime, timezone
from importlib.metadata import version
import secrets

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.models import TailorRequest, TailorResponse
from app.services.gemini_service import GeminiService
from app.services.pdf_service import PdfService
from app.services.template_service import TemplateService

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
def tailor_resume(request: Request, payload: TailorRequest) -> TailorResponse:
    bullets = template_service.load_master_bullets(Path("app/data/master_bullets.json"))
    try:
        rewritten_bullets = gemini_service.rewrite_bullets(payload.job_description, bullets)
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

    safe_context = bullets.copy()
    safe_context.update({k: rewritten_bullets.get(k, bullets[k]) for k in bullets.keys()})

    rendered_docx = template_service.render_docx(
        safe_context,
        settings.rendered_docx_output,
    )
    rendered_pdf: Path | None = None
    message = "Resume tailored successfully."
    try:
        rendered_pdf = pdf_service.convert_docx_to_pdf(rendered_docx, Path(settings.output_dir))
    except RuntimeError:
        # On Linux hosts without LibreOffice, DOCX generation still succeeds.
        message = (
            "Resume tailored successfully. PDF conversion unavailable on this host; "
            "DOCX output is ready."
        )

    return TailorResponse(
        message=message,
        output_docx_path=str(rendered_docx),
        output_pdf_path=str(rendered_pdf) if rendered_pdf else None,
        original_bullets=bullets,
        tailored_bullets=safe_context,
    )


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
