"""Visitor presence updates from opted-in location pings."""
from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.config import VISITOR_TIMEOUT_MINUTES
from app.database import get_db
from app.services.geofence_service import (
    is_inside_destination,
    is_inside_zone,
    validate_coordinates,
)
from app.services.crowd_engine import expire_stale_visitors


def hash_anonymous_id(raw_id: str) -> str:
    """Store only hashed anonymous identifiers."""
    raw = (raw_id or "").strip()
    if not raw:
        raise ValueError("anonymous_user_id is required")
    if raw.startswith("demo_") or len(raw) == 64:
        return raw[:64]
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def update_presence(
    anonymous_user_id: str,
    latitude: float,
    longitude: float,
    accuracy_m: Optional[float] = None,
    destination_id: Optional[int] = None,
) -> Dict[str, Any]:
    validate_coordinates(latitude, longitude)
    if accuracy_m is not None and float(accuracy_m) > 5000:
        # Extremely inaccurate — reject for geofence membership
        return {
            "accepted": False,
            "reason": "Location accuracy too poor for geofence detection",
            "active_destinations": [],
        }

    anon = hash_anonymous_id(anonymous_user_id)
    now = datetime.utcnow().isoformat(sep=" ")

    with get_db() as conn:
        cursor = conn.cursor()
        expire_stale_visitors(cursor, VISITOR_TIMEOUT_MINUTES)

        if destination_id:
            cursor.execute(
                "SELECT * FROM destinations WHERE id = ? AND crowd_status = 'active'",
                (destination_id,),
            )
            dests = cursor.fetchall()
        else:
            # Candidate destinations within ~5km bounding box (cheap prefilter)
            cursor.execute(
                """
                SELECT * FROM destinations
                WHERE crowd_status = 'active'
                  AND lat BETWEEN ? AND ?
                  AND lng BETWEEN ? AND ?
                """,
                (latitude - 0.08, latitude + 0.08, longitude - 0.08, longitude + 0.08),
            )
            dests = cursor.fetchall()

        active = []
        matched_ids = set()

        for row in dests:
            dest = dict(row)
            inside, dist_m = is_inside_destination(latitude, longitude, dest)
            if not inside:
                continue
            matched_ids.add(dest["id"])

            # Resolve zone if any
            zone_id = None
            cursor.execute(
                "SELECT * FROM destination_zones WHERE destination_id = ? AND status = 'active'",
                (dest["id"],),
            )
            for z in cursor.fetchall():
                if is_inside_zone(latitude, longitude, dict(z)):
                    zone_id = z["id"]
                    break

            cursor.execute(
                """
                INSERT INTO visitor_presence
                (anonymous_user_id, destination_id, zone_id, last_seen, entered_at, is_active, accuracy_m, source)
                VALUES (?, ?, ?, ?, ?, 1, ?, 'gps')
                ON CONFLICT(anonymous_user_id, destination_id) DO UPDATE SET
                    is_active = 1,
                    last_seen = excluded.last_seen,
                    exited_at = NULL,
                    zone_id = excluded.zone_id,
                    accuracy_m = excluded.accuracy_m,
                    source = 'gps'
                """,
                (anon, dest["id"], zone_id, now, now, accuracy_m),
            )
            active.append(
                {
                    "destination_id": dest["id"],
                    "destination_name": dest["name"],
                    "zone_id": zone_id,
                    "distance_m": dist_m,
                    "inside": True,
                }
            )

        # Mark exits for destinations this user was active in but no longer inside
        cursor.execute(
            """
            SELECT destination_id FROM visitor_presence
            WHERE anonymous_user_id = ? AND is_active = 1
            """,
            (anon,),
        )
        for row in cursor.fetchall():
            did = row["destination_id"]
            if did not in matched_ids:
                cursor.execute(
                    """
                    UPDATE visitor_presence
                    SET is_active = 0, exited_at = ?
                    WHERE anonymous_user_id = ? AND destination_id = ? AND is_active = 1
                    """,
                    (now, anon, did),
                )

        return {
            "accepted": True,
            "anonymous_user_id_hash_prefix": anon[:12],
            "active_destinations": active,
            "visitor_timeout_minutes": VISITOR_TIMEOUT_MINUTES,
            "note": "Precise coordinates are not stored; only geofence membership is retained.",
        }


def stop_presence(anonymous_user_id: str) -> Dict[str, Any]:
    anon = hash_anonymous_id(anonymous_user_id)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE visitor_presence
            SET is_active = 0, exited_at = CURRENT_TIMESTAMP
            WHERE anonymous_user_id = ? AND is_active = 1
            """,
            (anon,),
        )
        return {"success": True, "deactivated": cursor.rowcount}
