"""Transactional ticket booking with overbooking prevention."""
from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.database import get_db_connection
from app.services.prediction_engine import predict_for_slot, recommend_less_crowded_slots


def _booking_ref() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "ST-" + "".join(secrets.choice(alphabet) for _ in range(10))


def ensure_slots_for_date(
    destination_id: int,
    slot_date: str,
    opening_time: str = "09:00",
    closing_time: str = "17:00",
    slot_capacity: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Create hourly slots for a date if missing."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM destinations WHERE id = ?", (destination_id,))
        dest = cursor.fetchone()
        if not dest:
            raise ValueError("Destination not found")
        dest = dict(dest)
        capacity = slot_capacity or max(50, int((dest.get("maximum_capacity") or 1000) * 0.25))
        open_h = int((dest.get("opening_time") or opening_time).split(":")[0])
        close_h = int((dest.get("closing_time") or closing_time).split(":")[0])
        if close_h <= open_h:
            close_h = open_h + 8

        created = []
        for h in range(open_h, close_h):
            start = f"{h:02d}:00"
            end = f"{h+1:02d}:00"
            cursor.execute(
                """
                INSERT OR IGNORE INTO ticket_slots
                (destination_id, slot_date, start_time, end_time, capacity, booked_count, reserved_count, status)
                VALUES (?, ?, ?, ?, ?, 0, 0, 'open')
                """,
                (destination_id, slot_date, start, end, capacity),
            )
        conn.commit()
        cursor.execute(
            """
            SELECT * FROM ticket_slots
            WHERE destination_id = ? AND slot_date = ?
            ORDER BY start_time ASC
            """,
            (destination_id, slot_date),
        )
        created = [dict(r) for r in cursor.fetchall()]
        return created
    finally:
        conn.close()


def get_slots_with_crowd(destination_id: int, slot_date: str) -> List[Dict[str, Any]]:
    slots = ensure_slots_for_date(destination_id, slot_date)
    enriched = []
    for s in slots:
        remaining = max(0, int(s["capacity"]) - int(s["booked_count"]) - int(s.get("reserved_count") or 0))
        try:
            pred = predict_for_slot(destination_id, s["id"])
        except Exception:
            pred = {
                "predicted_crowd": None,
                "predicted_occupancy": None,
                "crowd_level": "UNKNOWN",
                "confidence": 0,
                "confidence_label": "Low",
            }
        enriched.append(
            {
                "id": s["id"],
                "destination_id": destination_id,
                "slot_date": s["slot_date"],
                "start_time": s["start_time"],
                "end_time": s["end_time"],
                "capacity": s["capacity"],
                "booked_count": s["booked_count"],
                "available": remaining,
                "status": s["status"] if remaining > 0 else "full",
                "predicted_crowd": pred.get("predicted_crowd"),
                "predicted_occupancy": pred.get("predicted_occupancy"),
                "crowd_level": pred.get("crowd_level"),
                "confidence": pred.get("confidence"),
                "confidence_label": pred.get("confidence_label"),
                "is_estimate": True,
                "label": "Predicted crowd for slot (estimate)",
            }
        )
    return enriched


