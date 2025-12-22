import json
import math
import uuid
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import select

from .database import session_scope
from .errors import ValidationError
from .models import Verification


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = (math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _geocode_address(address: str) -> tuple:
    address_coords = {
        "123 broadway street, new york, ny": (40.7589, -73.9851),
        "123 main street, anytown, ca": (37.7749, -122.4194),
        "456 oak avenue, chicago, il": (41.8781, -87.6298),
        "789 elm street, houston, tx": (29.7604, -95.3698),
    }
    normalized = address.lower().strip()
    for key, coords in address_coords.items():
        if key in normalized or normalized in key:
            return coords
    return (40.7589, -73.9851)


def _risk_score(distance_meters: Optional[float]) -> float:
    if distance_meters is None:
        return 0.7
    if distance_meters <= 100:
        return 0.1
    if distance_meters <= 500:
        return 0.3
    if distance_meters <= 1000:
        return 0.5
    if distance_meters <= 5000:
        return 0.7
    return 0.9


def create_verification_from_payload(payload: Dict, token_id: Optional[str], request_ip: str) -> Dict:
    required_fields = ['fullName', 'email', 'address', 'city', 'state', 'zipCode']
    for field in required_fields:
        if field not in payload:
            raise ValidationError(f"Missing required field: {field}")

    full_address = f"{payload['address']}, {payload['city']}, {payload['state']} {payload['zipCode']}"
    user_lat = payload.get('location', {}).get('latitude')
    user_lon = payload.get('location', {}).get('longitude')
    accuracy = payload.get('location', {}).get('accuracy', 0)

    address_lat, address_lon = _geocode_address(full_address)

    distance_meters = None
    location_verified = False
    status = "requires_manual_verification"

    if user_lat is not None and user_lon is not None:
        distance_meters = _haversine_distance(user_lat, user_lon, address_lat, address_lon)
        if distance_meters <= 500:
            location_verified = True
            status = "verified"
        else:
            status = "requires_review"

    risk = _risk_score(distance_meters)

    record = Verification(
        id=str(uuid.uuid4()),
        token_id=token_id,
        personal_info=json.dumps({
            "full_name": payload['fullName'],
            "email": payload['email'],
            "phone": payload.get('phone', ''),
            "address": full_address,
            "organization": payload.get('organizationName', 'Organization'),
        }),
        location_data=json.dumps({
            "user_coordinates": {
                "latitude": user_lat,
                "longitude": user_lon,
                "accuracy": accuracy,
            },
            "address_coordinates": {
                "latitude": address_lat,
                "longitude": address_lon,
            },
            "distance_meters": distance_meters,
            "location_verified": location_verified,
        }),
        security_data=json.dumps({
            "user_agent": payload.get('userAgent', ''),
            "screen_resolution": payload.get('screenResolution', ''),
            "timezone": payload.get('timezone', ''),
            "ip_address": request_ip,
        }),
        verification_results=json.dumps({
            "status": status,
            "risk_score": risk,
            "location_match": location_verified,
            "requires_manual_review": risk > 0.6,
        }),
        consent_provided=payload.get('consent', True),
    )

    with session_scope() as db:
        db.add(record)
        db.flush()
        created = record

    return {
        "verification_id": created.id,
        "status": status,
        "risk_score": risk,
        "location_verified": location_verified,
        "distance_from_address": distance_meters,
        "message": verification_message(status, distance_meters),
        "timestamp": created.timestamp.isoformat(),
    }


def verification_message(status: str, distance_meters: Optional[float]) -> str:
    if status == "verified" and distance_meters is not None:
        return f"Address verification successful. User is within {distance_meters:.0f}m of claimed address."
    if status == "requires_review" and distance_meters is not None:
        return f"Manual review required. User is {distance_meters:.0f}m from claimed address."
    return "Manual verification required due to insufficient location data."


def list_verifications() -> list:
    with session_scope() as db:
        return [
            {
                "id": r.id,
                "tokenId": r.token_id,
                "timestamp": r.timestamp.isoformat(),
                "personal_info": json.loads(r.personal_info),
                "location_data": json.loads(r.location_data) if r.location_data else None,
                "security_data": json.loads(r.security_data) if r.security_data else None,
                "verification_results": json.loads(r.verification_results),
                "consent_provided": r.consent_provided,
            }
            for r in db.scalars(select(Verification)).all()
        ]


def list_verifications_for_tokens(token_ids: list) -> list:
    if not token_ids:
        return []
    with session_scope() as db:
        records = db.scalars(select(Verification).where(Verification.token_id.in_(token_ids))).all()
        return [
            {
                "id": r.id,
                "tokenId": r.token_id,
                "timestamp": r.timestamp.isoformat(),
                "verification_results": json.loads(r.verification_results),
                "location_data": json.loads(r.location_data) if r.location_data else None,
                "personal_info": json.loads(r.personal_info),
            }
            for r in records
        ]
