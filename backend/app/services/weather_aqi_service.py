"""
SafeTour Bharat — Real-Time Extreme Weather, AQI & Landslide Intelligence Engine.
Integrates live environmental telemetry from Open-Meteo Forecast & Air Quality APIs:
- Monsoon & Hill Stations: Landslide & flash flood warnings (e.g. Lohagad, Munnar, Manali).
- North India & Urban Hubs: AQI warnings, PM2.5/PM10 levels & dense fog visibility alerts.
- Coastal & Islands: High tide & rough sea swell warnings (e.g. Lakshadweep, Goa, Andaman).
- Arid & Plains: Extreme heatwave & dehydration alerts (e.g. Rajasthan, Gujarat).
"""

from __future__ import annotations
import time
import httpx
from typing import Dict, Any, Optional, Tuple

# In-memory telemetry cache (key -> (timestamp, data)) with 10-minute TTL
_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SEC = 600

# WMO Weather Interpretation Map (Code -> Condition Name, Base Risk, Icon)
WMO_WEATHER_MAP: Dict[int, Tuple[str, float, str]] = {
    0: ("Clear Sky", 5.0, "fa-sun"),
    1: ("Mainly Clear", 8.0, "fa-cloud-sun"),
    2: ("Partly Cloudy", 10.0, "fa-cloud-sun"),
    3: ("Overcast", 14.0, "fa-cloud"),
    45: ("Dense Radiation Fog", 35.0, "fa-smog"),
    48: ("Depositing Rime Fog", 40.0, "fa-smog"),
    51: ("Light Drizzle", 15.0, "fa-cloud-rain"),
    53: ("Moderate Drizzle", 22.0, "fa-cloud-rain"),
    55: ("Dense Drizzle", 28.0, "fa-cloud-rain"),
    61: ("Slight Rain", 25.0, "fa-cloud-showers-heavy"),
    63: ("Moderate Rain", 42.0, "fa-cloud-showers-heavy"),
    65: ("Heavy Rain Hazard", 65.0, "fa-cloud-showers-heavy"),
    71: ("Slight Snowfall", 28.0, "fa-snowflake"),
    73: ("Moderate Snowfall", 45.0, "fa-snowflake"),
    75: ("Heavy Blizzard Hazard", 75.0, "fa-snowflake"),
    77: ("Snow Grains", 30.0, "fa-snowflake"),
    80: ("Light Rain Showers", 25.0, "fa-cloud-showers-heavy"),
    81: ("Moderate Showers", 45.0, "fa-cloud-showers-heavy"),
    82: ("Violent Downpour Hazard", 75.0, "fa-cloud-showers-heavy"),
    85: ("Light Snow Showers", 35.0, "fa-snowflake"),
    86: ("Heavy Snow Showers", 65.0, "fa-snowflake"),
    95: ("Severe Thunderstorm Hazard", 80.0, "fa-cloud-bolt"),
    96: ("Thunderstorm with Hail", 85.0, "fa-cloud-bolt"),
    99: ("Violent Hailstorm Hazard", 92.0, "fa-cloud-bolt"),
}

# Mountain and Hill Station Keywords in India
HILL_STATION_KEYWORDS = {
    "lohagad", "loha gad", "munnar", "coorg", "manali", "shimla", "ooty", "kodaikanal",
    "darjeeling", "gangtok", "shillong", "cherrapunji", "mussoorie", "nainital", "rishikesh",
    "tirthan", "leh", "ladakh", "kullu", "kasol", "dharamshala", "mcLeodganj", "panchgani",
    "mahabaleshwar", "matheran", "lonavala", "khandala", "araku", "chikmagalur", "wayanad",
    "gulmarg", "pahalgam", "sonamarg", "spiti", "almore", "ranikhet", "chamba", "kasol"
}

# Coastal and Beach Keywords in India
COASTAL_KEYWORDS = {
    "lakshadweep", "goa", "andaman", "alibaug", "puri", "gokarna", "kanyakumari", "daman",
    "diu", "pondicherry", "puducherry", "kovalam", "varkala", "marina", "gateway of india",
    "marine drive", "juhu", "digha", "mandarmani", "tarkarli", "bekal", "malpe", "radhanagar"
}

# North India / Dense Smog & AQI Sensitive Zones
NORTH_INDIA_SMOG_KEYWORDS = {
    "delhi", "new delhi", "agra", "varanasi", "lucknow", "kanpur", "noida", "gurugram",
    "ghaziabad", "patna", "amritsar", "ludhiana", "chandigarh", "faridabad", "meerut"
}


