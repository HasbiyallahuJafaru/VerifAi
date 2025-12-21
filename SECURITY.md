# Secure Verification Link System

## Overview

VerifAi now includes a secure, token-based verification link system that allows organizations to send personalized verification links to customers. Each link is unique, encrypted, and designed to prevent fraud and unauthorized access.

## Security Features

### 1. **Unique Token Generation**
- Each verification link contains a cryptographically secure token generated using `secrets.token_urlsafe(32)`
- Tokens are 32 bytes of random data, providing 256 bits of entropy
- Each customer receives a completely unique link that cannot be guessed or brute-forced

### 2. **Token Encryption & Signing**
- Tokens are encrypted and signed using `itsdangerous.URLSafeTimedSerializer`
- Uses HMAC-SHA256 for signature verification
- Prevents tampering - any modification to the token invalidates it
- Secret key (stored in environment variable) is required to generate valid tokens

### 3. **Time-Based Expiration**
- Links automatically expire after 24 hours (configurable)
- Timestamp is embedded in the encrypted token
- Server validates expiration on every use
- Expired links are rejected with clear error messages

### 4. **Single-Use Tokens**
- Each token can only be used once
- After successful verification, token is marked as "used"
- Prevents replay attacks and link sharing
- Attempted reuse results in immediate rejection

### 5. **Personalized Data Binding**
- Customer information (name, email, address) is encrypted within the token
- Verifies that the person using the link matches the intended recipient
- Address information pre-populated from token ensures verification accuracy
- Prevents one customer from using another's link

### 6. **Token Revocation**
- Administrators can revoke tokens before they're used
- Revoked tokens are immediately invalidated
- Useful for canceling pending verifications or responding to security concerns

### 7. **Additional Security Metadata**
- IP address logging
- User agent capture
- Screen resolution tracking
- Timezone information
- Helps detect suspicious activity and fraud patterns

## How It Works

### Link Generation Flow

```
1. Admin enters customer information in dashboard
   ↓
2. System generates unique token ID (32-byte random)
   ↓
3. Customer data encrypted and signed with secret key
   ↓
4. Token embedded in verification URL
   ↓
5. Link sent to customer (email/SMS)
```

### Verification Flow

```
1. Customer clicks link (e.g., verifai.app/verify?token=xxx)
   ↓
2. Frontend extracts token from URL
   ↓
3. Token validated with backend
   ↓
4. Backend decrypts token and checks:
   - Is signature valid?
   - Has token expired?
   - Has token been used?
   - Is token revoked?
   ↓
5. If valid: Display personalized verification page
   If invalid: Show error with explanation
   ↓
6. Customer grants location permission
   ↓
7. GPS coordinates sent with token to backend
   ↓
8. Backend verifies location matches address
   ↓
9. Token marked as "used"
   ↓
10. Results sent to organization
```

## API Endpoints

### Generate Verification Link
```
POST /api/generate-verification-link
```

**Request:**
```json
{
  "fullName": "John Doe",
  "email": "john@example.com",
  "address": "123 Main Street",
  "city": "New York",
  "state": "NY",
  "zipCode": "10001",
  "organizationName": "ABC Bank"
}
```

**Response:**
```json
{
  "status": "success",
  "tokenId": "abc123...",
  "verificationUrl": "https://verifai.app/verify?token=eyJhbGc...",
  "expiresAt": "2025-12-22T10:00:00",
  "expiresIn": "24 hours",
  "recipient": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

### Validate Token
```
POST /api/validate-token
```

**Request:**
```json
{
  "token": "eyJhbGc..."
}
```

**Response:**
```json
{
  "status": "success",
  "verification_data": {
    "fullName": "John Doe",
    "email": "john@example.com",
    "address": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zipCode": "10001",
    "organizationName": "ABC Bank",
    "expiresIn": "24 hours"
  }
}
```

### Submit Verification (Token-Based)
```
POST /api/submit-verification
```

**Request:**
```json
{
  "token": "eyJhbGc...",
  "consent": true,
  "location": {
    "latitude": 40.7589,
    "longitude": -73.9851,
    "accuracy": 10
  },
  "userAgent": "Mozilla/5.0...",
  "screenResolution": "1920x1080",
  "timezone": "America/New_York"
}
```

### Revoke Token
```
POST /api/revoke-token
```

**Request:**
```json
{
  "tokenId": "abc123..."
}
```

## Security Best Practices

### For Administrators

1. **Environment Variables**
   - Always set `SECRET_KEY` to a strong, random value in production
   - Never commit secret keys to version control
   - Rotate keys periodically

2. **Link Distribution**
   - Send links only through secure channels (encrypted email, SMS)
   - Verify recipient before sending
   - Use HTTPS for all communications

3. **Monitoring**
   - Review verification logs regularly
   - Monitor for unusual patterns (multiple failed attempts)
   - Set up alerts for suspicious activity

4. **Token Management**
   - Revoke tokens if customer reports not requesting verification
   - Clean up expired tokens from database
   - Maintain audit logs of all token operations

### For Customers

1. **Link Verification**
   - Verify the link is from a trusted source
   - Check the domain is correct (verifai.app)
   - Do not share the link with anyone

2. **Location Permissions**
   - Only grant location when you recognize the verification request
   - Ensure you're at the address being verified
   - Report suspicious links to the organization

## Token Structure

Example encrypted token:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbklkIjoiYWJjMTIzIiwiZnVsbE5hbWUiOiJKb2huIERvZSIsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImFkZHJlc3MiOiIxMjMgTWFpbiBTdHJlZXQiLCJjaXR5IjoiTmV3IFlvcmsiLCJzdGF0ZSI6Ik5ZIiwiemlwQ29kZSI6IjEwMDAxIiwib3JnYW5pemF0aW9uTmFtZSI6IkFCQyBCYW5rIiwiY3JlYXRlZEF0IjoiMjAyNS0xMi0yMVQxMDowMDowMCIsImV4cGlyZXNJbiI6IjI0IGhvdXJzIn0.signature
```

Decoded token contains:
- Token ID (unique identifier)
- Customer information (name, email, address)
- Organization name
- Creation timestamp
- Expiration information
- Cryptographic signature

## Compliance

This system is designed to comply with:

- **GDPR**: Customer consent required, data minimization, purpose limitation
- **CCPA**: Consumer rights respected, data security measures in place
- **TCPA**: Consent obtained before verification request
- **SOC 2**: Security controls, access logging, encryption

## Environment Configuration

```bash
# Backend (.env)
SECRET_KEY=your-super-secret-key-min-32-chars
FRONTEND_URL=https://verifai.app
CORS_ORIGINS=https://verifai.app,https://www.verifai.app
```

## Testing

### Generate a Test Link
1. Log into dashboard
2. Navigate to "Generate Link"
3. Fill in test customer information
4. Click "Generate Verification Link"
5. Copy the generated URL
6. Open in incognito/private window
7. Test the verification flow

### Security Testing
- Try using an expired token (wait 24+ hours)
- Try using a token twice
- Try modifying the token string
- Try accessing without a token
- Verify error messages don't leak sensitive info

## Future Enhancements

- [ ] SMS integration for automated link delivery
- [ ] Email template system for professional notifications
- [ ] Multi-language support for international customers
- [ ] Advanced fraud detection using ML models
- [ ] Biometric verification (face recognition)
- [ ] Document upload within verification flow
- [ ] Real-time verification status webhooks
- [ ] Customer verification history portal
