import json
from pathlib import Path

from docxtpl import DocxTemplate


class TemplateService:
    def __init__(self, template_path: Path) -> None:
        self.template_path = template_path

    def ensure_template_exists(self) -> None:
        if not self.template_path.exists():
            raise FileNotFoundError(
                "master_template.docx was not found. Place it at "
                f"{self.template_path.as_posix()}."
            )

    def load_master_bullets(self, bullets_json_path: Path) -> dict[str, str]:
        if not bullets_json_path.exists():
            raise FileNotFoundError(
                "master_bullets.json was not found. Create it in app/data with "
                "keys like bullet_1, bullet_2, ..."
            )

        with bullets_json_path.open("r", encoding="utf-8") as fp:
            payload = json.load(fp)

        if not isinstance(payload, dict) or not payload:
            raise ValueError("master_bullets.json must be a non-empty object.")

        return {str(k): str(v) for k, v in payload.items()}

    def render_docx(self, context: dict[str, str], output_path: Path) -> Path:
        self.ensure_template_exists()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = DocxTemplate(str(self.template_path))
        doc.render(context)
        doc.save(str(output_path))
        return output_path
