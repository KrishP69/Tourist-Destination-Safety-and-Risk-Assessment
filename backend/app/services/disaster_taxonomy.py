"""Configurable disaster event taxonomy for SafeTour live risk intelligence."""

from typing import Optional


EVENT_KEYWORDS = {
    "flood": [
        "flood", "flooding", "flash flood", "inundation", "river overflow",
        "waterlogged", "submerged", "deluge",
    ],
    "cyclone": [
        "cyclone", "tropical storm", "severe storm", "storm surge", "hurricane",
        "typhoon", "depression over bay",
    ],
    "landslide": [
        "landslide", "mudslide", "landslip", "rockfall", "road blocked by debris",
    ],
    "earthquake": [
        "earthquake", "seismic", "tremor", "aftershock",
    ],
    "tsunami": [
        "tsunami", "tidal wave warning",
    ],
    "wildfire": [
        "wildfire", "forest fire", "bushfire", "jungle fire",
    ],
    "extreme_weather": [
        "heavy rainfall", "cloudburst", "heatwave", "cold wave", "thunderstorm",
        "hailstorm", "dust storm", "extreme weather",
    ],
    "evacuation": [
        "evacuation", "evacuate", "relief camp", "disaster warning",
    ],
    "coastal_warning": [
        "coastal warning", "high tide alert", "rough sea", "fishermen advised",
    ],
    "road_blockage": [
        "road blocked", "highway closed", "nh closed", "traffic disrupted landslide",
    ],
}

# Base severity contribution (0-100 style starting points before signals)
EVENT_BASE_SEVERITY = {
    "flood": 55,
    "flash_flood": 65,
    "cyclone": 70,
    "landslide": 60,
    "earthquake": 65,
    "tsunami": 85,
    "wildfire": 55,
    "extreme_weather": 40,
    "evacuation": 50,
    "coastal_warning": 45,
    "road_blockage": 35,
    "other": 30,
}


def classify_event(text: str) -> Optional[str]:
    """Return primary event type from free text, or None if not disaster-related."""
    if not text:
        return None
    lower = text.lower()
    # Prefer more specific matches first
    priority = [
        "tsunami", "earthquake", "cyclone", "landslide", "flood",
        "wildfire", "evacuation", "coastal_warning", "road_blockage", "extreme_weather",
    ]
    for etype in priority:
        for kw in EVENT_KEYWORDS.get(etype, []):
            if kw in lower:
                return etype
    return None


def gdelt_query_terms() -> str:
    """Build a GDELT boolean query focused on India disaster coverage."""
    terms = [
        "flood", "flooding", "landslide", "cyclone", "earthquake",
        "cloudburst", "wildfire", "forest fire", "evacuation", "heavy rain",
    ]
    joined = " OR ".join(f'"{t}"' if " " in t else t for t in terms)
    return f"({joined}) (India OR Assam OR Kerala OR Maharashtra OR Odisha OR Gujarat)"
