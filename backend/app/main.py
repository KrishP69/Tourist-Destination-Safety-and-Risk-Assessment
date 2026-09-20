import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import APP_NAME, APP_VERSION, STATIC_DIR
from app.seed_data import seed_database
from app.routers import destinations, incidents, emergency, admin, auth, ground_pulse

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Intelligent Safety & Risk Assessment System for Indian Tourist Destinations with Ground Pulse & Geofencing."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event: Initialize & seed DB
@app.on_event("startup")
def on_startup():
    seed_database()

# Register Routers
app.include_router(auth.router)
app.include_router(ground_pulse.router)
app.include_router(destinations.router)
app.include_router(incidents.router)
app.include_router(emergency.router)
app.include_router(admin.router)

# Health Check
@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "online",
        "app": APP_NAME,
        "version": APP_VERSION,
        "coverage": "Bharat (India Exclusive)"
    }

# Mount static frontend
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
