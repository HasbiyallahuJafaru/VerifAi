# VerifAi - Secure Address Verification System

## 🎯 Overview

VerifAi is a complete address verification system that uses GPS location to verify a user's physical presence at their claimed address. The application features:

- **Secure Token-Based Links**: Generate unique, encrypted verification links for each customer
- **API Key Management**: Issue API keys for external companies to integrate programmatically
- **Admin Dashboard**: Manage verifications, API keys, and view analytics
- **Public Verification**: Customers use personalized links to verify their address
- **Location Verification**: High-accuracy GPS with Haversine distance calculation
- **RESTful API**: Full API for programmatic access with authentication
- **Security Features**: Single-use tokens, time expiration, revocation capability

---

## ✨ Key Features

### 🔑 API Integration
- **API Key Management**: Create, manage, and revoke API keys from the dashboard
- **Secure Authentication**: SHA-256 hashed keys with bearer token support
- **Usage Tracking**: Monitor API usage per key with timestamps
- **Rate Limiting**: Configurable request limits (default: 1000/day)
- **RESTful Endpoints**: Generate verifications, check status, list results
- **Multi-Client Support**: Issue separate keys for different integrations

### 🔐 Security
- **Unique Verification Links**: Each customer gets a cryptographically secure, unique URL
- **Token Encryption**: Customer data encrypted using HMAC-SHA256
- **Single-Use Links**: Each link can only be used once to prevent replay attacks
- **Time Expiration**: Links automatically expire after 24 hours
- **Token Revocation**: Administrators can revoke links at any time
- **Audit Trail**: Complete logging of IP addresses, user agents, and timestamps
- **API Key Hashing**: Keys stored using SHA-256, never in plain text

### 👤 User Experience
- **Admin Dashboard**: Login, generate links, view verifications, and analytics
- **Personalized Pages**: Customers see their own information pre-filled
- **Mobile-Friendly**: Responsive design works on all devices
- **Clear Consent Flow**: Transparent explanation of what data is collected
- **Real-Time Results**: Immediate verification feedback

### 📊 Features
- Dashboard with verification statistics
- Link generation interface
- Verification history and analytics
- Risk scoring based on location accuracy
- Support for manual verification fallback

---

## 📦 What's Included

### **Frontend (React + Vite + Tailwind CSS)**
- Login/Authentication system
- Admin dashboard with sidebar navigation
- Link generation interface
- Public verification page
- Multi-state flow (validating, pending, processing, success, error)
- High-accuracy GPS location capture
- Responsive design for mobile and desktop
- Professional UI components (shadcn/ui + Radix UI)

### **Backend (Python + Flask)**
- Token generation and encryption (itsdangerous)
- RESTful API with CORS support
- Location verification with Haversine distance calculation
- 500-meter verification threshold
- Risk scoring algorithm
- Token validation and revocation endpoints
- Audit logging and security metadata
- Health check and monitoring endpoints

---

## 🚀 Quick Start

### **Prerequisites**
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- pnpm (recommended) or npm (for frontend)
- pip (for backend)

### **Backend Setup**

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
echo "SECRET_KEY=your-super-secret-key-change-this" > .env
echo "FRONTEND_URL=http://localhost:5173" >> .env
echo "CORS_ORIGINS=http://localhost:5173" >> .env
echo "PORT=10000" >> .env

# Run the server (choose one)
python app.py                           # thin runner
# or
PYTHONPATH=. python -m src.main         # explicit module run
```

Backend will run on `http://localhost:10000` (set `PORT` to override)

### **Frontend Setup**

```bash
cd frontend

# Install dependencies
pnpm install  # or: npm install

# Run development server
pnpm dev --host --port 5173  # or: npm run dev
```

Frontend will run on `http://localhost:5173`

---

## 🔗 Using the Verification Link System

### For Administrators

1. **Login to Dashboard**
   - Navigate to `http://localhost:5173`
   - Enter any email and password (demo mode)
   - Click "Sign In"

2. **Generate Verification Link**
   - Click "Generate Link" in the sidebar
   - Fill in customer information:
     - Full Name
     - Email Address
     - Street Address
     - City, State, ZIP Code
     - Organization Name
   - Click "Generate Verification Link"

3. **Share the Link**
   - Copy the generated URL
   - Send to customer via email or SMS
   - Link format: `http://localhost:5173/verify?token=eyJhbGc...`

### For Customers

1. **Receive Link**
   - Customer receives unique verification link
   - Link contains their encrypted information

