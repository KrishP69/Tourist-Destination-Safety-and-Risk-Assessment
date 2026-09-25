import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import (
    APP_NAME,
    APP_VERSION,
    STATIC_DIR,
    CROWD_SNAPSHOT_INTERVAL_SEC,
    DEMO_MODE,
    DISASTER_POLL_INTERVAL_SEC,
)
from app.seed_data import seed_database
from app.routers import destinations, incidents, emergency, admin, auth, ground_pulse
from app.routers import location, crowd, tickets, risk_events
from app.services.demo_crowd_service import (
    is_demo_enabled,
    set_demo_mode,
    run_demo_tick,
    bootstrap_historical_demo_snapshots,
    seed_destination_crowd_defaults,
)
from app.database import get_db
from app.services.crowd_engine import capture_snapshot
from app.services.disaster_pipeline import run_disaster_pipeline

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Intelligent Safety, Crowd Intelligence & Smart Ticket System for Indian Tourist Destinations. "
        "Crowd figures are estimates (Observed / Estimated / Predicted) — never exact GPS headcounts."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_snapshot_task = None
_disaster_task = None


async def _periodic_crowd_jobs():
    """Periodic snapshots + optional demo tick. Avoids recalculating on every GPS ping."""
    while True:
        try:
            await asyncio.sleep(max(30, CROWD_SNAPSHOT_INTERVAL_SEC))
            if is_demo_enabled():
                await asyncio.to_thread(run_demo_tick)
            else:
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM destinations ORDER BY id ASC LIMIT 20")
                    ids = [r["id"] for r in cursor.fetchall()]
                for dest_id in ids:
                    try:
                        await asyncio.to_thread(capture_snapshot, dest_id)
                    except Exception:
                        continue
        except asyncio.CancelledError:
            break
        except Exception:
            continue


async def _periodic_disaster_jobs():
    """Live disaster / risk intelligence ingest (GDELT + news RSS + optional CAP)."""
    # Initial pass shortly after startup
    try:
        await asyncio.sleep(8)
        await asyncio.to_thread(run_disaster_pipeline)
    except Exception as e:
        print(f"[DisasterIntel] initial pipeline error: {e}")
    while True:
        try:
            await asyncio.sleep(max(120, DISASTER_POLL_INTERVAL_SEC))
            await asyncio.to_thread(run_disaster_pipeline)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[DisasterIntel] pipeline error: {e}")
            continue


@app.on_event("startup")
def on_startup():
    seed_database()
    # Ensure crowd schema defaults exist even when destinations were already seeded
    with get_db() as conn:
        seed_destination_crowd_defaults(conn.cursor())
    if DEMO_MODE:
        set_demo_mode(True)
        bootstrap_historical_demo_snapshots(days=5)
        run_demo_tick()


@app.on_event("startup")
async def on_startup_async():
    global _snapshot_task, _disaster_task
    _snapshot_task = asyncio.create_task(_periodic_crowd_jobs())
    _disaster_task = asyncio.create_task(_periodic_disaster_jobs())


@app.on_event("shutdown")
async def on_shutdown():
    global _snapshot_task, _disaster_task
    for task in (_snapshot_task, _disaster_task):
        if task:
            task.cancel()


# Register Routers
app.include_router(auth.router)
app.include_router(ground_pulse.router)
app.include_router(destinations.router)
app.include_router(incidents.router)
app.include_router(emergency.router)
app.include_router(admin.router)
app.include_router(location.router)
app.include_router(crowd.router)
app.include_router(tickets.router)
app.include_router(risk_events.router)


@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "online",
        "app": APP_NAME,
        "version": APP_VERSION,
        "coverage": "Bharat (India Exclusive)",
        "demo_mode": is_demo_enabled(),
        "crowd_terminology": {
            "observed_users": "Opted-in GPS users inside geofence",
            "estimated_crowd": "Weighted estimate from available signals",
            "predicted_crowd": "Forward-looking statistical estimate",
        },
        "live_risk_intelligence": True,
    }


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def serve_frontend_index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/admin")
    def serve_frontend_admin():
        return FileResponse(STATIC_DIR / "admin.html")

    @app.get("/responder")
    def serve_frontend_responder():
        return FileResponse(STATIC_DIR / "responder.html")

    @app.get("/emergency-monitor")
    def serve_frontend_emergency_monitor():
        return FileResponse(STATIC_DIR / "responder.html")
