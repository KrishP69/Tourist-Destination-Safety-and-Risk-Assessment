from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import math
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from app.database import get_db
from app.services.weather_service import fetch_live_weather
from app.services.risk_service import calculate_safety_score
from app.services.news_service import get_destination_news, get_national_travel_news
import urllib.request
import json

router = APIRouter(prefix="/api/destinations", tags=["Destinations & Tourist Spots"])

class NewDestinationPayload(BaseModel):
    name: str
    state: str = "India"
    region: str = "North India"
    category: str = "Heritage & Forts"
    lat: float
    lng: float
    description: Optional[str] = None
    image_url: Optional[str] = None
    best_visit_time: Optional[str] = "October to March"
    dress_code_etiquette: Optional[str] = "Modest attire recommended."
    opening_time: Optional[str] = "06:00"
    closing_time: Optional[str] = "18:30"
    weekly_off_day: Optional[str] = "None"
    peak_rush_hours: Optional[str] = "11:00 AM - 03:30 PM"
    entry_fee_domestic: Optional[str] = "Free"
    entry_fee_foreign: Optional[str] = "Free"
    booking_portal_url: Optional[str] = ""

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)

def check_is_open_now(opening_time: Optional[str], closing_time: Optional[str], weekly_off: Optional[str]) -> tuple[bool, str]:
    """
    Evaluates real-time opening status based on Indian Standard Time (UTC+5:30).
    """
    ist = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist)
    current_day = now_ist.strftime("%A") # e.g. Friday

    if weekly_off and weekly_off.lower() != "none" and current_day.lower() == weekly_off.lower():
        return False, f"Closed Today ({current_day} Weekly Off)"

    if not opening_time or not closing_time or "24/7" in str(opening_time).lower() or "24/7" in str(closing_time).lower():
        return True, "Open 24/7"

    try:
        open_parts = opening_time.strip().split(":")
        close_parts = closing_time.strip().split(":")
        open_h, open_m = int(open_parts[0]), int(open_parts[1]) if len(open_parts) > 1 else 0
        close_h, close_m = int(close_parts[0]), int(close_parts[1]) if len(close_parts) > 1 else 0

        now_mins = now_ist.hour * 60 + now_ist.minute
        open_mins = open_h * 60 + open_m
        close_mins = close_h * 60 + close_m

        if open_mins <= now_mins <= close_mins:
            return True, f"Open Now (Closes at {closing_time})"
        elif now_mins < open_mins:
            return False, f"Closed Now (Opens at {opening_time})"
        else:
            return False, f"Closed for the Day (Opens at {opening_time})"
    except Exception:
        return True, "Open Today"

@router.get("")
def get_destinations(
    search: Optional[str] = None,
    risk_tier: Optional[str] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None
):
    with get_db() as conn:
        cursor = conn.cursor()
        query = """
        SELECT d.*, 
               m.crime_index, m.scam_index, m.weather_risk, m.health_risk, m.night_safety, m.crowd_density, m.transport_safety,
               (SELECT COUNT(*) FROM incidents i WHERE i.destination_id = d.id AND i.status IN ('Active', 'Verified')) as active_incidents_count,
               (SELECT COUNT(*) FROM safety_advisories a WHERE a.destination_id = d.id AND a.is_active = 1) as active_advisories_count,
               (SELECT COUNT(*) FROM ground_pulse_votes p WHERE p.destination_id = d.id) as pulse_vote_count,
               (SELECT COUNT(*) FROM ground_pulse_votes p WHERE p.destination_id = d.id AND p.visit_recommendation = 'Recommended') as pulse_recommend_count
        FROM destinations d
        LEFT JOIN risk_metrics m ON d.id = m.destination_id
        WHERE 1=1
        """
        params = []

        if search:
            query += " AND (d.name LIKE ? OR d.state LIKE ? OR d.region LIKE ? OR d.category LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term, term])

        if risk_tier and risk_tier != "All":
            query += " AND d.risk_tier = ?"
            params.append(risk_tier)

        if category and category != "All":
            query += " AND d.category = ?"
            params.append(category)

        if region and region != "All":
            query += " AND d.region = ?"
            params.append(region)

        query += " ORDER BY d.overall_safety_score DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Fetch active incidents mapped by destination_id
        cursor.execute("""
            SELECT id, destination_id, title, category, category AS incident_type, severity, location_name, description, reported_at, status
            FROM incidents
            WHERE status IN ('Active', 'Verified')
            ORDER BY reported_at DESC
        """)
        incidents_by_dest: Dict[int, List[Dict[str, Any]]] = {}
        for inc_row in cursor.fetchall():
            d_id = inc_row["destination_id"]
            if d_id not in incidents_by_dest:
                incidents_by_dest[d_id] = []
            incidents_by_dest[d_id].append(dict(inc_row))
        
        results = []
        for r in rows:
            dest_dict = dict(r)

            # Calculate distance if user coords provided
            if user_lat is not None and user_lon is not None:
                dist = calculate_haversine_distance(user_lat, user_lon, dest_dict["lat"], dest_dict["lng"])
                dest_dict["distance_km"] = dist
                dest_dict["is_within_geofence"] = dist <= 25.0
            else:
                dest_dict["distance_km"] = None
                dest_dict["is_within_geofence"] = False

            # Calculate consensus recommendation %
            total_votes = dest_dict.get("pulse_vote_count", 0)
            rec_votes = dest_dict.get("pulse_recommend_count", 0)
            if total_votes > 0:
                dest_dict["recommend_percentage"] = round((rec_votes / total_votes) * 100.0, 1)
            else:
                dest_dict["recommend_percentage"] = 92.0

            # Real-time operational open/closed computation
            is_open, status_text = check_is_open_now(
                dest_dict.get("opening_time"),
                dest_dict.get("closing_time"),
                dest_dict.get("weekly_off_day")
            )
            dest_dict["is_currently_open"] = is_open
            dest_dict["open_status_text"] = status_text

            # Attach active hazards
            dest_dict["nearby_incidents"] = incidents_by_dest.get(dest_dict["id"], [])
            
            results.append(dest_dict)
            
        return results

