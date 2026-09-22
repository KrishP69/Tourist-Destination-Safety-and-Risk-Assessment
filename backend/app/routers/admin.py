from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.schemas import AdvisoryCreate, MetricUpdate, AdminDestinationCreate
from app.services.risk_service import calculate_safety_score
from app.auth import get_current_admin
from app.services.crowd_engine import estimate_current_crowd, capture_snapshot
from app.services.demo_crowd_service import (
    is_demo_enabled,
    set_demo_mode,
    run_demo_tick,
    bootstrap_historical_demo_snapshots,
    seed_destination_crowd_defaults,
)
from app.services.booking_service import ensure_slots_for_date

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class CrowdCapacityUpdate(BaseModel):
    maximum_capacity: Optional[int] = Field(None, ge=10, le=100000)
    comfortable_capacity: Optional[int] = Field(None, ge=10, le=100000)
    emergency_capacity_override: Optional[int] = Field(None, ge=0, le=100000)
    area_sq_meters: Optional[float] = Field(None, ge=1)
    geofence_radius_m: Optional[float] = Field(None, ge=50, le=20000)
    geofence_polygon: Optional[str] = None
    threshold_low_max: Optional[float] = Field(None, ge=0, le=100)
    threshold_moderate_max: Optional[float] = Field(None, ge=0, le=100)
    threshold_high_max: Optional[float] = Field(None, ge=0, le=100)
    threshold_very_high_max: Optional[float] = Field(None, ge=0, le=200)
    crowd_status: Optional[str] = None
    crowd_weight_gps: Optional[float] = None
    crowd_weight_bookings: Optional[float] = None
    crowd_weight_historical: Optional[float] = None
    crowd_weight_trend: Optional[float] = None


class SlotCreate(BaseModel):
    destination_id: int
    slot_date: str
    start_time: str
    end_time: str
    capacity: int = Field(..., ge=1, le=100000)
    status: str = "open"


class SlotUpdate(BaseModel):
    capacity: Optional[int] = Field(None, ge=1, le=100000)
    status: Optional[str] = None


class ZoneCreate(BaseModel):
    destination_id: int
    name: str
    zone_type: str = "general"
    capacity: int = Field(200, ge=1)
    area_sq_meters: Optional[float] = None
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    radius_m: Optional[float] = 150


class DemoModeUpdate(BaseModel):
    enabled: bool
    bootstrap_history: bool = False