def book_tickets(
    destination_id: int,
    slot_id: int,
    number_of_people: int,
    user_id: Optional[int] = None,
    anonymous_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    if number_of_people is None or int(number_of_people) < 1:
        raise ValueError("number_of_people must be at least 1")
    number_of_people = int(number_of_people)
    if number_of_people > 50:
        raise ValueError("Group bookings limited to 50 people per request")

    conn = get_db_connection()
    try:
        # BEGIN IMMEDIATE locks for write to prevent double-booking races
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM ticket_slots WHERE id = ? AND destination_id = ?",
            (slot_id, destination_id),
        )
        slot = cursor.fetchone()
        if not slot:
            conn.rollback()
            raise LookupError("Slot not found")
        slot = dict(slot)
        if slot["status"] not in ("open", "limited"):
            conn.rollback()
            raise ValueError("This slot is not available for booking.")

        remaining = (
            int(slot["capacity"])
            - int(slot["booked_count"])
            - int(slot.get("reserved_count") or 0)
        )
        if number_of_people > remaining:
            conn.rollback()
            alternatives = recommend_less_crowded_slots(destination_id, slot["slot_date"], limit=3)
            raise OverflowError(
                {
                    "message": "This slot is currently full.",
                    "remaining": remaining,
                    "requested": number_of_people,
                    "alternatives": alternatives,
                }
            )

        ref = _booking_ref()
        cursor.execute(
            """
            UPDATE ticket_slots
            SET booked_count = booked_count + ?
            WHERE id = ? AND (capacity - booked_count - reserved_count) >= ?
            """,
            (number_of_people, slot_id, number_of_people),
        )
        if cursor.rowcount != 1:
            conn.rollback()
            raise OverflowError(
                {
                    "message": "This slot is currently full.",
                    "remaining": 0,
                    "requested": number_of_people,
                    "alternatives": recommend_less_crowded_slots(
                        destination_id, slot["slot_date"], limit=3
                    ),
                }
            )

        cursor.execute(
            """
            INSERT INTO ticket_bookings (
                booking_reference, user_id, anonymous_user_id, destination_id,
                slot_id, number_of_people, booking_status
            ) VALUES (?, ?, ?, ?, ?, ?, 'confirmed')
            """,
            (ref, user_id, anonymous_user_id, destination_id, slot_id, number_of_people),
        )
        booking_id = cursor.lastrowid
        conn.commit()

        return {
            "success": True,
            "booking_id": booking_id,
            "booking_reference": ref,
            "destination_id": destination_id,
            "slot_id": slot_id,
            "slot_date": slot["slot_date"],
            "start_time": slot["start_time"],
            "end_time": slot["end_time"],
            "number_of_people": number_of_people,
            "booking_status": "confirmed",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()


def cancel_booking(booking_id: int, user_id: Optional[int] = None, is_admin: bool = False) -> Dict[str, Any]:
    conn = get_db_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ticket_bookings WHERE id = ?", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            conn.rollback()
            raise LookupError("Booking not found")
        booking = dict(booking)
        if booking["booking_status"] != "confirmed":
            conn.rollback()
            raise ValueError("Booking is not active")
        if not is_admin and user_id is not None and booking.get("user_id") != user_id:
            conn.rollback()
            raise PermissionError("Not authorized to cancel this booking")

        cursor.execute(
            """
            UPDATE ticket_bookings
            SET booking_status = 'cancelled', cancelled_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (booking_id,),
        )
        cursor.execute(
            """
            UPDATE ticket_slots
            SET booked_count = CASE
                WHEN booked_count >= ? THEN booked_count - ?
                ELSE 0
            END
            WHERE id = ?
            """,
            (booking["number_of_people"], booking["number_of_people"], booking["slot_id"]),
        )
        conn.commit()
        return {"success": True, "booking_id": booking_id, "booking_status": "cancelled"}
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()


def get_booking(booking_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT b.*, s.slot_date, s.start_time, s.end_time, d.name AS destination_name
            FROM ticket_bookings b
            JOIN ticket_slots s ON s.id = b.slot_id
            JOIN destinations d ON d.id = b.destination_id
            WHERE b.id = ?
            """,
            (booking_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_my_bookings(
    user_id: Optional[int] = None,
    anonymous_user_id: Optional[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        clauses = []
        params = []
        if user_id is not None:
            clauses.append("b.user_id = ?")
            params.append(user_id)
        if anonymous_user_id:
            clauses.append("b.anonymous_user_id = ?")
            params.append(anonymous_user_id)
        if not clauses:
            return {"upcoming": [], "completed": [], "cancelled": []}
        where = " OR ".join(clauses)
        cursor.execute(
            f"""
            SELECT b.*, s.slot_date, s.start_time, s.end_time, d.name AS destination_name,
                   d.state AS destination_state
            FROM ticket_bookings b
            JOIN ticket_slots s ON s.id = b.slot_id
            JOIN destinations d ON d.id = b.destination_id
            WHERE ({where})
            ORDER BY s.slot_date DESC, s.start_time DESC
            """,
            params,
        )
        rows = [dict(r) for r in cursor.fetchall()]
        today = datetime.utcnow().strftime("%Y-%m-%d")
        upcoming, completed, cancelled = [], [], []
        for r in rows:
            if r.get("booking_status") == "cancelled":
                cancelled.append(r)
            elif str(r.get("slot_date") or "") >= today and r.get("booking_status") == "confirmed":
                upcoming.append(r)
            else:
                completed.append(r)
        return {"upcoming": upcoming, "completed": completed, "cancelled": cancelled}
    finally:
        conn.close()
