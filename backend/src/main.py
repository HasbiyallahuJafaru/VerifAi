from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from functools import wraps
import math
import json
import requests
from datetime import datetime, timedelta
import os
import secrets
import hashlib
import base64
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

app = Flask(__name__)

# Configure CORS for production
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
CORS(app, origins=CORS_ORIGINS, supports_credentials=True)

# Secret key for token generation - should be stored in environment variable
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
serializer = URLSafeTimedSerializer(SECRET_KEY)

# In-memory storage for demo purposes
verifications = []
verification_tokens = {}  # Store token metadata
api_keys = {}  # Store API keys: {key_hash: {metadata}}

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def geocode_address(address):
    """Geocode address using a simple geocoding service"""
    # For demo purposes, we'll use a simple mapping
    # In production, you'd use Google Maps API, MapBox, etc.
    
    # Sample coordinates for common addresses
    address_coords = {
        "123 broadway street, new york, ny": (40.7589, -73.9851),
        "123 main street, anytown, ca": (37.7749, -122.4194),
        "456 oak avenue, chicago, il": (41.8781, -87.6298),
        "789 elm street, houston, tx": (29.7604, -95.3698)
    }
    
    # Normalize address for lookup
    normalized = address.lower().strip()
    
    # Check if we have coordinates for this address
    for key, coords in address_coords.items():
        if key in normalized or normalized in key:
            return coords
    
    # Default coordinates (New York City) if address not found
    return (40.7589, -73.9851)

def calculate_risk_score(distance_meters, accuracy_meters=None):
    """Calculate risk score based on distance from claimed address"""
    if distance_meters <= 100:
        return 0.1  # Very low risk
    elif distance_meters <= 500:
        return 0.3  # Low risk
    elif distance_meters <= 1000:
        return 0.5  # Medium risk
    elif distance_meters <= 5000:
        return 0.7  # High risk
    else:
        return 0.9  # Very high risk

