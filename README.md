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
- **Backend**: Deploy to [Fly.io](docs/FLY_DEPLOYMENT.md) (free tier available) or [DigitalOcean](docs/DIGITALOCEAN_DEPLOYMENT.md) ($5/month)

See deployment docs for detailed steps on connecting frontend to backend URL.

## Backend Features

- Strict DOCX template rendering with Jinja2 placeholders
- Gemini AI for JD-based bullet point rewriting
- PDF conversion via LibreOffice/docx2pdf
- SlowAPI rate limiting (5/min per IP)
- Global error handlers with helpful messages