def determine_terrain_archetype(name: str, state: str, category: str, lat: float, lng: float) -> str:
    """Categorizes destination terrain to apply contextual environmental hazard models."""
    combined = f"{name} {state} {category}".lower()

    if any(k in combined for k in HILL_STATION_KEYWORDS) or "hill" in combined or "trek" in combined or "mountain" in combined:
        return "Hill Station / Mountain Ghats"
    if any(k in combined for k in COASTAL_KEYWORDS) or "beach" in combined or "island" in combined or "coastal" in combined:
        return "Coastal / Maritime Island"
    if any(k in combined for k in NORTH_INDIA_SMOG_KEYWORDS) or state.lower() in ("delhi", "uttar pradesh", "punjab", "haryana", "bihar"):
        return "North India Plains / Urban Hub"
    if state.lower() in ("rajasthan", "gujarat", "madhya pradesh") or "desert" in combined:
        return "Arid / Plains"
    return "Standard Inland Plateau"


def parse_aqi_metrics(pm2_5: float, pm10: float, us_aqi: int) -> Dict[str, Any]:
    """Calculates standardized National Air Quality Index (NAQI) category and health advisory."""
    # Convert PM2.5 concentration to Indian NAQI equivalent or use US AQI
    score = int(us_aqi) if us_aqi > 0 else int(pm2_5 * 2.2)

    if score <= 50:
        category = "Good"
        color = "#10b981"
        badge_class = "aqi-good"
        advice = "Air quality is ideal for outdoor walks, sightseeing, and photography."
    elif score <= 100:
        category = "Satisfactory"
        color = "#84cc16"
        badge_class = "aqi-satisfactory"
        advice = "Air quality is acceptable. Normal outdoor tourist activities recommended."
    elif score <= 200:
        category = "Moderate"
        color = "#f59e0b"
        badge_class = "aqi-moderate"
        advice = "Breathing discomfort possible for asthmatic travelers and young children."
    elif score <= 300:
        category = "Poor"
        color = "#f97316"
        badge_class = "aqi-poor"
        advice = "Unhealthy smog canopy. Sensitive travelers should carry N95 masks."
    elif score <= 400:
        category = "Very Poor"
        color = "#ef4444"
        badge_class = "aqi-very-poor"
        advice = "Respiratory distress warning. Wear N95 filtration masks during outdoor sightseeing."
    else:
        category = "Severe / Hazardous"
        color = "#a855f7"
        badge_class = "aqi-severe"
        advice = "Hazardous air pollution emergency. Avoid strenuous outdoor activities."

    return {
        "aqi_score": score,
        "pm2_5": round(pm2_5, 1),
        "pm10": round(pm10, 1),
        "category": category,
        "color": color,
        "badge_class": badge_class,
        "health_advice": advice,
    }