def hash_api_key(api_key):
    """Hash API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def generate_api_key():
    """Generate a secure API key"""
    # Format: verifai_live_[32 random chars] or verifai_test_[32 random chars]
    random_part = secrets.token_urlsafe(32)
    return f"verifai_live_{random_part}"

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key in header
        api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not api_key:
            return jsonify({
                "error": "API key required. Include X-API-Key header or Authorization: Bearer <key>",
                "status": "unauthorized"
            }), 401
        
        # Hash and validate API key
        key_hash = hash_api_key(api_key)
        
        if key_hash not in api_keys:
            return jsonify({
                "error": "Invalid API key",
                "status": "unauthorized"
            }), 401
        
        api_key_data = api_keys[key_hash]
        
        # Check if API key is active
        if not api_key_data.get('active', False):
            return jsonify({
                "error": "API key has been disabled",
                "status": "unauthorized"
            }), 401
        
        # Check expiration
        expires_at = api_key_data.get('expiresAt')
        if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
            return jsonify({
                "error": "API key has expired",
                "status": "unauthorized"
            }), 401
        
        # Update last used timestamp and increment usage count
        api_keys[key_hash]['lastUsedAt'] = datetime.now().isoformat()
        api_keys[key_hash]['usageCount'] = api_keys[key_hash].get('usageCount', 0) + 1
        
        # Add API key data to request context
        request.api_key_data = api_key_data
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/')
def health_check():
    return jsonify({
        "message": "Address verification API is running",
        "status": "healthy",
        "version": "1.0.0"
    })

@app.route('/api/health')
def api_health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/generate-verification-link', methods=['POST'])
def generate_verification_link():
    """Generate a secure, unique verification link for a customer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['fullName', 'email', 'address', 'city', 'state', 'zipCode', 'organizationName']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}",
                    "status": "error"
                }), 400
        
        # Generate unique token ID
        token_id = secrets.token_urlsafe(32)
        
        # Prepare verification data to embed in token
        verification_data = {
            "tokenId": token_id,
            "fullName": data['fullName'],
            "email": data['email'],
            "address": data['address'],
            "city": data['city'],
            "state": data['state'],
            "zipCode": data['zipCode'],
            "organizationName": data['organizationName'],
            "createdAt": datetime.now().isoformat(),
            "expiresIn": data.get('expiresIn', '24 hours')
        }
        
        # Generate secure token - expires in 24 hours by default
        expiration_hours = 24
        token = serializer.dumps(verification_data, salt='verification-link')
        
        # Store token metadata (for tracking and revocation)
        verification_tokens[token_id] = {
            "token": token,
            "email": data['email'],
            "fullName": data['fullName'],
            "organizationName": data['organizationName'],
            "createdAt": datetime.now().isoformat(),
            "expiresAt": (datetime.now() + timedelta(hours=expiration_hours)).isoformat(),
            "used": False,
            "usedAt": None,
            "status": "active"
        }
        
        # Generate verification URL
        base_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        verification_url = f"{base_url}/verify?token={token}"
        
        return jsonify({
            "message": "Verification link generated successfully",
            "status": "success",
            "tokenId": token_id,
            "verificationUrl": verification_url,
            "token": token,
            "expiresAt": verification_tokens[token_id]["expiresAt"],
            "expiresIn": f"{expiration_hours} hours",
            "recipient": {
                "name": data['fullName'],
                "email": data['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate verification link: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/validate-token', methods=['POST'])
def validate_token():
    """Validate a verification token and return associated data"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                "error": "No token provided",
                "status": "error"
            }), 400
        
        try:
            # Decode and validate token - max_age is in seconds (24 hours = 86400 seconds)
            verification_data = serializer.loads(
                token,
                salt='verification-link',
                max_age=86400  # 24 hours
            )
            
            token_id = verification_data.get('tokenId')
            
            # Check if token exists and is active
            if token_id not in verification_tokens:
                return jsonify({
                    "error": "Invalid verification token",
                    "status": "error"
                }), 400
            
            token_metadata = verification_tokens[token_id]
            
            # Check if token has already been used
            if token_metadata.get('used', False):
                return jsonify({
                    "error": "This verification link has already been used",
                    "status": "error"
                }), 400
            
            # Check if token is still active
            if token_metadata.get('status') != 'active':
                return jsonify({
                    "error": "This verification link is no longer active",
                    "status": "error"
                }), 400
            
            # Token is valid, return verification data
            return jsonify({
                "message": "Token is valid",
                "status": "success",
                "verification_data": {
                    "fullName": verification_data['fullName'],
                    "email": verification_data['email'],
                    "address": verification_data['address'],
                    "city": verification_data['city'],
                    "state": verification_data['state'],
                    "zipCode": verification_data['zipCode'],
                    "organizationName": verification_data['organizationName'],
                    "expiresIn": verification_data.get('expiresIn', '24 hours')
                }
            }), 200
            
        except SignatureExpired:
            return jsonify({
                "error": "This verification link has expired",
                "status": "error"
            }), 400
        except BadSignature:
            return jsonify({
                "error": "Invalid or corrupted verification link",
                "status": "error"
            }), 400
            
    except Exception as e:
        return jsonify({
            "error": f"Token validation failed: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/verification-declined', methods=['POST'])
def verification_declined():
    """Record that user declined verification"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                "error": "No token provided",
                "status": "error"
            }), 400
        
        # Decode token to get token ID
        verification_data = serializer.loads(token, salt='verification-link', max_age=86400)
        token_id = verification_data.get('tokenId')
        
        # Mark token as used/declined
        if token_id in verification_tokens:
            verification_tokens[token_id]['used'] = True
            verification_tokens[token_id]['usedAt'] = datetime.now().isoformat()
            verification_tokens[token_id]['status'] = 'declined'
        
        # Create verification record
        verification_record = {
            "id": len(verifications) + 1,
            "tokenId": token_id,
            "timestamp": datetime.now().isoformat(),
            "personal_info": {
                "full_name": verification_data['fullName'],
                "email": verification_data['email'],
                "address": f"{verification_data['address']}, {verification_data['city']}, {verification_data['state']} {verification_data['zipCode']}"
            },
            "verification_results": {
                "status": "declined_by_user",
                "risk_score": 1.0,
                "location_verified": False,
                "requires_manual_review": True
            },
            "consent_provided": False
        }
        
        verifications.append(verification_record)
        
        return jsonify({
            "message": "Verification declined recorded",
            "status": "success"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to record declined verification: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/submit-verification', methods=['POST'])
def submit_verification():
    try:
        data = request.get_json()
        
        # Check if this is a token-based verification or manual entry
        token = data.get('token')
        
        if token:
            # Token-based verification (from public link)
            try:
                verification_data = serializer.loads(token, salt='verification-link', max_age=86400)
                token_id = verification_data.get('tokenId')
                
                # Check if token has been used
                if token_id in verification_tokens and verification_tokens[token_id].get('used'):
                    return jsonify({
                        "error": "This verification link has already been used",
                        "status": "error"
                    }), 400
                
                # Mark token as used
                if token_id in verification_tokens:
                    verification_tokens[token_id]['used'] = True
                    verification_tokens[token_id]['usedAt'] = datetime.now().isoformat()
                    verification_tokens[token_id]['status'] = 'completed'
                
                # Use data from token
                full_name = verification_data['fullName']
                email = verification_data['email']
                address = verification_data['address']
                city = verification_data['city']
                state = verification_data['state']
                zip_code = verification_data['zipCode']
                organization_name = verification_data.get('organizationName', 'Organization')
                
            except (SignatureExpired, BadSignature):
                return jsonify({
                    "error": "Invalid or expired verification token",
                    "status": "error"
                }), 400
        else:
            # Manual verification (from dashboard)
            required_fields = ['fullName', 'email', 'address', 'city', 'state', 'zipCode', 'consent']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        "error": f"Missing required field: {field}",
                        "status": "error"
                    }), 400
            
            full_name = data['fullName']
            email = data['email']
            address = data['address']
            city = data['city']
            state = data['state']
            zip_code = data['zipCode']
            organization_name = 'Organization'
            token_id = None
        
        # Get location data
        location_data = data.get('location', {})
        user_lat = location_data.get('latitude')
        user_lon = location_data.get('longitude')
        accuracy = location_data.get('accuracy', 0)
        
        # Get additional security data
        user_agent = data.get('userAgent', '')
        screen_resolution = data.get('screenResolution', '')
        timezone = data.get('timezone', '')
        
        # Construct full address
        full_address = f"{address}, {city}, {state} {zip_code}"
        
        # Geocode the claimed address
        address_lat, address_lon = geocode_address(full_address)
        
        # Calculate distance if user location is available
        distance_meters = None
        location_verified = False
        verification_status = "pending"
        
        if user_lat is not None and user_lon is not None:
            distance_meters = calculate_distance(user_lat, user_lon, address_lat, address_lon)
            
            # Location verification logic
            if distance_meters <= 500:  # Within 500 meters
                location_verified = True
                verification_status = "verified"
            else:
                location_verified = False
                verification_status = "requires_review"
        else:
            # No location data provided
            verification_status = "requires_manual_verification"
        
        # Calculate risk score
        risk_score = calculate_risk_score(distance_meters, user_agent)
        
        # Create verification record
        verification_record = {
            "id": str(uuid.uuid4()),
            "tokenId": token_id,
            "timestamp": datetime.now().isoformat(),
            "personal_info": {
                "full_name": full_name,
                "email": email,
                "phone": data.get('phone', ''),
                "address": full_address,
                "organization": organization_name
            },
            "location_data": {
                "user_coordinates": {
                    "latitude": user_lat,
                    "longitude": user_lon,
                    "accuracy": accuracy
                },
                "address_coordinates": {
                    "latitude": address_lat,
                    "longitude": address_lon
                },
                "distance_meters": distance_meters,
                "location_verified": location_verified
            },
            "security_data": {
                "user_agent": user_agent,
                "screen_resolution": screen_resolution,
                "timezone": timezone,
                "ip_address": request.remote_addr
            },
            "verification_results": {
                "status": verification_status,
                "risk_score": risk_score,
                "location_match": location_verified,
                "requires_manual_review": risk_score > 0.6
            },
            "consent_provided": data.get('consent', True)
        }
        
        # Store verification record
        verifications.append(verification_record)
        
        # Prepare response
        response = {
            "verification_id": verification_record["id"],
            "status": verification_status,
            "risk_score": risk_score,
            "location_verified": location_verified,
            "distance_from_address": distance_meters,
            "message": get_verification_message(verification_status, distance_meters),
            "timestamp": verification_record["timestamp"]
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Verification submission failed: {str(e)}",
            "status": "error"
        }), 500