@router.post("/advisories")
def publish_advisory(adv: AdvisoryCreate, current_admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO safety_advisories (destination_id, title, alert_level, summary, issued_by)
        VALUES (?, ?, ?, ?, ?)
        """, (adv.destination_id, adv.title, adv.alert_level, adv.summary, adv.issued_by))
        adv_id = cursor.lastrowid
        return {"success": True, "advisory_id": adv_id, "message": "Safety advisory published successfully."}

@router.patch("/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: int, action: str = "Resolved", current_admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        valid_actions = ["Resolved", "False Alarm", "Verified", "Active"]
        if action not in valid_actions:
            raise HTTPException(status_code=400, detail="Invalid action state")
        cursor.execute("UPDATE incidents SET status = ? WHERE id = ?", (action, incident_id))
        return {"success": True, "message": f"Incident marked as {action}."}

@router.put("/destinations/{dest_id}/metrics")
def update_destination_metrics(dest_id: int, updates: MetricUpdate, current_admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM risk_metrics WHERE destination_id = ?", (dest_id,))
        m = cursor.fetchone()
        if not m:
            raise HTTPException(status_code=404, detail="Destination metrics not found")

        curr = dict(m)
        for k, v in updates.model_dump(exclude_unset=True).items():
            if v is not None:
                curr[k] = float(v)

        # Count active critical incidents
        cursor.execute("SELECT COUNT(*) FROM incidents WHERE destination_id = ? AND severity = 'Critical' AND status = 'Active'", (dest_id,))
        crit_count = cursor.fetchone()[0]

        # Recalculate score and tier
        new_score, new_tier = calculate_safety_score(curr, crit_count)

        cursor.execute("""
        UPDATE risk_metrics 
        SET crime_index = ?, scam_index = ?, weather_risk = ?, health_risk = ?, night_safety = ?, crowd_density = ?, updated_at = CURRENT_TIMESTAMP
        WHERE destination_id = ?
        """, (curr["crime_index"], curr["scam_index"], curr["weather_risk"], curr["health_risk"], curr["night_safety"], curr["crowd_density"], dest_id))

        cursor.execute("""
        UPDATE destinations 
        SET overall_safety_score = ?, risk_tier = ?
        WHERE id = ?
        """, (new_score, new_tier, dest_id))

        return {
            "success": True,
            "destination_id": dest_id,
            "overall_safety_score": new_score,
            "risk_tier": new_tier,
            "message": "Metrics updated and safety score recalculated."
        }

@router.post("/destinations")
def create_destination_admin(payload: AdminDestinationCreate, current_admin: dict = Depends(get_current_admin)):
    """Create a new Indian tourist destination with operational telemetry, baseline metrics, and emergency contacts."""
    metrics_dict = {
        "crime_index": payload.crime_index if payload.crime_index is not None else 20.0,
        "scam_index": payload.scam_index if payload.scam_index is not None else 25.0,
        "weather_risk": payload.weather_risk if payload.weather_risk is not None else 15.0,
        "health_risk": 15.0,
        "night_safety": payload.night_safety if payload.night_safety is not None else 80.0,
        "crowd_density": payload.crowd_density if payload.crowd_density is not None else 50.0,
        "transport_safety": 85.0
    }
    score, tier = calculate_safety_score(metrics_dict)
    
    img = payload.image_url.strip() if payload.image_url else "https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO destinations (
                name, state, region, country, category, lat, lng,
                overall_safety_score, risk_tier, description, image_url,
                best_visit_time, dress_code_etiquette, opening_time, closing_time,
                weekly_off_day, peak_rush_hours, entry_fee_domestic, entry_fee_foreign, booking_portal_url
            ) VALUES (?, ?, ?, 'India', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payload.name.strip(), payload.state.strip(), payload.region.strip(), payload.category.strip(),
            payload.lat, payload.lng, score, tier,
            payload.description.strip() or f"Scenic tourist destination in {payload.state}, India.",
            img, payload.best_visit_time, payload.dress_code_etiquette,
            payload.opening_time or "06:00", payload.closing_time or "18:30",
            payload.weekly_off_day or "None", payload.peak_rush_hours or "10:30 AM - 03:00 PM",
            payload.entry_fee_domestic or "Rs 50", payload.entry_fee_foreign or "Rs 500",
            payload.booking_portal_url or ""
        ))
        dest_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO risk_metrics (
                destination_id, crime_index, scam_index, weather_risk,
                health_risk, night_safety, crowd_density, transport_safety
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (dest_id, metrics_dict["crime_index"], metrics_dict["scam_index"], metrics_dict["weather_risk"], metrics_dict["health_risk"], metrics_dict["night_safety"], metrics_dict["crowd_density"], metrics_dict["transport_safety"]))

        fac_name = payload.emergency_facility_name or f"{payload.name} Tourist Police Desk"
        fac_type = payload.emergency_facility_type or "Police"
        fac_phone = payload.emergency_facility_phone or "112"
        cursor.execute("""
            INSERT INTO emergency_contacts (
                destination_id, facility_name, facility_type, phone, address, lat, lng, is_24_7
            ) VALUES (?, ?, ?, ?, 'Central Desk', ?, ?, 1)
        """, (dest_id, fac_name, fac_type, fac_phone, payload.lat, payload.lng))

        cursor.execute("""
            INSERT INTO safety_tips (destination_id, tip_text, category)
            VALUES (?, 'Follow local guidelines and state tourist police advisories for a safe trip.', 'General')
        """, (dest_id,))

        return {
            "success": True,
            "destination_id": dest_id,
            "name": payload.name,
            "overall_safety_score": score,
            "risk_tier": tier,
            "message": f"Successfully created destination '{payload.name}' with safety score {score}/100."
        }


@router.get("/crowd")
def admin_crowd_overview(current_admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, maximum_capacity, comfortable_capacity, emergency_capacity_override,
                   geofence_radius_m, crowd_status, threshold_low_max, threshold_moderate_max,
                   threshold_high_max, threshold_very_high_max
            FROM destinations ORDER BY name
            """
        )
        dests = [dict(d) for d in cursor.fetchall()]
    results = []
    for d in dests:
        try:
            s = estimate_current_crowd(d["id"])
            results.append({**d, "live": s})
        except Exception as e:
            results.append({**d, "live": {"error": str(e)}})
    return {
        "demo_mode": is_demo_enabled(),
        "destinations": results,
        "label": "Admin crowd console — estimates only",
    }


