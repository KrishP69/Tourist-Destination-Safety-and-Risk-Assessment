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
    port = int(os.environ.get("PORT", 8000))
    is_prod = bool(os.environ.get("PORT"))
    print("=" * 65)
    print(" [SAFE-TOUR AI] TOURIST DESTINATION SAFETY & RISK ASSESSMENT SYSTEM")
    print(f" [*] Server starting on port: {port}")
    print("=" * 65)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=not is_prod, app_dir=str(BASE_DIR))

