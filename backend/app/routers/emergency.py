import math
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from app.database import get_db
from app.auth import verify_password, create_access_token, decode_access_token, get_optional_user, get_current_user
from app.models.schemas import SOSRequest, DispatchCreate, DispatchStatusUpdate

router = APIRouter(prefix="/api/emergency", tags=["Emergency"])

class ResponderLoginPayload(BaseModel):
    login_id: str
    password: str
    agency: Optional[str] = "All"

class ResponderBroadcastPayload(BaseModel):
    destination_id: int
    title: str
    alert_level: str = "Warning"
    summary: str
    issued_by: Optional[str] = None

class FacilityCreatePayload(BaseModel):
    destination_id: int
    facility_name: str
    facility_type: str = "Police"
    phone: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

def haversine_distance(lat1, lon1, lat2, lon2):
    # Radius of earth in km
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

@router.post("/sos")
def trigger_sos(req: SOSRequest):
    """Simulate instant SOS panic dispatch, find nearest assistance point"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Look up all emergency contacts
        cursor.execute("""
        SELECT e.*, d.name as destination_name, d.country
        FROM emergency_contacts e
        JOIN destinations d ON e.destination_id = d.id
        """)
        facilities = [dict(r) for r in cursor.fetchall()]

        # Compute distance to each facility if coords exist
        for fac in facilities:
            if fac.get("lat") and fac.get("lng"):
                fac["distance_km"] = haversine_distance(req.lat, req.lng, fac["lat"], fac["lng"])
            else:
                fac["distance_km"] = 9999.0

        facilities.sort(key=lambda x: x["distance_km"])
        nearest = facilities[:4]

        # Log emergency dispatch incident
        target_dest_id = req.destination_id or (nearest[0]["destination_id"] if nearest else 1)
        user_notes = req.user_note or "Immediate emergency assistance requested via traveler SOS beacon."
        cursor.execute("""
        INSERT INTO incidents (destination_id, title, category, severity, location_name, lat, lng, description, upvotes, status)
        VALUES (?, '🚨 EMERGENCY SOS BEACON TRIGGERED', ?, 'Critical', 'Traveler GPS Coordinates', ?, ?, ?, 10, 'Active')
        """, (target_dest_id, req.emergency_type or "Medical Emergency", req.lat, req.lng, f"Emergency alert: {req.emergency_type}. Details: {user_notes}"))
        inc_id = cursor.lastrowid

        # Auto-create initial dispatch alert
        cursor.execute("""
            INSERT INTO emergency_dispatches (incident_id, agency_type, unit_callsign, contact_phone, dispatch_status, eta_minutes, responder_notes)
            VALUES (?, 'Police', 'PCR-RAPID-INTERCEPT-112', '112', 'DISPATCHED', 5, 'Incoming SOS alert logged. Nearest patrol squad assigned.')
        """, (inc_id,))

        return {
            "sos_active": True,
            "incident_id": inc_id,
            "message": "Emergency SOS broadcasted. Police, Fire, and Medical Command Centers notified.",
            "nearest_facilities": nearest,
            "universal_emergency_numbers": {
                "National Emergency Support": "112",
                "Tourist Police Hotline": "1364 / 112",
                "Fire & Rescue": "101",
                "Ambulance / Medical": "108"
            }
        }

@router.get("/facilities")
def get_all_facilities(destination_id: Optional[int] = None):
    with get_db() as conn:
        cursor = conn.cursor()
        if destination_id:
            cursor.execute("""
            SELECT e.*, d.name as destination_name 
            FROM emergency_contacts e
            JOIN destinations d ON e.destination_id = d.id
            WHERE e.destination_id = ?
            """, (destination_id,))
        else:
            cursor.execute("""
            SELECT e.*, d.name as destination_name 
            FROM emergency_contacts e
            JOIN destinations d ON e.destination_id = d.id
            """)
        return [dict(r) for r in cursor.fetchall()]

# --- Dedicated Responder Command Center Endpoints ---

@router.get("/responder/feed")
def get_responder_feed(agency: Optional[str] = None):
    """Fetch live queue of active emergencies and SOS beacons for Police, Fire, Ambulance & NDRF"""
    with get_db() as conn:
        cursor = conn.cursor()
        query = """
        SELECT 
            i.id as incident_id, i.destination_id, i.title, i.category, i.severity, 
            i.location_name, i.lat, i.lng, i.description, i.reported_at, i.status as incident_status,
            d.name as destination_name, d.state as state_name,
            ed.id as dispatch_id, ed.agency_type, ed.unit_callsign, ed.contact_phone,
            ed.dispatch_status, ed.eta_minutes, ed.responder_notes, ed.updated_at as dispatch_updated_at
        FROM incidents i
        LEFT JOIN destinations d ON i.destination_id = d.id
        LEFT JOIN emergency_dispatches ed ON i.id = ed.incident_id
        WHERE i.status IN ('Active', 'In Progress', 'Verified')
        """
        params = []
        if agency and agency != "All":
            query += " AND (ed.agency_type = ? OR ed.agency_type IS NULL)"
            params.append(agency)
        
        query += " ORDER BY CASE i.severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END, i.reported_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@router.post("/responder/dispatch")
def dispatch_response_unit(payload: DispatchCreate):
    """Assign an emergency response unit (Police, Fire Brigade, ALS Ambulance, NDRF) to an incident"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidents WHERE id = ?", (payload.incident_id,))
        inc = cursor.fetchone()
        if not inc:
            raise HTTPException(status_code=404, detail="Incident not found")

        cursor.execute("SELECT id FROM emergency_dispatches WHERE incident_id = ?", (payload.incident_id,))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
                UPDATE emergency_dispatches
                SET agency_type = ?, unit_callsign = ?, contact_phone = ?, dispatch_status = 'DISPATCHED', eta_minutes = ?, responder_notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE incident_id = ?
            """, (payload.agency_type, payload.unit_callsign, payload.contact_phone or "112", payload.eta_minutes or 5, payload.responder_notes or f"Dispatched {payload.unit_callsign} to scene.", payload.incident_id))
            disp_id = existing["id"]
        else:
            cursor.execute("""
                INSERT INTO emergency_dispatches (incident_id, agency_type, unit_callsign, contact_phone, dispatch_status, eta_minutes, responder_notes)
                VALUES (?, ?, ?, ?, 'DISPATCHED', ?, ?)
            """, (payload.incident_id, payload.agency_type, payload.unit_callsign, payload.contact_phone or "112", payload.eta_minutes or 5, payload.responder_notes or f"Dispatched {payload.unit_callsign} to scene."))
            disp_id = cursor.lastrowid

        cursor.execute("UPDATE incidents SET status = 'In Progress' WHERE id = ?", (payload.incident_id,))
        return {
            "success": True,
            "dispatch_id": disp_id,
            "incident_id": payload.incident_id,
            "agency_type": payload.agency_type,
            "unit_callsign": payload.unit_callsign,
            "dispatch_status": "DISPATCHED",
            "eta_minutes": payload.eta_minutes or 5,
            "message": f"Unit {payload.unit_callsign} ({payload.agency_type}) successfully dispatched!"
        }

@router.patch("/responder/dispatch/{dispatch_id}/status")
def update_dispatch_status(dispatch_id: int, payload: DispatchStatusUpdate):
    """Transition dispatch state: DISPATCHED -> EN_ROUTE -> ON_SCENE -> RESOLVED"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emergency_dispatches WHERE id = ?", (dispatch_id,))
        disp = cursor.fetchone()
        if not disp:
            raise HTTPException(status_code=404, detail="Dispatch record not found")

        valid_statuses = ["DISPATCHED", "EN_ROUTE", "ON_SCENE", "RESOLVED"]
        status_val = payload.status.upper()
        if status_val not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid dispatch status")

        notes = payload.notes or disp["responder_notes"]
        eta = 0 if status_val in ("ON_SCENE", "RESOLVED") else disp["eta_minutes"]
        cursor.execute("""
            UPDATE emergency_dispatches
            SET dispatch_status = ?, eta_minutes = ?, responder_notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status_val, eta, notes, dispatch_id))

        if status_val == "RESOLVED":
            cursor.execute("UPDATE incidents SET status = 'Resolved' WHERE id = ?", (disp["incident_id"],))

        return {
            "success": True,
            "dispatch_id": dispatch_id,
            "dispatch_status": status_val,
            "eta_minutes": eta,
            "message": f"Dispatch status updated to {status_val}."
        }

@router.get("/responder/kpis")
def get_responder_kpis():
    """Real-time emergency operational metrics"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM incidents WHERE status IN ('Active', 'In Progress') AND severity IN ('Critical', 'High')")
        active_critical = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM emergency_dispatches WHERE dispatch_status IN ('DISPATCHED', 'EN_ROUTE', 'ON_SCENE')")
        active_units = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(eta_minutes) FROM emergency_dispatches WHERE dispatch_status IN ('DISPATCHED', 'EN_ROUTE')")
        avg_eta = cursor.fetchone()[0]
        avg_eta_val = round(avg_eta, 1) if avg_eta else 4.5

        cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = 'Resolved'")
        resolved_today = cursor.fetchone()[0]

        return {
            "active_distress_calls": active_critical,
            "active_units_deployed": active_units,
            "average_response_eta_minutes": avg_eta_val,
            "incidents_resolved": resolved_today
        }