@router.get("/stats/overview")
def get_overview_stats():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), AVG(overall_safety_score) FROM destinations")
        total_dest, avg_score = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM incidents WHERE status IN ('Active', 'Verified')")
        active_incidents = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM safety_advisories WHERE is_active = 1")
        active_advisories = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM ground_pulse_votes")
        total_pulse_votes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users")
        total_registered_users = cursor.fetchone()[0]

        return {
            "total_destinations": total_dest or 0,
            "average_safety_score": round(avg_score or 0, 1),
            "active_incidents": active_incidents,
            "active_advisories": active_advisories,
            "total_ground_pulse_votes": total_pulse_votes,
            "total_travelers": total_registered_users
        }

@router.post("")
async def create_new_destination(dest: NewDestinationPayload):
    """Dynamically add an Indian tourist spot with real-time baseline assessment"""
    temp, condition, wind, precip, live_weather_risk = await fetch_live_weather(dest.lat, dest.lng)

    default_metrics = {
        "crime_index": 18.0,
        "scam_index": 22.0,
        "weather_risk": live_weather_risk,
        "health_risk": 15.0,
        "night_safety": 84.0,
        "crowd_density": 50.0,
        "transport_safety": 82.0
    }

    score, tier = calculate_safety_score(default_metrics)
    img = dest.image_url or "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=800"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO destinations (
            name, state, region, category, lat, lng,
            overall_safety_score, risk_tier, description, image_url,
            best_visit_time, dress_code_etiquette, opening_time, closing_time,
            weekly_off_day, peak_rush_hours, entry_fee_domestic, entry_fee_foreign, booking_portal_url
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dest.name, dest.state, dest.region, dest.category, dest.lat, dest.lng,
            score, tier, dest.description or f"Scenic tourist destination in {dest.state}, India.", img,
            dest.best_visit_time, dest.dress_code_etiquette, dest.opening_time, dest.closing_time,
            dest.weekly_off_day, dest.peak_rush_hours, dest.entry_fee_domestic, dest.entry_fee_foreign, dest.booking_portal_url
        ))
        dest_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO risk_metrics (destination_id, crime_index, scam_index, weather_risk, health_risk, night_safety, crowd_density, transport_safety)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (dest_id, default_metrics["crime_index"], default_metrics["scam_index"], default_metrics["weather_risk"], default_metrics["health_risk"], default_metrics["night_safety"], default_metrics["crowd_density"], default_metrics["transport_safety"]))

        cursor.execute("""
        INSERT INTO emergency_contacts (destination_id, facility_name, facility_type, phone, address, lat, lng, is_24_7)
        VALUES (?, 'State Tourist Police Desk', 'Police', '112', 'Central Police Station', ?, ?, 1)
        """, (dest_id, dest.lat, dest.lng))

        return {
            "success": True,
            "destination_id": dest_id,
            "overall_safety_score": score,
            "risk_tier": tier,
            "live_weather": {
                "temperature_c": temp,
                "condition": condition,
                "wind_speed_kmh": wind
            },
            "message": f"'{dest.name}' successfully added and evaluated for Bharat network!"
        }

