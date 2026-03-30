# Resume Tailor Pro

This repository contains:

- A React frontend in `src/`
- A Python FastAPI backend in `backend/` that uses `docxtpl` and Gemini to tailor resume bullet points while preserving strict template formatting

## Backend Quick Start

1. Go to `backend/`
2. Install dependencies:
	- `pip install -r requirements.txt`
3. Create `.env` from `.env.example` and set `GOOGLE_API_KEY`
4. Add `backend/app/templates/master_template.docx`
5. Ensure template uses Jinja tags like `{{bullet_1}}`, `{{bullet_2}}`
6. Run API:
	- `uvicorn app.main:app --reload --port 8000`

Detailed backend docs: `backend/README.md`
