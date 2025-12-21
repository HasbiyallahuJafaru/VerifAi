# VerifAi API Documentation

## Overview

The VerifAi API allows you to programmatically generate address verification links, check verification status, and retrieve verification results. All API requests require authentication using an API key.

**Base URL**: `https://api.verifai.app` (Production) or `http://localhost:10000` (Development)

---

## Authentication

All API requests must include your API key in the request headers.

### Methods

You can authenticate using either of these headers:

```http
X-API-Key: verifai_live_your_api_key_here
```

or

```http
Authorization: Bearer verifai_live_your_api_key_here
```

### Getting an API Key

1. Log in to your VerifAi dashboard
2. Navigate to **API Keys** in the sidebar
3. Click **Create API Key**
4. Fill in the required information
5. Copy and save your API key securely (it won't be shown again!)

---

## API Endpoints

### 1. Generate Verification Link

Create a unique verification link for a customer.

**Endpoint**: `POST /api/v1/generate-verification`

**Headers**:
```http
Content-Type: application/json
X-API-Key: your_api_key_here
```

**Request Body**:
```json
{
  "fullName": "John Doe",
  "email": "john@example.com",
  "address": "123 Main Street",
  "city": "New York",
  "state": "NY",
  "zipCode": "10001"
}
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| fullName | string | Yes | Customer's full name |
| email | string | Yes | Customer's email address |
| address | string | Yes | Street address to verify |
| city | string | Yes | City name |
| state | string | Yes | State code (2 letters) |
| zipCode | string | Yes | ZIP/postal code |

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "verificationId": "abc123xyz789",
    "verificationUrl": "https://verifai.app/verify?token=eyJhbGc...",
    "expiresAt": "2025-12-22T10:00:00",
    "recipient": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

**Example (cURL)**:
```bash
curl -X POST https://api.verifai.app/api/v1/generate-verification \
  -H "Content-Type: application/json" \
  -H "X-API-Key: verifai_live_your_api_key" \
  -d '{
    "fullName": "John Doe",
    "email": "john@example.com",
    "address": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zipCode": "10001"
  }'
```

**Example (JavaScript)**:
```javascript
const response = await fetch('https://api.verifai.app/api/v1/generate-verification', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'verifai_live_your_api_key'
  },
  body: JSON.stringify({
    fullName: 'John Doe',
    email: 'john@example.com',
    address: '123 Main Street',
    city: 'New York',
    state: 'NY',
    zipCode: '10001'
  })
});

const data = await response.json();
console.log(data.data.verificationUrl);
```

**Example (Python)**:
```python
import requests

url = 'https://api.verifai.app/api/v1/generate-verification'
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'verifai_live_your_api_key'
}
payload = {
    'fullName': 'John Doe',
    'email': 'john@example.com',
    'address': '123 Main Street',
    'city': 'New York',
    'state': 'NY',
    'zipCode': '10001'
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()
print(data['data']['verificationUrl'])
```

---

### 2. Get Verification Status

Retrieve the status and results of a specific verification.

**Endpoint**: `GET /api/v1/verifications/{verification_id}`

**Headers**:
```http
X-API-Key: your_api_key_here
```

**URL Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| verification_id | string | Yes | The verification ID returned from generate-verification |

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": 123,
    "status": "verified",
    "locationVerified": true,
    "riskScore": 0.1,
    "distance": 15.5,
    "timestamp": "2025-12-21T10:30:00",
    "customer": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| status | string | Verification status: `verified`, `requires_review`, `declined_by_user` |
| locationVerified | boolean | Whether GPS location matched address |
| riskScore | number | Risk score from 0.0 to 1.0 (lower is better) |
| distance | number | Distance in meters from verified address |
| timestamp | string | ISO 8601 timestamp of verification |

**Example (cURL)**:
```bash
curl -X GET https://api.verifai.app/api/v1/verifications/abc123xyz789 \
  -H "X-API-Key: verifai_live_your_api_key"
```

**Example (JavaScript)**:
```javascript
const response = await fetch(
  'https://api.verifai.app/api/v1/verifications/abc123xyz789',
  {
    headers: {
      'X-API-Key': 'verifai_live_your_api_key'
    }
  }
);

const data = await response.json();
console.log(data.data.status);
```

---

### 3. List All Verifications

Get a list of all verifications created with your API key.

**Endpoint**: `GET /api/v1/verifications`

**Headers**:
```http
X-API-Key: your_api_key_here
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "verifications": [
      {
        "id": 123,
        "status": "verified",
        "locationVerified": true,
        "riskScore": 0.1,
        "timestamp": "2025-12-21T10:30:00",
        "customer": {
          "name": "John Doe",
          "email": "john@example.com"
        }
      }
    ],
    "total": 1
  }
}
```

**Example (cURL)**:
```bash
curl -X GET https://api.verifai.app/api/v1/verifications \
  -H "X-API-Key: verifai_live_your_api_key"