# --- Official Department Responder Authentication & Body Management ---

DEPARTMENT_METADATA = {
    "police_112": {"agency": "Police", "callsign": "PCR-COMMAND-112", "dept_name": "Delhi Police & All-India Tourist Police Wing (112)", "clearance": "TIER-1 CHIEF DISPATCHER"},
    "medical_108": {"agency": "Ambulance", "callsign": "ALS-TRAUMA-108", "dept_name": "Emergency Medical Services & Trauma Hospitals (108)", "clearance": "TIER-1 MEDICAL DIRECTOR"},
    "fire_101": {"agency": "Fire & Rescue", "callsign": "FIRE-TACTICAL-101", "dept_name": "National Fire & Heavy Rescue Service (101)", "clearance": "TIER-1 CHIEF FIRE MARSHAL"},
    "ndrf_command": {"agency": "NDRF", "callsign": "NDRF-DISASTER-HQ", "dept_name": "National Disaster Response Force (NDRF)", "clearance": "COMMANDANT DISASTER CLEARANCE"},
    "eoc_commander": {"agency": "All", "callsign": "CENTRAL-OPS-COMMAND", "dept_name": "Unified Multi-Agency Emergency Operations Body", "clearance": "DIRECTOR GENERAL - ALL DEPARTMENTS"},
    "safetour_admin": {"agency": "All", "callsign": "CHIEF-SAFETY-OFFICER", "dept_name": "Ministry of Tourism & Public Safety Command", "clearance": "SUPREME ADMINISTRATIVE ACCESS"}
}

