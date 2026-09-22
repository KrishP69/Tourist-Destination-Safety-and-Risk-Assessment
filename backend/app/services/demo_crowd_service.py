"""
Demo mode: generates simulated GPS presence / bookings / trends.
ALWAYS labeled as DEMO DATA — never presented as live measurements.
"""
from __future__ import annotations

import hashlib
import math
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

from app.config import DEMO_MODE
from app.database import get_db
from app.services.crowd_engine import capture_snapshot
from app.services.booking_service import ensure_slots_for_date


def is_demo_enabled() -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = 'DEMO_MODE'")
        row = cursor.fetchone()
        if row:
            return str(row["value"]).lower() in ("1", "true", "yes")
    return DEMO_MODE


def set_demo_mode(enabled: bool) -> None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO app_settings (key, value) VALUES ('DEMO_MODE', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            ("true" if enabled else "false",),
        )


def _anon(seed: str) -> str:
    return "demo_" + hashlib.sha256(seed.encode()).hexdigest()[:16]


def seed_destination_crowd_defaults(cursor) -> None:
    """Backfill capacity/geofence/zones for destinations."""
    cursor.execute(
        """
        SELECT d.id, d.name, COALESCE(rm.crowd_density, 50) AS crowd_density,
               d.maximum_capacity, d.comfortable_capacity, d.geofence_radius_m, d.area_sq_meters
        FROM destinations d
        LEFT JOIN risk_metrics rm ON rm.destination_id = d.id
        """
    )
    rows = [dict(r) for r in cursor.fetchall()]
    for row in rows:
        dens = float(row["crowd_density"] or 50)
        max_cap = 800 + int(dens * 12)
        comfort = int(max_cap * 0.6)
        area = float(max_cap * 2.5)
        radius = 600 if dens < 60 else 900 if dens < 85 else 1200

        # Only overwrite placeholder defaults
        new_max = max_cap if int(row["maximum_capacity"] or 1000) == 1000 else int(row["maximum_capacity"])
        new_comfort = comfort if int(row["comfortable_capacity"] or 600) == 600 else int(row["comfortable_capacity"])
        new_radius = radius if float(row["geofence_radius_m"] or 800) == 800 else float(row["geofence_radius_m"])
        new_area = area if row["area_sq_meters"] is None else float(row["area_sq_meters"])

        cursor.execute(
            """
            UPDATE destinations SET
                maximum_capacity = ?,
                comfortable_capacity = ?,
                area_sq_meters = ?,
                geofence_radius_m = ?
            WHERE id = ?
            """,
            (new_max, new_comfort, new_area, new_radius, row["id"]),
        )
        cursor.execute(
            "SELECT COUNT(*) AS c FROM destination_zones WHERE destination_id = ?",
            (row["id"],),
        )
        if cursor.fetchone()["c"] == 0:
            cursor.execute("SELECT lat, lng FROM destinations WHERE id = ?", (row["id"],))
            d = cursor.fetchone()
            zones = [
                ("Entrance", "entrance", 0.15),
                ("Main Square", "main", 0.40),
                ("Facilities", "facilities", 0.20),
                ("Exit", "exit", 0.15),
            ]
            for name, ztype, share in zones:
                cursor.execute(
                    """
                    INSERT INTO destination_zones
                    (destination_id, name, zone_type, capacity, area_sq_meters, center_lat, center_lng, radius_m, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
                    """,
                    (
                        row["id"],
                        name,
                        ztype,
                        max(50, int(new_max * share)),
                        max(100, new_area * share),
                        float(d["lat"]) + random.uniform(-0.001, 0.001),
                        float(d["lng"]) + random.uniform(-0.001, 0.001),
                        180,
                    ),
                )


