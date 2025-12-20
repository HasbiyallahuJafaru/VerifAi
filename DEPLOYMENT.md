# VerifAi Deployment Guide

This guide will help you deploy VerifAi's address verification system to production.

## Architecture
- **Frontend**: React + Vite → Netlify
- **Backend**: Flask API → Render

## Prerequisites
- GitHub account
- Netlify account
- Render account

---

## 📦 Backend Deployment (Render)

### Step 1: Prepare Repository
1. Push your code to GitHub (if not already done)
2. Ensure all files are committed

### Step 2: Create Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

   **Basic Settings:**
   - **Name**: `verifai-backend` (or your choice)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your primary branch)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`

   **Build & Deploy:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`

### Step 3: Set Environment Variables
In Render's Environment section, add:

```
PORT=10000
FLASK_ENV=production
CORS_ORIGINS=https://your-app-name.netlify.app
```

> ⚠️ **Important**: Replace `your-app-name.netlify.app` with your actual Netlify URL after frontend deployment

### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (usually 2-5 minutes)
3. Note your backend URL: `https://verifai-backend.onrender.com`

### Step 5: Verify Backend
Test your API:
```bash
curl https://verifai-backend.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-20T..."
}
```

---

## 🌐 Frontend Deployment (Netlify)

### Step 1: Create Netlify Site
1. Go to [Netlify Dashboard](https://app.netlify.com/)
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect to your GitHub repository
4. Configure build settings:

   **Build Settings:**
   - **Base directory**: `frontend`
   - **Build command**: `pnpm install && pnpm build`
   - **Publish directory**: `frontend/dist`

### Step 2: Set Environment Variables
In Netlify's **Site settings** → **Environment variables**, add:

```
VITE_API_URL=https://verifai-backend.onrender.com
```

> ⚠️ **Important**: Replace with your actual Render backend URL from Step 4 above

### Step 3: Deploy
1. Click **"Deploy site"**
2. Wait for deployment (usually 1-3 minutes)
3. Note your frontend URL: `https://your-app-name.netlify.app`

### Step 4: Update Backend CORS
1. Go back to Render dashboard
2. Update the `CORS_ORIGINS` environment variable with your actual Netlify URL:
   ```
   CORS_ORIGINS=https://your-app-name.netlify.app
   ```
3. Render will automatically redeploy

---

## ✅ Final Testing

### Test Complete Flow
1. Visit your Netlify URL: `https://your-app-name.netlify.app`
2. Click **"Yes, I Consent"**
3. Allow location access when prompted
4. Verify that the verification completes successfully

### Common Issues & Solutions

#### Issue: CORS Error
**Symptom**: "Access to fetch... has been blocked by CORS policy"

**Solution**: 
- Verify `CORS_ORIGINS` in Render matches your Netlify URL exactly
- Ensure no trailing slash in URL
- Wait for Render to redeploy after changing environment variables

#### Issue: API Not Found
**Symptom**: "Failed to fetch" or 404 errors

**Solution**:
- Verify `VITE_API_URL` in Netlify is correct
- Check that backend is running on Render
- Ensure API endpoints start with `/api/`

#### Issue: Location Permission Denied
**Symptom**: "Location access denied" error

**Solution**:
- Ensure site is served over HTTPS (Netlify provides this automatically)
- Check browser location permissions
- Try in a different browser

---

## 🔒 Security Considerations

### Production Checklist
- [ ] Backend uses environment-based CORS (✅ Already configured)
- [ ] Frontend uses environment variables for API URL (✅ Already configured)
- [ ] HTTPS enabled on both frontend and backend (✅ Netlify & Render provide this)
- [ ] Debug mode disabled in production (✅ Already configured)
- [ ] Sensitive data not committed to git

### Recommended Improvements
For production use, consider:

1. **Database**: Replace in-memory storage with PostgreSQL or MongoDB
2. **Authentication**: Add API key validation
3. **Rate Limiting**: Prevent API abuse
4. **Monitoring**: Set up error tracking (Sentry, LogRocket)
5. **Real Geocoding**: Use Google Maps API or Mapbox for accurate geocoding

---

## 📊 Monitoring

### Render Monitoring
- View logs: Render Dashboard → Your Service → Logs
- Monitor health: `/api/health` endpoint
- Set up alerts for downtime

### Netlify Monitoring
- View deployment logs: Netlify Dashboard → Deploys
- Monitor performance: Analytics tab
- Set up form notifications for errors

---

## 🚀 CI/CD (Automatic Deployments)

Both Netlify and Render support automatic deployments:

### Auto-Deploy on Git Push
- **Render**: Automatically deploys when you push to main branch
- **Netlify**: Automatically deploys when you push to main branch

To trigger a deployment:
```bash
git add .
git commit -m "Update verification logic"
git push origin main
```

Both services will automatically rebuild and deploy within 2-5 minutes.

---

## 📝 Environment Variables Summary

### Backend (Render)
```env
PORT=10000
FLASK_ENV=production
CORS_ORIGINS=https://your-app-name.netlify.app
```

### Frontend (Netlify)
```env
VITE_API_URL=https://verifai-backend.onrender.com
```

---

## 🆘 Support

### Render Support
- [Documentation](https://render.com/docs)
- [Community Forum](https://community.render.com/)

### Netlify Support
- [Documentation](https://docs.netlify.com/)
- [Community Forum](https://answers.netlify.com/)

---

## 🎉 You're Done!

Your VerifAi system is now deployed and ready for production use!

**Frontend**: https://your-app-name.netlify.app  
**Backend**: https://verifai-backend.onrender.com

Remember to update these URLs in your documentation and share them with your users.
