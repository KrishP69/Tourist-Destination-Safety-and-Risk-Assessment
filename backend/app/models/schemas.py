from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any

# --- Auth Schemas ---
class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=60)
    email: EmailStr
    username: Optional[str] = None
    password: str = Field(..., min_length=6, max_length=100)
    home_city: Optional[str] = "India"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    username: str
    role: str = "tourist"
    reputation_xp: int = 100
    reputation_badge: str = "Verified Explorer"
    home_city: Optional[str] = "India"
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# --- Ground Pulse MCQ Schemas ---
class PulseVoteCreate(BaseModel):
    destination_id: int
    user_lat: float
    user_lon: float
    crowd_rush: str = Field(..., description="Peaceful, Moderate, Heavy, Extreme")
    visit_recommendation: str = Field(..., description="Recommended, Neutral, Avoid")
    safety_vibe: str = Field(..., description="Very Safe, Standard Vigilance, Caution Needed")
    ground_weather: str = Field(..., description="Pleasant, Raining/Wet, Heavy Fog, Cold/Chilly, Sweltering Heat")
    clean_sanitation: Optional[str] = Field("Good", description="Good, Average, Poor")
    user_comment: Optional[str] = Field(None, max_length=500)
    is_simulated_override: Optional[bool] = False

class PulseVoteOut(BaseModel):
    id: int
    destination_id: int
    user_name: str
    user_badge: str
    user_city: str
    crowd_rush: str
    visit_recommendation: str
    safety_vibe: str
    ground_weather: str
    clean_sanitation: str
    user_comment: Optional[str]
    distance_km: float
    is_onsite_verified: bool
    helpful_count: int = 1
    created_at: str

class ConsensusStats(BaseModel):
    destination_id: int
    total_votes: int
    recommendation_breakdown: Dict[str, int]
    recommend_percentage: float
    crowd_consensus: str
    safety_consensus: str
    weather_consensus: str
    cleanliness_consensus: str
    recent_pulse_feed: List[PulseVoteOut]

# --- Destination Schemas ---
class DestinationOut(BaseModel):
    id: int
    name: str
    state: str
    region: str
    country: str = "India"
    category: str
    lat: float
    lng: float
    overall_safety_score: int
    risk_tier: str
    description: Optional[str]
    image_url: Optional[str] = None
    best_visit_time: Optional[str]
    dress_code_etiquette: Optional[str]
    opening_time: Optional[str] = "06:00"
    closing_time: Optional[str] = "18:30"
    weekly_off_day: Optional[str] = "None"
    peak_rush_hours: Optional[str] = "11:00 AM - 03:30 PM"
    entry_fee_domestic: Optional[str] = "Free"
    entry_fee_foreign: Optional[str] = "Free"
    booking_portal_url: Optional[str] = ""
    is_currently_open: Optional[bool] = True
    open_status_text: Optional[str] = "Open Now"
    nearby_incidents: Optional[List[Dict[str, Any]]] = []
    distance_km: Optional[float] = None
    consensus: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

# --- Incident Schemas ---
class IncidentCreate(BaseModel):
    destination_id: int
    title: str
    category: str
    severity: str = "Medium"
    location_name: str
    lat: Optional[float] = 0.0
    lng: Optional[float] = 0.0
    description: str

# --- Emergency & SOS Schemas ---
class SOSRequest(BaseModel):
    lat: float
    lng: float
    destination_id: Optional[int] = None
    emergency_type: Optional[str] = "General Emergency"
    user_note: Optional[str] = None

# --- Admin Schemas ---
class AdvisoryCreate(BaseModel):
    destination_id: int
    title: str
    alert_level: str = "Advisory"
    summary: str
    issued_by: Optional[str] = "Ministry of Tourism / State Police"

class MetricUpdate(BaseModel):
    crime_index: Optional[float] = None
    scam_index: Optional[float] = None
    weather_risk: Optional[float] = None
    health_risk: Optional[float] = None
    night_safety: Optional[float] = None
    crowd_density: Optional[float] = None
    transport_safety: Optional[float] = None

class AdminDestinationCreate(BaseModel):
    name: str
    state: str
    region: str
    category: str = "Heritage & Forts"
    lat: float
    lng: float
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    best_visit_time: Optional[str] = "October to March"
    dress_code_etiquette: Optional[str] = "Modest attire recommended."
    opening_time: Optional[str] = "06:00"
    closing_time: Optional[str] = "18:30"
    weekly_off_day: Optional[str] = "None"
    peak_rush_hours: Optional[str] = "10:30 AM - 03:00 PM"
    entry_fee_domestic: Optional[str] = "Rs 50"
    entry_fee_foreign: Optional[str] = "Rs 500"
    booking_portal_url: Optional[str] = ""
    # Risk baselines
    crime_index: Optional[float] = 20.0
    scam_index: Optional[float] = 25.0
    weather_risk: Optional[float] = 15.0
    night_safety: Optional[float] = 80.0
    crowd_density: Optional[float] = 50.0
    # Primary emergency facility
    emergency_facility_name: Optional[str] = "State Tourist Police Desk"
    emergency_facility_type: Optional[str] = "Police"
    emergency_facility_phone: Optional[str] = "112"

class DispatchCreate(BaseModel):
    incident_id: int
    agency_type: str = "Police" # Police, Fire & Rescue, Ambulance, NDRF
    unit_callsign: str
    contact_phone: Optional[str] = "112"
    eta_minutes: Optional[int] = 5
    responder_notes: Optional[str] = None

class DispatchStatusUpdate(BaseModel):
    status: str # DISPATCHED, EN_ROUTE, ON_SCENE, RESOLVED
    notes: Optional[str] = None

