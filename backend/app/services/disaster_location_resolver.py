"""
India location resolver for disaster articles.
Matches known places (longest-first) — never invents coordinates.
State-only matches are allowed but marked low specificity (lower confidence).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

# Real approximate centroids — used only when article text matches the place name.
# Prefer district/city over bare state when both appear.
INDIA_PLACES: List[Dict[str, Any]] = [
    # States / UTs (centroids) — lower specificity
    {"name": "Assam", "kind": "state", "state": "Assam", "lat": 26.2006, "lng": 92.9376},
    {"name": "Kerala", "kind": "state", "state": "Kerala", "lat": 10.8505, "lng": 76.2711},
    {"name": "Maharashtra", "kind": "state", "state": "Maharashtra", "lat": 19.7515, "lng": 75.7139},
    {"name": "Gujarat", "kind": "state", "state": "Gujarat", "lat": 22.2587, "lng": 71.1924},
    {"name": "Rajasthan", "kind": "state", "state": "Rajasthan", "lat": 27.0238, "lng": 74.2179},
    {"name": "Odisha", "kind": "state", "state": "Odisha", "lat": 20.9517, "lng": 85.0985},
    {"name": "Orissa", "kind": "state", "state": "Odisha", "lat": 20.9517, "lng": 85.0985},
    {"name": "West Bengal", "kind": "state", "state": "West Bengal", "lat": 22.9868, "lng": 87.8550},
    {"name": "Tamil Nadu", "kind": "state", "state": "Tamil Nadu", "lat": 11.1271, "lng": 78.6569},
    {"name": "Karnataka", "kind": "state", "state": "Karnataka", "lat": 15.3173, "lng": 75.7139},
    {"name": "Himachal Pradesh", "kind": "state", "state": "Himachal Pradesh", "lat": 31.1048, "lng": 77.1734},
    {"name": "Uttarakhand", "kind": "state", "state": "Uttarakhand", "lat": 30.0668, "lng": 79.0193},
    {"name": "Uttar Pradesh", "kind": "state", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462},
    {"name": "Bihar", "kind": "state", "state": "Bihar", "lat": 25.0961, "lng": 85.3131},
    {"name": "Madhya Pradesh", "kind": "state", "state": "Madhya Pradesh", "lat": 22.9734, "lng": 78.6569},
    {"name": "Telangana", "kind": "state", "state": "Telangana", "lat": 18.1124, "lng": 79.0193},
    {"name": "Andhra Pradesh", "kind": "state", "state": "Andhra Pradesh", "lat": 15.9129, "lng": 79.7400},
    {"name": "Punjab", "kind": "state", "state": "Punjab", "lat": 31.1471, "lng": 75.3412},
    {"name": "Haryana", "kind": "state", "state": "Haryana", "lat": 29.0588, "lng": 76.0856},
    {"name": "Delhi", "kind": "state", "state": "Delhi", "lat": 28.6139, "lng": 77.2090},
    {"name": "Jammu and Kashmir", "kind": "state", "state": "Jammu & Kashmir", "lat": 33.7782, "lng": 76.5762},
    {"name": "Jammu & Kashmir", "kind": "state", "state": "Jammu & Kashmir", "lat": 33.7782, "lng": 76.5762},
    {"name": "Ladakh", "kind": "state", "state": "Ladakh (UT)", "lat": 34.1526, "lng": 77.5770},
    {"name": "Sikkim", "kind": "state", "state": "Sikkim", "lat": 27.5330, "lng": 88.5122},
    {"name": "Meghalaya", "kind": "state", "state": "Meghalaya", "lat": 25.4670, "lng": 91.3662},
    {"name": "Arunachal Pradesh", "kind": "state", "state": "Arunachal Pradesh", "lat": 28.2180, "lng": 94.7278},
    {"name": "Goa", "kind": "state", "state": "Goa", "lat": 15.2993, "lng": 74.1240},
    # Assam / NE districts & cities (higher specificity)
    {"name": "Sivasagar", "kind": "district", "state": "Assam", "district": "Sivasagar", "lat": 26.9826, "lng": 94.6414},
    {"name": "Sibsagar", "kind": "district", "state": "Assam", "district": "Sivasagar", "lat": 26.9826, "lng": 94.6414},
    {"name": "Guwahati", "kind": "city", "state": "Assam", "city": "Guwahati", "lat": 26.1445, "lng": 91.7362},
    {"name": "Dibrugarh", "kind": "district", "state": "Assam", "district": "Dibrugarh", "lat": 27.4728, "lng": 94.9120},
    {"name": "Jorhat", "kind": "district", "state": "Assam", "district": "Jorhat", "lat": 26.7509, "lng": 94.2037},
    {"name": "Kaziranga", "kind": "city", "state": "Assam", "city": "Kaziranga", "lat": 26.5775, "lng": 93.1711},
    {"name": "Majuli", "kind": "district", "state": "Assam", "district": "Majuli", "lat": 26.9500, "lng": 94.1667},
    {"name": "Cachar", "kind": "district", "state": "Assam", "district": "Cachar", "lat": 24.8333, "lng": 92.7789},
    {"name": "Barpeta", "kind": "district", "state": "Assam", "district": "Barpeta", "lat": 26.3228, "lng": 91.0063},
    {"name": "Lakhimpur", "kind": "district", "state": "Assam", "district": "Lakhimpur", "lat": 27.2350, "lng": 94.0987},
    {"name": "Dhemaji", "kind": "district", "state": "Assam", "district": "Dhemaji", "lat": 27.4833, "lng": 94.5833},
    {"name": "Imphal", "kind": "city", "state": "Manipur", "city": "Imphal", "lat": 24.8170, "lng": 93.9368},
    {"name": "Aizawl", "kind": "city", "state": "Mizoram", "city": "Aizawl", "lat": 23.7271, "lng": 92.7176},
    {"name": "Agartala", "kind": "city", "state": "Tripura", "city": "Agartala", "lat": 23.8315, "lng": 91.2868},
    {"name": "Shillong", "kind": "city", "state": "Meghalaya", "city": "Shillong", "lat": 25.5788, "lng": 91.8933},
    {"name": "Cherrapunji", "kind": "city", "state": "Meghalaya", "city": "Cherrapunji", "lat": 25.2843, "lng": 91.7216},
    {"name": "Gangtok", "kind": "city", "state": "Sikkim", "city": "Gangtok", "lat": 27.3389, "lng": 88.6065},
    # Flood / cyclone prone cities
    {"name": "Mumbai", "kind": "city", "state": "Maharashtra", "city": "Mumbai", "lat": 19.0760, "lng": 72.8777},
    {"name": "Chennai", "kind": "city", "state": "Tamil Nadu", "city": "Chennai", "lat": 13.0827, "lng": 80.2707},
    {"name": "Kolkata", "kind": "city", "state": "West Bengal", "city": "Kolkata", "lat": 22.5726, "lng": 88.3639},
    {"name": "Kochi", "kind": "city", "state": "Kerala", "city": "Kochi", "lat": 9.9312, "lng": 76.2673},
    {"name": "Ernakulam", "kind": "district", "state": "Kerala", "district": "Ernakulam", "lat": 9.9816, "lng": 76.2999},
    {"name": "Alappuzha", "kind": "district", "state": "Kerala", "district": "Alappuzha", "lat": 9.4981, "lng": 76.3388},
    {"name": "Alleppey", "kind": "district", "state": "Kerala", "district": "Alappuzha", "lat": 9.4981, "lng": 76.3388},
    {"name": "Wayanad", "kind": "district", "state": "Kerala", "district": "Wayanad", "lat": 11.6854, "lng": 76.1320},
    {"name": "Idukki", "kind": "district", "state": "Kerala", "district": "Idukki", "lat": 9.8500, "lng": 76.9700},
    {"name": "Puri", "kind": "district", "state": "Odisha", "district": "Puri", "lat": 19.8135, "lng": 85.8312},
    {"name": "Bhubaneswar", "kind": "city", "state": "Odisha", "city": "Bhubaneswar", "lat": 20.2961, "lng": 85.8245},
    {"name": "Bhadrak", "kind": "district", "state": "Odisha", "district": "Bhadrak", "lat": 21.0574, "lng": 86.4960},
    {"name": "Kendrapara", "kind": "district", "state": "Odisha", "district": "Kendrapara", "lat": 20.5000, "lng": 86.4200},
    {"name": "Mandi", "kind": "district", "state": "Himachal Pradesh", "district": "Mandi", "lat": 31.7086, "lng": 76.9320},
    {"name": "Kullu", "kind": "district", "state": "Himachal Pradesh", "district": "Kullu", "lat": 31.9579, "lng": 77.1095},
    {"name": "Manali", "kind": "city", "state": "Himachal Pradesh", "city": "Manali", "lat": 32.2396, "lng": 77.1887},
    {"name": "Shimla", "kind": "city", "state": "Himachal Pradesh", "city": "Shimla", "lat": 31.1048, "lng": 77.1734},
    {"name": "Joshimath", "kind": "city", "state": "Uttarakhand", "city": "Joshimath", "lat": 30.5552, "lng": 79.5645},
    {"name": "Chamoli", "kind": "district", "state": "Uttarakhand", "district": "Chamoli", "lat": 30.4040, "lng": 79.3260},
    {"name": "Rudraprayag", "kind": "district", "state": "Uttarakhand", "district": "Rudraprayag", "lat": 30.2844, "lng": 78.9811},
    {"name": "Srinagar", "kind": "city", "state": "Jammu & Kashmir", "city": "Srinagar", "lat": 34.0837, "lng": 74.7973},
    {"name": "Leh", "kind": "city", "state": "Ladakh (UT)", "city": "Leh", "lat": 34.1526, "lng": 77.5770},
    {"name": "Ahmedabad", "kind": "city", "state": "Gujarat", "city": "Ahmedabad", "lat": 23.0225, "lng": 72.5714},
    {"name": "Surat", "kind": "city", "state": "Gujarat", "city": "Surat", "lat": 21.1702, "lng": 72.8311},
    {"name": "Jaipur", "kind": "city", "state": "Rajasthan", "city": "Jaipur", "lat": 26.9124, "lng": 75.7873},
    {"name": "Hyderabad", "kind": "city", "state": "Telangana", "city": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
    {"name": "Bengaluru", "kind": "city", "state": "Karnataka", "city": "Bengaluru", "lat": 12.9716, "lng": 77.5946},
    {"name": "Bangalore", "kind": "city", "state": "Karnataka", "city": "Bengaluru", "lat": 12.9716, "lng": 77.5946},
    {"name": "Patna", "kind": "city", "state": "Bihar", "city": "Patna", "lat": 25.5941, "lng": 85.1376},
    {"name": "Varanasi", "kind": "city", "state": "Uttar Pradesh", "city": "Varanasi", "lat": 25.3176, "lng": 82.9739},
]

# Sort longest names first to avoid partial collisions (e.g. "Assam" inside longer phrases still ok with word boundaries)
_SORTED_PLACES = sorted(INDIA_PLACES, key=lambda p: len(p["name"]), reverse=True)


def _word_boundary_search(haystack: str, needle: str) -> bool:
    pattern = r"(?<![a-zA-Z])" + re.escape(needle) + r"(?![a-zA-Z])"
    return re.search(pattern, haystack, flags=re.IGNORECASE) is not None


def resolve_location(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract best matching place from article text.
    Prefer district/city over state-only.
    Returns None if no known India place is found (do not invent coords).
    """
    if not text:
        return None

    district_or_city = None
    state_only = None

    for place in _SORTED_PLACES:
        if not _word_boundary_search(text, place["name"]):
            continue
        kind = place.get("kind")
        if kind in ("district", "city") and district_or_city is None:
            district_or_city = place
        elif kind == "state" and state_only is None:
            state_only = place

    chosen = district_or_city or state_only
    if not chosen:
        return None

    specificity = {"city": 3, "district": 2, "state": 1}.get(chosen.get("kind"), 1)
    label_parts = []
    if chosen.get("city"):
        label_parts.append(chosen["city"])
    if chosen.get("district") and chosen.get("district") not in label_parts:
        label_parts.append(chosen["district"])
    if chosen.get("state"):
        label_parts.append(chosen["state"])

    return {
        "country": "India",
        "state": chosen.get("state"),
        "district": chosen.get("district"),
        "city": chosen.get("city"),
        "location_label": ", ".join(label_parts) if label_parts else chosen["name"],
        "lat": float(chosen["lat"]),
        "lng": float(chosen["lng"]),
        "specificity": specificity,
        "matched_name": chosen["name"],
        "kind": chosen.get("kind"),
    }


def enrich_from_destinations(cursor) -> None:
    """Optionally cache destination lat/lng into geocode_cache for future matching."""
    try:
        cursor.execute("SELECT name, state, lat, lng FROM destinations WHERE lat IS NOT NULL")
        for row in cursor.fetchall():
            key = (row["name"] or "").strip().lower()
            if not key:
                continue
            cursor.execute(
                """
                INSERT INTO geocode_cache (place_key, display_name, state, city, lat, lng, source)
                VALUES (?, ?, ?, ?, ?, ?, 'destination')
                ON CONFLICT(place_key) DO UPDATE SET
                  lat=excluded.lat, lng=excluded.lng, updated_at=CURRENT_TIMESTAMP
                """,
                (key, row["name"], row["state"], row["name"], row["lat"], row["lng"]),
            )
    except Exception:
        pass