@router.put("/destinations/{dest_id}/crowd-config")
def update_crowd_config(
    dest_id: int,
    payload: CrowdCapacityUpdate,
    current_admin: dict = Depends(get_current_admin),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM destinations WHERE id = ?", (dest_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Destination not found")
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        allowed = set(CrowdCapacityUpdate.model_fields.keys())
        parts = []
        values = []
        for k, v in updates.items():
            if k in allowed:
                parts.append(f"{k} = ?")
                values.append(v)
        values.append(dest_id)
        cursor.execute(f"UPDATE destinations SET {', '.join(parts)} WHERE id = ?", values)
        return {"success": True, "destination_id": dest_id, "updated": list(updates.keys())}


@router.post("/slots")
def admin_create_slot(payload: SlotCreate, current_admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO ticket_slots
                (destination_id, slot_date, start_time, end_time, capacity, booked_count, reserved_count, status)
                VALUES (?, ?, ?, ?, ?, 0, 0, ?)
                """,
                (
                    payload.destination_id,
                    payload.slot_date,
                    payload.start_time,
                    payload.end_time,
                    payload.capacity,
                    payload.status,
                ),
            )
            return {"success": True, "slot_id": cursor.lastrowid}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


@router.put("/slots/{slot_id}")
def admin_update_slot(
    slot_id: int, payload: SlotUpdate, current_admin: dict = Depends(get_current_admin)
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ticket_slots WHERE id = ?", (slot_id,))
        slot = cursor.fetchone()
        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")
        updates = payload.model_dump(exclude_unset=True)
        if "capacity" in updates and updates["capacity"] < int(slot["booked_count"]):
            raise HTTPException(
                status_code=400,
                detail="Capacity cannot be below already booked tickets",
            )
        parts, values = [], []
        for k, v in updates.items():
            parts.append(f"{k} = ?")
            values.append(v)
        if not parts:
            raise HTTPException(status_code=400, detail="No fields to update")
        values.append(slot_id)
        cursor.execute(f"UPDATE ticket_slots SET {', '.join(parts)} WHERE id = ?", values)
        return {"success": True, "slot_id": slot_id}


@router.post("/zones")
def admin_create_zone(payload: ZoneCreate, current_admin: dict = Depends(get_current_admin)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO destination_zones
            (destination_id, name, zone_type, capacity, area_sq_meters, center_lat, center_lng, radius_m, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """,
            (
                payload.destination_id,
                payload.name,
                payload.zone_type,
                payload.capacity,
                payload.area_sq_meters,
                payload.center_lat,
                payload.center_lng,
                payload.radius_m,
            ),
        )
        return {"success": True, "zone_id": cursor.lastrowid}


@router.post("/demo-mode")
def admin_demo_mode(payload: DemoModeUpdate, current_admin: dict = Depends(get_current_admin)):
    set_demo_mode(payload.enabled)
    history = 0
    tick = None
    if payload.enabled:
        with get_db() as conn:
            seed_destination_crowd_defaults(conn.cursor())
        if payload.bootstrap_history:
            history = bootstrap_historical_demo_snapshots(days=7)
        tick = run_demo_tick()
    return {
        "success": True,
        "demo_mode": payload.enabled,
        "label": "DEMO DATA" if payload.enabled else "LIVE / ESTIMATE MODE",
        "historical_snapshots_created": history,
        "tick": tick,
        "warning": "Demo data must never be presented as real live measurements.",
    }


@router.post("/demo-tick")
def admin_demo_tick(current_admin: dict = Depends(get_current_admin)):
    if not is_demo_enabled():
        raise HTTPException(status_code=400, detail="DEMO_MODE is not enabled")
    return run_demo_tick()


@router.post("/destinations/{dest_id}/ensure-slots")
def admin_ensure_slots(
    dest_id: int,
    date: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin),
):
    slot_date = date or datetime.utcnow().strftime("%Y-%m-%d")
    slots = ensure_slots_for_date(dest_id, slot_date)
    return {"success": True, "date": slot_date, "slots": len(slots)}


@router.post("/destinations/{dest_id}/snapshot")
def admin_snapshot(dest_id: int, current_admin: dict = Depends(get_current_admin)):
    try:
        return capture_snapshot(dest_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