```

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Examples

**Missing API Key**:
```json
{
  "success": false,
  "error": "API key required. Include X-API-Key header or Authorization: Bearer <key>"
}
```

**Invalid API Key**:
```json
{
  "success": false,
  "error": "Invalid API key"
}
```

**Expired API Key**:
```json
{
  "success": false,
  "error": "API key has expired"
}
```

**Missing Required Field**:
```json
{
  "success": false,
  "error": "Missing required field: email"
}
```

---

## Rate Limits

API keys have the following default limits:

- **1,000 requests per day** (can be adjusted in dashboard)
- Requests are counted per 24-hour rolling window
- Rate limit headers are included in responses:
  ```http
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 950
  X-RateLimit-Reset: 1640095200
  ```

If you exceed your rate limit, you'll receive a `429 Too Many Requests` response.

---

## Webhooks (Coming Soon)

Receive real-time notifications when verifications are completed:

```json
POST https://your-server.com/webhook
{
  "event": "verification.completed",
  "verificationId": "abc123xyz789",
  "status": "verified",
  "timestamp": "2025-12-21T10:30:00"
}
```

---

## Integration Examples

### Node.js/Express

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
const VERIFAI_API_KEY = process.env.VERIFAI_API_KEY;

app.post('/verify-address', async (req, res) => {
  try {
    const { name, email, address, city, state, zipCode } = req.body;
    
    const response = await axios.post(
      'https://api.verifai.app/api/v1/generate-verification',
      {
        fullName: name,
        email: email,
        address: address,
        city: city,
        state: state,
        zipCode: zipCode
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': VERIFAI_API_KEY
        }
      }
    );
    
    const { verificationUrl } = response.data.data;
    
    // Send verification link to customer via email
    await sendEmail(email, verificationUrl);
    
    res.json({ success: true, message: 'Verification link sent' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### Python/Django

```python
import requests
from django.conf import settings
from django.http import JsonResponse

def verify_address(request):
    api_key = settings.VERIFAI_API_KEY
    
    data = {
        'fullName': request.POST.get('name'),
        'email': request.POST.get('email'),
        'address': request.POST.get('address'),
        'city': request.POST.get('city'),
        'state': request.POST.get('state'),
        'zipCode': request.POST.get('zip_code')
    }
    
    response = requests.post(
        'https://api.verifai.app/api/v1/generate-verification',
        json=data,
        headers={
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }
    )
    
    if response.status_code == 201:
        result = response.json()
        verification_url = result['data']['verificationUrl']
        
        # Send verification link to customer
        send_email(data['email'], verification_url)
        
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': response.json()}, status=400)
```

### PHP/Laravel

```php
<?php

use Illuminate\Support\Facades\Http;

class VerificationController extends Controller
{
    public function createVerification(Request $request)
    {
        $apiKey = config('services.verifai.api_key');
        
        $response = Http::withHeaders([
            'Content-Type' => 'application/json',
            'X-API-Key' => $apiKey
        ])->post('https://api.verifai.app/api/v1/generate-verification', [
            'fullName' => $request->input('name'),
            'email' => $request->input('email'),
            'address' => $request->input('address'),
            'city' => $request->input('city'),
            'state' => $request->input('state'),
            'zipCode' => $request->input('zip_code')
        ]);
        
        if ($response->successful()) {
            $data = $response->json();
            $verificationUrl = $data['data']['verificationUrl'];
            
            // Send verification link
            Mail::to($request->input('email'))
                ->send(new VerificationLink($verificationUrl));
            
            return response()->json(['success' => true]);
        }
        
        return response()->json(['error' => $response->json()], 400);
    }
}
```

---

## Best Practices

### Security

1. **Keep API keys secret**: Never commit API keys to version control
2. **Use environment variables**: Store keys in `.env` files or secure vaults
3. **Rotate keys regularly**: Generate new keys periodically
4. **Use HTTPS**: Always use HTTPS in production
5. **Validate responses**: Check `success` field before using data

### Performance

1. **Cache results**: Store verification results to avoid duplicate requests
2. **Implement retry logic**: Handle temporary failures gracefully
3. **Monitor rate limits**: Track usage to avoid hitting limits
4. **Use async requests**: Don't block user operations waiting for API responses

### Error Handling

```javascript
try {
  const response = await fetch(url, options);
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error);
  }
  
  // Handle success
  return data.data;
} catch (error) {
  console.error('VerifAi API Error:', error);
  
  // Implement fallback or retry logic
  if (error.message.includes('rate limit')) {
    // Wait and retry
  } else if (error.message.includes('unauthorized')) {
    // Check API key configuration
  } else {
    // Log error and notify admin
  }
}
```

---

## Support

- **Email**: support@verifai.app
- **Documentation**: https://docs.verifai.app
- **Status Page**: https://status.verifai.app
- **Community**: https://community.verifai.app

For API issues, please include:
- Your API key prefix (first 20 characters)
- Request timestamp
- Full error message
- Request/response examples (remove sensitive data)

---

## Changelog

### Version 1.0 (December 2025)
- Initial API release
- Generate verification links
- Get verification status
- List verifications
- API key management
