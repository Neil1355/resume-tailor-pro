# Changelog

## 2026-03-30

- Added new FastAPI backend under `backend/` for resume tailoring pipeline.
- Implemented stable template rendering using `docxtpl` with Jinja bullet tags (`bullet_1`, `bullet_2`, etc.).
- Added Gemini integration for JD-based bullet rewriting with JSON-only output contract.
- Added PDF conversion service with LibreOffice-first strategy and docx2pdf fallback support.
- Updated tailoring endpoint to gracefully return DOCX-only success when PDF conversion tools are unavailable on Linux hosts.
- Added `backend/Dockerfile` and Render Docker deployment guidance to guarantee LibreOffice-based PDF conversion in production.
- Added backend download endpoints and frontend blob-download wiring so export buttons trigger real DOCX/PDF downloads.
- Added "See What's Changed" preview in the frontend with bullet-by-bullet original vs tailored text before export.
- Cleaned project scaffold by removing unused UI/component/test files and redundant deployment summary docs.
- Hardened backend CORS and exception responses; added `CORS_ORIGINS` configuration.
- Updated frontend/backend dependencies and lockfiles from audit findings; npm and pip-audit now report no known package CVEs in project dependencies.
- Added SlowAPI rate limiting (`5/minute`) on tailoring endpoint.
- Added global error handlers for file-not-found and API timeout conditions with HTTP 500 responses.
- Added backend setup/configuration docs and sample data/template guidance.
