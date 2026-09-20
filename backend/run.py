import os
import sys

# Configure UTF-8 output if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import uvicorn
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    print("=" * 65)
    print(" [SAFE-TOUR AI] TOURIST DESTINATION SAFETY & RISK ASSESSMENT SYSTEM")
    print(" [*] Server starting at: http://127.0.0.1:8000")
    print(" [*] Public Traveler Portal: http://127.0.0.1:8000")
    print(" [*] Authority Admin Portal: http://127.0.0.1:8000/admin")
    print(" [*] Interactive API Docs:  http://127.0.0.1:8000/docs")
    print("=" * 65)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, app_dir=str(BASE_DIR))
