from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import math
import json
import requests
from datetime import datetime
import os

app = Flask(__name__)

# Configure CORS for production
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
CORS(app, origins=CORS_ORIGINS, supports_credentials=True)

# In-memory storage for demo purposes
verifications = []

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

@app.route('/api/submit-verification', methods=['POST'])
def submit_verification():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['fullName', 'email', 'address', 'city', 'state', 'zipCode', 'consent']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}",
                    "status": "error"
                }), 400
        
        # Get location data
        location_data = data.get('location', {})
        user_lat = location_data.get('latitude')
        user_lon = location_data.get('longitude')
        accuracy = location_data.get('accuracy', 0)
        
        # Construct full address
        full_address = f"{data['address']}, {data['city']}, {data['state']} {data['zipCode']}"
        
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
        risk_score = calculate_risk_score(distance_meters or 10000, accuracy)
        
        # Create verification record
        verification_record = {
            "id": len(verifications) + 1,
            "timestamp": datetime.now().isoformat(),
            "personal_info": {
                "full_name": data['fullName'],
                "email": data['email'],
                "phone": data.get('phone', ''),
                "address": full_address
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
            "verification_results": {
                "status": verification_status,
                "risk_score": risk_score,
                "location_match": location_verified,
                "requires_manual_review": risk_score > 0.6
            },
            "consent_provided": data['consent']
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
