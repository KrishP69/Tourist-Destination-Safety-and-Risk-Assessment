"""
Orchestrate live disaster ingest → location resolve → risk scoring → DB.
No fake events. Unresolved locations are stored as articles only (no map zone).
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.config import DISASTER_EVENT_TTL_HOURS
from app.database import get_db, init_db
from app.services.disaster_ingest_service import fetch_all_live_articles
from app.services.disaster_location_resolver import enrich_from_destinations, resolve_location
from app.services.disaster_risk_engine import compute_risk_and_confidence, suggested_radius_m


def _event_key(event_type: str, location: Dict[str, Any]) -> str:
    parts = [
        event_type,
        (location.get("state") or "").lower(),
        (location.get("district") or "").lower(),
        (location.get("city") or "").lower(),
        f"{round(float(location['lat']), 2)}_{round(float(location['lng']), 2)}",
    ]
    return "|".join(parts)


def run_disaster_pipeline() -> Dict[str, Any]:
    init_db()
    articles = fetch_all_live_articles()
    resolved_groups: Dict[str, Dict[str, Any]] = {}
    skipped_no_location = 0
    stored_articles = 0

    with get_db() as conn:
        cursor = conn.cursor()
        enrich_from_destinations(cursor)

        for art in articles:
            # Persist article (deduped)
            try:
                cursor.execute(
                    """
                    INSERT INTO disaster_articles
                      (dedupe_key, title, summary, source, url, published_at, event_type, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(dedupe_key) DO UPDATE SET
                      fetched_at=CURRENT_TIMESTAMP
                    """,
                    (
                        art["dedupe_key"],
                        art["title"],
                        art.get("summary"),
                        art.get("source"),
                        art.get("url"),
                        art.get("published_at"),
                        art.get("event_type"),
                        json.dumps({"provider": art.get("provider")}),
                    ),
                )
                stored_articles += 1
            except Exception:
                continue

            text = " ".join(
                [
                    art.get("title") or "",
                    art.get("summary") or "",
                    art.get("area_hint") or "",
                ]
            )
            loc = resolve_location(text)
            if not loc:
                skipped_no_location += 1
                continue

            key = _event_key(art["event_type"], loc)
            bucket = resolved_groups.setdefault(
                key,
                {
                    "event_type": art["event_type"],
                    "location": loc,
                    "articles": [],
                    "official": False,
                },
            )
            bucket["articles"].append(art)
            if art.get("official_alert"):
                bucket["official"] = True

        # Expire old events
        cursor.execute(
            """
            UPDATE disaster_risk_events
            SET is_active=0
            WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP
            """
        )

        upserted = 0
        for key, bucket in resolved_groups.items():
            loc = bucket["location"]
            arts = bucket["articles"]
            scores = compute_risk_and_confidence(
                bucket["event_type"], arts, loc, official_alert=bucket["official"]
            )
            radius = suggested_radius_m(bucket["event_type"], int(loc.get("specificity") or 1))
            expires = (datetime.utcnow() + timedelta(hours=DISASTER_EVENT_TTL_HOURS)).isoformat(sep=" ")
            sources_payload = [
                {
                    "title": a.get("title"),
                    "source": a.get("source"),
                    "url": a.get("url"),
                    "published_at": a.get("published_at"),
                    "provider": a.get("provider"),
                    "official_alert": bool(a.get("official_alert")),
                }
                for a in arts[:12]
            ]
            title = f"{bucket['event_type'].replace('_', ' ').title()} — {loc['location_label']}"
            summary = (
                f"Recent {bucket['event_type'].replace('_', ' ')}-related reports detected "
                f"near {loc['location_label']}. This is system-detected news intelligence, "
                f"not a verified safety judgment unless marked as an official alert."
            )
            source_kind = "official" if bucket["official"] else "news"
            if bucket["official"] and scores["independent_sources"] > 1:
                source_kind = "both"

            cursor.execute(
                """
                INSERT INTO disaster_risk_events (
                  event_key, event_type, title, summary, country, state, district, city,
                  location_label, lat, lng, radius_m, risk_score, risk_level, confidence_score,
                  official_alert, source_kind, independent_sources, article_count,
                  last_seen_at, expires_at, is_active, sources_json
                ) VALUES (?, ?, ?, ?, 'India', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, 1, ?)
                ON CONFLICT(event_key) DO UPDATE SET
                  title=excluded.title,
                  summary=excluded.summary,
                  risk_score=excluded.risk_score,
                  risk_level=excluded.risk_level,
                  confidence_score=excluded.confidence_score,
                  official_alert=excluded.official_alert,
                  source_kind=excluded.source_kind,
                  independent_sources=excluded.independent_sources,
                  article_count=excluded.article_count,
                  last_seen_at=CURRENT_TIMESTAMP,
                  expires_at=excluded.expires_at,
                  is_active=1,
                  sources_json=excluded.sources_json,
                  radius_m=excluded.radius_m
                """,
                (
                    key,
                    bucket["event_type"],
                    title,
                    summary,
                    loc.get("state"),
                    loc.get("district"),
                    loc.get("city"),
                    loc["location_label"],
                    loc["lat"],
                    loc["lng"],
                    radius,
                    scores["risk_score"],
                    scores["risk_level"],
                    scores["confidence_score"],
                    1 if bucket["official"] else 0,
                    source_kind,
                    scores["independent_sources"],
                    scores["article_count"],
                    expires,
                    json.dumps(sources_payload),
                ),
            )
            upserted += 1

    return {
        "fetched_articles": len(articles),
        "stored_articles": stored_articles,
        "skipped_no_location": skipped_no_location,
        "active_events_upserted": upserted,
        "ran_at": datetime.utcnow().isoformat() + "Z",
    }


def list_active_events(
    event_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    source_kind: Optional[str] = None,
) -> List[Dict[str, Any]]:
    init_db()
    with get_db() as conn:
        cursor = conn.cursor()
        q = """
          SELECT * FROM disaster_risk_events
          WHERE is_active=1
            AND (expires_at IS NULL OR expires_at >= CURRENT_TIMESTAMP)
        """
        params: List[Any] = []
        if event_type and event_type.lower() not in ("all", ""):
            q += " AND event_type = ?"
            params.append(event_type.lower())
        if risk_level and risk_level.upper() not in ("ALL", ""):
            q += " AND risk_level = ?"
            params.append(risk_level.upper())
        if source_kind and source_kind.lower() not in ("all", "both", ""):
            if source_kind.lower() == "official":
                q += " AND official_alert = 1"
            elif source_kind.lower() == "news":
                q += " AND official_alert = 0"
        q += " ORDER BY risk_score DESC, last_seen_at DESC"
        cursor.execute(q, params)
        rows = []
        for r in cursor.fetchall():
            d = dict(r)
            try:
                d["sources"] = json.loads(d.get("sources_json") or "[]")
            except Exception:
                d["sources"] = []
            d.pop("sources_json", None)
            rows.append(d)
        return rows


def events_summary() -> Dict[str, Any]:
    events = list_active_events()
    counts = {"CRITICAL": 0, "HIGH": 0, "MODERATE": 0, "LOW": 0}
    for e in events:
        lvl = e.get("risk_level") or "LOW"
        if lvl in counts:
            counts[lvl] += 1
    last = None
    if events:
        last = max((e.get("last_seen_at") or "") for e in events)
    return {
        "total": len(events),
        "counts": counts,
        "last_updated": last,
        "disclaimer": (
            "Risk zones are derived from live news/official feeds with location extraction. "
            "They are not a guarantee of on-ground conditions. Prefer official alerts when available."
        ),
    }


def nearby_events_for_point(lat: float, lng: float, max_km: float = 80.0) -> List[Dict[str, Any]]:
    """Haversine filter of active events near a point (user or destination)."""
    from math import radians, sin, cos, asin, sqrt

    def hav(a_lat, a_lng, b_lat, b_lng):
        r = 6371.0
        dlat = radians(b_lat - a_lat)
        dlng = radians(b_lng - a_lng)
        x = sin(dlat / 2) ** 2 + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(dlng / 2) ** 2
        return 2 * r * asin(sqrt(x))

    out = []
    for e in list_active_events():
        try:
            dist = hav(lat, lng, float(e["lat"]), float(e["lng"]))
        except Exception:
            continue
        if dist <= max_km:
            item = dict(e)
            item["distance_km"] = round(dist, 1)
            out.append(item)
    out.sort(key=lambda x: (x.get("distance_km", 999), -int(x.get("risk_score") or 0)))
    return out