@router.post("/{dest_id}/sync-live")
async def sync_destination_live_weather(dest_id: int):
    """Sync real-time atmospheric hazards from Open-Meteo and recalibrate safety score on the fly"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT d.*, m.* FROM destinations d JOIN risk_metrics m ON d.id = m.destination_id WHERE d.id = ?", (dest_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Destination not found")

        lat = row["lat"]
        lng = row["lng"]

        temp, condition, wind, precip, live_weather_risk = await fetch_live_weather(lat, lng)

        cursor.execute("UPDATE risk_metrics SET weather_risk = ?, updated_at = CURRENT_TIMESTAMP WHERE destination_id = ?", (live_weather_risk, dest_id))
        cursor.execute("SELECT * FROM risk_metrics WHERE destination_id = ?", (dest_id,))
        m = dict(cursor.fetchone())

        cursor.execute("SELECT COUNT(*) FROM incidents WHERE destination_id = ? AND severity = 'Critical' AND status = 'Active'", (dest_id,))
        crit_count = cursor.fetchone()[0]

        new_score, new_tier = calculate_safety_score(m, crit_count)
        cursor.execute("UPDATE destinations SET overall_safety_score = ?, risk_tier = ? WHERE id = ?", (new_score, new_tier, dest_id))

        return {
            "success": True,
            "destination_id": dest_id,
            "name": row["name"],
            "live_weather": {
                "temperature_c": temp,
                "condition": condition,
                "wind_kmh": wind,
                "precipitation_mm": precip,
                "weather_risk_index": live_weather_risk
            },
            "overall_safety_score": new_score,
            "risk_tier": new_tier,
            "message": f"Real-time weather synced: {temp}°C ({condition}). Safety index: {new_score}/100."
        }

@router.get("/{dest_id}")
async def get_destination_details(
    dest_id: int,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT d.*, 
               m.crime_index, m.scam_index, m.weather_risk, m.health_risk, m.night_safety, m.crowd_density, m.transport_safety
        FROM destinations d
        LEFT JOIN risk_metrics m ON d.id = m.destination_id
        WHERE d.id = ?
        """, (dest_id,))
        dest = cursor.fetchone()
        if not dest:
            raise HTTPException(status_code=404, detail="Destination not found")

        cursor.execute("SELECT * FROM emergency_contacts WHERE destination_id = ? ORDER BY facility_type", (dest_id,))
        contacts = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM safety_advisories WHERE destination_id = ? AND is_active = 1 ORDER BY issued_at DESC", (dest_id,))
        advisories = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM incidents WHERE destination_id = ? ORDER BY reported_at DESC LIMIT 10", (dest_id,))
        incidents = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM safety_tips WHERE destination_id = ?", (dest_id,))
        tips = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM ground_pulse_votes WHERE destination_id = ? ORDER BY id DESC LIMIT 10", (dest_id,))
        recent_votes = [dict(r) for r in cursor.fetchall()]

        result = dict(dest)
        result["emergency_contacts"] = contacts
        result["advisories"] = advisories
        result["incidents"] = incidents
        result["tips"] = tips
        result["recent_ground_pulse"] = recent_votes

        # Compute real-time IST open/closed status
        is_open, status_text = check_is_open_now(
            result.get("opening_time"),
            result.get("closing_time"),
            result.get("weekly_off_day")
        )
        result["is_currently_open"] = is_open
        result["open_status_text"] = status_text

        # Active incidents tagged
        for inc_item in incidents:
            inc_item["incident_type"] = inc_item.get("category", "Hazard")
        result["nearby_incidents"] = [i for i in incidents if i.get("status") in ("Active", "Verified")]

        if user_lat is not None and user_lon is not None:
            dist = calculate_haversine_distance(user_lat, user_lon, result["lat"], result["lng"])
            result["distance_km"] = dist
            result["is_within_geofence"] = dist <= 25.0
        else:
            result["distance_km"] = None
            result["is_within_geofence"] = False

        # Attach real-time Google News & Safety Bulletins
        result["live_news"] = get_destination_news(result["name"], result.get("state", "India"))

        return result

@router.get("/{dest_id}/live-news")
def get_single_destination_news(dest_id: int):
    """Fetches real-time live Google News updates and safety bulletins for a specific destination"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, state FROM destinations WHERE id = ?", (dest_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Destination not found")
        news = get_destination_news(row["name"], row["state"])
        return {
            "destination_id": dest_id,
            "destination_name": row["name"],
            "news_count": len(news),
            "news": news
        }

@router.get("/news/live-travel-alerts")
def get_live_national_travel_alerts():
    """Fetches real-time national travel advisories and news from Google News"""
    news = get_national_travel_news()
    return {
        "status": "success",
        "source": "Google News India",
        "alerts_count": len(news),
        "alerts": news
    }

@router.get("/network/ip-location")
def get_network_ip_location():
    """Fallback IP geolocation to acquire user's city and coordinates when device GPS is unavailable"""
    try:
        req = urllib.request.Request(
            "http://ip-api.com/json/",
            headers={"User-Agent": "Mozilla/5.0 SafeTour-Bharat"}
        )
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "success":
                return {
                    "success": True,
                    "city": data.get("city", "Mumbai"),
                    "region": data.get("regionName", "India"),
                    "country": data.get("country", "India"),
                    "lat": float(data.get("lat", 19.0760)),
                    "lng": float(data.get("lon", 72.8777)),
                    "source": "Network IP Telemetry"
                }
    except Exception as e:
        print(f"[IPLocation] Failed: {e}")

    # Default fallback to Delhi Central
    return {
        "success": False,
        "city": "New Delhi",
        "region": "Delhi",
        "country": "India",
        "lat": 28.6139,
        "lng": 77.2090,
        "source": "Default Fallback"
    }