def evaluate_environmental_hazard(
    terrain: str,
    temp: float,
    precip: float,
    wind_speed: float,
    wind_gusts: float,
    weather_code: int,
    aqi_data: Dict[str, Any],
    name: str
) -> Optional[Dict[str, Any]]:
    """
    Evaluates terrain-specific hazard models:
    - Hill stations: Landslides & flash floods
    - Coastal: High tide & rough sea
    - North India: Dense winter fog & severe AQI
    - Plains: Extreme heatwave
    """
    is_hill = "hill" in terrain.lower() or "mountain" in terrain.lower()
    is_coastal = "coastal" in terrain.lower() or "island" in terrain.lower()

    # 1. Monsoon / Hill Station Landslide & Flash Flood Warning
    if is_hill and (precip >= 4.0 or weather_code in (65, 81, 82, 95, 96, 99)):
        severity = "DANGER" if precip > 12.0 or weather_code in (82, 99) else "WARNING"
        return {
            "hazard_type": "LANDSLIDE_FLASH_FLOOD_ALERT",
            "severity": severity,
            "badge_label": f"LANDSLIDE CAUTION • {precip} mm/h",
            "icon": "fa-mountain",
            "accent_color": "#ef4444" if severity == "DANGER" else "#f59e0b",
            "title": f"Landslide & Slippery Ghat Trail Alert ({name})",
            "description": f"Heavy rain detected ({precip} mm/h). Trekking ascents, stone steps, and ghat roads are extremely slippery with localized rockfall risks.",
            "recommendation": "Delay summit climbs until rain subsides. Check local tourist police / forest department trail clearances before ascending.",
        }

    # 2. Coastal / Island High Tide & Rough Sea Swell Warning
    if is_coastal and (wind_gusts >= 32.0 or wind_speed >= 26.0 or weather_code in (95, 96, 99)):
        severity = "DANGER" if wind_gusts > 50.0 or weather_code in (95, 99) else "WARNING"
        return {
            "hazard_type": "ROUGH_SEA_HIGH_TIDE_ALERT",
            "severity": severity,
            "badge_label": f"ROUGH SURF ALERT • {round(wind_gusts)} km/h GUSTS",
            "icon": "fa-water",
            "accent_color": "#0284c7",
            "title": f"High Tide & Rough Surf Warning ({name})",
            "description": f"Strong coastal winds ({round(wind_speed)} km/h, gusts up to {round(wind_gusts)} km/h) creating heavy sea swells and hazardous littoral rip currents.",
            "recommendation": "Beach swimming and recreational boating are strictly restricted. Keep safe distance from rocky breakwaters and wet tide zones.",
        }

    # 3. Dense Winter Radiation Fog & Low Visibility
    if weather_code in (45, 48) or (temp < 15.0 and precip == 0 and wind_speed < 8.0 and aqi_data["aqi_score"] > 180):
        return {
            "hazard_type": "DENSE_FOG_VISIBILITY_ALERT",
            "severity": "WARNING",
            "badge_label": "DENSE FOG • LOW VISIBILITY",
            "icon": "fa-smog",
            "accent_color": "#94a3b8",
            "title": f"Dense Winter Fog Advisory ({name})",
            "description": "Dense fog / smog inversion layer with surface visibility below 400 meters. Architectural sightlines and photography views heavily obscured.",
            "recommendation": "Plan monument visits during midday hours (11:30 AM - 3:00 PM) when sun burns off fog layer. Drive with low-beam fog lights.",
        }

    # 4. Severe / Hazardous Air Quality Emergency
    if aqi_data["aqi_score"] >= 250:
        severity = "DANGER" if aqi_data["aqi_score"] >= 350 else "WARNING"
        return {
            "hazard_type": "SEVERE_AQI_HAZARD",
            "severity": severity,
            "badge_label": f"SEVERE SMOG • AQI {aqi_data['aqi_score']}",
            "icon": "fa-mask-face",
            "accent_color": "#a855f7" if severity == "DANGER" else "#ea580c",
            "title": f"Severe Air Quality Hazard ({name})",
            "description": f"Elevated particulate matter concentrations (PM2.5: {aqi_data['pm2_5']} µg/m³, PM10: {aqi_data['pm10']} µg/m³). High inhalation risk.",
            "recommendation": "N95/FFP2 filtration masks strongly advised for all outdoor activities. Asthmatic and senior travelers should limit outdoor exposure.",
        }

    # 5. Extreme Summer Heatwave & Sunstroke Warning
    if temp >= 40.0:
        return {
            "hazard_type": "HEATWAVE_SUNSTROKE_ALERT",
            "severity": "WARNING",
            "badge_label": f"HEATWAVE • {round(temp, 1)}°C",
            "icon": "fa-sun",
            "accent_color": "#f97316",
            "title": f"Extreme Heatwave & Sunstroke Advisory ({name})",
            "description": f"Severe ambient temperature ({round(temp, 1)}°C) creating elevated heat index. Dehydration and sunstroke risk during midday.",
            "recommendation": "Carry oral rehydration salts (ORS) and water. Visit early morning (before 10:00 AM) or sunset (after 5:00 PM). Avoid exposed stone courtyards at noon.",
        }

    # 6. Mountain Sub-Zero Frost / Black Ice Warning
    if is_hill and temp <= 1.0:
        return {
            "hazard_type": "FROST_BLACK_ICE_ALERT",
            "severity": "WARNING",
            "badge_label": f"FREEZING • {round(temp, 1)}°C",
            "icon": "fa-snowflake",
            "accent_color": "#38bdf8",
            "title": f"Sub-Zero Frost & Black Ice Warning ({name})",
            "description": f"Near-freezing temperatures ({round(temp, 1)}°C) causing slippery black ice patches on shaded bends and stone pathways.",
            "recommendation": "Wear thermal multi-layer clothing and anti-slip trekking shoes. Exercise caution on elevated steps.",
        }

    return None


