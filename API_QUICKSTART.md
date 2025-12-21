# API Key Management - Quick Start Guide

## Overview

VerifAi now supports API key authentication, allowing external companies and applications to programmatically integrate with your address verification system.

## Features

### 🔑 API Key Management
- **Create unlimited API keys** for different clients/applications
- **Secure key generation** using cryptographically secure random tokens (format: `verifai_live_xxxxx`)
- **Key activation/deactivation** - Enable or disable keys without deleting them
- **Usage tracking** - Monitor how many times each key has been used
- **Expiration dates** - Set optional expiration for temporary access
- **Company association** - Track which company owns each key

### 🔐 Security Features
- **One-time display** - API keys are only shown once upon creation
- **SHA-256 hashing** - Keys are hashed before storage
- **Rate limiting** - Configurable request limits per key (default: 1000/day)
- **Automatic expiration** - Keys expire based on configured duration
- **Activity logging** - Track last used date and usage count

### 📊 Management Dashboard
- View all API keys with status
- See usage statistics
- Activate/deactivate keys
- Delete keys permanently
- Copy-friendly key display

## Getting Started

### Step 1: Create an API Key

1. **Log into VerifAi Dashboard**
   ```
   http://localhost:5173/login
   ```

2. **Navigate to API Keys**
   - Click "API Keys" in the sidebar
   
3. **Create New Key**
   - Click "Create API Key" button
   - Fill in the form:
     - **Key Name**: Descriptive name (e.g., "Production API Key")
     - **Company Name**: Client company name (e.g., "Acme Corporation")
     - **Description**: Optional purpose description
     - **Expires In (days)**: Optional expiration (leave empty for no expiration)
   
4. **Save the Key**
   - Click "Create API Key"
   - **IMPORTANT**: Copy and save the key immediately
   - The full key will never be shown again!

### Step 2: Test the API

Using cURL:
```bash
# Generate a verification link
curl -X POST http://localhost:10000/api/v1/generate-verification \
  -H "Content-Type: application/json" \
  -H "X-API-Key: verifai_live_your_key_here" \
  -d '{
    "fullName": "Test User",
    "email": "test@example.com",
    "address": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zipCode": "10001"
  }'
```

Expected response:
```json
{
  "success": true,
  "data": {
    "verificationId": "abc123xyz",
    "verificationUrl": "http://localhost:5173/verify?token=eyJhbGc...",
    "expiresAt": "2025-12-22T10:00:00",
    "recipient": {
      "name": "Test User",
      "email": "test@example.com"
    }
  }
}
```

### Step 3: Integrate into Your Application

**JavaScript Example:**
```javascript
const VERIFAI_API_KEY = 'verifai_live_your_key_here';
const VERIFAI_API_URL = 'http://localhost:10000';

async function createVerification(customerData) {
  const response = await fetch(`${VERIFAI_API_URL}/api/v1/generate-verification`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': VERIFAI_API_KEY
    },
    body: JSON.stringify({
      fullName: customerData.name,
      email: customerData.email,
      address: customerData.address,
      city: customerData.city,
      state: customerData.state,
      zipCode: customerData.zipCode
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Send verification URL to customer
    console.log('Verification Link:', data.data.verificationUrl);
    return data.data;
  } else {
    throw new Error(data.error);
  }
}

// Usage
createVerification({
  name: 'John Doe',
  email: 'john@example.com',
  address: '123 Main St',
  city: 'New York',
  state: 'NY',
  zipCode: '10001'
}).then(result => {
  console.log('Success:', result);
}).catch(error => {
  console.error('Error:', error);
});
```

**Python Example:**
```python
import requests
import os

VERIFAI_API_KEY = os.getenv('VERIFAI_API_KEY')
VERIFAI_API_URL = 'http://localhost:10000'

def create_verification(customer_data):
    url = f'{VERIFAI_API_URL}/api/v1/generate-verification'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': VERIFAI_API_KEY
    }
    payload = {
        'fullName': customer_data['name'],
        'email': customer_data['email'],
        'address': customer_data['address'],
        'city': customer_data['city'],
        'state': customer_data['state'],
        'zipCode': customer_data['zip_code']
    }
    
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    
    if data['success']:
        print(f"Verification Link: {data['data']['verificationUrl']}")
        return data['data']
    else:
        raise Exception(data['error'])

# Usage
customer = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'address': '123 Main St',
    'city': 'New York',
    'state': 'NY',
    'zip_code': '10001'
}

try:
    result = create_verification(customer)
    print('Success:', result)
except Exception as e:
    print('Error:', str(e))
```

## API Endpoints

### 1. Generate Verification Link
```
POST /api/v1/generate-verification
```
Creates a unique verification link for a customer.

**Required Headers:**
- `Content-Type: application/json`
- `X-API-Key: your_api_key`

**Request Body:**
```json
{
  "fullName": "string (required)",
  "email": "string (required)",
  "address": "string (required)",
  "city": "string (required)",
  "state": "string (required)",
  "zipCode": "string (required)"
}
```

