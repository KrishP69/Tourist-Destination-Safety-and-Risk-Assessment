from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.auth import get_current_user, get_optional_user
from app.services.booking_service import (
    get_slots_with_crowd,
    book_tickets,
    cancel_booking,
    get_booking,
    ensure_slots_for_date,
    list_my_bookings,
)
from app.services.prediction_engine import recommend_less_crowded_slots, best_time_to_visit

router = APIRouter(prefix="/api/tickets", tags=["Smart Ticket Booking"])


class BookRequest(BaseModel):
    destination_id: int
    slot_id: int
    number_of_people: int = Field(..., ge=1, le=50)
    anonymous_user_id: Optional[str] = Field(None, min_length=8, max_length=128)


@router.get("/my-bookings")
def my_bookings(
    anonymous_user_id: Optional[str] = Query(None),
    user=Depends(get_optional_user),
):
    data = list_my_bookings(
        user_id=user["id"] if user else None,
        anonymous_user_id=anonymous_user_id,
    )
    return {
        **data,
        "label": "Your SafeTour ticket bookings",
    }


@router.get("/booking/{booking_id}")
def fetch_booking(booking_id: int, user=Depends(get_optional_user)):
    booking = get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.get("/{destination_id}/slots")
def list_slots(destination_id: int, date: Optional[str] = None):
    slot_date = date or datetime.utcnow().strftime("%Y-%m-%d")
    try:
        slots = get_slots_with_crowd(destination_id, slot_date)
        return {
            "destination_id": destination_id,
            "date": slot_date,
            "slots": slots,
            "label": "Slots include predicted crowd estimates — not exact counts",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{destination_id}/recommend")
def recommend(destination_id: int, date: Optional[str] = None, limit: int = Query(5, ge=1, le=10)):
    slot_date = date or datetime.utcnow().strftime("%Y-%m-%d")
    ensure_slots_for_date(destination_id, slot_date)
    return {
        "destination_id": destination_id,
        "date": slot_date,
        "recommendations": recommend_less_crowded_slots(destination_id, slot_date, limit),
        "best_time": best_time_to_visit(destination_id, slot_date, limit=min(3, limit)),
        "label": "Less-crowded recommendations (estimates)",
    }


@router.post("/book")
def create_booking(payload: BookRequest, user=Depends(get_optional_user)):
    try:
        result = book_tickets(
            destination_id=payload.destination_id,
            slot_id=payload.slot_id,
            number_of_people=payload.number_of_people,
            user_id=user["id"] if user else None,
            anonymous_user_id=payload.anonymous_user_id,
        )
        # Enrich confirmation payload
        booking = get_booking(result["booking_id"])
        if booking:
            result["destination_name"] = booking.get("destination_name")
        return result
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OverflowError as e:
        detail = e.args[0] if e.args else {"message": "This slot is currently full."}
        raise HTTPException(status_code=409, detail=detail)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{booking_id}/cancel")
def cancel(booking_id: int, user=Depends(get_current_user)):
    try:
        is_admin = user.get("role") == "admin"
        return cancel_booking(booking_id, user_id=user["id"], is_admin=is_admin)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