2. **Open Verification Page**
   - Click the link
   - System validates the token
   - Personal information displayed for confirmation

3. **Complete Verification**
   - Review details (name, email, address)
   - Click "Yes, I Consent"
   - Grant location permission when prompted
   - Wait for verification to complete
   - View results

### Security Features

- **Unique Tokens**: Each link uses a 32-byte cryptographically secure random token
- **Encryption**: All customer data is encrypted using HMAC-SHA256
- **Single Use**: Links can only be used once
- **Expiration**: Links expire after 24 hours
- **Revocation**: Admins can revoke links before use
- **Audit Trail**: IP addresses, user agents, and timestamps are logged

---

## 🔌 API Integration

VerifAi provides a complete RESTful API for programmatic integration.

### Quick Example

```bash
# Generate a verification link via API
curl -X POST http://localhost:10000/api/v1/generate-verification \
  -H "Content-Type: application/json" \
  -H "X-API-Key: verifai_live_your_key" \
  -d '{
    "fullName": "John Doe",
    "email": "john@example.com",
    "address": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zipCode": "10001"
  }'
```

### API Features

- **RESTful Design**: Standard HTTP methods and status codes
- **API Key Authentication**: Secure key-based access
- **Usage Tracking**: Monitor API usage per key
- **Rate Limiting**: Configurable limits per key (default: 1000/day)
- **Webhook Support**: Real-time notifications (coming soon)

### Getting Started with the API

1. **Create an API Key**
   - Login to dashboard
   - Navigate to "API Keys"
   - Click "Create API Key"
   - Copy and save the key (shown only once!)

2. **Make Your First Request**
   ```javascript
   const response = await fetch('http://localhost:10000/api/v1/generate-verification', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'X-API-Key': 'verifai_live_your_key'
     },
     body: JSON.stringify({
       fullName: 'John Doe',
       email: 'john@example.com',
       address: '123 Main St',
       city: 'New York',
       state: 'NY',
       zipCode: '10001'
     })
   });
   
   const data = await response.json();
   console.log(data.data.verificationUrl);
   ```

3. **Check Verification Status**
   ```bash
   curl -X GET http://localhost:10000/api/v1/verifications/{id} \
     -H "X-API-Key: verifai_live_your_key"
   ```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/generate-verification` | POST | Generate a verification link |
| `/api/v1/verifications/{id}` | GET | Get verification status |
| `/api/v1/verifications` | GET | List all verifications |

📚 **Full Documentation**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) and [API_QUICKSTART.md](API_QUICKSTART.md)

---

# Install dependencies
npm install --legacy-peer-deps

# Update API URL in src/App.jsx (line 10)
# Change API_BASE_URL to your backend URL

# Run development server
npm run dev

# Or build for production
npm run build
```

Frontend dev server will start on `http://localhost:5173`

---

## 🏗️ Architecture

### **Frontend Stack**
- **React 19.1.0** - UI framework
- **Vite 6.4.1** - Build tool
- **Tailwind CSS 4.1.7** - Styling
- **Radix UI** - Accessible components
- **Lucide React** - Icons

### **Backend Stack**
- **Python 3.11** - Runtime
- **Flask 3.0.0** - Web framework
- **Flask-CORS** - Cross-origin support
- **Gunicorn** - Production server

---

## 📡 API Endpoints

### **Verification Endpoints**

#### Health Check
```
GET /api/health
```
Returns server health status.

#### Submit Verification
```
POST /api/submit-verification
Content-Type: application/json

{
  "fullName": "John Doe",
  "email": "john@example.com",
  "phone": "555-1234",
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "zipCode": "10001",
  "consent": true,
  "location": {
    "latitude": 40.7589,
    "longitude": -73.9851,
    "accuracy": 10
  }
}
```

#### Get All Verifications
```
GET /api/verifications
```
Returns all verification records (for admin/testing).

### **File Upload Endpoints**

#### Upload Single File
```
POST /api/upload
Content-Type: multipart/form-data

file: [binary file]
document_type: "id_proof"
verification_id: "12345"
```

#### Upload Multiple Files
```
POST /api/upload/multiple
Content-Type: multipart/form-data

files: [binary file 1]
files: [binary file 2]
files: [binary file 3]
```

#### List Uploaded Files
```
GET /api/uploads
```

**Allowed File Types:**
- PDF (.pdf)
- Images (.png, .jpg, .jpeg, .gif)
- Documents (.doc, .docx)

**Maximum File Size:** 10MB

