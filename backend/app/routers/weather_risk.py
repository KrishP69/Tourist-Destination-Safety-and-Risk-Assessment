from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
from app.database import get_db
from app.services.weather_aqi_service import fetch_complete_environmental_intelligence

router = APIRouter(prefix="/api/weather-risk", tags=["Weather, AQI & Extreme Hazard Intelligence"])


@router.get("/destination/{dest_id}")
async def get_destination_environmental_intelligence(
    dest_id: int,
    force_refresh: bool = Query(False, description="Bypass cache and query Open-Meteo fresh")
):
    """
    Fetches real-time environmental telemetry (Temperature, Weather, AQI, PM2.5, PM10)
    and evaluates terrain-specific hazard models (Landslides, High Tides, Smog, Heatwaves).
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, state, region, category, lat, lng FROM destinations WHERE id = ?", (dest_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Destination not found")

        dest = dict(row)

    data = await fetch_complete_environmental_intelligence(
        lat=dest["lat"],
        lng=dest["lng"],
        name=dest["name"],
        state=dest.get("state", "India"),
        category=dest.get("category", "Monument"),
        force_refresh=force_refresh
    )
    data["destination_id"] = dest_id
    return data


@router.get("/live")
async def get_live_coordinates_environmental_intelligence(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    name: str = Query("Current Location", description="Location name"),
    state: str = Query("India", description="State"),
    category: str = Query("Tourist Spot", description="Category"),
    force_refresh: bool = Query(False)
):
    """
    Fetches live weather & AQI intelligence for any dynamic coordinate (e.g. user GPS location).
    """
    return await fetch_complete_environmental_intelligence(
        lat=lat,
        lng=lng,
        name=name,
        state=state,
        category=category,
        force_refresh=force_refresh
    )


@router.get("/alerts-summary")
async def get_national_environmental_alerts_summary():
    """
    Scans iconic representative destinations across India (Hill Stations, Coastal, Urban North, Arid Plains)
    and returns all active environmental hazard warnings and high-priority travel advisories.
    """
    targets = [
        {"name": "Lohagad Fort (Lonavala)", "lat": 18.70, "lng": 73.47, "state": "Maharashtra", "cat": "Hill Stations & Treks"},
        {"name": "Munnar Tea Hills", "lat": 10.08, "lng": 77.06, "state": "Kerala", "cat": "Hill Stations & Treks"},
        {"name": "Lotus Temple (Delhi)", "lat": 28.55, "lng": 77.25, "state": "Delhi", "cat": "Monument & Urban"},
        {"name": "Taj Mahal (Agra)", "lat": 27.17, "lng": 78.04, "state": "Uttar Pradesh", "cat": "Monument & Heritage"},
        {"name": "Calangute Beach (Goa)", "lat": 15.54, "lng": 73.75, "state": "Goa", "cat": "Beach & Coastal"},
        {"name": "Bangaram Island (Lakshadweep)", "lat": 10.94, "lng": 72.29, "state": "Lakshadweep", "cat": "Island & Coastal"},
        {"name": "Golden Temple (Amritsar)", "lat": 31.62, "lng": 74.87, "state": "Punjab", "cat": "Heritage & Spiritual"},
        {"name": "Jaisalmer Fort", "lat": 26.91, "lng": 70.91, "state": "Rajasthan", "cat": "Forts & Desert"},
        {"name": "Manali Valley", "lat": 32.24, "lng": 77.18, "state": "Himachal Pradesh", "cat": "Hill Stations & Treks"},
    ]

    active_alerts = []
    overall_telemetry = []

    for t in targets:
        try:
            res = await fetch_complete_environmental_intelligence(
                lat=t["lat"],
                lng=t["lng"],
                name=t["name"],
                state=t["state"],
                category=t["cat"],
                force_refresh=False
            )
            overall_telemetry.append(res)
            if res.get("has_active_hazard") and res.get("hazard_alert"):
                active_alerts.append({
                    "destination": t["name"],
                    "state": t["state"],
                    "hazard": res["hazard_alert"],
                    "temperature_c": res["weather"]["temperature_c"],
                    "aqi": res["air_quality"]["aqi_score"],
                    "pm2_5": res["air_quality"]["pm2_5"]
                })
        except Exception:
            continue

    return {
        "status": "success",
        "total_monitored": len(targets),
        "active_alerts_count": len(active_alerts),
        "alerts": active_alerts,
        "sample_telemetry": overall_telemetry[:5]
    }
