"""Live Disaster / Risk Intelligence API — additive endpoints."""
from fastapi import APIRouter, Query
from typing import Optional

from app.services.disaster_pipeline import (
    events_summary,
    list_active_events,
    nearby_events_for_point,
    run_disaster_pipeline,
)

router = APIRouter(prefix="/api/risk-events", tags=["Live Risk Intelligence"])


@router.get("")
def get_risk_events(
    event_type: Optional[str] = Query(None, description="flood|cyclone|landslide|...|all"),
    risk_level: Optional[str] = Query(None, description="LOW|MODERATE|HIGH|CRITICAL|all"),
    source: Optional[str] = Query(None, description="news|official|all"),
):
    events = list_active_events(event_type=event_type, risk_level=risk_level, source_kind=source)
    summary = events_summary()
    return {
        "events": events,
        "summary": summary,
        "count": len(events),
    }


@router.get("/summary")
def get_risk_summary():
    return events_summary()


@router.get("/nearby")
def get_nearby_risk(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(80.0, ge=1, le=500),
):
    events = nearby_events_for_point(lat, lng, max_km=radius_km)
    return {"events": events, "count": len(events), "radius_km": radius_km}


@router.post("/refresh")
def refresh_risk_events():
    """Trigger ingest+processing. Safe to call manually; also runs on a schedule."""
    result = run_disaster_pipeline()
    summary = events_summary()
    return {"ok": True, "pipeline": result, "summary": summary}