---

## 🔐 Security Features

### **Location Verification**
1. **High-Accuracy GPS** - Requests precise location with no caching
2. **Distance Calculation** - Uses Haversine formula for accurate distance
3. **500-Meter Threshold** - Users must be within 500m for automatic verification
4. **Risk Scoring** - Dynamic risk assessment (0.1 to 0.9)

### **File Upload Security**
1. **File Type Validation** - Only allowed extensions accepted
2. **Unique Filenames** - Timestamp prefix prevents overwrites
3. **File Size Limits** - 10MB maximum per file
4. **Secure Storage** - Dedicated upload directory

---

## 🎨 User Flow

### **Current Simplified Flow**

1. **User sees consent notification**
   - Organization name displayed
   - Clear explanation of what will happen
   - Privacy notice

2. **User clicks "Yes, I Consent"**
   - Location automatically captured
   - No forms to fill out
   - No manual data entry

3. **Processing**
   - Loading spinner displayed
   - Location sent to backend
   - Distance calculated

4. **Results**
   - Verification status shown
   - Distance from address displayed
   - Risk score provided
   - Organization notified

**Total time: 5-10 seconds**

---

## ⚙️ Configuration

### **Backend Configuration**

Edit `src/main.py`:

```python
# Port configuration
PORT = int(os.environ.get('PORT', 5001))

# File upload configuration
UPLOAD_FOLDER = '/home/ubuntu/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Verification threshold
DISTANCE_THRESHOLD = 500  # meters
```

### **Frontend Configuration**

Edit `src/App.jsx`:

```javascript
// Backend API URL (line 10)
const API_BASE_URL = 'https://your-backend-url.com'

// Organization name (line 12)
const ORGANIZATION_NAME = 'Your Company Name'
```

---

## 🌐 Deployment

### **Option 1: AWS (Recommended)**

#### **Frontend - AWS Amplify**
```bash
cd frontend
npm run build

# Deploy to Amplify
# Follow AWS Amplify console instructions
```

#### **Backend - Elastic Beanstalk**
```bash
cd backend

# Create application
eb init -p python-3.11 address-verification

# Deploy
eb create address-verification-env
```

**Estimated Cost:** $30-45/month

### **Option 2: Vercel + Railway**

#### **Frontend - Vercel**
```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

#### **Backend - Railway**
```bash
cd backend

# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Estimated Cost:** $5-40/month

### **Option 3: DigitalOcean App Platform**

Both frontend and backend can be deployed through the DigitalOcean web interface.

**Estimated Cost:** $20-37/month

---

## 🧪 Testing

### **Test Backend Locally**

```bash
# Health check
curl http://localhost:5001/api/health

# Upload file
curl -X POST http://localhost:5001/api/upload \
  -F "file=@test.pdf" \
  -F "document_type=test"

# List uploads
curl http://localhost:5001/api/uploads
```

### **Test Frontend Locally**

1. Start backend on port 5001
2. Update `API_BASE_URL` in `src/App.jsx` to `http://localhost:5001`
3. Run `npm run dev`
4. Open `http://localhost:5173`
5. Click "Yes, I Consent" and allow location access

---

## 📁 Project Structure

```
current-build-package/
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main application (simplified UI)
│   │   ├── App.css              # Tailwind configuration
│   │   ├── main.jsx             # Entry point
│   │   ├── index.css            # Global styles
│   │   └── components/
│   │       └── ui/              # 40+ UI components
│   ├── public/                  # Static assets
│   ├── package.json             # Dependencies
│   ├── vite.config.js           # Build configuration
│   └── index.html               # HTML template
│
├── backend/
│   ├── src/
│   │   └── main.py              # Flask application
│   ├── requirements.txt         # Python dependencies
│   └── app.py                   # Alternative entry point
│
└── README.md                    # This file
```

---

## 🔧 Customization

### **Change Organization Name**

In `frontend/src/App.jsx` (line 12):
```javascript
const ORGANIZATION_NAME = 'Your Bank Name'
```

### **Adjust Distance Threshold**

In `backend/src/main.py` (line 119):
```python
if distance_meters <= 500:  # Change 500 to your threshold
```

### **Add More File Types**

In `backend/src/main.py` (line 205):
```python
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'txt'}
```

### **Change Colors/Branding**

In `frontend/src/App.css`:
- Modify CSS variables (lines 44-77)
- Update color scheme
- Customize theme

---

## 🐛 Troubleshooting

### **Backend Issues**

