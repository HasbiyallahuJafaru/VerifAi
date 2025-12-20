# VerifAi - Quick Start

## Local Development

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python src/main.py
```
Backend runs on: http://localhost:10000

### Frontend Setup
```bash
cd frontend
pnpm install
pnpm dev
```
Frontend runs on: http://localhost:5173

Set environment variable before running frontend:
```bash
# Windows PowerShell
$env:VITE_API_URL="http://localhost:10000"

# Linux/Mac
export VITE_API_URL=http://localhost:10000
```

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions.

Quick summary:
1. **Backend** → Deploy to Render
2. **Frontend** → Deploy to Netlify
3. Update environment variables to point to production URLs

## Project Structure

```
├── backend/
│   ├── src/
│   │   └── main.py          # Main Flask application
│   ├── wsgi.py              # WSGI entry point for production
│   ├── requirements.txt     # Python dependencies
│   └── render.yaml          # Render deployment config
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   └── config.js        # API configuration
│   ├── netlify.toml         # Netlify deployment config
│   └── package.json         # Node dependencies
└── DEPLOYMENT.md            # Deployment guide
```
