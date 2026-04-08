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
- Added protected `/admin/security-summary` endpoint with token auth for runtime security and dependency version checks.
- Improved `/api/tailor` error handling to return actionable `502` when Gemini API key is invalid/expired.
- Added endpoint-specific rate limits for download/admin routes and security headers middleware (`nosniff`, frame deny, referrer policy, permissions policy).
- Added `CORS_ORIGIN_REGEX` support for stable Vercel preview-domain preflight handling.
- Updated frontend/backend dependencies and lockfiles from audit findings; npm and pip-audit now report no known package CVEs in project dependencies.
- Improved frontend tailoring progress UX with request timeout handling, stage-based status messages under the progress bar, and ETA estimates based on recent run durations.
- Added resume parsing service to extract job positions and bullet points from uploaded DOCX files.
- Updated `/api/tailor` endpoint to accept file upload with FormData instead of static master bullets.
- Enhanced "See What's Changed" preview to group bullets by job position/title, showing position headers with their associated before/after bullets.
- Added SlowAPI rate limiting (`5/minute`) on tailoring endpoint.
- Added global error handlers for file-not-found and API timeout conditions with HTTP 500 responses.
- Added backend setup/configuration docs and sample data/template guidance.
- Added a portfolio-ready README snapshot section including architecture highlights and reusable resume bullets.
