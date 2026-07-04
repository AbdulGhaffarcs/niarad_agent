# NIARAD Full-Stack Deployment Guide (Vercel + Render)

## Overview

This guide walks you through deploying NIARAD:
- **Frontend:** Vercel (Next.js)
- **Backend:** Render (Python/FastAPI)

Both platforms have generous free tiers. Estimated cost: **$0-5/month**

---

## Part 1: Deploy Backend to Render

### Prerequisites
- Render account: https://render.com (free)
- GitHub repository pushed (already done ✅)
- Groq API key: https://console.groq.com (free)

### Step 1: Create Render Web Service

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Select **"Build and deploy from a Git repository"**
4. Click **"Connect account"** and authorize GitHub
5. Select **`AbdulGhaffarcs/niarad_agent`** repository

### Step 2: Configure Deployment Settings

| Setting | Value |
|---------|-------|
| **Name** | `niarad-backend` |
| **Region** | Choose closest to you (e.g., US) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

### Step 3: Add Environment Variables

In the **Environment** section:

1. Click **"Add Environment Variable"**
2. Add:
   - **Key:** `GROQ_API_KEY`
   - **Value:** `your_actual_groq_api_key_here` (paste from console.groq.com)
3. Click **"Add Environment Variable"** again for Python version:
   - **Key:** `PYTHON_VERSION`
   - **Value:** `3.10`

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will build and deploy (takes 3-5 minutes)
3. When complete, you'll see:
   ```
   ✓ Your service is live at https://niarad-backend.onrender.com
   ```

**Save this URL!** You'll need it for the frontend.

---

## Part 2: Deploy Frontend to Vercel

### Prerequisites
- Vercel account: https://vercel.com (free)
- Your Render backend URL (from Part 1)

### Step 1: Deploy to Vercel

1. Go to https://vercel.com/new
2. Click **"Import Git Repository"**
3. Authorize GitHub and select **`niarad_agent`**
4. Configure:
   - **Project Name:** `niarad-frontend` (or any name)
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

### Step 2: Add Environment Variables

Before deploying, add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://niarad-backend.onrender.com` (your Render URL) |

### Step 3: Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build to complete
3. You'll get a Vercel URL: `https://niarad-frontend.vercel.app`

---

## Part 3: Update Backend CORS

Now that you have your Vercel frontend URL, update the backend to allow requests:

### Edit `backend/main.py`

Find this section (around line 21):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Update to:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://niarad-frontend.vercel.app"  # Your exact Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Push the change:

```bash
git add backend/main.py
git commit -m "Update CORS for Vercel frontend"
git push
```

**Render will auto-redeploy** within 1 minute.

---

## Part 4: Test Your Deployment

### Test Backend API

1. Open: `https://niarad-backend.onrender.com/`
2. Should see:
   ```json
   {"status": "NIARAD Agent API online", "version": "3.1.0"}
   ```

### Test Frontend

1. Open: `https://niarad-frontend.vercel.app`
2. Try the **Chat** tab:
   - Type: "What is 2+2?"
   - Should see agent response

### Test File Upload (Vault)

1. Go to **Vault** tab
2. Upload a PDF or DOCX
3. Should process and index

### Test Study Loop

1. Go to **Study** tab
2. Click "Generate Cards"
3. Should create flashcards

---

## Troubleshooting

### Backend shows "Service is sleeping"

**Why:** Render free tier auto-suspends after 15 minutes of inactivity.

**Fix:** Click the URL again; it wakes up in ~30 seconds. For production, upgrade to Render Paid ($7/month).

### CORS errors in browser console

**Error:** `Access to XMLHttpRequest from origin 'https://niarad-frontend.vercel.app' has been blocked`

**Fix:**
1. Check your Vercel URL is correct
2. Update `backend/main.py` CORS as shown in Part 3
3. Push the change; Render auto-redeploys

### Groq API 401 (Unauthorized)

**Error:** `Invalid API key provided`

**Fix:**
1. Go to Render dashboard → Your service
2. Click **Environment**
3. Verify `GROQ_API_KEY` is set correctly
4. Re-trigger deployment: Click **Manual Deploy** → **Deploy Latest Commit**

### File uploads fail

**Why:** Render free tier has ephemeral storage (files disappear on restart).

**Fix:** For production, add a persistent disk (see `render.yaml`).

### Frontend won't load

**Why:** `NEXT_PUBLIC_API_URL` not set or incorrect.

**Fix:**
1. Go to Vercel → Project Settings → Environment Variables
2. Verify `NEXT_PUBLIC_API_URL` = `https://niarad-backend.onrender.com`
3. Redeploy: Deployments → Latest → Redeploy

---

## Production Upgrades

When you're ready for production:

### Backend (Render)

- **Upgrade to Paid ($7/month):** Always-on, no cold starts
- **Add PostgreSQL:** Replace SQLite for multi-instance
- **Add persistent disk:** Store FAISS index, uploads, generated files

### Frontend (Vercel)

- Already production-ready; no upgrade needed
- Optional: Custom domain ($12/year)

---

## Cost Summary

| Service | Free Tier | Paid Tier | Status |
|---------|-----------|-----------|--------|
| Vercel (Frontend) | ✅ Unlimited | Not needed | Free forever |
| Render (Backend) | ✅ Auto-sleep | $7/month | Free + optional upgrade |
| Groq API | ✅ Free tier | Pay-as-you-go | Free tier sufficient |
| **Total** | **$0/month** | **$7/month (optional)** | ✅ |

---

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Deploy frontend to Vercel
3. ✅ Update CORS in backend
4. ✅ Test all features
5. ⏭️ (Optional) Upgrade to production tiers

**Questions?** Check the README.md or Render/Vercel docs.
