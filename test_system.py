import os
import sys
import unittest
import json

# Ensure python path includes project files
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.database import init_db, get_db
from app.seed_data import seed_database
from app.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.routers.ground_pulse import calculate_haversine_distance, calculate_badge
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSafeTourBharatSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n==========================================")
        print("  Running SafeTour Bharat Verification Suite  ")
        print("==========================================")
        seed_database(force_refresh=True)

    def test_01_destinations_loaded(self):
        """Verify India-exclusive database has all iconic destinations loaded."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM destinations")
            count = cursor.fetchone()["count"]
            self.assertGreaterEqual(count, 20, f"Expected >= 20 Indian destinations, found {count}")
            print(f"  [PASS] 20+ Iconic Indian destinations initialized (Found {count})")

    def test_02_auth_bcrypt_and_jwt(self):
        """Verify password hashing with Bcrypt rounds=12 and PyJWT token generation."""
        password = "SecureTravelerPass#2026"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

        token = create_access_token({"sub": "42", "email": "test@traveler.in"})
        decoded = decode_access_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], "42")
        print("  [PASS] Bcrypt password hashing & JWT token generation verified")

    def test_03_auth_api_register_and_login(self):
        """Test API endpoints for traveler registration and sign-in."""
        email = f"explorer_test_{int(os.getpid())}@traveler.in"
        reg_payload = {
            "full_name": "Test Explorer",
            "email": email,
            "password": "Password@123",
            "home_city": "Jaipur"
        }
        res = client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res.status_code, 201, res.text)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["full_name"], "Test Explorer")
        self.assertEqual(data["user"]["reputation_xp"], 100)

        # Test login
        login_res = client.post("/api/auth/login", json={"email": email, "password": "Password@123"})
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.json()
        self.assertIn("access_token", login_data)
        print("  [PASS] Traveler registration & login endpoints functional")

    def test_04_haversine_geofencing_math(self):
        """Verify Haversine distance calculations and 25km geofence boundary."""
        # Delhi Rashtrapati Bhavan (28.6143, 77.1994) to Taj Mahal Agra (27.1751, 78.0421) ~ 180 km
        dist_agra = calculate_haversine_distance(28.6143, 77.1994, 27.1751, 78.0421)
        self.assertGreater(dist_agra, 150.0)
        self.assertLess(dist_agra, 220.0)

        # Same spot distance ~ 0 km (within 25km geofence)
        dist_onsite = calculate_haversine_distance(27.1751, 78.0421, 27.1760, 78.0430)
        self.assertLess(dist_onsite, 1.0)
        print(f"  [PASS] Haversine geofence calculation accurate (Delhi-Agra: {dist_agra}km, On-Site: {dist_onsite}km)")

    def test_05_ground_pulse_geofence_and_voting(self):
        """Test on-site Ground Pulse voting, XP reward, and geofence restriction."""
        # 1. Login demo user Arjun
        login_res = client.post("/api/auth/login", json={"email": "arjun@traveler.in", "password": "Traveler@123"})
        self.assertEqual(login_res.status_code, 200)
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get Taj Mahal ID
        dest_res = client.get("/api/destinations?search=Taj Mahal")
        self.assertEqual(dest_res.status_code, 200)
        dests = dest_res.json()
        taj_id = dests[0]["id"]
        taj_lat = dests[0]["lat"]
        taj_lng = dests[0]["lng"]

        # 3. Attempt vote from far away (Delhi, ~180 km away) WITHOUT override -> Should be 403 Forbidden
        far_vote_payload = {
            "destination_id": taj_id,
            "user_lat": 28.6143,
            "user_lon": 77.1994,
            "crowd_rush": "Heavy",
            "visit_recommendation": "Recommended",
            "safety_vibe": "Very Safe",
            "ground_weather": "Pleasant",
            "clean_sanitation": "Good",
            "user_comment": "Far away test comment",
            "is_simulated_override": False
        }
        far_res = client.post("/api/pulse/vote", json=far_vote_payload, headers=headers)
        self.assertEqual(far_res.status_code, 403, "Should reject vote when > 25km away without simulator override")

        # 4. Attempt vote standing right on-site at Taj Mahal (0.2 km away) -> Should SUCCEED with +50 XP
        onsite_vote_payload = {
            "destination_id": taj_id,
            "user_lat": taj_lat + 0.001,
            "user_lon": taj_lng + 0.001,
            "crowd_rush": "Moderate",
            "visit_recommendation": "Recommended",
            "safety_vibe": "Very Safe",
            "ground_weather": "Pleasant",
            "clean_sanitation": "Good",
            "user_comment": "Live test from East Gate! Queues moving smoothly.",
            "is_simulated_override": False
        }
        vote_res = client.post("/api/pulse/vote", json=onsite_vote_payload, headers=headers)
        self.assertEqual(vote_res.status_code, 201, vote_res.text)
        vote_data = vote_res.json()
        self.assertTrue(vote_data["success"])
        self.assertEqual(vote_data["awarded_xp"], 50)
        self.assertTrue(vote_data["is_onsite_verified"])
        print("  [PASS] Geofence rejection (>25km) and on-site vote verification (<25km +50 XP) verified")

    def test_06_pulse_consensus_aggregation(self):
        """Verify dynamic calculation of recommendation %, crowd consensus, and review feed."""
        dest_res = client.get("/api/destinations?search=Taj Mahal")
        taj_id = dest_res.json()[0]["id"]

        consensus_res = client.get(f"/api/pulse/{taj_id}/consensus")
        self.assertEqual(consensus_res.status_code, 200)
        data = consensus_res.json()
        self.assertGreater(data["total_votes"], 0)
        self.assertIn("recommend_percentage", data)
        self.assertIn("crowd_consensus", data)
        self.assertGreater(len(data["recent_pulse_feed"]), 0)
        print(f"  [PASS] Consensus aggregation verified ({data['total_votes']} votes, {data['recommend_percentage']}% recommend)")

    def test_07_destinations_with_proximity_query(self):
        """Verify destination search returns calculated distances when user GPS is provided."""
        res = client.get("/api/destinations?user_lat=28.6143&user_lon=77.1994")
        self.assertEqual(res.status_code, 200)
        items = res.json()
        self.assertGreater(len(items), 0)
        first = items[0]
        self.assertIsNotNone(first["distance_km"])
        self.assertIn("is_within_geofence", first)
        print(f"  [PASS] Proximity queries compute dynamic distance for all spots ({first['name']}: {first['distance_km']}km)")

    def test_08_operational_telemetry_and_hazard_alerts(self):
        """Verify operational timings, IST open/closed status calculation, and nearby hazard alerts."""
        res = client.get("/api/destinations?search=Taj Mahal")
        self.assertEqual(res.status_code, 200)
        taj = res.json()[0]
        self.assertEqual(taj["opening_time"], "06:00")
        self.assertEqual(taj["closing_time"], "18:30")
        self.assertEqual(taj["weekly_off_day"], "Friday")
        self.assertIn("peak_rush_hours", taj)
        self.assertIsInstance(taj["is_currently_open"], bool)
        self.assertIn("open_status_text", taj)
        self.assertIn("entry_fee_domestic", taj)
        self.assertIn("entry_fee_foreign", taj)
        self.assertIn("booking_portal_url", taj)
        print(f"  [PASS] Operational telemetry verified for Taj Mahal (Status: {taj['open_status_text']}, Hours: {taj['opening_time']}-{taj['closing_time']}, Off: {taj['weekly_off_day']})")

        # Verify Solang Valley / Rohtang has landslide hazard alert
        manali_res = client.get("/api/destinations?search=Solang")
        self.assertEqual(manali_res.status_code, 200)
        solang = manali_res.json()[0]
        self.assertGreater(len(solang["nearby_incidents"]), 0)
        hazard = solang["nearby_incidents"][0]
        self.assertEqual(hazard["incident_type"], "Weather Hazard")
        self.assertEqual(hazard["severity"], "High")
        self.assertIn("Landslide", hazard["title"])
        print(f"  [PASS] Real-time hazard alerts verified (Incident: {hazard['title']}, Severity: {hazard['severity']})")

    def test_09_admin_auth_and_pass_protection(self):
        """Verify Admin password protection and RBAC enforcement on administrative APIs."""
        # 1. Admin login with valid credentials
        admin_login = client.post("/api/auth/login", json={"email": "admin@safetour.gov.in", "password": "AdminPass#2026"})
        self.assertEqual(admin_login.status_code, 200)
        admin_data = admin_login.json()
        self.assertEqual(admin_data["user"]["role"], "admin")
        admin_token = admin_data["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 2. Rejection with invalid pass
        bad_login = client.post("/api/auth/login", json={"email": "admin@safetour.gov.in", "password": "WrongPassword"})
        self.assertEqual(bad_login.status_code, 401)

        # 3. Rejection of unauthenticated request to admin route
        dest_res = client.get("/api/destinations")
        sample_dest_id = dest_res.json()[0]["id"]

        unauth_adv = client.post("/api/admin/advisories", json={"destination_id": sample_dest_id, "title": "Test", "alert_level": "Warning", "summary": "Test"})
        self.assertEqual(unauth_adv.status_code, 401)

        # 4. Rejection of tourist user attempting to access admin route
        tourist_login = client.post("/api/auth/login", json={"email": "arjun@traveler.in", "password": "Traveler@123"})
        tourist_token = tourist_login.json()["access_token"]
        tourist_headers = {"Authorization": f"Bearer {tourist_token}"}
        forbidden_adv = client.post("/api/admin/advisories", json={"destination_id": sample_dest_id, "title": "Test", "alert_level": "Warning", "summary": "Test"}, headers=tourist_headers)
        self.assertEqual(forbidden_adv.status_code, 403)

        # 5. Success with admin credentials
        valid_adv = client.post("/api/admin/advisories", json={"destination_id": sample_dest_id, "title": "Auth Verification Pass", "alert_level": "Info", "summary": "Test"}, headers=admin_headers)
        self.assertEqual(valid_adv.status_code, 200)
        print("  [PASS] Admin pass authentication and role-based access control (RBAC) verified")

    def test_10_admin_create_destination(self):
        """Verify Admin capability to add new Indian tourist destinations with operational telemetry."""
        admin_login = client.post("/api/auth/login", json={"email": "admin@safetour.gov.in", "password": "AdminPass#2026"})
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        new_dest_payload = {
            "name": "Kanyakumari: Vivekananda Rock Memorial & Thiruvalluvar Statue",
            "state": "Tamil Nadu",
            "region": "South India",
            "category": "Heritage & Forts",
            "lat": 8.0780,
            "lng": 77.5550,
            "description": "The southernmost tip of mainland India, where Arabian Sea, Bay of Bengal, and Indian Ocean meet.",
            "image_url": "https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800",
            "best_visit_time": "October to March",
            "dress_code_etiquette": "Modest clothing recommended for memorial entry.",
            "opening_time": "07:00",
            "closing_time": "17:00",
            "weekly_off_day": "None",
            "peak_rush_hours": "09:30 AM - 02:00 PM",
            "entry_fee_domestic": "Rs 70 (Ferry Rs 50)",
            "entry_fee_foreign": "Rs 500",
            "booking_portal_url": "https://tamilnadutourism.tn.gov.in",
            "crime_index": 16.0,
            "scam_index": 20.0,
            "weather_risk": 15.0,
            "night_safety": 84.0,
            "crowd_density": 60.0,
            "emergency_facility_name": "Kanyakumari Coastal Police Station",
            "emergency_facility_phone": "+91-4652-246233"
        }

        create_res = client.post("/api/admin/destinations", json=new_dest_payload, headers=admin_headers)
        self.assertEqual(create_res.status_code, 200, create_res.text)
        data = create_res.json()
        self.assertTrue(data["success"])
        self.assertIn("destination_id", data)
        self.assertGreater(data["overall_safety_score"], 75)

        # Verify it now appears in public destinations search
        dest_res = client.get("/api/destinations?search=Thiruvalluvar")
        self.assertEqual(dest_res.status_code, 200)
        found = dest_res.json()
        self.assertGreater(len(found), 0)
        self.assertEqual(found[0]["name"], new_dest_payload["name"])
        self.assertEqual(found[0]["opening_time"], "07:00")
        print(f"  [PASS] Admin destination registration verified (Created #{data['destination_id']}: {data['name']}, Safety Score: {data['overall_safety_score']}/100)")

    def test_11_emergency_responder_command_center(self):
        """Verify dedicated Emergency Command Center (EOC) feed, dispatch dispatching, and status progression."""
        # 1. Fetch live responder feed
        feed_res = client.get("/api/emergency/responder/feed")
        self.assertEqual(feed_res.status_code, 200)
        incidents = feed_res.json()
        self.assertGreater(len(incidents), 0)
        target_inc = incidents[0]
        inc_id = target_inc["incident_id"]

        # 2. Dispatch a Police PCR squad
        dispatch_payload = {
            "incident_id": inc_id,
            "agency_type": "Police",
            "unit_callsign": "PCR-INTERCEPT-ALPHA-01",
            "contact_phone": "112",
            "eta_minutes": 3,
            "responder_notes": "Rapid response vehicle deployed with emergency flashers."
        }
        dispatch_res = client.post("/api/emergency/responder/dispatch", json=dispatch_payload)
        self.assertEqual(dispatch_res.status_code, 200)
        disp_data = dispatch_res.json()
        self.assertTrue(disp_data["success"])
        disp_id = disp_data["dispatch_id"]

        # 3. Advance status: EN_ROUTE -> ON_SCENE -> RESOLVED
        step_res = client.patch(f"/api/emergency/responder/dispatch/{disp_id}/status", json={"status": "ON_SCENE"})
        self.assertEqual(step_res.status_code, 200)
        self.assertEqual(step_res.json()["dispatch_status"], "ON_SCENE")

        resolve_res = client.patch(f"/api/emergency/responder/dispatch/{disp_id}/status", json={"status": "RESOLVED"})
        self.assertEqual(resolve_res.status_code, 200)
        self.assertEqual(resolve_res.json()["dispatch_status"], "RESOLVED")

        # 4. Check KPIs
        kpi_res = client.get("/api/emergency/responder/kpis")
        self.assertEqual(kpi_res.status_code, 200)
        kpis = kpi_res.json()
        self.assertIn("active_distress_calls", kpis)
        self.assertIn("active_units_deployed", kpis)
        self.assertGreaterEqual(kpis["incidents_resolved"], 1)
        print("  [PASS] Emergency Responder Command Center (EOC) feed, unit dispatch, and status transition verified")

if __name__ == "__main__":
    unittest.main()


