# VerifAi - System Architecture

## User Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ADMINISTRATOR FLOW                           │
└─────────────────────────────────────────────────────────────────────┘

1. Login to Dashboard
   └→ http://verifai.app/login
      └→ Enter credentials
         └→ Redirect to /dashboard

2. Generate Verification Link
   └→ Click "Generate Link" in sidebar
      └→ Enter customer information:
         • Name: John Doe
         • Email: john@example.com
         • Address: 123 Main St, New York, NY 10001
         • Organization: ABC Bank
      └→ Backend generates:
         • Unique Token ID (32-byte random)
         • Encrypted token with customer data
         • Verification URL: verifai.app/verify?token={encrypted}
      └→ Admin copies and sends link to customer


┌─────────────────────────────────────────────────────────────────────┐
│                           CUSTOMER FLOW                              │
└─────────────────────────────────────────────────────────────────────┘

1. Receive Link
   └→ Email or SMS: "Click here to verify your address"
      └→ Link: https://verifai.app/verify?token=eyJhbGc...

2. Click Link
   └→ Opens verification page
      └→ Frontend extracts token from URL
      └→ Sends token to backend for validation

3. Token Validation
   └→ Backend checks:
      ✓ Is signature valid?
      ✓ Has token expired? (24hr limit)
      ✓ Has token been used?
      ✓ Is token revoked?
   └→ If valid: Return decrypted customer data
   └→ If invalid: Show error page

4. Review Personalized Page
   └→ Customer sees their information:
      • Name: John Doe
      • Email: john@example.com
      • Address to verify: 123 Main St, New York, NY 10001
      • Organization: ABC Bank
   └→ Security notice: "This link is unique to you"

5. Grant Consent
   └→ Customer clicks "Yes, I Consent"
      └→ Browser requests location permission
      └→ Customer grants permission

6. Location Verification
   └→ Browser gets GPS coordinates
   └→ Sends to backend with token:
      • Latitude: 40.7589
      • Longitude: -73.9851
      • Accuracy: 10 meters
      • User agent, timezone, etc.
   └→ Backend:
      • Marks token as "used"
      • Geocodes address to coordinates
      • Calculates distance between GPS and address
      • Generates risk score
      • Stores verification record

7. Results
   └→ Customer sees confirmation:
      ✓ Verification Complete
      ✓ Status: VERIFIED
      ✓ Distance from address: 15m
      ✓ Risk Score: 10%
   └→ Organization notified


┌─────────────────────────────────────────────────────────────────────┐
│                          SECURITY LAYERS                             │
└─────────────────────────────────────────────────────────────────────┘

Layer 1: Unique Token Generation
├─ 32-byte random token ID
├─ 256 bits of entropy
└─ Cryptographically secure

Layer 2: Encryption
├─ Customer data encrypted in token
├─ HMAC-SHA256 signature
├─ Secret key (environment variable)
└─ Tamper-proof

Layer 3: Time Expiration
├─ Timestamp embedded in token
├─ 24-hour validity
└─ Server-side validation

Layer 4: Single-Use
├─ Token marked as "used" after verification
├─ Prevents replay attacks
└─ Database tracking

Layer 5: Revocation
├─ Admin can invalidate tokens
├─ Immediate effect
└─ Audit trail

Layer 6: Metadata Collection
├─ IP address logging
├─ User agent capture
├─ Device fingerprinting
└─ Fraud detection


┌─────────────────────────────────────────────────────────────────────┐
│                         TOKEN STRUCTURE                              │
└─────────────────────────────────────────────────────────────────────┘

Encrypted Token (URL-safe):
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbklk...

Decrypted Payload:
  {
    "tokenId": "abc123xyz789...",
    "fullName": "John Doe",
    "email": "john@example.com",
    "address": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zipCode": "10001",
    "organizationName": "ABC Bank",
    "createdAt": "2025-12-21T10:00:00",
    "expiresIn": "24 hours"
  }