### 2. Get Verification Status
```
GET /api/v1/verifications/{verification_id}
```
Retrieve the status of a specific verification.

**Required Headers:**
- `X-API-Key: your_api_key`

### 3. List All Verifications
```
GET /api/v1/verifications
```
Get all verifications created with your API key.

**Required Headers:**
- `X-API-Key: your_api_key`

## Managing API Keys

### View All Keys
- Navigate to **Dashboard → API Keys**
- See all keys with their status, usage, and details

### Deactivate a Key
1. Find the key in the list
2. Click the power icon (🔴)
3. Key is immediately disabled
4. Can be reactivated later

### Delete a Key
1. Find the key in the list
2. Click the trash icon (🗑️)
3. Confirm deletion
4. Key is permanently removed

### Monitor Usage
- **Usage Count**: Total number of API calls made with this key
- **Last Used**: Timestamp of the most recent API call
- **Created**: When the key was generated

## Security Best Practices

### For Administrators

1. **Unique Keys per Client**
   - Create separate keys for each client/application
   - Easier to track usage and revoke access

2. **Set Expiration Dates**
   - For temporary integrations, set an expiration date
   - Forces clients to renew access periodically

3. **Monitor Usage**
   - Regularly check usage counts
   - Look for unusual spikes in activity

4. **Rotate Keys**
   - Periodically create new keys and deprecate old ones
   - Inform clients in advance of rotation schedule

5. **Immediate Revocation**
   - If a key is compromised, deactivate it immediately
   - Generate a new key for the client

### For API Clients

1. **Secure Storage**
   - Never commit API keys to version control
   - Use environment variables or secure vaults
   - Don't expose keys in client-side code

2. **Error Handling**
   - Check for `success: false` in responses
   - Handle 401 (unauthorized) errors
   - Implement retry logic for 429 (rate limit) errors

3. **Rate Limit Management**
   - Track your API usage
   - Implement caching to reduce calls
   - Contact admin if you need higher limits

4. **HTTPS in Production**
   - Always use HTTPS in production
   - Never send API keys over unencrypted connections

## Troubleshooting

### "Invalid API key" Error
- **Check**: Key is correctly copied (no extra spaces)
- **Check**: Key is active in the dashboard
- **Check**: Key hasn't expired

### "API key has been disabled" Error
- Key was deactivated by administrator
- Contact VerifAi admin to reactivate

### "API key has expired" Error
- Key reached its expiration date
- Request a new key from administrator

### "Missing required field" Error
- Ensure all required fields are included in request body
- Check field names match exactly (case-sensitive)

### Rate Limit Errors
- You've exceeded your daily request limit
- Wait for reset or contact admin for higher limits
- Check `X-RateLimit-Reset` header for reset time

## Example Use Cases

### 1. E-commerce Platform
```javascript
// When customer signs up
async function verifyCustomerAddress(customer) {
  const verification = await createVerification({
    fullName: customer.name,
    email: customer.email,
    address: customer.shippingAddress,
    city: customer.city,
    state: customer.state,
    zipCode: customer.zipCode
  });
  
  // Send verification link via email
  await sendEmail(customer.email, {
    subject: 'Verify Your Shipping Address',
    body: `Click here to verify: ${verification.verificationUrl}`
  });
  
  return verification.verificationId;
}
```

### 2. Banking Application
```python
# KYC address verification
def initiate_kyc_verification(customer_id):
    customer = get_customer(customer_id)
    
    verification = create_verification({
        'name': customer.full_name,
        'email': customer.email,
        'address': customer.residential_address,
        'city': customer.city,
        'state': customer.state,
        'zip_code': customer.zip_code
    })
    
    # Store verification ID for later status check
    save_verification_id(customer_id, verification['verificationId'])
    
    # Send SMS with link
    send_sms(customer.phone, f"Verify your address: {verification['verificationUrl']}")
    
    return verification
```

### 3. Background Job Processing
```javascript
// Check verification status periodically
async function checkVerificationStatus(verificationId) {
  const response = await fetch(
    `${VERIFAI_API_URL}/api/v1/verifications/${verificationId}`,
    {
      headers: {
        'X-API-Key': VERIFAI_API_KEY
      }
    }
  );
  
  const data = await response.json();
  
  if (data.success) {
    const status = data.data.status;
    
    if (status === 'verified') {
      console.log('✓ Address verified');
      await approveCustomer(data.data.customer.email);
    } else if (status === 'requires_review') {
      console.log('⚠ Manual review required');
      await flagForReview(data.data.customer.email);
    } else if (status === 'declined_by_user') {
      console.log('✗ User declined verification');
      await notifyCustomerService(data.data.customer.email);
    }
  }
  
  return data;
}
```

## Need Help?

- **Full API Documentation**: See `API_DOCUMENTATION.md`
- **Security Details**: See `SECURITY.md`
- **Architecture Overview**: See `ARCHITECTURE.md`

For support, contact your VerifAi administrator.
