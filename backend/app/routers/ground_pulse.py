from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Any, Optional
import math
from datetime import datetime

from ..database import get_db
from ..models.schemas import PulseVoteCreate, PulseVoteOut, ConsensusStats
from ..auth import get_current_user

router = APIRouter(prefix="/api/pulse", tags=["Ground Pulse MCQ & Proximity Voting"])

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in kilometers between two points on Earth."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)

def calculate_badge(xp: int) -> str:
    if xp >= 1000:
        return "Bharat Trail Master"
    elif xp >= 500:
        return "Trail Guardian"
    elif xp >= 250:
        return "Field Scout"
    return "Verified Explorer"

@router.get("/proximity-check")
def check_proximity(
    dest_id: int = Query(..., description="Destination ID"),
    lat: float = Query(..., description="User latitude"),
    lon: float = Query(..., description="User longitude")
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, lat, lng FROM destinations WHERE id = ?", (dest_id,))
        dest = cursor.fetchone()
        if not dest:
            raise HTTPException(status_code=404, detail="Destination not found")
        
        distance = calculate_haversine_distance(lat, lon, dest["lat"], dest["lng"])
        is_within_range = distance <= 25.0
        return {
            "destination_id": dest["id"],
            "destination_name": dest["name"],
            "distance_km": distance,
            "threshold_km": 25.0,
            "is_within_range": is_within_range,
            "status_message": "Within verified on-site perimeter (<=25 km)" if is_within_range else f"{distance:.1f} km away. Use demo simulator or travel within 25 km."
        }

@router.post("/vote", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def submit_ground_pulse_vote(
    payload: PulseVoteCreate,
    current_user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, lat, lng, overall_safety_score FROM destinations WHERE id = ?", (payload.destination_id,))
        dest = cursor.fetchone()
        if not dest:
            raise HTTPException(status_code=404, detail="Destination not found")
        
        distance = calculate_haversine_distance(
            payload.user_lat, payload.user_lon,
            dest["lat"], dest["lng"]
        )

        is_onsite = (distance <= 25.0) or payload.is_simulated_override

        if not is_onsite:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Geofence perimeter restriction: You are currently {distance:.1f} km away from {dest['name']}. "
                       f"Authentic Ground Pulse voting requires being within 25 km. "
                       f"To test, select a destination from the 'Demo Location Simulator' in the top bar."
            )
        
        # Insert vote
        cursor.execute("""
            INSERT INTO ground_pulse_votes (
                destination_id, user_id, user_name, user_city,
                is_onsite_verified, distance_km, crowd_rush, visit_recommendation,
                safety_vibe, ground_weather, clean_sanitation, user_comment, helpful_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            dest["id"],
            current_user["id"],
            current_user["full_name"],
            current_user.get("home_city", "Traveler"),
            1 if is_onsite else 0,
            distance,
            payload.crowd_rush,
            payload.visit_recommendation,
            payload.safety_vibe,
            payload.ground_weather,
            payload.clean_sanitation or "Good",
            payload.user_comment.strip() if payload.user_comment else None
        ))
        vote_id = cursor.lastrowid

        # Update User XP (+50 points for on-site report)
        cursor.execute("SELECT reputation_xp FROM users WHERE id = ?", (current_user["id"],))
        u_row = cursor.fetchone()
        new_xp = (u_row["reputation_xp"] or 100) + 50
        new_badge = calculate_badge(new_xp)

        cursor.execute("UPDATE users SET reputation_xp = ? WHERE id = ?", (new_xp, current_user["id"]))

        # Check if crowd_density needs update
        cursor.execute("""
            SELECT crowd_rush FROM ground_pulse_votes 
            WHERE destination_id = ? 
            ORDER BY id DESC LIMIT 10
        """, (dest["id"],))
        recent_rushes = [r["crowd_rush"] for r in cursor.fetchall()]
        if recent_rushes:
            rush_score_map = {"Peaceful": 25.0, "Moderate": 50.0, "Heavy": 80.0, "Extreme": 95.0}
            avg_density = sum(rush_score_map.get(r, 50.0) for r in recent_rushes) / len(recent_rushes)
            cursor.execute("UPDATE risk_metrics SET crowd_density = ? WHERE destination_id = ?", (round(avg_density, 1), dest["id"]))

        conn.commit()

        return {
            "success": True,
            "vote_id": vote_id,
            "message": "Ground pulse registered! +50 Reputation XP awarded.",
            "awarded_xp": 50,
            "new_reputation_xp": new_xp,
            "new_badge": new_badge,
            "distance_km": distance,
            "is_onsite_verified": is_onsite
        }

@router.get("/{dest_id}/consensus", response_model=ConsensusStats)
def get_destination_consensus(dest_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM destinations WHERE id = ?", (dest_id,))
        dest = cursor.fetchone()
        if not dest:
            raise HTTPException(status_code=404, detail="Destination not found")
        
        cursor.execute("""
            SELECT v.*, u.reputation_xp 
            FROM ground_pulse_votes v
            LEFT JOIN users u ON v.user_id = u.id
            WHERE v.destination_id = ?
            ORDER BY v.id DESC
        """, (dest_id,))
        votes = cursor.fetchall()
        
        total_votes = len(votes)
        if total_votes == 0:
            return ConsensusStats(
                destination_id=dest_id,
                total_votes=0,
                recommendation_breakdown={"Recommended": 0, "Neutral": 0, "Avoid": 0},
                recommend_percentage=90.0,
                crowd_consensus="Moderate",
                safety_consensus="Very Safe",
                weather_consensus="Pleasant",
                cleanliness_consensus="Good",
                recent_pulse_feed=[]
            )
        
        recs = {"Recommended": 0, "Neutral": 0, "Avoid": 0}
        crowd_counts: Dict[str, int] = {}
        safety_counts: Dict[str, int] = {}
        weather_counts: Dict[str, int] = {}
        clean_counts: Dict[str, int] = {}

        feed: List[PulseVoteOut] = []
        for row in votes:
            rec = row["visit_recommendation"]
            recs[rec] = recs.get(rec, 0) + 1

            cr = row["crowd_rush"]
            crowd_counts[cr] = crowd_counts.get(cr, 0) + 1

            sf = row["safety_vibe"]
            safety_counts[sf] = safety_counts.get(sf, 0) + 1

            wt = row["ground_weather"]
            weather_counts[wt] = weather_counts.get(wt, 0) + 1

            cl = row["clean_sanitation"] or "Good"
            clean_counts[cl] = clean_counts.get(cl, 0) + 1

            if len(feed) < 15:
                badge = calculate_badge(row["reputation_xp"] or 100)
                feed.append(PulseVoteOut(
                    id=row["id"],
                    destination_id=row["destination_id"],
                    user_name=row["user_name"],
                    user_badge=badge,
                    user_city=row["user_city"] or "India",
                    crowd_rush=row["crowd_rush"],
                    visit_recommendation=row["visit_recommendation"],
                    safety_vibe=row["safety_vibe"],
                    ground_weather=row["ground_weather"],
                    clean_sanitation=row["clean_sanitation"] or "Good",
                    user_comment=row["user_comment"],
                    distance_km=row["distance_km"],
                    is_onsite_verified=bool(row["is_onsite_verified"]),
                    helpful_count=row["helpful_count"] or 1,
                    created_at=str(row["created_at"])
                ))
        
        recommended_count = recs.get("Recommended", 0)
        rec_pct = round((recommended_count / total_votes) * 100.0, 1)
        crowd_cons = max(crowd_counts, key=crowd_counts.get) if crowd_counts else "Moderate"
        safety_cons = max(safety_counts, key=safety_counts.get) if safety_counts else "Very Safe"
        weather_cons = max(weather_counts, key=weather_counts.get) if weather_counts else "Pleasant"
        clean_cons = max(clean_counts, key=clean_counts.get) if clean_counts else "Good"

        return ConsensusStats(
            destination_id=dest_id,
            total_votes=total_votes,
            recommendation_breakdown=recs,
            recommend_percentage=rec_pct,
            crowd_consensus=crowd_cons,
            safety_consensus=safety_cons,
            weather_consensus=weather_cons,
            cleanliness_consensus=clean_cons,
            recent_pulse_feed=feed
        )
