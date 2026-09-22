"""
Crowd prediction engine (v1 statistical).

Modular: replace predict_for_slot / predict_horizon with ML later without changing API.
Does NOT train on fabricated data — uses available history/bookings/trend with transparent fallbacks.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.database import get_db
from app.services.crowd_engine import (
    crowd_level_from_occupancy,
    estimate_current_crowd,
    get_effective_capacity,
    historical_average,
    recent_trend_delta,
    compute_confidence,
)


MODEL_VERSION = "v1-statistical"


def _parse_slot_hours(start_time: str, end_time: str) -> tuple:
    sh, sm = [int(x) for x in start_time.split(":")[:2]]
    eh, em = [int(x) for x in end_time.split(":")[:2]]
    return sh + sm / 60.0, eh + em / 60.0


def predict_for_slot(destination_id: int, slot_id: int) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM destinations WHERE id = ?", (destination_id,))
        dest = cursor.fetchone()
        if not dest:
            raise ValueError("Destination not found")
        dest = dict(dest)

        cursor.execute(
            "SELECT * FROM ticket_slots WHERE id = ? AND destination_id = ?",
            (slot_id, destination_id),
        )
        slot = cursor.fetchone()
        if not slot:
            raise ValueError("Slot not found")
        slot = dict(slot)

        capacity = int(slot.get("capacity") or get_effective_capacity(dest))
        booked = int(slot.get("booked_count") or 0)

        # Day-of-week for slot date
        try:
            slot_date = datetime.strptime(slot["slot_date"], "%Y-%m-%d")
            dow = slot_date.weekday()
        except Exception:
            dow = datetime.utcnow().weekday()

        start_h, end_h = _parse_slot_hours(slot["start_time"], slot["end_time"])
        hour = int(start_h)

        hist = historical_average(cursor, destination_id, dow, hour)
        current = estimate_current_crowd(destination_id)
        trend_delta, trend_label = recent_trend_delta(cursor, destination_id, 30)

        cursor.execute(
            "SELECT COUNT(*) AS n FROM crowd_snapshots WHERE destination_id = ?",
            (destination_id,),
        )
        history_n = int(cursor.fetchone()["n"])

        # Expected arrivals ≈ booked * show-up rate; departures ≈ portion of current leaving
        show_up_rate = 0.85
        expected_arrivals = int(round(booked * show_up_rate))
        current_est = current.get("estimated_crowd") or 0
        expected_departures = int(round(current_est * 0.20))

        baseline = hist if hist is not None else max(current_est, booked * 0.7, capacity * 0.3)
        # Blend: current crowd continuity + arrivals - departures + historical pull
        predicted = (
            0.35 * current_est
            + 0.35 * expected_arrivals
            + 0.20 * baseline
            + 0.10 * max(0, current_est + trend_delta)
            - 0.15 * expected_departures
        )
        predicted = max(booked * 0.5, predicted)  # bookings imply lower bound of interest
        predicted_int = int(round(min(capacity * 1.15, max(0, predicted))))
        occupancy = round(predicted_int / max(1, capacity) * 100.0, 1)
        level = crowd_level_from_occupancy(occupancy, dest)

        confidence = compute_confidence(
            current.get("observed_users") or 0,
            capacity,
            history_n,
            booked > 0,
            30.0,
        )
        # Reduce confidence when no history
        if hist is None:
            confidence = round(max(15.0, confidence * 0.65), 1)

        fallback_note = None
        if hist is None and history_n < 3:
            fallback_note = "Statistical fallback: limited historical data; based on current crowd + bookings."

        result = {
            "destination_id": destination_id,
            "slot_id": slot_id,
            "slot_date": slot["slot_date"],
            "start_time": slot["start_time"],
            "end_time": slot["end_time"],
            "slot_capacity": capacity,
            "booked_visitors": booked,
            "available_capacity": max(0, capacity - booked - int(slot.get("reserved_count") or 0)),
            "current_estimated_crowd": current_est,
            "expected_arrivals": expected_arrivals,
            "expected_departures": expected_departures,
            "predicted_crowd": predicted_int,
            "predicted_occupancy": occupancy,
            "crowd_level": level,
            "confidence": confidence,
            "confidence_label": (
                "High" if confidence >= 75 else "Moderate" if confidence >= 50 else "Low"
            ),
            "trend": trend_label,
            "model_version": MODEL_VERSION,
            "is_estimate": True,
            "fallback_note": fallback_note,
            "label": "Predicted crowd (estimate)",
        }

        # Persist prediction
        pred_for = f"{slot['slot_date']} {slot['start_time']}:00"
        cursor.execute(
            """
            INSERT INTO crowd_predictions (
                destination_id, slot_id, prediction_for, predicted_crowd,
                predicted_occupancy, crowd_level, confidence, model_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                destination_id,
                slot_id,
                pred_for,
                predicted_int,
                occupancy,
                level,
                confidence,
                MODEL_VERSION,
            ),
        )
        return result