def simulate_presence_for_destination(destination_id: int, target_observed: int) -> int:
    """Upsert demo anonymous visitors inside geofence. Returns count written."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM destination_zones WHERE destination_id = ? AND status = 'active'",
            (destination_id,),
        )
        zones = [z["id"] for z in cursor.fetchall()]
        # Deactivate previous demo visitors
        cursor.execute(
            """
            UPDATE visitor_presence SET is_active = 0, exited_at = CURRENT_TIMESTAMP
            WHERE destination_id = ? AND anonymous_user_id LIKE 'demo_%' AND is_active = 1
            """,
            (destination_id,),
        )
        now = datetime.utcnow().isoformat(sep=" ")
        for i in range(target_observed):
            anon = _anon(f"{destination_id}-{i}-{datetime.utcnow().date()}")
            zone_id = random.choice(zones) if zones else None
            cursor.execute(
                """
                INSERT INTO visitor_presence
                (anonymous_user_id, destination_id, zone_id, last_seen, entered_at, is_active, source)
                VALUES (?, ?, ?, ?, ?, 1, 'demo')
                ON CONFLICT(anonymous_user_id, destination_id) DO UPDATE SET
                    is_active = 1,
                    last_seen = excluded.last_seen,
                    exited_at = NULL,
                    zone_id = excluded.zone_id,
                    source = 'demo'
                """,
                (anon, destination_id, zone_id, now, now),
            )
        return target_observed


def run_demo_tick() -> Dict[str, Any]:
    """
    Advance simulated crowd for a few popular destinations.
    Clearly marks snapshots as demo.
    """
    if not is_demo_enabled():
        return {"demo_mode": False, "updated": 0}

    updated = []
    with get_db() as conn:
        cursor = conn.cursor()
        seed_destination_crowd_defaults(cursor)
        cursor.execute(
            "SELECT id, name, maximum_capacity FROM destinations ORDER BY id ASC LIMIT 12"
        )
        dests = [dict(d) for d in cursor.fetchall()]

    today = datetime.utcnow().strftime("%Y-%m-%d")
    hour = datetime.utcnow().hour

    for d in dests:
        cap = max(100, int(d.get("maximum_capacity") or 1000))
        # Diurnal curve: peak midday
        diurnal = 0.35 + 0.55 * max(0, math.sin((hour - 6) / 14 * math.pi))
        noise = random.uniform(0.85, 1.15)
        target_obs = max(5, int(cap * 0.08 * diurnal * noise))
        simulate_presence_for_destination(d["id"], target_obs)

        # Seed a few bookings into today's slots
        slots = ensure_slots_for_date(d["id"], today)
        with get_db() as conn:
            cursor = conn.cursor()
            for s in slots[:6]:
                if int(s["booked_count"]) < int(s["capacity"]) * 0.4:
                    add = random.randint(5, max(6, int(s["capacity"] * 0.08)))
                    cursor.execute(
                        """
                        UPDATE ticket_slots
                        SET booked_count = MIN(capacity, booked_count + ?)
                        WHERE id = ?
                        """,
                        (add, s["id"]),
                    )

        summary = capture_snapshot(d["id"], weather_condition="DEMO")
        # Force is_demo flag on latest snapshot
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE crowd_snapshots SET is_demo = 1
                WHERE id = (SELECT id FROM crowd_snapshots WHERE destination_id = ? ORDER BY id DESC LIMIT 1)
                """,
                (d["id"],),
            )
        updated.append(
            {
                "destination_id": d["id"],
                "name": d["name"],
                "observed_users": summary.get("observed_users"),
                "estimated_crowd": summary.get("estimated_crowd"),
                "is_demo_data": True,
            }
        )

    return {"demo_mode": True, "label": "DEMO DATA", "updated": len(updated), "destinations": updated}


def bootstrap_historical_demo_snapshots(days: int = 7) -> int:
    """Create labeled demo historical snapshots for prediction baselines."""
    if not is_demo_enabled():
        return 0
    count = 0
    with get_db() as conn:
        cursor = conn.cursor()
        seed_destination_crowd_defaults(cursor)
        cursor.execute("SELECT id, maximum_capacity FROM destinations LIMIT 12")
        dests = [dict(d) for d in cursor.fetchall()]
        for d in dests:
            cap = max(100, int(d["maximum_capacity"] or 1000))
            for day_offset in range(days):
                for hour in range(8, 20):
                    base = datetime.utcnow() - timedelta(days=day_offset)
                    ts = base.replace(hour=hour, minute=0, second=0, microsecond=0)
                    diurnal = 0.35 + 0.55 * max(0, math.sin((hour - 6) / 14 * math.pi))
                    weekend_boost = 1.25 if ts.weekday() >= 5 else 1.0
                    est = int(cap * diurnal * weekend_boost * random.uniform(0.8, 1.1))
                    obs = max(3, int(est * random.uniform(0.15, 0.35)))
                    booked = max(0, int(est * random.uniform(0.2, 0.45)))
                    occ = round(est / cap * 100, 1)
                    cursor.execute(
                        """
                        INSERT INTO crowd_snapshots (
                            destination_id, captured_at, day_of_week, hour,
                            observed_users, booked_visitors, estimated_crowd, capacity,
                            occupancy_percentage, density, crowd_level, confidence,
                            weather_condition, is_demo
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, 'DEMO', 1)
                        """,
                        (
                            d["id"],
                            ts.isoformat(sep=" "),
                            ts.weekday(),
                            hour,
                            obs,
                            booked,
                            est,
                            cap,
                            occ,
                            "HIGH" if occ >= 75 else "MODERATE" if occ >= 60 else "LOW",
                            45.0,
                        ),
                    )
                    count += 1
    return count
