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
    """
    crime = metrics.get("crime_index", 20.0)
    scam = metrics.get("scam_index", 25.0)
    weather = metrics.get("weather_risk", 15.0)
    health = metrics.get("health_risk", 15.0)
    night = metrics.get("night_safety", 80.0)
    transport = metrics.get("transport_safety", 85.0)

    # Inverted night risk: (100 - night)
    night_risk = 100.0 - night
    transport_risk = 100.0 - transport

    # Weighted risk deduction from perfect 100
    # Weights: Crime 0.28, Scam 0.16, Weather 0.18, Health 0.14, Night 0.14, Transport 0.10
    total_penalty = (
        (0.28 * crime) +
        (0.16 * scam) +
        (0.18 * weather) +
        (0.14 * health) +
        (0.14 * night_risk) +
        (0.10 * transport_risk)
    )

    # Active critical incident penalty (capped at 15 points)
    incident_penalty = min(active_critical_incidents * 5.0, 15.0)

    raw_score = 100.0 - total_penalty - incident_penalty
    final_score = int(max(5, min(99, round(raw_score))))

    # Determine Risk Tier
    if final_score >= 80:
        tier = "Low Risk (Safe)"
    elif final_score >= 60:
        tier = "Moderate Risk"
    elif final_score >= 40:
        tier = "High Caution"
    else:
        tier = "Severe Risk"

    return final_score, tier