def predict_horizon(destination_id: int, hours_ahead: int = 1) -> Dict[str, Any]:
    current = estimate_current_crowd(destination_id)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM destinations WHERE id = ?", (destination_id,))
        dest = dict(cursor.fetchone())
        capacity = get_effective_capacity(dest)
        future = datetime.utcnow() + timedelta(hours=hours_ahead)
        hist = historical_average(cursor, destination_id, future.weekday(), future.hour)
        trend_delta, trend_label = recent_trend_delta(cursor, destination_id, 30)
        current_est = current.get("estimated_crowd") or 0
        baseline = hist if hist is not None else current_est
        predicted = int(round(0.5 * current_est + 0.35 * baseline + 0.15 * (current_est + trend_delta)))
        predicted = max(0, min(int(capacity * 1.15), predicted))
        occupancy = round(predicted / max(1, capacity) * 100.0, 1)
        conf = current.get("confidence") or 30.0
        if hist is None:
            conf = round(conf * 0.7, 1)
        return {
            "destination_id": destination_id,
            "hours_ahead": hours_ahead,
            "prediction_for": future.isoformat() + "Z",
            "current_estimated_crowd": current_est,
            "predicted_crowd": predicted if current.get("data_available") else None,
            "predicted_occupancy": occupancy if current.get("data_available") else None,
            "crowd_level": crowd_level_from_occupancy(occupancy, dest),
            "confidence": conf,
            "confidence_label": (
                "High" if conf >= 75 else "Moderate" if conf >= 50 else "Low"
            ),
            "trend": trend_label,
            "model_version": MODEL_VERSION,
            "is_estimate": True,
            "label": "Predicted crowd (estimate)",
            "data_available": current.get("data_available"),
        }


