import httpx
from typing import Dict, Any, Tuple

# WMO Weather interpretation codes
WMO_WEATHER_MAP = {
    0: ("Clear Sky", 5.0),
    1: ("Mainly Clear", 8.0),
    2: ("Partly Cloudy", 10.0),
    3: ("Overcast", 12.0),
    45: ("Foggy Conditions", 20.0),
    48: ("Depositing Rime Fog", 25.0),
    51: ("Light Drizzle", 18.0),
    53: ("Moderate Drizzle", 22.0),
    55: ("Dense Drizzle", 28.0),
    61: ("Slight Rain", 22.0),
    63: ("Moderate Rain", 35.0),
    65: ("Heavy Rain Hazard", 55.0),
    71: ("Slight Snow Fall", 28.0),
    73: ("Moderate Snow Fall", 42.0),
    75: ("Heavy Snow / Blizzard Hazard", 65.0),
    77: ("Snow Grains", 30.0),
    80: ("Slight Rain Showers", 25.0),
    81: ("Moderate Rain Showers", 40.0),
    82: ("Violent Rain Downpour Hazard", 70.0),
    85: ("Slight Snow Showers", 32.0),
    86: ("Heavy Snow Showers", 60.0),
    95: ("Severe Thunderstorm Hazard", 75.0),
    96: ("Thunderstorm with Slight Hail", 82.0),
    99: ("Severe Thunderstorm with Heavy Hail Hazard", 90.0)
}

async def fetch_live_weather(lat: float, lng: float) -> Tuple[float, str, float, float, float]:
    """
    Queries Open-Meteo API (free, zero-key) for real-time live telemetry:
    Returns: (temp_c, condition_text, wind_speed_kmh, precipitation_mm, computed_weather_risk)
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "weather_code", "wind_speed_10m"],
        "timezone": "auto"
    }

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                temp = float(current.get("temperature_2m", 24.0))
                precip = float(current.get("precipitation", 0.0))
                wind = float(current.get("wind_speed_10m", 12.0))
                code = int(current.get("weather_code", 0))

                condition_name, base_risk = WMO_WEATHER_MAP.get(code, ("Variable Conditions", 15.0))

                # Extra hazard adjustments:
                # 1. High wind squall penalty
                if wind > 60.0:
                    base_risk = max(base_risk, 70.0)
                    condition_name += " • Gale Squall Warning"
                elif wind > 40.0:
                    base_risk = max(base_risk, 45.0)

                # 2. Extreme temperature penalty (Heatwave > 40C or Severe Cold < -8C)
                if temp > 42.0:
                    base_risk = max(base_risk, 55.0)
                    condition_name += " • Extreme Heatwave"
                elif temp < -10.0:
                    base_risk = max(base_risk, 50.0)
                    condition_name += " • Severe Freeze"

                # 3. Heavy rain accumulation
                if precip > 15.0:
                    base_risk = max(base_risk, 65.0)
                    condition_name += " • Flash Flood Risk"

                final_weather_risk = round(min(95.0, max(5.0, base_risk)), 1)
                return temp, condition_name, wind, precip, final_weather_risk
    except Exception as e:
        print(f"[WeatherService] Live fetch fallback for ({lat}, {lng}): {e}")

    # Fallback to mild seasonal default
    return 24.0, "Partly Cloudy", 12.0, 0.0, 15.0