# ==================== API KEY MANAGEMENT ENDPOINTS ====================

@app.route('/api/api-keys', methods=['GET'])
def list_api_keys():
    """List all API keys (admin only)"""
    try:
        # Return sanitized list (without actual keys)
        keys_list = []
        for key_hash, data in api_keys.items():
            keys_list.append({
                "id": data.get('id'),
                "name": data.get('name'),
                "company": data.get('company'),
                "keyPrefix": data.get('keyPrefix'),
                "active": data.get('active'),
                "createdAt": data.get('createdAt'),
                "expiresAt": data.get('expiresAt'),
                "lastUsedAt": data.get('lastUsedAt'),
                "usageCount": data.get('usageCount', 0),
                "permissions": data.get('permissions', [])
            })
        
        return jsonify({
            "apiKeys": sorted(keys_list, key=lambda x: x['createdAt'], reverse=True),
            "total_count": len(keys_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to list API keys: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/api-keys', methods=['POST'])
def create_api_key():
    """Create a new API key"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'company']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}",
                    "status": "error"
                }), 400
        
        # Generate API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        
        # Create API key record
        api_key_id = f"key_{secrets.token_urlsafe(8)}"
        key_prefix = api_key[:20] + "..."  # Store only prefix for display
        
        # Set expiration (optional, default no expiration)
        expires_in_days = data.get('expiresInDays')
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        api_key_data = {
            "id": api_key_id,
            "name": data['name'],
            "company": data['company'],
            "description": data.get('description', ''),
            "keyPrefix": key_prefix,
            "keyHash": key_hash,
            "active": True,
            "createdAt": datetime.now().isoformat(),
            "createdBy": data.get('createdBy', 'admin'),
            "expiresAt": expires_at,
            "lastUsedAt": None,
            "usageCount": 0,
            "permissions": data.get('permissions', ['verification:create', 'verification:read']),
            "rateLimit": data.get('rateLimit', 1000),  # requests per day
            "environment": data.get('environment', 'production')
        }
        
        # Store API key
        api_keys[key_hash] = api_key_data
        
        # Return API key (only shown once!)
        return jsonify({
            "message": "API key created successfully",
            "status": "success",
            "apiKey": api_key,  # Only time the full key is shown
            "apiKeyData": {
                "id": api_key_id,
                "name": data['name'],
                "company": data['company'],
                "keyPrefix": key_prefix,
                "createdAt": api_key_data['createdAt'],
                "expiresAt": expires_at,
                "permissions": api_key_data['permissions']
            },
            "warning": "Save this key securely. You won't be able to see it again!"
        }), 201
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to create API key: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/api-keys/<key_id>', methods=['PUT'])
def update_api_key(key_id):
    """Update an API key (activate/deactivate, update name, etc.)"""
    try:
        data = request.get_json()
        
        # Find API key by ID
        target_key = None
        for key_hash, key_data in api_keys.items():
            if key_data.get('id') == key_id:
                target_key = key_hash
                break
        
        if not target_key:
            return jsonify({
                "error": "API key not found",
                "status": "error"
            }), 404
        
        # Update fields
        if 'active' in data:
            api_keys[target_key]['active'] = data['active']
        if 'name' in data:
            api_keys[target_key]['name'] = data['name']
        if 'description' in data:
            api_keys[target_key]['description'] = data['description']
        if 'permissions' in data:
            api_keys[target_key]['permissions'] = data['permissions']
        if 'rateLimit' in data:
            api_keys[target_key]['rateLimit'] = data['rateLimit']
        
        api_keys[target_key]['updatedAt'] = datetime.now().isoformat()
        
        return jsonify({
            "message": "API key updated successfully",
            "status": "success",
            "apiKeyData": {
                "id": api_keys[target_key]['id'],
                "name": api_keys[target_key]['name'],
                "active": api_keys[target_key]['active'],
                "updatedAt": api_keys[target_key]['updatedAt']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to update API key: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/api-keys/<key_id>', methods=['DELETE'])
def delete_api_key(key_id):
    """Delete (revoke) an API key"""
    try:
        # Find and remove API key by ID
        target_key = None
        for key_hash, key_data in api_keys.items():
            if key_data.get('id') == key_id:
                target_key = key_hash
                break
        
        if not target_key:
            return jsonify({
                "error": "API key not found",
                "status": "error"
            }), 404
        
        # Mark as deleted (or actually delete)
        api_keys[target_key]['active'] = False
        api_keys[target_key]['deletedAt'] = datetime.now().isoformat()
        # Optionally: del api_keys[target_key]
        
        return jsonify({
            "message": "API key deleted successfully",
            "status": "success"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to delete API key: {str(e)}",
            "status": "error"
        }), 500

# ==================== API ENDPOINTS (WITH API KEY AUTH) ====================

@app.route('/api/v1/generate-verification', methods=['POST'])
@require_api_key
def api_generate_verification():
    """Generate a verification link via API (requires API key)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['fullName', 'email', 'address', 'city', 'state', 'zipCode']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}",
                    "status": "error"
                }), 400
        
        # Use company name from API key
        organization_name = request.api_key_data.get('company', data.get('organizationName', 'Organization'))
        
        # Generate unique token ID
        token_id = secrets.token_urlsafe(32)
        
        # Prepare verification data
        verification_data = {
            "tokenId": token_id,
            "fullName": data['fullName'],
            "email": data['email'],
            "address": data['address'],
            "city": data['city'],
            "state": data['state'],
            "zipCode": data['zipCode'],
            "organizationName": organization_name,
            "createdAt": datetime.now().isoformat(),
            "expiresIn": data.get('expiresIn', '24 hours'),
            "apiKeyId": request.api_key_data.get('id')
        }
        
        # Generate secure token
        expiration_hours = 24
        token = serializer.dumps(verification_data, salt='verification-link')
        
        # Store token metadata
        verification_tokens[token_id] = {
            "token": token,
            "email": data['email'],
            "fullName": data['fullName'],
            "organizationName": organization_name,
            "createdAt": datetime.now().isoformat(),
            "expiresAt": (datetime.now() + timedelta(hours=expiration_hours)).isoformat(),
            "used": False,
            "usedAt": None,
            "status": "active",
            "apiKeyId": request.api_key_data.get('id')
        }
        
        # Generate verification URL
        base_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        verification_url = f"{base_url}/verify?token={token}"
        
        return jsonify({
            "success": True,
            "data": {
                "verificationId": token_id,
                "verificationUrl": verification_url,
                "expiresAt": verification_tokens[token_id]["expiresAt"],
                "recipient": {
                    "name": data['fullName'],
                    "email": data['email']
                }
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to generate verification: {str(e)}"
        }), 500

@app.route('/api/v1/verifications/<verification_id>', methods=['GET'])
@require_api_key
def api_get_verification(verification_id):
    """Get verification status via API (requires API key)"""
    try:
        # Find verification
        verification = None
        for v in verifications:
            if str(v.get('id')) == verification_id or v.get('tokenId') == verification_id:
                verification = v
                break
        
        if not verification:
            return jsonify({
                "success": False,
                "error": "Verification not found"
            }), 404
        
        # Return verification data
        return jsonify({
            "success": True,
            "data": {
                "id": verification.get('id'),
                "status": verification.get('verification_results', {}).get('status'),
                "locationVerified": verification.get('location_data', {}).get('location_verified'),
                "riskScore": verification.get('verification_results', {}).get('risk_score'),
                "distance": verification.get('location_data', {}).get('distance_meters'),
                "timestamp": verification.get('timestamp'),
                "customer": {
                    "name": verification.get('personal_info', {}).get('full_name'),
                    "email": verification.get('personal_info', {}).get('email')
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get verification: {str(e)}"
        }), 500

@app.route('/api/v1/verifications', methods=['GET'])
@require_api_key
def api_list_verifications():
    """List all verifications via API (requires API key)"""
    try:
        # Filter verifications by API key if needed
        api_key_id = request.api_key_data.get('id')
        filtered_verifications = [
            v for v in verifications 
            if v.get('tokenId') in [t for t, data in verification_tokens.items() 
                                    if data.get('apiKeyId') == api_key_id]
        ]
        
        # Return list
        return jsonify({
            "success": True,
            "data": {
                "verifications": filtered_verifications,
                "total": len(filtered_verifications)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list verifications: {str(e)}"
        }), 500
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Verification failed: {str(e)}",
            "status": "error"
        }), 500

def get_verification_message(status, distance_meters):
    """Get appropriate message based on verification status"""
    if status == "verified":
        return f"Address verification successful. User is within {distance_meters:.0f}m of claimed address."
    elif status == "requires_review":
        return f"Manual review required. User is {distance_meters:.0f}m from claimed address."
    else:
        return "Manual verification required due to insufficient location data."

@app.route('/api/verifications', methods=['GET'])
def get_verifications():
    """Get all verification records (for admin/testing purposes)"""
    return jsonify({
        "verifications": verifications,
        "total_count": len(verifications)
    })

@app.route('/api/verification-tokens', methods=['GET'])
def get_verification_tokens():
    """Get all verification tokens (for admin purposes)"""
    return jsonify({
        "tokens": list(verification_tokens.values()),
        "total_count": len(verification_tokens)
    })

@app.route('/api/revoke-token', methods=['POST'])
def revoke_token():
    """Revoke a verification token"""
    try:
        data = request.get_json()
        token_id = data.get('tokenId')
        
        if not token_id or token_id not in verification_tokens:
            return jsonify({
                "error": "Invalid token ID",
                "status": "error"
            }), 400
        
        verification_tokens[token_id]['status'] = 'revoked'
        verification_tokens[token_id]['revokedAt'] = datetime.now().isoformat()
        
        return jsonify({
            "message": "Token revoked successfully",
            "status": "success"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to revoke token: {str(e)}",
            "status": "error"
        }), 500

# File upload configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                "error": "No file part in request",
                "status": "error"
            }), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({
                "error": "No file selected",
                "status": "error"
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
                "status": "error"
            }), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = file.filename
        filename = f"{timestamp}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(filepath)
        
        # Get file info
        file_size = os.path.getsize(filepath)
        
        # Optional: Get additional form data
        verification_id = request.form.get('verification_id', None)
        document_type = request.form.get('document_type', 'unknown')
        
        # Store upload record
        upload_record = {
            "upload_id": len(verifications) + 1,
            "filename": filename,
            "original_filename": original_filename,
            "filepath": filepath,
            "file_size": file_size,
            "document_type": document_type,
            "verification_id": verification_id,
            "uploaded_at": datetime.now().isoformat()
        }
        
        return jsonify({
            "message": "File uploaded successfully",
            "status": "success",
            "upload_id": upload_record["upload_id"],
            "filename": filename,
            "file_size": file_size,
            "uploaded_at": upload_record["uploaded_at"]
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Upload failed: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/upload/multiple', methods=['POST'])
def upload_multiple_files():
    """Handle multiple file uploads"""
    try:
        files = request.files.getlist('files')
        
        if not files or len(files) == 0:
            return jsonify({
                "error": "No files provided",
                "status": "error"
            }), 400
        
        uploaded_files = []
        errors = []
        
        for file in files:
            if file.filename == '':
                continue
                
            if not allowed_file(file.filename):
                errors.append(f"{file.filename}: File type not allowed")
                continue
            
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{file.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                file.save(filepath)
                file_size = os.path.getsize(filepath)
                
                uploaded_files.append({
                    "filename": filename,
                    "original_filename": file.filename,
                    "file_size": file_size
                })
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
        
        return jsonify({
            "message": f"Uploaded {len(uploaded_files)} file(s)",
            "status": "success" if len(uploaded_files) > 0 else "error",
            "uploaded_files": uploaded_files,
            "errors": errors if errors else None
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Upload failed: {str(e)}",
            "status": "error"
        }), 500

@app.route('/api/uploads', methods=['GET'])
def list_uploads():
    """List all uploaded files"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                files.append({
                    "filename": filename,
                    "file_size": os.path.getsize(filepath),
                    "uploaded_at": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
        
        return jsonify({
            "files": files,
            "total_count": len(files)
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"Failed to list files: {str(e)}",
            "status": "error"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_ENV', 'development') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
