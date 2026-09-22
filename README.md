# SafeTour AI — Tourist Destination Safety and Risk Assessment System

An enterprise-grade, geospatial AI safety platform engineered to evaluate multi-factor risk, empower travelers with real-time risk heatmaps, crowd-sourced hazard feeds, instant emergency SOS response, **Crowd Intelligence**, and **Smart Ticket Booking**.

---

## Key Capabilities

1. **Multi-Factor Risk Assessment Engine** — crime, scam, weather, health, night safety, transport, and **crowd density** (now included in the safety score).
2. **Geospatial Interactive Safety Heatmap (Leaflet.js)**
3. **Live Crowd-Sourced Hazard Reporting** (Ground Pulse)
4. **1-Click SOS Emergency Panic Hub**
5. **Tourism Authority / Admin Console**
6. **Crowd Intelligence & Smart Tickets (v3)**
   - Opt-in GPS presence inside destination geofences
   - Observed users ≠ estimated crowd ≠ predicted crowd
   - Slot-level predicted occupancy and less-crowded recommendations
   - Transactional overbooking prevention
   - Admin capacity / threshold / DEMO MODE controls

---

## Crowd terminology (important)

| Term | Meaning |
|------|---------|
| **Observed users** | Opted-in GPS users currently inside the destination geofence |
| **Booked visitors** | Confirmed ticket holders (signal, not on-site proof) |
| **Estimated crowd** | Weighted estimate from GPS + bookings + history + trend |
| **Predicted crowd** | Forward-looking statistical estimate for a time / slot |
| **Confidence** | Data-quality score (GPS participation, history, freshness) |

GPS does **not** provide an exact headcount. The UI always labels estimates clearly. DEMO MODE data is tagged **DEMO DATA**.

---

## Architecture

```
Browser (Leaflet + vanilla JS)
    │  HTTP + optional WebSocket /api/crowd/ws
    ▼
FastAPI (uvicorn :8000)
    ├── Auth (JWT) · Destinations · Pulse · Incidents · SOS · Admin
    ├── /api/location  (presence pings)
    ├── /api/crowd     (estimates, history, zones, heatmap, WS)
    └── /api/tickets   (slots, book, cancel, recommend)
         ▼
SQLite (WAL)  backend/data/safety_assessment.db
```

### Crowd calculation (v1)

```
estimated_crowd = w_gps * observed
                + w_bookings * booked_signal
                + w_historical * historical_avg(day, hour)
                + w_trend * (history + recent_delta)
```

Weights are configurable via env / per-destination admin fields. Low GPS participation down-weights the GPS term and confidence.

### Prediction (v1 statistical)

Baseline historical average for destination + weekday + hour, adjusted with current estimate, slot bookings (show-up rate), trend, and expected departures. Modular `prediction_engine.py` can later host ML without API changes. No ML is trained on fabricated data.

### Geofencing

Circular radius (default) or optional polygon JSON. Presence stores **hashed anonymous id + destination + last_seen** — not a precise trail.

### Ticket capacity

`BEGIN IMMEDIATE` SQLite transactions; `UPDATE … WHERE remaining >= requested` prevents race overbooking. Cancellations restore capacity.

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Environment (optional)
```bash
copy .env.example .env
```

Set `DEMO_MODE=true` to simulate labeled crowd activity for demos.

### 3. Run the Application
```bash
python backend/run.py
```

- Public Safety Portal: **http://localhost:8000**
- Authority Admin Portal: **http://localhost:8000/admin**
- API Docs: **http://localhost:8000/docs**
- Crowd WebSocket: **ws://localhost:8000/api/crowd/ws**

Frontend is served by FastAPI from `/static` — no separate frontend server.

---

## Crowd / Ticket API (new)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/location/config` | Consent copy + intervals |
| POST | `/api/location/update` | Opt-in presence ping |
| POST | `/api/location/stop` | Leave all geofences |
| GET | `/api/crowd/overview` | Map overview estimates |
| GET | `/api/crowd/{id}` | Live estimate + trend + next-hour prediction |
| GET | `/api/crowd/{id}/history` | Snapshots |
| GET | `/api/crowd/{id}/prediction` | Horizon prediction |
| GET | `/api/crowd/{id}/slots` | Slot predictions |
| GET | `/api/crowd/{id}/zones` | Zone estimates |
| GET | `/api/crowd/{id}/heatmap` | Aggregated zone cells |
| GET | `/api/crowd/{id}/recommend-slots` | Less-crowded slots |
| WS | `/api/crowd/ws` | Push overview / subscribe detail |
| GET | `/api/tickets/{id}/slots` | Bookable slots |
| GET | `/api/tickets/{id}/recommend` | Recommendations |
| POST | `/api/tickets/book` | Book (server-validated) |
| POST | `/api/tickets/{id}/cancel` | Cancel |
| GET | `/api/tickets/booking/{id}` | Booking detail |
| GET | `/api/admin/crowd` | Admin overview |
| PUT | `/api/admin/destinations/{id}/crowd-config` | Capacity / thresholds |
| POST | `/api/admin/demo-mode` | Toggle DEMO MODE |
| POST | `/api/admin/demo-tick` | Advance demo simulation |

---

## Database additions

Additive tables (existing data preserved):

- `visitor_presence`, `destination_zones`, `ticket_slots`, `ticket_bookings`
- `crowd_snapshots`, `crowd_predictions`, `crowd_events`, `app_settings`
- Destination columns: `maximum_capacity`, `comfortable_capacity`, `area_sq_meters`, `geofence_radius_m`, `geofence_polygon`, thresholds, emergency override, estimation weights

---

## Environment variables

See `.env.example`. Important keys:

- `DEMO_MODE` — simulate labeled crowd data
- `VISITOR_TIMEOUT_MINUTES` — inactive GPS timeout
- `LOCATION_UPDATE_INTERVAL` — client ping interval (seconds)
- `WEIGHT_*` — estimation weights
- `WEATHER_API_KEY` — reserved; Open-Meteo currently needs no key
- `JWT_SECRET` — auth signing secret

---

## Testing

```bash
python test_system.py
python test_crowd_system.py
```

Crowd tests cover geofence, presence, estimation scenario, confidence, booking, overbooking, predictions, admin capacity.

---

## How to demo with DEMO MODE

1. Start the server: `python backend/run.py`
2. Open **http://localhost:8000/admin** — login `admin@safetour.gov.in` / `AdminPass#2026`
3. Click **Enable DEMO MODE + bootstrap history**
4. Optionally **Run demo tick**
5. Open the public portal, select a destination — look for the **DEMO DATA** badge on Crowd Intelligence
6. Book a slot / use **Find Less Crowded Time**

Never present DEMO DATA as real live measurements.

---

## Privacy

- Explicit location permission before presence sharing
- Hashed anonymous identifiers
- No public exposure of individual coordinates (zone heatmap only)
- Admin APIs require admin JWT

---

## Tech Stack

- **Backend**: FastAPI, SQLite (WAL), Pydantic, Uvicorn, WebSockets
- **Frontend**: Vanilla JS SPA, Leaflet, glassmorphic CSS
- **Weather**: Open-Meteo (`WeatherService` interface for prediction hooks)

---

## Limitations

- v1 prediction is statistical, not trained ML
- Without opt-in GPS users, estimates rely on bookings/history and confidence drops
- WebSocket may be blocked by some proxies — HTTP polling remains the fallback
- DEMO MODE history is synthetic and labeled `is_demo=1`
