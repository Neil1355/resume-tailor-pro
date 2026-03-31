from pathlib import Path
from typing import TYPE_CHECKING

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Resume Tailor API"
    google_api_key: str = ""
    master_template_path: str = "app/templates/master_template.docx"
    libreoffice_bin: str = "soffice"
    rate_limit_per_minute: int = 5
    output_dir: str = "output"
    cors_origins: str = "http://localhost:8080"
    cors_origin_regex: str = r"^https://.*\.vercel\.app$|^http://localhost(:\d+)?$"
    admin_audit_token: str = ""

    @property
    def master_template(self) -> Path:
        return Path(self.master_template_path)

    @property
    def rendered_docx_output(self) -> Path:
        return Path(self.output_dir) / "tailored_resume.docx"

    @property
    def rendered_pdf_output(self) -> Path:
        return Path(self.output_dir) / "tailored_resume.pdf"

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


if TYPE_CHECKING:
    settings = Settings(google_api_key="")
else:
    settings = Settings()