def recommend_less_crowded_slots(
    destination_id: int, slot_date: str, limit: int = 5
) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM ticket_slots
            WHERE destination_id = ? AND slot_date = ? AND status = 'open'
            ORDER BY start_time ASC
            """,
            (destination_id, slot_date),
        )
        slots = [dict(s) for s in cursor.fetchall()]

    current = estimate_current_crowd(destination_id)
    trend = current.get("trend") or "stable"
    scored = []
    for s in slots:
        remaining = max(0, int(s["capacity"]) - int(s["booked_count"]) - int(s.get("reserved_count") or 0))
        if remaining <= 0:
            continue
        try:
            pred = predict_for_slot(destination_id, s["id"])
        except Exception:
            continue
        conf = float(pred.get("confidence") or 0)
        occ = float(pred.get("predicted_occupancy") or 100)
        # Prefer lower occupancy, availability, and confidence — not earliest slot
        avail_ratio = remaining / max(1, int(s["capacity"]))
        score = (
            (100 - occ) * 0.55
            + avail_ratio * 25
            + min(conf, 100) * 0.15
            + (5 if trend.startswith("increasing") and occ < 50 else 0)
        )
        scored.append(
            {
                **pred,
                "recommendation_score": round(score, 2),
                "available": remaining,
                "wording": "Lower predicted crowd",
                "recommendation_label": "Recommended based on current data",
            }
        )

    scored.sort(key=lambda x: (-x["recommendation_score"], x["predicted_occupancy"]))
    return scored[:limit]


def best_time_to_visit(destination_id: int, slot_date: Optional[str] = None, limit: int = 3) -> Dict[str, Any]:
    """Signature Best Time to Visit payload for destination UI."""
    if not slot_date:
        slot_date = datetime.utcnow().strftime("%Y-%m-%d")
    from app.services.booking_service import ensure_slots_for_date

    ensure_slots_for_date(destination_id, slot_date)
    options = recommend_less_crowded_slots(destination_id, slot_date, limit=max(limit, 3))
    current = estimate_current_crowd(destination_id)
    top = options[0] if options else None
    avg_conf = (
        round(sum(o.get("confidence") or 0 for o in options) / len(options), 1) if options else 0
    )
    return {
        "destination_id": destination_id,
        "date": slot_date,
        "title": "Best Time to Visit",
        "subtitle": "Based on current crowd + bookings + historical patterns",
        "wording": "Recommended based on current data — lower predicted crowd",
        "recommended": top,
        "top_options": options[:limit],
        "current_estimated_crowd": current.get("estimated_crowd"),
        "current_trend": current.get("trend"),
        "confidence": top.get("confidence") if top else avg_conf,
        "confidence_label": top.get("confidence_label") if top else "Low",
        "limited_data": (top.get("confidence") or 0) < 50 if top else True,
        "is_estimate": True,
        "data_available": bool(options),
        "unavailable_message": None if options else "No bookable lower-crowd slots available for this date.",
    }


def crowd_forecast(destination_id: int) -> Dict[str, Any]:
    """Now / +30m / +1h / +2h forecast with peak estimate."""
    current = estimate_current_crowd(destination_id)
    points = []
    now_est = current.get("estimated_crowd")
    points.append(
        {
            "label": "Now",
            "minutes_ahead": 0,
            "value": now_est,
            "kind": "estimated",
            "is_estimate": True,
        }
    )
    for mins, label in [(30, "+30 min"), (60, "+1 hour"), (120, "+2 hours")]:
        hours = max(1, int(round(mins / 60))) if mins >= 60 else 1
        # For 30 min, blend current with 1h prediction
        pred = predict_horizon(destination_id, hours_ahead=1 if mins <= 60 else 2)
        val = pred.get("predicted_crowd")
        if mins == 30 and now_est is not None and val is not None:
            val = int(round(0.6 * now_est + 0.4 * val))
        points.append(
            {
                "label": label,
                "minutes_ahead": mins,
                "value": val,
                "kind": "predicted",
                "is_estimate": True,
                "confidence": pred.get("confidence"),
            }
        )

    numeric = [p["value"] for p in points if p["value"] is not None]
    peak_idx = None
    peak_label = None
    if numeric:
        peak_idx = max(range(len(points)), key=lambda i: points[i]["value"] or -1)
        # Approximate clock time for peak
        peak_dt = datetime.utcnow() + timedelta(minutes=points[peak_idx]["minutes_ahead"])
        peak_label = peak_dt.strftime("%I:%M %p").lstrip("0")

    insight = build_crowd_insight(destination_id, current, points)

    return {
        "destination_id": destination_id,
        "points": points,
        "trend": current.get("trend"),
        "trend_delta_30m": current.get("trend_delta_30m"),
        "peak_expected_around": peak_label,
        "peak_index": peak_idx,
        "confidence": current.get("confidence"),
        "confidence_label": current.get("confidence_label"),
        "limited_data": (current.get("confidence") or 0) < 50,
        "is_demo_data": current.get("is_demo_data"),
        "data_available": current.get("data_available"),
        "insight": insight,
        "label": "Crowd forecast mixes current estimate with predictions",
    }


def build_crowd_insight(
    destination_id: int, current: Dict[str, Any], forecast_points: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Explain expected crowd change using only available signals — never invent."""
    reasons = []
    with get_db() as conn:
        cursor = conn.cursor()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        cursor.execute(
            """
            SELECT COALESCE(SUM(booked_count), 0) AS booked
            FROM ticket_slots
            WHERE destination_id = ? AND slot_date = ?
            """,
            (destination_id, today),
        )
        booked_today = int(cursor.fetchone()["booked"] or 0)
        if booked_today > 0:
            reasons.append(
                {
                    "direction": "up",
                    "text": f"{booked_today} tickets booked across today's slots",
                }
            )

    delta = current.get("trend_delta_30m")
    trend = current.get("trend") or "stable"
    if delta is not None and abs(float(delta)) >= 10:
        direction = "up" if float(delta) > 0 else "down"
        reasons.append(
            {
                "direction": direction,
                "text": f"Recent 30-minute crowd change: {float(delta):+.0f} (estimate)",
            }
        )

    if datetime.utcnow().weekday() >= 5:
        reasons.append(
            {
                "direction": "up",
                "text": "Weekend historical pattern typically elevates attendance",
            }
        )

    # Expected departures soft signal from current estimate
    cur = current.get("estimated_crowd") or 0
    if cur > 0:
        dep = int(round(cur * 0.20))
        reasons.append(
            {
                "direction": "down",
                "text": f"About {dep} expected departures in the next slot window (model assumption)",
            }
        )

    peak = None
    if forecast_points:
        vals = [(p["label"], p["value"]) for p in forecast_points if p.get("value") is not None]
        if vals:
            peak = max(vals, key=lambda x: x[1])

    rising = trend.startswith("increasing") or (
        forecast_points
        and forecast_points[-1].get("value") is not None
        and forecast_points[0].get("value") is not None
        and forecast_points[-1]["value"] > forecast_points[0]["value"]
    )

    return {
        "title": "Crowd insight",
        "question": "Why is crowd expected to change?" if rising else "What is shaping today's crowd?",
        "reasons": reasons[:5],
        "expected_peak": peak[0] if peak else None,
        "expected_peak_crowd": peak[1] if peak else None,
        "confidence": current.get("confidence"),
        "confidence_label": current.get("confidence_label"),
        "limited_data": (current.get("confidence") or 0) < 50,
        "based_on_available_data": True,
    }
