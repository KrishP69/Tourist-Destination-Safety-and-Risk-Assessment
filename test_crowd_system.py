"""
Crowd Intelligence & Smart Booking test suite.
Run: python test_crowd_system.py
"""
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.seed_data import seed_database
from app.database import get_db, init_db
from app.services.geofence_service import (
    validate_coordinates,
    is_inside_destination,
    point_in_polygon,
    haversine_meters,
)
from app.services.crowd_engine import (
    crowd_level_from_occupancy,
    estimate_current_crowd,
    compute_confidence,
    get_effective_capacity,
)
from app.services.prediction_engine import predict_for_slot, recommend_less_crowded_slots
from app.services.booking_service import ensure_slots_for_date, book_tickets, cancel_booking
from app.services.presence_service import update_presence, stop_presence
from app.services.demo_crowd_service import set_demo_mode, run_demo_tick, bootstrap_historical_demo_snapshots
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestCrowdGeofence(unittest.TestCase):
    def test_coordinate_validation(self):
        validate_coordinates(27.17, 78.04)
        with self.assertRaises(ValueError):
            validate_coordinates(120, 78)
        with self.assertRaises(ValueError):
            validate_coordinates(27, 200)
        print("  [PASS] Coordinate validation")

    def test_circular_geofence(self):
        dest = {"lat": 27.1751, "lng": 78.0421, "geofence_radius_m": 500, "geofence_polygon": None}
        inside, dist = is_inside_destination(27.1751, 78.0421, dest)
        self.assertTrue(inside)
        self.assertLess(dist, 10)
        outside, _ = is_inside_destination(27.20, 78.10, dest)
        self.assertFalse(outside)
        print("  [PASS] Circular geofence enter/exit")

    def test_polygon_geofence(self):
        poly = [(0, 0), (0, 1), (1, 1), (1, 0)]
        self.assertTrue(point_in_polygon(0.5, 0.5, poly))
        self.assertFalse(point_in_polygon(2, 2, poly))
        print("  [PASS] Polygon geofence")


class TestCrowdEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_database()
        set_demo_mode(True)
        bootstrap_historical_demo_snapshots(days=3)
        run_demo_tick()

    def test_crowd_level_thresholds(self):
        dest = {
            "threshold_low_max": 60,
            "threshold_moderate_max": 75,
            "threshold_high_max": 90,
            "threshold_very_high_max": 100,
        }
        self.assertEqual(crowd_level_from_occupancy(50, dest), "LOW")
        self.assertEqual(crowd_level_from_occupancy(70, dest), "MODERATE")
        self.assertEqual(crowd_level_from_occupancy(80, dest), "HIGH")
        self.assertEqual(crowd_level_from_occupancy(95, dest), "VERY_HIGH")
        self.assertEqual(crowd_level_from_occupancy(110, dest), "CRITICAL")
        print("  [PASS] Crowd level thresholds")

    def test_confidence_scales_with_gps(self):
        low = compute_confidence(5, 1000, 2, False, 600)
        high = compute_confidence(320, 1000, 40, True, 30)
        self.assertGreater(high, low)
        print(f"  [PASS] Confidence low={low} high={high}")

    def test_estimate_scenario(self):
        """Realistic scenario: capacity 1000, GPS 300, bookings, history."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM destinations ORDER BY id LIMIT 1")
            dest_id = cursor.fetchone()["id"]
            cursor.execute(
                "UPDATE destinations SET maximum_capacity = 1000, comfortable_capacity = 600 WHERE id = ?",
                (dest_id,),
            )
            # Clear and inject 300 observed demo visitors
            cursor.execute("DELETE FROM visitor_presence WHERE destination_id = ?", (dest_id,))
            now = datetime.utcnow().isoformat(sep=" ")
            for i in range(300):
                cursor.execute(
                    """
                    INSERT INTO visitor_presence
                    (anonymous_user_id, destination_id, last_seen, entered_at, is_active, source)
                    VALUES (?, ?, ?, ?, 1, 'demo')
                    """,
                    (f"scenario_{dest_id}_{i}", dest_id, now, now),
                )

        summary = estimate_current_crowd(dest_id)
        self.assertEqual(summary["observed_users"], 300)
        self.assertIsNotNone(summary["estimated_crowd"])
        self.assertGreaterEqual(summary["estimated_crowd"], 300)
        self.assertIn(summary["crowd_level"], ["LOW", "MODERATE", "HIGH", "VERY_HIGH", "CRITICAL"])
        print(
            f"  [PASS] Scenario estimate={summary['estimated_crowd']} "
            f"occ={summary['occupancy_percentage']}% level={summary['crowd_level']} "
            f"conf={summary['confidence']}"
        )


class TestPresenceAndBooking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_database()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, lat, lng FROM destinations ORDER BY id LIMIT 1")
            row = cursor.fetchone()
            cls.dest_id = row["id"]
            cls.lat = row["lat"]
            cls.lng = row["lng"]
            cursor.execute(
                "UPDATE destinations SET maximum_capacity = 1000, geofence_radius_m = 1000 WHERE id = ?",
                (cls.dest_id,),
            )

    def test_presence_enter_exit_timeout_fields(self):
        anon = "test_presence_user_abcdef12"
        result = update_presence(anon, self.lat, self.lng, accuracy_m=20, destination_id=self.dest_id)
        self.assertTrue(result["accepted"])
        self.assertTrue(any(a["destination_id"] == self.dest_id for a in result["active_destinations"]))
        stop = stop_presence(anon)
        self.assertTrue(stop["success"])
        print("  [PASS] Presence enter/exit")

    def test_location_api_validation(self):
        res = client.post(
            "/api/location/update",
            json={
                "anonymous_user_id": "api_user_abcdefgh",
                "latitude": 999,
                "longitude": 78.0,
            },
        )
        self.assertEqual(res.status_code, 400)
        print("  [PASS] Location API rejects invalid coords")

    def test_booking_and_overbooking(self):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        slots = ensure_slots_for_date(self.dest_id, today)
        self.assertTrue(len(slots) > 0)
        slot = slots[0]
        # Shrink capacity for deterministic overbooking test
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE ticket_slots SET capacity = 10, booked_count = 0 WHERE id = ?",
                (slot["id"],),
            )

        ok = book_tickets(self.dest_id, slot["id"], 5, anonymous_user_id="booker_aaaaaaa1")
        self.assertTrue(ok["success"])
        self.assertIn("booking_reference", ok)

        with self.assertRaises(OverflowError):
            book_tickets(self.dest_id, slot["id"], 6, anonymous_user_id="booker_bbbbbbb2")

        # Cancel restores capacity
        cancel_booking(ok["booking_id"], is_admin=True)
        again = book_tickets(self.dest_id, slot["id"], 3, anonymous_user_id="booker_ccccccc3")
        self.assertTrue(again["success"])
        print("  [PASS] Booking + overbooking prevention + cancel")

    def test_ticket_api_conflict(self):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        slots = ensure_slots_for_date(self.dest_id, today)
        slot_id = slots[0]["id"]
        with get_db() as conn:
            conn.cursor().execute(
                "UPDATE ticket_slots SET capacity = 2, booked_count = 2 WHERE id = ?",
                (slot_id,),
            )
        res = client.post(
            "/api/tickets/book",
            json={
                "destination_id": self.dest_id,
                "slot_id": slot_id,
                "number_of_people": 1,
                "anonymous_user_id": "api_booker_zzzzzz",
            },
        )
        self.assertEqual(res.status_code, 409)
        detail = res.json()["detail"]
        self.assertIn("full", str(detail).lower() if isinstance(detail, str) else detail.get("message", "").lower())
        print("  [PASS] Ticket API returns 409 when full")

    def test_slot_predictions_and_recommendations(self):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        ensure_slots_for_date(self.dest_id, today)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM ticket_slots WHERE destination_id = ? AND slot_date = ? LIMIT 1",
                (self.dest_id, today),
            )
            slot_id = cursor.fetchone()["id"]
        pred = predict_for_slot(self.dest_id, slot_id)
        self.assertIn("predicted_crowd", pred)
        self.assertIn("confidence", pred)
        recs = recommend_less_crowded_slots(self.dest_id, today, limit=3)
        self.assertIsInstance(recs, list)
        print("  [PASS] Slot prediction + recommendations")

    def test_crowd_api(self):
        res = client.get(f"/api/crowd/{self.dest_id}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("observed_users", data)
        self.assertIn("estimated_crowd", data)
        self.assertTrue(data.get("is_estimate", True))
        print("  [PASS] Crowd API terminology fields present")

    def test_admin_capacity_change(self):
        login = client.post(
            "/api/auth/login",
            json={"email": "admin@safetour.gov.in", "password": "AdminPass#2026"},
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["access_token"]
        res = client.put(
            f"/api/admin/destinations/{self.dest_id}/crowd-config",
            headers={"Authorization": f"Bearer {token}"},
            json={"maximum_capacity": 800, "emergency_capacity_override": 500},
        )
        self.assertEqual(res.status_code, 200)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM destinations WHERE id = ?", (self.dest_id,))
            dest = dict(cursor.fetchone())
            self.assertEqual(get_effective_capacity(dest), 500)
        print("  [PASS] Admin capacity / emergency override")


if __name__ == "__main__":
    print("\n==========================================")
    print("  Crowd Intelligence Verification Suite  ")
    print("==========================================")
    unittest.main(verbosity=1)
