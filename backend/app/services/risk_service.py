def calculate_safety_score(metrics: dict, active_critical_incidents: int = 0) -> tuple[int, str]:
    """
    Algorithmic Multi-Factor Safety Score Calculation:
    Metrics:
    - crime_index (0-100, lower is better)
    - scam_index (0-100, lower is better)
    - weather_risk (0-100, lower is better)
    - health_risk (0-100, lower is better)
    - night_safety (0-100, higher is better)
    - transport_safety (0-100, higher is better)
    - crowd_density (0-100, higher = denser / more crowd pressure — lower is better for safety)
    """
    crime = metrics.get("crime_index", 20.0)
    scam = metrics.get("scam_index", 25.0)
    weather = metrics.get("weather_risk", 15.0)
    health = metrics.get("health_risk", 15.0)
    night = metrics.get("night_safety", 80.0)
    transport = metrics.get("transport_safety", 85.0)
    crowd = metrics.get("crowd_density", 50.0)

    night_risk = 100.0 - night
    transport_risk = 100.0 - transport

    # Weights sum to 1.0 — crowd pressure now included (was previously unused)
    total_penalty = (
        (0.25 * crime) +
        (0.14 * scam) +
        (0.16 * weather) +
        (0.12 * health) +
        (0.12 * night_risk) +
        (0.09 * transport_risk) +
        (0.12 * crowd)
    )

    incident_penalty = min(active_critical_incidents * 5.0, 15.0)

    raw_score = 100.0 - total_penalty - incident_penalty
    final_score = int(max(5, min(99, round(raw_score))))

    if final_score >= 80:
        tier = "Low Risk (Safe)"
    elif final_score >= 60:
        tier = "Moderate Risk"
    elif final_score >= 40:
        tier = "High Caution"
    else:
        tier = "Severe Risk"

    return final_score, tier
