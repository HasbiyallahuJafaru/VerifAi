# Deployment Authentication Fixes

## Issues Found and Fixed

### 1. **Missing Environment Variables in Render**
The backend deployment was missing critical environment variables:
- `BACKEND_URL` - Required for the backend to know its own URL
- `SECRET_KEY` - Required for session security (was using dev key)
- `JWT_SECRET` - Required for JWT token signing (was using dev key)
- `DATABASE_URL` - Required for PostgreSQL database connection
- `FLASK_ENV` - Should be set to "production"

### 2. **CORS Configuration Issues**
- Missing explicit CORS headers configuration
- Not properly configured for credentials support
- Missing Authorization header in allowed headers

### 3. **Frontend API Call Issues**
- Missing `credentials: 'include'` in fetch requests
- Missing Authorization headers in protected API endpoints
- API Keys management was not sending JWT tokens

## Applied Fixes

### Backend Changes

#### 1. Updated `render.yaml`
```yaml
services:
  - type: web
    name: verifai-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn wsgi:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        value: 10000
      - key: PYTHONPATH
        value: .
      - key: FLASK_ENV
        value: production
      - key: BACKEND_URL
        value: https://verifai-backend-owak.onrender.com
      - key: FRONTEND_URL
        value: https://verifai.netlify.app
      - key: CORS_ORIGINS
        value: https://verifai.netlify.app
      - key: SECRET_KEY
        generateValue: true  # Auto-generates secure secret
      - key: JWT_SECRET
        generateValue: true  # Auto-generates secure secret
      - key: DATABASE_URL
        fromDatabase:
          name: verifai-db
          property: connectionString
    healthCheckPath: /api/health

databases:
  - name: verifai-db
    databaseName: verifai
    user: verifai
```

#### 2. Updated `app_factory.py`
Enhanced CORS configuration with explicit headers:
```python
CORS(
    app,
    origins=settings.cors_origins,
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)
```

### Frontend Changes

#### 1. Updated `Login.jsx`
Added credentials to fetch requests:
```javascript
const apiCall = async (path, body) => {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',  // Added this
    body: JSON.stringify(body)
  })
  // ... rest of code
}
```

#### 2. Updated `ApiKeys.jsx`
Added Authorization headers to all API key management calls:
```javascript
// All fetch calls now include:
headers: {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`
}
```

## Deployment Steps

### Step 1: Push Changes to Git
```bash
git add .
git commit -m "Fix authentication issues for production deployment"
git push origin main
```

### Step 2: Redeploy Backend on Render
1. Go to https://dashboard.render.com
2. Select your `verifai-backend` service
3. Click "Manual Deploy" → "Deploy latest commit"
4. Wait for deployment to complete (~3-5 minutes)

### Step 3: Create PostgreSQL Database (if not exists)
1. In Render dashboard, click "New +" → "PostgreSQL"
2. Name: `verifai-db`
3. Database Name: `verifai`
4. User: `verifai`
5. Click "Create Database"
6. The `DATABASE_URL` will be automatically linked to your backend service

### Step 4: Verify Environment Variables
In Render dashboard → verifai-backend → Environment:
- Confirm `SECRET_KEY` has a generated value
- Confirm `JWT_SECRET` has a generated value
- Confirm `DATABASE_URL` is linked to the database
- Confirm all URLs match your deployment

### Step 5: Redeploy Frontend on Netlify
```bash
cd frontend
pnpm install
pnpm build
# Or commit and push - Netlify will auto-deploy
```

Or manually in Netlify:
1. Go to https://app.netlify.com
2. Select your `verifai` site
3. Click "Deploys" → "Trigger deploy" → "Deploy site"

### Step 6: Test Authentication
1. Open https://verifai.netlify.app
2. Try logging in with any email/password
3. Check browser console for any CORS errors
4. Verify you can access dashboard after login
5. Test generating verification links
6. Test API key management

## Troubleshooting

### If login still fails:

1. **Check Browser Console**
   ```
   F12 → Console tab
   Look for CORS or 401/403 errors
   ```

2. **Check Render Logs**
   ```
   Render Dashboard → verifai-backend → Logs
   Look for JWT errors or database connection issues
   ```

3. **Verify Environment Variables**
   ```bash
   # In Render dashboard, check all env vars are set
   # Especially: SECRET_KEY, JWT_SECRET, DATABASE_URL
   ```

4. **Test Backend Health**
   ```
   Visit: https://verifai-backend-owak.onrender.com/api/health
   Should return: {"status": "healthy", "timestamp": "..."}
   ```

5. **Clear Browser Cache**
   ```
   F12 → Application → Clear site data
   Then try logging in again
   ```

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Failed to fetch" | Backend down or CORS issue | Check Render deployment status and logs |
| "Authentication failed" | JWT secret mismatch | Redeploy backend with new JWT_SECRET |
| "401 Unauthorized" | Token not being sent | Check Authorization header in Network tab |
| "Database connection error" | DATABASE_URL not set | Link PostgreSQL database in Render |
| "CORS policy error" | Frontend URL not in CORS_ORIGINS | Update CORS_ORIGINS in Render env vars |

## Security Notes

✅ **Production secrets are now auto-generated** - No more dev keys!
✅ **Database uses PostgreSQL** - Not SQLite anymore
✅ **CORS properly configured** - Only allows your frontend
✅ **JWT tokens properly validated** - Signed with secure secret

## Next Steps

After successful deployment:

1. **Create an admin user** (first login creates user automatically)
2. **Generate API keys** for programmatic access
3. **Test verification flow** end-to-end
4. **Monitor logs** for any errors in production
5. **Set up monitoring** (optional: Render provides basic monitoring)

## Environment Variables Reference

### Required for Production

| Variable | Value | Source |
|----------|-------|--------|
| `FLASK_ENV` | `production` | Manual |
| `PORT` | `10000` | Manual |
| `BACKEND_URL` | `https://verifai-backend-owak.onrender.com` | Manual |
| `FRONTEND_URL` | `https://verifai.netlify.app` | Manual |
| `CORS_ORIGINS` | `https://verifai.netlify.app` | Manual |
| `SECRET_KEY` | Auto-generated | Render |
| `JWT_SECRET` | Auto-generated | Render |
| `DATABASE_URL` | PostgreSQL connection string | Render Database |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `UPLOAD_FOLDER` | `/tmp/uploads` | Where uploaded files are stored |
| `MAX_FILE_SIZE_MB` | `10` | Maximum file upload size |