@router.post("/responder/login")
def responder_officer_login(payload: ResponderLoginPayload):
    """Authenticate authorized Department Officer (Police, Fire, Medical, NDRF, Unified Command)"""
    login_str = payload.login_id.strip()
    pwd = payload.password.strip()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? OR username = ?", (login_str, login_str))
        user = cursor.fetchone()
        
        if not user or not verify_password(pwd, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid Officer ID, Badge Credentials, or Access Key.")

        # Require administrative or officer privileges
        if user["role"] not in ("admin", "verified_guide"):
            raise HTTPException(status_code=403, detail="Access Denied: Standard traveler accounts cannot access the Departmental Command Portal.")

        uname = user["username"]
        meta = DEPARTMENT_METADATA.get(uname, {
            "agency": payload.agency if payload.agency != "All" else "All",
            "callsign": f"OFFICER-{uname[:6].upper()}",
            "dept_name": "Emergency Services Operations Unit",
            "clearance": "FIELD COMMANDER"
        })

        token_data = {
            "sub": str(user["id"]),
            "role": user["role"],
            "agency": meta["agency"],
            "callsign": meta["callsign"],
            "full_name": user["full_name"],
            "dept_name": meta["dept_name"]
        }
        token = create_access_token(token_data)

        return {
            "success": True,
            "access_token": token,
            "token_type": "bearer",
            "officer": {
                "id": user["id"],
                "full_name": user["full_name"],
                "username": user["username"],
                "email": user["email"],
                "agency": meta["agency"],
                "callsign": meta["callsign"],
                "department": meta["dept_name"],
                "clearance_level": meta["clearance"]
            },
            "message": f"Welcome Officer {user['full_name']}. Terminal authenticated for {meta['dept_name']}."
        }

@router.get("/responder/me")
def get_current_responder_profile(authorization: Optional[str] = Header(None)):
    """Verify active Department Officer session"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Officer authentication required.")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Session expired or invalid credentials.")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, username, role FROM users WHERE id = ?", (int(payload["sub"]),))
        user = cursor.fetchone()
        if not user or user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Officer authorization revoked.")

        uname = user["username"]
        meta = DEPARTMENT_METADATA.get(uname, {
            "agency": payload.get("agency", "All"),
            "callsign": payload.get("callsign", "OFFICER"),
            "dept_name": payload.get("dept_name", "Emergency Operations Unit"),
            "clearance": "OPERATIONAL"
        })

        return {
            "authenticated": True,
            "officer": {
                "id": user["id"],
                "full_name": user["full_name"],
                "username": user["username"],
                "email": user["email"],
                "agency": meta["agency"],
                "callsign": meta["callsign"],
                "department": meta["dept_name"],
                "clearance_level": meta["clearance"]
            }
        }

@router.post("/responder/broadcast-advisory")
def broadcast_department_advisory(payload: ResponderBroadcastPayload, authorization: Optional[str] = Header(None)):
    """Broadcast an official Department Advisory to the public portal and field networks"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO safety_advisories (destination_id, title, alert_level, summary, issued_by, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (payload.destination_id, payload.title, payload.alert_level, payload.summary, payload.issued_by or "Emergency Services Departmental Command"))
        adv_id = cursor.lastrowid

        return {
            "success": True,
            "advisory_id": adv_id,
            "message": f"Official Advisory '{payload.title}' successfully broadcast to all public travelers and police logs."
        }

@router.post("/facilities/register")
def register_emergency_facility(payload: FacilityCreatePayload, authorization: Optional[str] = Header(None)):
    """Add a new Police Station, Hospital, or Emergency Facility to the network"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emergency_contacts (destination_id, facility_name, facility_type, phone, address, lat, lng, is_24_7)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (payload.destination_id, payload.facility_name, payload.facility_type, payload.phone, payload.address, payload.lat, payload.lng))
        fac_id = cursor.lastrowid

        return {
            "success": True,
            "facility_id": fac_id,
            "message": f"New {payload.facility_type} station '{payload.facility_name}' successfully added to the National Emergency Directory."
        }
