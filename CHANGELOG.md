# Changelog

All notable changes to the Address Verification Application.

## [2.0.0] - 2025-12-16

### 🎉 Major Changes

#### Simplified UI (Customer Feedback Implementation)
- **BREAKING:** Removed multi-step form
- **NEW:** Single-screen consent notification
- **NEW:** One-click verification flow
- **IMPROVED:** Reduced verification time from 2-3 minutes to 5-10 seconds
- **IMPROVED:** Mobile-optimized design

#### File Upload Feature
- **NEW:** Single file upload endpoint (`POST /api/upload`)
- **NEW:** Multiple file upload endpoint (`POST /api/upload/multiple`)
- **NEW:** List uploaded files endpoint (`GET /api/uploads`)
- **NEW:** Support for PDF, images, and documents
- **NEW:** 10MB file size limit
- **NEW:** Automatic filename uniqueness with timestamps

### ✨ Features Added

#### Frontend
- Simplified consent-based UI
- Organization name display
- Clear privacy notice
- Professional loading states
- Better error handling
- Improved mobile responsiveness

#### Backend
- File upload with validation
- Secure file storage
- File type restrictions
- Error handling for uploads
- Upload history tracking

### 🔧 Technical Improvements
- Updated Flask CORS configuration
- Added werkzeug for secure filenames
- Improved error messages
- Better API response formats
- Enhanced security features

### 📝 Documentation
- Complete README with setup instructions
- File upload testing guide
- AWS deployment guide
- Production checklist
- API documentation

---

## [1.0.0] - 2025-12-05

### Initial Release

#### Core Features
- Multi-step verification form
- GPS location capture
- Distance calculation (Haversine formula)
- 500-meter verification threshold
- Risk scoring algorithm
- CORS-enabled API
- React frontend with Tailwind CSS
- Flask backend with Python 3.11

#### Endpoints
- `GET /api/health` - Health check
- `POST /api/submit-verification` - Submit verification
- `GET /api/verifications` - List verifications

#### Security Features
- High-accuracy GPS location
- Distance-based verification
- Risk assessment
- Consent collection
- CORS protection

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 2.0.0 | 2025-12-16 | Simplified UI + File Upload |
| 1.0.0 | 2025-12-05 | Initial Release |

---

## Upgrade Guide

### From 1.0.0 to 2.0.0

#### Frontend Changes
The UI has been completely redesigned. If you customized the old multi-step form:

**Old (v1.0.0):**
```javascript
// Multi-step form with 4 steps
<Step1 /> // Personal info
<Step2 /> // Location
<Step3 /> // Review
<Step4 /> // Results
```

**New (v2.0.0):**
```javascript
// Single consent screen
<ConsentNotification />
<ProcessingScreen />
<ResultsScreen />
```

#### Backend Changes
New file upload endpoints added. No breaking changes to existing endpoints.

**Migration Steps:**
1. Update frontend code to new App.jsx
2. Update backend to include file upload endpoints
3. Create upload directory: `mkdir -p /home/ubuntu/uploads`
4. Test file upload functionality
5. Update API documentation

---

## Breaking Changes

### v2.0.0
- **Frontend:** Complete UI redesign - old form components removed
- **Frontend:** Organization name now required (hardcoded or from URL params)
- **Frontend:** Removed manual form input fields

### Non-Breaking Changes
- All v1.0.0 API endpoints still work
- Backend is backward compatible
- File upload is additive (optional feature)

---

## Planned Features

### v2.1.0 (Planned)
- [ ] Database integration (PostgreSQL)
- [ ] Real geocoding API (Google Maps)
- [ ] User authentication
- [ ] Admin dashboard
- [ ] Email notifications

### v2.2.0 (Planned)
- [ ] Multi-language support
- [ ] Custom branding per organization
- [ ] Advanced analytics
- [ ] Webhook support
- [ ] API rate limiting

### v3.0.0 (Future)
- [ ] Mobile app (React Native)
- [ ] Biometric verification
- [ ] Document OCR
- [ ] Blockchain verification records
- [ ] AI-powered fraud detection