Metadata (Database):
  {
    "token": "eyJhbGc...",
    "email": "john@example.com",
    "fullName": "John Doe",
    "organizationName": "ABC Bank",
    "createdAt": "2025-12-21T10:00:00",
    "expiresAt": "2025-12-22T10:00:00",
    "used": false,
    "usedAt": null,
    "status": "active"
  }


┌─────────────────────────────────────────────────────────────────────┐
│                         API ENDPOINTS                                │
└─────────────────────────────────────────────────────────────────────┘

Admin (Protected):
├─ POST /api/generate-verification-link
│  └─ Input: Customer information
│  └─ Output: Unique verification URL
│
├─ POST /api/revoke-token
│  └─ Input: Token ID
│  └─ Output: Success confirmation
│
└─ GET /api/verification-tokens
   └─ Output: List of all tokens

Public (No Auth):
├─ POST /api/validate-token
│  └─ Input: Encrypted token
│  └─ Output: Customer data (if valid)
│
├─ POST /api/submit-verification
│  └─ Input: Token + GPS coordinates
│  └─ Output: Verification results
│
└─ POST /api/verification-declined
   └─ Input: Token
   └─ Output: Declined recorded


┌─────────────────────────────────────────────────────────────────────┐
│                      VERIFICATION STATES                             │
└─────────────────────────────────────────────────────────────────────┘

Token States:
├─ active: Link generated, not yet used
├─ completed: Verification successful
├─ declined: Customer declined
└─ revoked: Admin canceled

Verification States:
├─ verified: GPS matches address (≤500m)
├─ requires_review: GPS distant from address (>500m)
├─ requires_manual_verification: No GPS data
└─ declined_by_user: Customer declined consent


┌─────────────────────────────────────────────────────────────────────┐
│                     DISTANCE CALCULATION                             │
└─────────────────────────────────────────────────────────────────────┘

Haversine Formula:
1. Get customer GPS coordinates (latitude, longitude)
2. Geocode registered address to coordinates
3. Calculate great-circle distance
4. Determine risk score:
   ├─ ≤100m  → Risk: 10% (Very Low)
   ├─ ≤500m  → Risk: 30% (Low)
   ├─ ≤1000m → Risk: 50% (Medium)
   ├─ ≤5000m → Risk: 70% (High)
   └─ >5000m → Risk: 90% (Very High)


┌─────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────────┘

Frontend (Netlify):
├─ React + Vite
├─ Routing: React Router
├─ UI: Shadcn/ui + Tailwind
└─ Routes:
   ├─ /login (public)
   ├─ /verify (public)
   └─ /dashboard/* (protected)

Backend (Render):
├─ Python + Flask
├─ Token encryption: itsdangerous
├─ CORS enabled
└─ Endpoints: /api/*

Database (Future):
├─ PostgreSQL for production
├─ Store: tokens, verifications, audit logs
└─ Currently: In-memory (demo)


┌─────────────────────────────────────────────────────────────────────┐
│                       COMPLIANCE & PRIVACY                           │
└─────────────────────────────────────────────────────────────────────┘

GDPR Compliance:
✓ Explicit consent required
✓ Purpose limitation (address verification only)
✓ Data minimization (only necessary fields)
✓ Right to revoke (token revocation)
✓ Data security (encryption)

CCPA Compliance:
✓ Consumer rights respected
✓ Data security measures
✓ Opt-out capability

TCPA Compliance:
✓ Prior consent for verification request
✓ Clear purpose communication
```

## Quick Reference

### Generate Link
```bash
curl -X POST http://localhost:10000/api/generate-verification-link \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "John Doe",
    "email": "john@example.com",
    "address": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zipCode": "10001",
    "organizationName": "ABC Bank"
  }'
```

### Validate Token
```bash
curl -X POST http://localhost:10000/api/validate-token \
  -H "Content-Type: application/json" \
  -d '{"token": "eyJhbGc..."}'
```

### Submit Verification
```bash
curl -X POST http://localhost:10000/api/submit-verification \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGc...",
    "consent": true,
    "location": {
      "latitude": 40.7589,
      "longitude": -73.9851,
      "accuracy": 10
    }
  }'
```
