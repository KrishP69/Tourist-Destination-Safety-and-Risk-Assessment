"""
Crowd estimation engine.

Terminology (never claim GPS = exact headcount):
- observed_users: opted-in GPS users currently inside geofence
- booked_visitors: confirmed ticket holders for near-term slots
- estimated_crowd: transparent weighted estimate
- predicted_crowd: future expectation
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.config import (
    DEFAULT_THRESHOLDS,
    VISITOR_TIMEOUT_MINUTES,
    WEIGHT_BOOKINGS,
    WEIGHT_HISTORICAL,
    WEIGHT_OBSERVED_GPS,
    WEIGHT_TREND,
)
from app.database import get_db


def _demo_flag() -> bool:
    try:
        from app.services.demo_crowd_service import is_demo_enabled
        return is_demo_enabled()
    except Exception:
        from app.config import DEMO_MODE
        return DEMO_MODE


def expire_stale_visitors(cursor, timeout_minutes: Optional[int] = None) -> int:
    minutes = timeout_minutes if timeout_minutes is not None else VISITOR_TIMEOUT_MINUTES
    cursor.execute(
        """
        UPDATE visitor_presence
        SET is_active = 0, exited_at = CURRENT_TIMESTAMP
        WHERE is_active = 1
          AND datetime(last_seen) < datetime('now', ?)
        """,
        (f"-{int(minutes)} minutes",),
    )
    return cursor.rowcount


def get_effective_capacity(dest: Dict[str, Any]) -> int:
    override = dest.get("emergency_capacity_override")
    if override is not None and int(override) > 0:
        return int(override)
    return max(1, int(dest.get("maximum_capacity") or 1000))


def get_weights(dest: Dict[str, Any]) -> Dict[str, float]:
    w = {
        "gps": float(dest.get("crowd_weight_gps") or WEIGHT_OBSERVED_GPS),
        "bookings": float(dest.get("crowd_weight_bookings") or WEIGHT_BOOKINGS),
        "historical": float(dest.get("crowd_weight_historical") or WEIGHT_HISTORICAL),
        "trend": float(dest.get("crowd_weight_trend") or WEIGHT_TREND),
    }
    total = sum(w.values()) or 1.0
    return {k: v / total for k, v in w.items()}


def crowd_level_from_occupancy(occupancy: float, dest: Dict[str, Any]) -> str:
    low = float(dest.get("threshold_low_max") or DEFAULT_THRESHOLDS["low_max"])
    mod = float(dest.get("threshold_moderate_max") or DEFAULT_THRESHOLDS["moderate_max"])
    high = float(dest.get("threshold_high_max") or DEFAULT_THRESHOLDS["high_max"])
    vh = float(dest.get("threshold_very_high_max") or DEFAULT_THRESHOLDS["very_high_max"])
    if occupancy < low:
        return "LOW"
    if occupancy < mod:
        return "MODERATE"
    if occupancy < high:
        return "HIGH"
    if occupancy <= vh:
        return "VERY_HIGH"
    return "CRITICAL"


def count_observed_users(cursor, destination_id: int) -> int:
    expire_stale_visitors(cursor)
    cursor.execute(
        """
        SELECT COUNT(*) AS c FROM visitor_presence
        WHERE destination_id = ? AND is_active = 1
        """,
        (destination_id,),
    )
    return int(cursor.fetchone()["c"])


def count_booked_visitors_now(cursor, destination_id: int, window_hours: int = 2) -> int:
    """Confirmed bookings for slots overlapping 'now' ± window."""
    now = datetime.utcnow()
    today = now.strftime("%Y-%m-%d")
    cursor.execute(
        """
        SELECT COALESCE(SUM(b.number_of_people), 0) AS c
        FROM ticket_bookings b
        JOIN ticket_slots s ON s.id = b.slot_id
        WHERE b.destination_id = ?
          AND b.booking_status = 'confirmed'
          AND s.slot_date = ?
          AND s.status != 'cancelled'
        """,
        (destination_id, today),
    )
    today_booked = int(cursor.fetchone()["c"] or 0)
    # Soften: only a portion of today's bookings are expected on-site at any moment
    return max(0, int(round(today_booked * 0.35)))


def historical_average(cursor, destination_id: int, day_of_week: int, hour: int) -> Optional[float]:
    cursor.execute(
        """
        SELECT AVG(estimated_crowd) AS avg_crowd, COUNT(*) AS n
        FROM crowd_snapshots
        WHERE destination_id = ?
          AND day_of_week = ?
          AND hour = ?
          AND is_demo = 0
        """,
        (destination_id, day_of_week, hour),
    )
    row = cursor.fetchone()
    if not row or not row["n"] or row["n"] < 1:
        # Fall back including demo snapshots only if no real history
        cursor.execute(
            """
            SELECT AVG(estimated_crowd) AS avg_crowd, COUNT(*) AS n
            FROM crowd_snapshots
            WHERE destination_id = ? AND day_of_week = ? AND hour = ?
            """,
            (destination_id, day_of_week, hour),
        )
        row = cursor.fetchone()
    if not row or not row["n"] or row["avg_crowd"] is None:
        return None
    return float(row["avg_crowd"])


def recent_trend_delta(cursor, destination_id: int, minutes: int = 30) -> Tuple[float, str]:
    cursor.execute(
        """
        SELECT estimated_crowd, captured_at FROM crowd_snapshots
        WHERE destination_id = ?
        ORDER BY datetime(captured_at) DESC
        LIMIT 1
        """,
        (destination_id,),
    )
    latest = cursor.fetchone()
    cursor.execute(
        """
        SELECT estimated_crowd FROM crowd_snapshots
        WHERE destination_id = ?
          AND datetime(captured_at) <= datetime('now', ?)
        ORDER BY datetime(captured_at) DESC
        LIMIT 1
        """,
        (destination_id, f"-{int(minutes)} minutes"),
    )
    older = cursor.fetchone()
    if not latest or not older:
        return 0.0, "stable"
    delta = float(latest["estimated_crowd"]) - float(older["estimated_crowd"])
    if delta > 40:
        label = "increasing_rapidly"
    elif delta > 10:
        label = "increasing"
    elif delta < -40:
        label = "decreasing_rapidly"
    elif delta < -10:
        label = "decreasing"
    else:
        label = "stable"
    return delta, label


def pulse_crowd_hint(cursor, destination_id: int) -> Optional[float]:
    """Map recent Ground Pulse rush votes to a soft crowd hint (0-100 scale index)."""
    cursor.execute(
        """
        SELECT crowd_rush FROM ground_pulse_votes
        WHERE destination_id = ?
        ORDER BY id DESC LIMIT 10
        """,
        (destination_id,),
    )
    rushes = [r["crowd_rush"] for r in cursor.fetchall()]
    if not rushes:
        return None
    mapping = {"Peaceful": 0.25, "Moderate": 0.50, "Heavy": 0.80, "Extreme": 0.95}
    scores = [mapping.get(r, 0.5) for r in rushes]
    return sum(scores) / len(scores)


def compute_confidence(
    observed: int,
    capacity: int,
    history_n: int,
    has_bookings: bool,
    data_fresh_seconds: Optional[float],
) -> float:
    """0–100 confidence based on GPS participation, history, bookings, freshness."""
    gps_ratio = min(1.0, observed / max(20.0, capacity * 0.05))
    gps_score = gps_ratio * 40.0
    hist_score = min(25.0, history_n * 2.5)
    booking_score = 15.0 if has_bookings else 5.0
    if data_fresh_seconds is None:
        fresh_score = 5.0
    elif data_fresh_seconds <= 60:
        fresh_score = 20.0
    elif data_fresh_seconds <= 300:
        fresh_score = 14.0
    elif data_fresh_seconds <= 900:
        fresh_score = 8.0
    else:
        fresh_score = 3.0
    return round(min(95.0, max(8.0, gps_score + hist_score + booking_score + fresh_score)), 1)


def estimate_current_crowd(destination_id: int) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM destinations WHERE id = ?", (destination_id,))
        dest = cursor.fetchone()
        if not dest:
            raise ValueError("Destination not found")
        dest = dict(dest)

        expire_stale_visitors(cursor)
        observed = count_observed_users(cursor, destination_id)
        booked = count_booked_visitors_now(cursor, destination_id)
        capacity = get_effective_capacity(dest)
        comfortable = int(dest.get("comfortable_capacity") or max(1, int(capacity * 0.6)))
        area = dest.get("area_sq_meters")

        now = datetime.utcnow()
        hist = historical_average(cursor, destination_id, now.weekday(), now.hour)
        trend_delta, trend_label = recent_trend_delta(cursor, destination_id, 30)

        cursor.execute(
            "SELECT COUNT(*) AS n FROM crowd_snapshots WHERE destination_id = ?",
            (destination_id,),
        )
        history_n = int(cursor.fetchone()["n"])

        pulse_hint = pulse_crowd_hint(cursor, destination_id)
        weights = get_weights(dest)

        # Baseline from history or pulse/capacity heuristic when history missing
        if hist is not None:
            historical_component = hist
        elif pulse_hint is not None:
            historical_component = pulse_hint * capacity
        else:
            historical_component = capacity * 0.35

        # Observed GPS alone undercounts; bookings alone over/under depending on no-shows
        gps_component = float(observed)
        booking_component = float(booked)
        trend_component = max(0.0, historical_component + trend_delta)

        # If GPS participation is very low, down-weight GPS and up-weight history/bookings
        gps_participation = observed / max(1.0, capacity * 0.08)
        if gps_participation < 0.3:
            adj = {
                "gps": weights["gps"] * 0.4,
                "bookings": weights["bookings"] * 1.2,
                "historical": weights["historical"] * 1.3,
                "trend": weights["trend"],
            }
            s = sum(adj.values()) or 1.0
            weights = {k: v / s for k, v in adj.items()}

        estimated = (
            weights["gps"] * gps_component
            + weights["bookings"] * booking_component
            + weights["historical"] * historical_component
            + weights["trend"] * trend_component
        )
        # Soft floor: never below observed users
        estimated = max(float(observed), estimated)
        estimated_int = int(round(min(capacity * 1.25, estimated)))

        occupancy = round((estimated_int / capacity) * 100.0, 1)
        density = round(estimated_int / float(area), 5) if area and float(area) > 0 else None
        level = crowd_level_from_occupancy(occupancy, dest)

        cursor.execute(
            """
            SELECT captured_at FROM crowd_snapshots
            WHERE destination_id = ?
            ORDER BY datetime(captured_at) DESC LIMIT 1
            """,
            (destination_id,),
        )
        last_snap = cursor.fetchone()
        fresh_secs = None
        if last_snap and last_snap["captured_at"]:
            try:
                ts = datetime.fromisoformat(str(last_snap["captured_at"]).replace("Z", ""))
                fresh_secs = abs((datetime.utcnow() - ts).total_seconds())
            except Exception:
                fresh_secs = None

        confidence = compute_confidence(
            observed, capacity, history_n, booked > 0, fresh_secs
        )

        data_available = observed > 0 or booked > 0 or hist is not None or pulse_hint is not None
        is_demo = _demo_flag()

        return {
            "destination_id": destination_id,
            "destination_name": dest["name"],
            "observed_users": observed,
            "booked_visitors": booked,
            "estimated_crowd": estimated_int if data_available else None,
            "capacity": capacity,
            "comfortable_capacity": comfortable,
            "occupancy_percentage": occupancy if data_available else None,
            "density": density if data_available else None,
            "crowd_level": level if data_available else "UNKNOWN",
            "trend": trend_label,
            "trend_delta_30m": round(trend_delta, 1),
            "confidence": confidence if data_available else 0.0,
            "confidence_label": (
                "High" if confidence >= 75 else "Moderate" if confidence >= 50 else "Low"
            ),
            "data_available": data_available,
            "is_estimate": True,
            "is_demo_data": is_demo,
            "label": "Estimated based on available data",
            "weights_used": weights,
            "signals": {
                "historical_average": round(historical_component, 1) if hist is not None or pulse_hint else None,
                "pulse_hint_ratio": pulse_hint,
                "history_snapshots": history_n,
            },
            "geofence_radius_m": dest.get("geofence_radius_m"),
            "area_sq_meters": area,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "unavailable_message": None
            if data_available
            else "Live crowd information currently unavailable.",
        }


def compute_zone_crowds(destination_id: int) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        expire_stale_visitors(cursor)
        cursor.execute(
            "SELECT * FROM destination_zones WHERE destination_id = ? AND status = 'active'",
            (destination_id,),
        )
        zones = [dict(z) for z in cursor.fetchall()]
        results = []
        for z in zones:
            cursor.execute(
                """
                SELECT COUNT(*) AS c FROM visitor_presence
                WHERE destination_id = ? AND zone_id = ? AND is_active = 1
                """,
                (destination_id, z["id"]),
            )
            observed = int(cursor.fetchone()["c"])
            # Zone estimate: observed + soft booking share
            cap = max(1, int(z.get("capacity") or 200))
            est = max(observed, int(round(observed * 1.8 + cap * 0.1)))
            occ = round(est / cap * 100.0, 1)
            area = z.get("area_sq_meters")
            results.append(
                {
                    "zone_id": z["id"],
                    "name": z["name"],
                    "zone_type": z.get("zone_type"),
                    "observed_users": observed,
                    "estimated_crowd": est,
                    "capacity": cap,
                    "occupancy_percentage": occ,
                    "density": round(est / float(area), 5) if area else None,
                    "crowd_level": crowd_level_from_occupancy(occ, {}),
                    "is_estimate": True,
                }
            )
        return results


def capture_snapshot(destination_id: int, weather_condition: Optional[str] = None) -> Dict[str, Any]:
    summary = estimate_current_crowd(destination_id)
    if summary["estimated_crowd"] is None:
        return summary
    now = datetime.utcnow()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO crowd_snapshots (
                destination_id, captured_at, day_of_week, hour,
                observed_users, booked_visitors, estimated_crowd, capacity,
                occupancy_percentage, density, crowd_level, confidence,
                weather_condition, is_demo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                destination_id,
                now.isoformat(sep=" "),
                now.weekday(),
                now.hour,
                summary["observed_users"],
                summary["booked_visitors"],
                summary["estimated_crowd"],
                summary["capacity"],
                summary["occupancy_percentage"],
                summary["density"],
                summary["crowd_level"],
                summary["confidence"],
                weather_condition,
                1 if summary["is_demo_data"] else 0,
            ),
        )
        # Sync crowd_density metric (0-100) for existing UI + risk score
        density_index = min(99.0, max(5.0, float(summary["occupancy_percentage"] or 50)))
        cursor.execute(
            """
            UPDATE risk_metrics SET crowd_density = ?, updated_at = CURRENT_TIMESTAMP
            WHERE destination_id = ?
            """,
            (density_index, destination_id),
        )
    return summary


def get_crowd_history(destination_id: int, hours: int = 24) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM crowd_snapshots
            WHERE destination_id = ?
              AND datetime(captured_at) >= datetime('now', ?)
            ORDER BY datetime(captured_at) ASC
            """,
            (destination_id, f"-{int(hours)} hours"),
        )
        return [dict(r) for r in cursor.fetchall()]


def get_trend_windows(destination_id: int) -> Dict[str, Any]:
    windows = {}
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT estimated_crowd FROM crowd_snapshots
            WHERE destination_id = ?
            ORDER BY datetime(captured_at) DESC LIMIT 1
            """,
            (destination_id,),
        )
        now_row = cursor.fetchone()
        current = int(now_row["estimated_crowd"]) if now_row else None
        for label, mins in [("5m", 5), ("10m", 10), ("30m", 30), ("60m", 60)]:
            cursor.execute(
                """
                SELECT estimated_crowd FROM crowd_snapshots
                WHERE destination_id = ?
                  AND datetime(captured_at) <= datetime('now', ?)
                ORDER BY datetime(captured_at) DESC LIMIT 1
                """,
                (destination_id, f"-{mins} minutes"),
            )
            older = cursor.fetchone()
            if current is None or not older:
                windows[label] = {"change": None, "direction": "unknown"}
            else:
                change = current - int(older["estimated_crowd"])
                windows[label] = {
                    "change": change,
                    "direction": "up" if change > 5 else "down" if change < -5 else "flat",
                }
        windows["current_estimated"] = current
    return windows
