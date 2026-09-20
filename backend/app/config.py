import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "safety_assessment.db"
STATIC_DIR = BASE_DIR.parent / "frontend"

APP_NAME = "SafeTour Bharat — Indian Tourism Safety & Ground Pulse System"
APP_VERSION = "2.0.0"

JWT_SECRET = os.getenv("JWT_SECRET", "safetour-bharat-jwt-secret-mumbai-delhi-2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
