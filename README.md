# Resume Tailor Pro

## Portfolio Snapshot

Resume Tailor Pro is a full-stack AI application that rewrites resume bullets against a target job description while preserving strict Word-template layout constraints for export-ready output.

### Why This Project Is Strong Portfolio Material

- Solves a real hiring workflow problem end-to-end (analysis, rewriting, preview, export)
- Demonstrates production deployment across separate frontend/backend services
- Balances AI quality with formatting stability constraints in document generation
- Includes practical security hardening (rate limiting, CORS controls, token-protected admin endpoint, dependency audits)

### Architecture Highlights

- Frontend: React + Vite UI with progress flow, change preview, and file export
- Backend: FastAPI service with Gemini-based rewriting, docxtpl rendering, and PDF conversion pipeline
- Template strategy: stable master `.docx` with bullet tags (`bullet_1`, `bullet_2`, etc.)
- Export pipeline: generates tailored DOCX and optional PDF (LibreOffice-backed in containerized deploys)

### Resume Bullets You Can Reuse

- Built and deployed a full-stack AI resume-tailoring platform using React/Vite and FastAPI, enabling JD-aligned bullet rewriting with stable DOCX/PDF export.
- Engineered a layout-safe document generation workflow with `docxtpl` placeholders and controlled LLM prompting to preserve resume formatting fidelity.
- Implemented security and reliability controls including endpoint-specific rate limiting, CORS hardening for preview domains, token-protected admin diagnostics, and dependency vulnerability remediation.

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
