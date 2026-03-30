import shutil
import subprocess
from pathlib import Path


class PdfService:
    def __init__(self, libreoffice_bin: str = "soffice") -> None:
        self.libreoffice_bin = libreoffice_bin

    def convert_docx_to_pdf(self, input_docx: Path, output_dir: Path) -> Path:
        if not input_docx.exists():
            raise FileNotFoundError(f"DOCX file not found: {input_docx.as_posix()}")

        output_dir.mkdir(parents=True, exist_ok=True)

        libreoffice_path = shutil.which(self.libreoffice_bin)
        if libreoffice_path:
            completed = subprocess.run(
                [
                    libreoffice_path,
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(output_dir),
                    str(input_docx),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    "LibreOffice conversion failed. "
                    f"stderr: {completed.stderr.strip()}"
                )

            output_pdf = output_dir / f"{input_docx.stem}.pdf"
            if output_pdf.exists():
                return output_pdf

        try:
            from docx2pdf import convert as docx2pdf_convert  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "No PDF converter available. Install LibreOffice or add docx2pdf."
            ) from exc

        output_pdf = output_dir / f"{input_docx.stem}.pdf"
        docx2pdf_convert(str(input_docx), str(output_pdf))
        if not output_pdf.exists():
            raise RuntimeError("PDF conversion failed with docx2pdf.")

        return output_pdf
