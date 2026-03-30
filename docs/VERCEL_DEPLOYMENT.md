# Vercel Frontend Deployment Guide

## Step 1: Add `.env.local` for development
```bash
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
```

## Step 2: Deploy to Vercel

### Option A: Via Vercel Dashboard
1. Go to https://vercel.com
2. Sign in or create account
3. Click "Add New" → "Project"
4. Import your GitHub repo (Neil1355/resume-tailor-pro)
5. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: ./ (leave as is)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
6. Add Environment Variables:
   - Key: `VITE_API_BASE_URL`
   - Value: `https://your-backend-url.com` (replace with actual backend)
7. Click "Deploy"

### Option B: Via Vercel CLI
```bash
npm install -g vercel
vercel login
vercel --prod
```

## Step 3: Set Backend URL After Backend Deploy
After deploying your backend to Fly.io/DigitalOcean:
1. Get your backend API URL (e.g., https://my-resume-api.fly.dev)
2. In Vercel Dashboard → Project Settings → Environment Variables
3. Update `VITE_API_BASE_URL` to your backend URL
4. Vercel auto-redeploys with new env var

## Common Issues

**CORS Error**: Backend must allow frontend domain
- Add to `backend/app/main.py`:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  
  app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )
  ```

**Network Error**: Check that backend URL matches exactly (no trailing slash)

## Local Development
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
npm run dev
```
Frontend will connect to `localhost:8000` via `.env.local`.
