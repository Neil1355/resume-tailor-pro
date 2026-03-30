# Resume Tailor Backend (FastAPI)

This backend keeps your resume layout stable by rendering from a strict Word master template.

## Folder Structure

backend/
- app/
  - main.py                      # FastAPI app and endpoints
  - config.py                    # Env-based settings
  - models.py                    # Request/response models
  - services/
    - gemini_service.py          # Gemini rewrite logic
    - template_service.py        # docxtpl rendering
    - pdf_service.py             # DOCX -> PDF conversion
  - templates/
    - master_template.docx       # Required, add manually
  - data/
    - master_bullets.json        # Original bullets mapped to Jinja tags
    - master_bullets.sample.json # Example mapping file
- output/                        # Generated DOCX/PDF output
- requirements.txt
- .env.example

## Requirements

- Python 3.11+
- LibreOffice installed and available as `soffice` in PATH (recommended)
- Gemini API key

## Setup

1. Create and activate a virtual environment.
2. Install packages:
   pip install -r requirements.txt
3. Create `.env` from `.env.example` and set `GOOGLE_API_KEY`.
4. Put your template at `app/templates/master_template.docx`.
5. Ensure bullets in template use Jinja tags like `{{bullet_1}}`, `{{bullet_2}}`.
6. Ensure `app/data/master_bullets.json` contains those matching keys.

## Run

uvicorn app.main:app --reload --port 8000

## API

- GET `/health`
- POST `/api/tailor`

Request body:
{
  "job_description": "Paste target job description here"
}

Response body:
{
  "message": "Resume tailored successfully.",
  "output_docx_path": "output/tailored_resume.docx",
  "output_pdf_path": "output/tailored_resume.pdf"
}

## Security and Robustness

- SlowAPI rate limit: `5/minute` per client IP
- Global 500 handlers for:
  - missing files (`FileNotFoundError`)
  - AI timeout (`TimeoutError`)
  - unexpected exceptions
