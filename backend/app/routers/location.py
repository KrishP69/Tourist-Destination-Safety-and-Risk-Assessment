from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional

from app.services.presence_service import update_presence, stop_presence
from app.services.geofence_service import validate_coordinates
from app.auth import get_optional_user
from app.config import LOCATION_UPDATE_INTERVAL_SEC, VISITOR_TIMEOUT_MINUTES, DEMO_MODE
from app.services.demo_crowd_service import is_demo_enabled

router = APIRouter(prefix="/api/location", tags=["Location & Presence"])


class LocationUpdate(BaseModel):
    anonymous_user_id: str = Field(..., min_length=8, max_length=128)
    latitude: float
    longitude: float
    accuracy_m: Optional[float] = Field(None, ge=0, le=10000)
    destination_id: Optional[int] = None


class LocationStop(BaseModel):
    anonymous_user_id: str = Field(..., min_length=8, max_length=128)


@router.get("/config")
def location_config():
    return {
        "update_interval_sec": LOCATION_UPDATE_INTERVAL_SEC,
        "visitor_timeout_minutes": VISITOR_TIMEOUT_MINUTES,
        "demo_mode": is_demo_enabled(),
        "purpose": (
            "Your location helps us estimate crowd levels and provide real-time "
            "safety information around tourist destinations."
        ),
        "privacy": (
            "We determine geofence membership only. Precise location history is not stored. "
            "Active visitor records use hashed anonymous identifiers."
        ),
    }


@router.post("/update")
def location_update(payload: LocationUpdate, user=Depends(get_optional_user)):
    try:
        validate_coordinates(payload.latitude, payload.longitude)
        result = update_presence(
            anonymous_user_id=payload.anonymous_user_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            accuracy_m=payload.accuracy_m,
            destination_id=payload.destination_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stop")
def location_stop(payload: LocationStop):
    try:
        return stop_presence(payload.anonymous_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
