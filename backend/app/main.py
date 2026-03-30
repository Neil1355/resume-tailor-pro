from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.models import TailorRequest, TailorResponse
from app.services.gemini_service import GeminiService
from app.services.pdf_service import PdfService
from app.services.template_service import TemplateService

app = FastAPI(title=settings.app_name)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


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
        content={"detail": f"Internal server error: {exc}"},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/tailor", response_model=TailorResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
def tailor_resume(request: Request, payload: TailorRequest) -> TailorResponse:
    bullets = template_service.load_master_bullets(Path("app/data/master_bullets.json"))
    rewritten_bullets = gemini_service.rewrite_bullets(payload.job_description, bullets)

    safe_context = bullets.copy()
    safe_context.update({k: rewritten_bullets.get(k, bullets[k]) for k in bullets.keys()})

    rendered_docx = template_service.render_docx(
        safe_context,
        settings.rendered_docx_output,
    )
    rendered_pdf = pdf_service.convert_docx_to_pdf(rendered_docx, Path(settings.output_dir))

    return TailorResponse(
        message="Resume tailored successfully.",
        output_docx_path=str(rendered_docx),
        output_pdf_path=str(rendered_pdf),
    )
