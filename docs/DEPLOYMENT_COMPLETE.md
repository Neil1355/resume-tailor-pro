# Vercel + Render Setup Complete

Your backend is live at: https://resume-tailor-pro.onrender.com

## Update Vercel Environment Variable

Go to Vercel Dashboard:
1. Project: resume-tailor-pro
2. Settings → Environment Variables
3. Find `VITE_API_BASE_URL`
4. Change value from `http://localhost:8000` to:
   ```
   https://resume-tailor-pro.onrender.com
   ```
5. Redeploy (click "Redeploy" button)

## Test the Full System

Once Vercel redeeploys (~1 min):
1. Visit your Vercel frontend URL (check dashboard for it)
2. Upload a resume (or use the sample)
3. Paste a job description
4. Click "Tailor Resume"
5. Check results

## Troubleshooting

**CORS Error**: Already fixed in backend (allows all origins in dev)

**API Timeout**: Gemini models not available on your account
- Check https://aistudio.google.com
- Verify API key has model access
- Update backend/.env with correct key
- Redeploy Render

**No PDF Generated**: LibreOffice not available on Render free tier
- Render will try docx2pdf fallback
- For production: upgrade Render plan or use DigitalOcean

## Backend URL Reference
- Health: https://resume-tailor-pro.onrender.com/health
- Tailor: POST https://resume-tailor-pro.onrender.com/api/tailor
- Rate Limit: 5 requests/minute per IP
