from pydantic import BaseModel, Field


class TailorRequest(BaseModel):
    job_description: str = Field(..., min_length=20, max_length=10000)


class TailorResponse(BaseModel):
    message: str
    output_docx_path: str
    output_pdf_path: str
