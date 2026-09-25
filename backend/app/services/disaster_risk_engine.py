"""Risk score + confidence for live disaster events (separate concepts)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import RISK_HIGH_MAX, RISK_LOW_MAX, RISK_MODERATE_MAX
from app.services.disaster_taxonomy import EVENT_BASE_SEVERITY


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    text = value.strip()
    if len(text) >= 14 and text[:14].isdigit():
        try:
            return datetime.strptime(text[:14], "%Y%m%d%H%M%S")
        except Exception:
            pass
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(text.replace("Z", "+0000"), fmt).replace(tzinfo=None)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def time_decay_factor(published_at: Optional[str], now: Optional[datetime] = None) -> float:
    """1.0 = very recent, down toward 0.25 after ~48h."""
    now = now or datetime.utcnow()
    dt = _parse_dt(published_at)
    if not dt:
        return 0.7
    hours = max(0.0, (now - dt).total_seconds() / 3600.0)
    if hours <= 3:
        return 1.0
    if hours <= 12:
        return 0.9
    if hours <= 24:
        return 0.75
    if hours <= 48:
        return 0.55
    if hours <= 72:
        return 0.4
    return 0.25


def score_to_level(score: int) -> str:
    if score <= RISK_LOW_MAX:
        return "LOW"
    if score <= RISK_MODERATE_MAX:
        return "MODERATE"
    if score <= RISK_HIGH_MAX:
        return "HIGH"
    return "CRITICAL"


def compute_risk_and_confidence(
    event_type: str,
    articles: List[Dict[str, Any]],
    location: Dict[str, Any],
    official_alert: bool = False,
) -> Dict[str, Any]:
    """
    risk_score: how severe the hazard type + corroboration (0-100)
    confidence_score: how sure we are about location/source quality (0-100)
    """
    base = EVENT_BASE_SEVERITY.get(event_type, EVENT_BASE_SEVERITY["other"])

    # Independent sources (unique source names)
    sources = []
    for a in articles:
        s = (a.get("source") or "").strip().lower()
        if s and s not in sources:
            sources.append(s)
    independent = max(1, len(sources))

    # Recency: use newest article
    newest = None
    for a in articles:
        dt = _parse_dt(a.get("published_at"))
        if dt and (newest is None or dt > newest):
            newest = dt
    decay = time_decay_factor(newest.isoformat() if newest else articles[0].get("published_at") if articles else None)

    corroboration = min(25, (independent - 1) * 8)
    official_boost = 25 if official_alert else 0

    # State-only location should not auto-max severity on map messaging — slight risk dampen
    specificity = int(location.get("specificity") or 1)
    location_dampen = 0 if specificity >= 2 else 8

    raw_risk = (base * decay) + corroboration + official_boost - location_dampen
    risk_score = int(max(5, min(99, round(raw_risk))))

    # Confidence
    conf = 35
    conf += {1: 10, 2: 28, 3: 40}.get(specificity, 10)
    conf += min(25, independent * 7)
    conf += 15 if official_alert else 0
    conf = int(max(10, min(98, conf * decay + (5 if specificity >= 2 else 0))))

    return {
        "risk_score": risk_score,
        "risk_level": score_to_level(risk_score),
        "confidence_score": conf,
        "independent_sources": independent,
        "article_count": len(articles),
        "time_decay": decay,
    }


def suggested_radius_m(event_type: str, specificity: int) -> float:
    """Defensible default radii — not arbitrary danger zones."""
    if specificity <= 1:
        # state-level: larger soft radius but UI must label as state-level report
        return 80000.0
    if event_type in ("cyclone", "tsunami"):
        return 60000.0
    if event_type in ("flood", "extreme_weather"):
        return 35000.0
    if event_type in ("earthquake",):
        return 40000.0
    if event_type in ("landslide", "road_blockage", "wildfire"):
        return 15000.0
    return 25000.0
