from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import List, Optional
import asyncio
import json

from app.services.crowd_engine import (
    estimate_current_crowd,
    get_crowd_history,
    get_trend_windows,
    compute_zone_crowds,
    capture_snapshot,
)
from app.services.prediction_engine import (
    predict_horizon,
    predict_for_slot,
    recommend_less_crowded_slots,
    best_time_to_visit,
    crowd_forecast,
)
from app.services.booking_service import get_slots_with_crowd, ensure_slots_for_date
from app.services.demo_crowd_service import is_demo_enabled
from app.database import get_db

router = APIRouter(prefix="/api/crowd", tags=["Crowd Intelligence"])


@router.get("/overview")
def crowd_overview():
    """Lightweight overview for map markers / dashboard list."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, lat, lng, maximum_capacity FROM destinations ORDER BY name")
        dests = [dict(d) for d in cursor.fetchall()]
    results = []
    for d in dests:
        try:
            s = estimate_current_crowd(d["id"])
            results.append(
                {
                    "destination_id": d["id"],
                    "name": d["name"],
                    "lat": d["lat"],
                    "lng": d["lng"],
                    "estimated_crowd": s.get("estimated_crowd"),
                    "observed_users": s.get("observed_users"),
                    "occupancy_percentage": s.get("occupancy_percentage"),
                    "crowd_level": s.get("crowd_level"),
                    "confidence": s.get("confidence"),
                    "is_estimate": True,
                    "is_demo_data": s.get("is_demo_data"),
                    "data_available": s.get("data_available"),
                }
            )
        except Exception:
            continue
    return {
        "destinations": results,
        "demo_mode": is_demo_enabled(),
        "label": "Estimated crowd (not exact GPS headcount)",
    }


@router.get("/{destination_id}")
def get_crowd(destination_id: int):
    try:
        summary = estimate_current_crowd(destination_id)
        trends = get_trend_windows(destination_id)
        next_hour = predict_horizon(destination_id, hours_ahead=1)
        return {
            **summary,
            "trends": trends,
            "next_hour_prediction": next_hour,
            "demo_mode": is_demo_enabled(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{destination_id}/history")
def crowd_history(destination_id: int, hours: int = Query(24, ge=1, le=168)):
    rows = get_crowd_history(destination_id, hours=hours)
    return {
        "destination_id": destination_id,
        "hours": hours,
        "snapshots": rows,
        "label": "Historical estimated crowd snapshots",
        "note": "Entries with is_demo=1 are DEMO DATA and are not live measurements.",
    }


@router.get("/{destination_id}/prediction")
def crowd_prediction(destination_id: int, hours_ahead: int = Query(1, ge=1, le=12)):
    try:
        return predict_horizon(destination_id, hours_ahead=hours_ahead)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{destination_id}/slots")
def crowd_slots(destination_id: int, date: Optional[str] = None):
    from datetime import datetime
    slot_date = date or datetime.utcnow().strftime("%Y-%m-%d")
    try:
        slots = get_slots_with_crowd(destination_id, slot_date)
        return {
            "destination_id": destination_id,
            "date": slot_date,
            "slots": slots,
            "label": "Predicted crowd per ticket slot (estimate)",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{destination_id}/zones")
def crowd_zones(destination_id: int):
    zones = compute_zone_crowds(destination_id)
    return {
        "destination_id": destination_id,
        "zones": zones,
        "label": "Zone estimates (aggregated; individuals not shown)",
        "privacy": "Individual tourist locations are never exposed.",
    }


@router.get("/{destination_id}/heatmap")
def crowd_heatmap(destination_id: int):
    """Aggregated zone heatmap — never individual points."""
    zones = compute_zone_crowds(destination_id)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, center_lat, center_lng, radius_m FROM destination_zones WHERE destination_id = ?",
            (destination_id,),
        )
        meta = {z["id"]: dict(z) for z in cursor.fetchall()}
    cells = []
    for z in zones:
        m = meta.get(z["zone_id"], {})
        if m.get("center_lat") is None:
            continue
        cells.append(
            {
                "zone_id": z["zone_id"],
                "name": z["name"],
                "lat": m["center_lat"],
                "lng": m["center_lng"],
                "radius_m": m.get("radius_m") or 150,
                "crowd_level": z["crowd_level"],
                "estimated_crowd": z["estimated_crowd"],
                "occupancy_percentage": z["occupancy_percentage"],
                "is_estimate": True,
            }
        )
    return {
        "destination_id": destination_id,
        "cells": cells,
        "privacy": "Aggregated zones only — no individual locations.",
        "insufficient_data": len(cells) == 0,
    }


@router.get("/{destination_id}/recommend-slots")
def recommend_slots(destination_id: int, date: Optional[str] = None, limit: int = Query(5, ge=1, le=10)):
    from datetime import datetime
    slot_date = date or datetime.utcnow().strftime("%Y-%m-%d")
    ensure_slots_for_date(destination_id, slot_date)
    recs = recommend_less_crowded_slots(destination_id, slot_date, limit=limit)
    return {
        "destination_id": destination_id,
        "date": slot_date,
        "recommendations": recs,
        "label": "Less-crowded slot recommendations (estimates)",
    }


@router.get("/{destination_id}/best-time")
def best_time(destination_id: int, date: Optional[str] = None, limit: int = Query(3, ge=1, le=5)):
    try:
        return best_time_to_visit(destination_id, slot_date=date, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{destination_id}/forecast")
def forecast(destination_id: int):
    try:
        return crowd_forecast(destination_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{destination_id}/snapshot")
def force_snapshot(destination_id: int):
    try:
        return capture_snapshot(destination_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class CrowdConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


crowd_ws_manager = CrowdConnectionManager()


@router.websocket("/ws")
async def crowd_websocket(websocket: WebSocket):
    """Push periodic crowd overview. Clients may also use HTTP polling."""
    await crowd_ws_manager.connect(websocket)
    try:
        while True:
            overview = crowd_overview()
            await websocket.send_json({"type": "crowd_overview", "payload": overview})
            try:
                # Allow client ping / destination subscribe messages without blocking long
                data = await asyncio.wait_for(websocket.receive_text(), timeout=15.0)
                msg = json.loads(data) if data else {}
                if msg.get("type") == "subscribe" and msg.get("destination_id"):
                    detail = estimate_current_crowd(int(msg["destination_id"]))
                    await websocket.send_json({"type": "crowd_detail", "payload": detail})
            except asyncio.TimeoutError:
                continue
    except WebSocketDisconnect:
        crowd_ws_manager.disconnect(websocket)
    except Exception:
        crowd_ws_manager.disconnect(websocket)