async def fetch_complete_environmental_intelligence(
    lat: float,
    lng: float,
    name: str = "Tourist Destination",
    state: str = "India",
    category: str = "Monument & Heritage",
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Fetches real-time weather + air quality from Open-Meteo APIs, calculates AQI index,
    identifies terrain archetypes, and synthesizes hazard advisories for Indian tourists.
    """
    cache_key = f"{round(lat, 3)}_{round(lng, 3)}_{name[:15]}"
    now = time.time()

    if not force_refresh and cache_key in _CACHE:
        cached_time, cached_data = _CACHE[cache_key]
        if (now - cached_time) < CACHE_TTL_SEC:
            return cached_data

    terrain = determine_terrain_archetype(name, state, category, lat, lng)

    # Defaults in case of network timeout
    temp = 24.5
    humidity = 55
    precip = 0.0
    rain = 0.0
    showers = 0.0
    snow = 0.0
    weather_code = 1
    wind_speed = 12.0
    wind_gusts = 18.0
    pm2_5 = 35.0
    pm10 = 60.0
    us_aqi = 68

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lng,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "rain",
            "showers",
            "snowfall",
            "weather_code",
            "wind_speed_10m",
            "wind_gusts_10m"
        ],
        "timezone": "auto"
    }

    aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    aqi_params = {
        "latitude": lat,
        "longitude": lng,
        "current": ["pm10", "pm2_5", "us_aqi", "european_aqi"]
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Parallel or sequential requests to Open-Meteo
            w_res = await client.get(weather_url, params=weather_params)
            if w_res.status_code == 200:
                w_data = w_res.json().get("current", {})
                temp = float(w_data.get("temperature_2m", temp))
                humidity = int(w_data.get("relative_humidity_2m", humidity))
                precip = float(w_data.get("precipitation", precip))
                rain = float(w_data.get("rain", rain))
                showers = float(w_data.get("showers", showers))
                snow = float(w_data.get("snowfall", snow))
                weather_code = int(w_data.get("weather_code", weather_code))
                wind_speed = float(w_data.get("wind_speed_10m", wind_speed))
                wind_gusts = float(w_data.get("wind_gusts_10m", wind_gusts))

            aqi_res = await client.get(aqi_url, params=aqi_params)
            if aqi_res.status_code == 200:
                a_data = aqi_res.json().get("current", {})
                pm2_5 = float(a_data.get("pm2_5", pm2_5))
                pm10 = float(a_data.get("pm10", pm10))
                us_aqi = int(a_data.get("us_aqi", us_aqi))
    except Exception as e:
        print(f"[WeatherAQIService] Live telemetry notice for {name} ({lat}, {lng}): {e}")

    condition_text, base_risk, icon_name = WMO_WEATHER_MAP.get(
        weather_code, ("Fair Conditions", 12.0, "fa-cloud-sun")
    )

    aqi_data = parse_aqi_metrics(pm2_5, pm10, us_aqi)
    hazard = evaluate_environmental_hazard(
        terrain, temp, precip, wind_speed, wind_gusts, weather_code, aqi_data, name
    )

    # Compute overall composite environmental safety index (0 to 100)
    penalty = 0.0
    if hazard:
        penalty += 25.0 if hazard["severity"] == "DANGER" else 15.0
    if aqi_data["aqi_score"] > 200:
        penalty += 12.0
    if precip > 5.0:
        penalty += 10.0
    if wind_speed > 30.0:
        penalty += 8.0

    env_safety_score = round(max(15.0, min(99.0, 100.0 - (base_risk + penalty))), 1)

    result = {
        "timestamp": int(now),
        "destination_name": name,
        "terrain_archetype": terrain,
        "weather": {
            "temperature_c": round(temp, 1),
            "condition": condition_text,
            "icon": icon_name,
            "weather_code": weather_code,
            "humidity_pct": humidity,
            "precipitation_mm": round(precip, 1),
            "wind_speed_kmh": round(wind_speed, 1),
            "wind_gusts_kmh": round(wind_gusts, 1),
        },
        "air_quality": aqi_data,
        "hazard_alert": hazard,
        "has_active_hazard": hazard is not None,
        "environmental_safety_score": env_safety_score,
        "provider": "Open-Meteo & Central Pollution Control Board Standards",
    }

    _CACHE[cache_key] = (now, result)
    return result
