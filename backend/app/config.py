import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path(os.getenv("DATABASE_URL", str(DATA_DIR / "safety_assessment.db")))
if str(DB_PATH).startswith("sqlite:///"):
    DB_PATH = Path(str(DB_PATH).replace("sqlite:///", ""))
STATIC_DIR = BASE_DIR.parent / "frontend"

APP_NAME = "SafeTour Bharat — Indian Tourism Safety & Crowd Intelligence System"
APP_VERSION = "3.0.0"

JWT_SECRET = os.getenv("JWT_SECRET", "safetour-bharat-jwt-secret-mumbai-delhi-2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Crowd / location configuration
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("1", "true", "yes")
VISITOR_TIMEOUT_MINUTES = int(os.getenv("VISITOR_TIMEOUT_MINUTES", "10"))
LOCATION_UPDATE_INTERVAL_SEC = int(os.getenv("LOCATION_UPDATE_INTERVAL", "30"))
CROWD_PREDICTION_INTERVAL_SEC = int(os.getenv("CROWD_PREDICTION_INTERVAL", "60"))
CROWD_SNAPSHOT_INTERVAL_SEC = int(os.getenv("CROWD_SNAPSHOT_INTERVAL", "120"))
DEFAULT_GEOFENCE_RADIUS_M = float(os.getenv("DEFAULT_GEOFENCE_RADIUS_M", "800"))
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")  # optional; Open-Meteo needs no key

# Live Disaster / Risk Intelligence (additive)
GDELT_DOC_API_URL = os.getenv(
    "GDELT_DOC_API_URL",
    "https://api.gdeltproject.org/api/v2/doc/doc",
)
DISASTER_ALERT_API_URL = os.getenv("DISASTER_ALERT_API_URL", "")  # optional CAP/SACHET feed
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")  # reserved; Google News RSS needs no key
DISASTER_POLL_INTERVAL_SEC = int(os.getenv("DISASTER_POLL_INTERVAL_SEC", "600"))  # 10 min
DISASTER_TIMESPAN = os.getenv("DISASTER_TIMESPAN", "24h")
DISASTER_MAX_ARTICLES = int(os.getenv("DISASTER_MAX_ARTICLES", "60"))
DISASTER_EVENT_TTL_HOURS = int(os.getenv("DISASTER_EVENT_TTL_HOURS", "48"))
# Risk score thresholds (0-100)
RISK_LOW_MAX = int(os.getenv("RISK_LOW_MAX", "24"))
RISK_MODERATE_MAX = int(os.getenv("RISK_MODERATE_MAX", "49"))
RISK_HIGH_MAX = int(os.getenv("RISK_HIGH_MAX", "74"))

# Estimation weights (must roughly sum to 1.0 for interpretability)
WEIGHT_OBSERVED_GPS = float(os.getenv("WEIGHT_OBSERVED_GPS", "0.35"))
WEIGHT_BOOKINGS = float(os.getenv("WEIGHT_BOOKINGS", "0.30"))
WEIGHT_HISTORICAL = float(os.getenv("WEIGHT_HISTORICAL", "0.25"))
WEIGHT_TREND = float(os.getenv("WEIGHT_TREND", "0.10"))

# Default crowd level thresholds (occupancy %) — overridable per destination
DEFAULT_THRESHOLDS = {
    "low_max": float(os.getenv("CROWD_LOW_MAX", "60")),
    "moderate_max": float(os.getenv("CROWD_MODERATE_MAX", "75")),
    "high_max": float(os.getenv("CROWD_HIGH_MAX", "90")),
    "very_high_max": float(os.getenv("CROWD_VERY_HIGH_MAX", "100")),
}
