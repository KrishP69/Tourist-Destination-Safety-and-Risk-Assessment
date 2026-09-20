from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.models.schemas import AdvisoryCreate, MetricUpdate, AdminDestinationCreate
from app.services.risk_service import calculate_safety_score
from app.auth import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])

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

