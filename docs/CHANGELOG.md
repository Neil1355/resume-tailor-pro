# Changelog

## 2026-03-30

- Added new FastAPI backend under `backend/` for resume tailoring pipeline.
- Implemented stable template rendering using `docxtpl` with Jinja bullet tags (`bullet_1`, `bullet_2`, etc.).
- Added Gemini integration for JD-based bullet rewriting with JSON-only output contract.
- Added PDF conversion service with LibreOffice-first strategy and docx2pdf fallback support.
- Added SlowAPI rate limiting (`5/minute`) on tailoring endpoint.
- Added global error handlers for file-not-found and API timeout conditions with HTTP 500 responses.
- Added backend setup/configuration docs and sample data/template guidance.
