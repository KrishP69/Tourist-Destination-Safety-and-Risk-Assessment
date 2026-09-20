import sqlite3
import json
from contextlib import contextmanager
from app.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'tourist' CHECK(role IN ('tourist', 'verified_guide', 'admin')),
            reputation_xp INTEGER DEFAULT 100,
            home_city TEXT DEFAULT 'India',
            avatar_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 2. Destinations Table (Exclusive to India)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            state TEXT NOT NULL,
            region TEXT NOT NULL, -- North India, South India, West India, East & North-East India, Central India
            country TEXT NOT NULL DEFAULT 'India',
            category TEXT NOT NULL DEFAULT 'Heritage & Forts', -- Mountain & Adventure, Heritage & Forts, Beach & Coastal, Spiritual & Sacred, Wildlife & Nature, Urban & Culture
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            overall_safety_score INTEGER NOT NULL DEFAULT 85,
            risk_tier TEXT NOT NULL DEFAULT 'Low Risk (Safe)',
            description TEXT,
            image_url TEXT,
            best_visit_time TEXT,
            dress_code_etiquette TEXT,
            opening_time TEXT DEFAULT '06:00',
            closing_time TEXT DEFAULT '18:30',
            weekly_off_day TEXT DEFAULT 'None',
            peak_rush_hours TEXT DEFAULT '11:00 AM - 03:30 PM',
            entry_fee_domestic TEXT DEFAULT 'Free',
            entry_fee_foreign TEXT DEFAULT 'Free',
            booking_portal_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 3. Risk Metrics Breakdown
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id INTEGER NOT NULL UNIQUE,
            crime_index REAL NOT NULL DEFAULT 20.0,
            scam_index REAL NOT NULL DEFAULT 25.0,
            weather_risk REAL NOT NULL DEFAULT 15.0,
            health_risk REAL NOT NULL DEFAULT 15.0,
            night_safety REAL NOT NULL DEFAULT 80.0,
            crowd_density REAL NOT NULL DEFAULT 50.0,
            transport_safety REAL NOT NULL DEFAULT 85.0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (destination_id) REFERENCES destinations (id) ON DELETE CASCADE
        )
        """)

        # 4. On-Site MCQ Ground Pulse Votes (Crowd Truth & Field Verification)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ground_pulse_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id INTEGER NOT NULL,
            user_id INTEGER,
            user_name TEXT NOT NULL,
            user_city TEXT DEFAULT 'Traveler',
            is_onsite_verified INTEGER DEFAULT 1,
            distance_km REAL NOT NULL DEFAULT 0.0,
            crowd_rush TEXT NOT NULL, -- Peaceful, Moderate, Heavy, Extreme
            visit_recommendation TEXT NOT NULL, -- Recommended, Neutral, Avoid
            safety_vibe TEXT NOT NULL, -- Very Safe, Standard Vigilance, Caution Needed
            ground_weather TEXT NOT NULL, -- Pleasant, Raining/Wet, Heavy Fog, Cold/Chilly, Sweltering Heat
            clean_sanitation TEXT DEFAULT 'Good', -- Good, Average, Poor
            user_comment TEXT,
            helpful_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (destination_id) REFERENCES destinations (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
        """)

        # 5. Incidents Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'Medium',
            location_name TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            description TEXT NOT NULL,
            reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            upvotes INTEGER DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'Active',
            FOREIGN KEY (destination_id) REFERENCES destinations (id) ON DELETE CASCADE
        )
        """)

        # 6. Emergency Contacts & Facilities
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id INTEGER NOT NULL,
            facility_name TEXT NOT NULL,
            facility_type TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT,
            lat REAL,
            lng REAL,
            is_24_7 INTEGER DEFAULT 1,
            FOREIGN KEY (destination_id) REFERENCES destinations (id) ON DELETE CASCADE
        )
        """)

        # 7. Official Safety Advisories
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS safety_advisories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            alert_level TEXT NOT NULL,
            summary TEXT NOT NULL,
            issued_by TEXT NOT NULL DEFAULT 'Ministry of Tourism / State Police',
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (destination_id) REFERENCES destinations (id) ON DELETE CASCADE
        )
        """)

        # 8. Safety Tips & Checklists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS safety_tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id INTEGER NOT NULL,
            tip_text TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'General',
            FOREIGN KEY (destination_id) REFERENCES destinations (id) ON DELETE CASCADE
        )
        """)

        # 9. User Checkins & Reputation Log
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            destination_id INTEGER NOT NULL,
            checked_in_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (destination_id) REFERENCES destinations (id) ON DELETE CASCADE
        )
        """)

        # 10. Emergency Unit Dispatches (Police PCR, Fire Brigade, Ambulance, NDRF)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_dispatches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            agency_type TEXT NOT NULL, -- Police, Fire & Rescue, Ambulance, NDRF
            unit_callsign TEXT NOT NULL, -- PCR-DELHI-04, FIRE-TENDER-02, ALS-AMB-108
            contact_phone TEXT DEFAULT '112',
            dispatch_status TEXT NOT NULL DEFAULT 'DISPATCHED', -- DISPATCHED, EN_ROUTE, ON_SCENE, RESOLVED
            eta_minutes INTEGER DEFAULT 5,
            responder_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (incident_id) REFERENCES incidents (id) ON DELETE CASCADE
        )
        """)

        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dest_state ON destinations(state)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dest_region ON destinations(region)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pulse_dest ON ground_pulse_votes(destination_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pulse_user ON ground_pulse_votes(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_dest ON incidents(destination_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emergency_dest ON emergency_contacts(destination_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dispatches_incident ON emergency_dispatches(incident_id)")
