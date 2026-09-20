# SafeTour AI — Tourist Destination Safety and Risk Assessment System

An enterprise-grade, geospatial AI safety platform engineered to evaluate multi-factor risk, empower travelers with real-time risk heatmaps, crowd-sourced hazard feeds, and instant emergency SOS response.

---

## 🌟 Key Capabilities

1. **Multi-Factor Risk Assessment Engine**:
   - Computes dynamic safety index (0–100) combining crime rate, tourist scam density, natural hazard/weather risks, health sanitation, nighttime street safety, and emergency response latency.
   - Categorizes destinations into 4 distinct risk tiers:
     - 🟢 **Low Risk (Safe)** (80–100)
     - 🟡 **Moderate Risk** (60–79)
     - 🟠 **High Caution** (40–59)
     - 🔴 **Severe Risk** (<40)

2. **Geospatial Interactive Safety Heatmap (Leaflet.js)**:
   - High-contrast DarkMatter map tiles with color-coded safety radius rings.
   - Pulsing radar marker pins with live safety score badges.
   - Interactive layer switches for Safety Zones, Live Hazard Incidents, and 24/7 Emergency Medical / Police Centers.

3. **Live Crowd-Sourced Hazard Reporting**:
   - Community-driven hazard reports (Pickpocketing, Tourist Scams, Route Blockages, Extreme Weather, Harassment).
   - Upvote verification mechanism with live community ticker.

4. **1-Click SOS Emergency Panic Hub**:
   - Emergency distress beacon with GPS coordinate telemetry acquisition.
   - 5-second automatic countdown with cancel safety switch.
   - Automatic identification and routing to the nearest 4 emergency response facilities (Hospital, Tourist Police, Embassy).
   - Universal quick-dial triggers (112, 1364).

5. **Tourism Authority / Admin Console**:
   - Broadcast official travel advisories and warning notices.
   - Dynamic real-time risk coefficient calibration sliders.
   - Incident moderation queue (Verify, Resolve, Dismiss).

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Run the Application
```bash
python backend/run.py
```

- Public Safety Portal: **`http://localhost:8000`**
- Authority Admin Portal: **`http://localhost:8000/admin`**
- Interactive API Documentation: **`http://localhost:8000/docs`**

---

## 🏗️ Architecture & Tech Stack

- **Backend**: FastAPI (Python 3.10+), SQLite (WAL mode with foreign keys), Pydantic v2, Uvicorn
- **Frontend**: Vanilla JavaScript (SPA), HTML5 Semantic markup, Modern Glassmorphic CSS Design System
- **Mapping & GIS**: Leaflet.js, OpenStreetMap, CartoDB DarkMatter
- **Icons & Typography**: FontAwesome 6, Google Fonts (Outfit & Inter)