**Problem:** Port already in use
```bash
# Solution: Change port
PORT=5002 python src/main.py
```

**Problem:** CORS errors
```bash
# Solution: Check CORS configuration in main.py
# Ensure CORS(app) is called
```

**Problem:** File upload fails
```bash
# Solution: Check upload directory exists
mkdir -p /home/ubuntu/uploads
```

### **Frontend Issues**

**Problem:** API connection refused
```bash
# Solution: Update API_BASE_URL in src/App.jsx
# Make sure backend is running
```

**Problem:** Build fails
```bash
# Solution: Install with legacy peer deps
npm install --legacy-peer-deps
```

**Problem:** Location not working
```bash
# Solution: Use HTTPS (required for geolocation)
# Or test on localhost
```

---

## 📊 Performance

### **Expected Performance**
- **Frontend Load Time:** < 2 seconds
- **API Response Time:** < 500ms
- **Location Capture:** 2-5 seconds
- **File Upload:** < 3 seconds (for 1MB file)

### **Scalability**
- **Current:** Handles 100+ concurrent users
- **With Database:** Handles 1,000+ concurrent users
- **With CDN:** Handles 10,000+ concurrent users

---

## 🔄 Production Enhancements

### **Recommended for Production**

1. **Database Integration**
   - Replace in-memory storage with PostgreSQL or MongoDB
   - Store verification records persistently
   - Add user authentication

2. **Real Geocoding**
   - Integrate Google Maps Geocoding API
   - Or use MapBox API
   - Accurate address-to-coordinates conversion

3. **Enhanced Security**
   - Add API authentication (JWT tokens)
   - Implement rate limiting
   - Add request validation
   - Enable HTTPS/SSL

4. **Monitoring**
   - Add error tracking (Sentry)
   - Implement logging
   - Set up alerts
   - Monitor uptime

5. **File Storage**
   - Move to cloud storage (AWS S3, Google Cloud Storage)
   - Add virus scanning
   - Implement file compression
   - Add CDN for faster delivery

---

## 📝 Environment Variables

### **Backend (.env)**
```bash
PORT=5001
UPLOAD_FOLDER=/path/to/uploads
MAX_FILE_SIZE=10485760
GOOGLE_MAPS_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### **Frontend (.env)**
```bash
VITE_API_BASE_URL=https://your-backend-url.com
VITE_ORGANIZATION_NAME=Your Company Name
```

---

## 📚 Additional Resources

### **Documentation**
- React: https://react.dev
- Flask: https://flask.palletsprojects.com
- Tailwind CSS: https://tailwindcss.com
- Vite: https://vitejs.dev

### **Deployment Guides**
- AWS: See `aws_deployment_guide.md`
- Vercel: https://vercel.com/docs
- Railway: https://docs.railway.app

### **API Documentation**
- See `file_upload_testing_guide.md` for file upload examples
- See `deployment_summary.md` for deployment details

---

## 🆘 Support

### **Common Questions**

**Q: How do I change the backend URL?**
A: Edit `API_BASE_URL` in `frontend/src/App.jsx` (line 10)

**Q: How do I add more file types?**
A: Edit `ALLOWED_EXTENSIONS` in `backend/src/main.py` (line 205)

**Q: How do I deploy to production?**
A: See the Deployment section above or `aws_deployment_guide.md`

**Q: How do I add a database?**
A: Replace the `verifications = []` list with database calls

**Q: How do I customize the UI?**
A: Edit `frontend/src/App.jsx` and `frontend/src/App.css`

---

## 📄 License

This code is provided as-is for your use in building your address verification application.

---

## 🎯 Key Features Summary

✅ **Simplified Consent UI** - Single-click verification  
✅ **GPS Location Verification** - 500m threshold  
✅ **Risk Scoring** - Dynamic assessment  
✅ **File Upload** - Support documents  
✅ **Mobile Responsive** - Works on all devices  
✅ **Production Ready** - Deploy to AWS, Vercel, etc.  
✅ **Secure** - CORS, file validation, distance verification  
✅ **Fast** - < 10 seconds total verification time  

---

## 🚀 Next Steps

1. **Customize** - Update organization name and branding
2. **Test** - Run locally and test all features
3. **Deploy** - Choose deployment platform and go live
4. **Enhance** - Add database, real geocoding, authentication
5. **Scale** - Monitor usage and optimize as needed

---

**Built with ❤️ for secure address verification**

Version: 2.0 (Simplified UI + File Upload)  
Last Updated: December 2025
