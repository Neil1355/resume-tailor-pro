# Resume Tailor Pro

This repository contains:

- A React frontend in `src/` (deploy to Vercel)
- A Python FastAPI backend in `backend/` that uses `docxtpl` and Gemini to tailor resume bullet points while preserving strict template formatting (deploy to Fly.io, DigitalOcean, or similar)

## Quick Start (Local Development)

### Prerequisites
- Node.js/npm (frontend)
- Python 3.11+ (backend)
- Google Gemini API key

### Setup

1. **Frontend** (.env.local already created, points to localhost:8000):
   ```bash
   npm install
   npm run dev
   ```
   Opens http://localhost:8080

2. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   # Create .env with your GOOGLE_API_KEY
   uvicorn app.main:app --reload --port 8000
   ```

## Deployment

- **Frontend**: Deploy to [Vercel](docs/VERCEL_DEPLOYMENT.md) (free tier available)
- **Backend**: Deploy to Render/Fly.io/DigitalOcean (see [backend/README.md](backend/README.md) for Docker + LibreOffice details)

See deployment docs for detailed steps on connecting frontend to backend URL.

## Backend Features

- Strict DOCX template rendering with Jinja2 placeholders
- Gemini AI for JD-based bullet point rewriting
- PDF conversion via LibreOffice/docx2pdf
- SlowAPI rate limiting (5/min per IP)
- Global error handlers with helpful messages

## Security Checklist

- Keep secrets only in environment variables (`backend/.env`, Render, Vercel), never in tracked files.
- Set `CORS_ORIGINS` and `CORS_ORIGIN_REGEX` for your frontend domains.
- Set `ADMIN_AUDIT_TOKEN` to use the protected `/admin/security-summary` endpoint.
- Rotate Gemini key immediately if exposed.
- Run regular audits:
   - `npm audit --json`
   - `python -m pip_audit` (inside backend venv)

## Project TODO

- Add authenticated user accounts for multi-user resume storage.
- Add persistent storage for generated files (currently local output directory).
- Add integration tests for tailoring + download flows against deployed environments.
