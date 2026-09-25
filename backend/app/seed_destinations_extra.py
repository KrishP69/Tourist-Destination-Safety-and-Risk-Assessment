"""
Additional real Indian tourist destinations (additive seed).
Merged into INDIA_DESTINATIONS — do not duplicate names already in seed_data.py.
"""

ADDITIONAL_INDIA_DESTINATIONS = [
    # =========================================================================
    # MAHARASHTRA
    # =========================================================================
    {
        "name": "Elephanta Caves",
        "state": "Maharashtra",
        "region": "West India",
        "category": "Heritage & Forts",
        "lat": 18.9633,
        "lng": 72.9315,
        "overall_safety_score": 84,
        "risk_tier": "Low Risk (Safe)",
        "description": "UNESCO rock-cut cave temples dedicated to Lord Shiva on Elephanta Island in Mumbai Harbour, reached by ferry from the Gateway of India.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to February",
        "dress_code_etiquette": "Comfortable walking shoes; modest attire inside cave sanctums.",
        "opening_time": "09:00",
        "closing_time": "17:30",
        "weekly_off_day": "Monday",
        "peak_rush_hours": "11:00 AM - 02:30 PM",
        "entry_fee_domestic": "Rs 40",
        "entry_fee_foreign": "Rs 600",
        "booking_portal_url": "https://asi.payumoney.com",
        "metrics": {"crime_index": 14.0, "scam_index": 22.0, "weather_risk": 18.0, "health_risk": 12.0, "night_safety": 70.0, "crowd_density": 60.0, "transport_safety": 78.0},
        "tips": [
            "Buy ferry tickets from official MTDC / Gateway counters; avoid touts quoting inflated same-day rates.",
            "Carry drinking water — island stairs are steep and shaded areas are limited.",
            "Closed on Mondays; plan weekend trips early to skip afternoon heat."
        ],
        "emergency": [
            {"name": "Colaba Police Station", "type": "Police", "phone": "+91-22-22851717", "address": "Colaba, Mumbai", "lat": 18.9210, "lng": 72.8340},
            {"name": "Bombay Hospital", "type": "Hospital", "phone": "+91-22-22067676", "address": "Marine Lines, Mumbai", "lat": 18.9400, "lng": 72.8280}
        ],
        "advisory": {"title": "Ferry Weather Advisory", "level": "Advisory", "summary": "Ferry services may pause during monsoon high seas. Confirm sailings before travel."}
    },
    {
        "name": "Lonavala & Khandala",
        "state": "Maharashtra",
        "region": "West India",
        "category": "Mountain & Adventure",
        "lat": 18.7557,
        "lng": 73.4057,
        "overall_safety_score": 86,
        "risk_tier": "Low Risk (Safe)",
        "description": "Popular Western Ghats hill stations near Mumbai and Pune, known for monsoon waterfalls, Bhushi Dam, Tiger's Leap, and misty valley viewpoints.",
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "June to September (monsoon) & October to February",
        "dress_code_etiquette": "Light rain jacket in monsoon; sturdy footwear for viewpoints.",
        "opening_time": "06:00",
        "closing_time": "20:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:00 AM - 04:00 PM (Weekends)",
        "entry_fee_domestic": "Free (viewpoint parking charges vary)",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 12.0, "scam_index": 18.0, "weather_risk": 32.0, "health_risk": 10.0, "night_safety": 82.0, "crowd_density": 70.0, "transport_safety": 74.0},
        "tips": [
            "Avoid standing on Bhushi Dam spillway rocks during heavy discharge.",
            "Weekend Mumbai–Pune Expressway traffic is severe; start early.",
            "Use only authorized parking near viewpoints."
        ],
        "emergency": [
            {"name": "Lonavala Police Station", "type": "Police", "phone": "+91-2114-273033", "address": "Lonavala, Pune District", "lat": 18.7530, "lng": 73.4070},
            {"name": "Bharati Hospital Lonavala", "type": "Hospital", "phone": "+91-2114-273456", "address": "Lonavala", "lat": 18.7560, "lng": 73.4100}
        ],
        "advisory": {"title": "Monsoon Cliff Caution", "level": "Warning", "summary": "Slippery rocks and sudden waterfall surge near dams — heed local barricades."}
    },
    {
        "name": "Mahabaleshwar",
        "state": "Maharashtra",
        "region": "West India",
        "category": "Mountain & Adventure",
        "lat": 17.9307,
        "lng": 73.6477,
        "overall_safety_score": 87,
        "risk_tier": "Low Risk (Safe)",
        "description": "Historic hill station in the Sahyadris famous for strawberry farms, Arthur's Seat, Venna Lake, and panoramic Western Ghats vistas.",
        "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to June",
        "dress_code_etiquette": "Light woolens in winter evenings; casual daywear.",
        "opening_time": "06:00",
        "closing_time": "19:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "11:00 AM - 03:00 PM",
        "entry_fee_domestic": "Free (point entry fees vary)",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 10.0, "scam_index": 16.0, "weather_risk": 28.0, "health_risk": 10.0, "night_safety": 86.0, "crowd_density": 55.0, "transport_safety": 76.0},
        "tips": [
            "Book hotels ahead during Christmas and strawberry season weekends.",
            "Fog reduces visibility on ghat roads after sunset — drive cautiously.",
            "Boating on Venna Lake only via licensed operators with life jackets."
        ],
        "emergency": [
            {"name": "Mahabaleshwar Police Station", "type": "Police", "phone": "+91-2168-260233", "address": "Mahabaleshwar", "lat": 17.9310, "lng": 73.6480},
            {"name": "Civil Hospital Mahabaleshwar", "type": "Hospital", "phone": "+91-2168-260244", "address": "Mahabaleshwar", "lat": 17.9290, "lng": 73.6500}
        ],
        "advisory": {"title": "Ghat Fog Advisory", "level": "Advisory", "summary": "Dense fog common Dec–Jan evenings on approach roads."}
    },
    {
        "name": "Shirdi Sai Baba Temple",
        "state": "Maharashtra",
        "region": "West India",
        "category": "Spiritual & Sacred",
        "lat": 19.7645,
        "lng": 74.4773,
        "overall_safety_score": 85,
        "risk_tier": "Low Risk (Safe)",
        "description": "Major pilgrimage centre dedicated to Sai Baba of Shirdi, drawing millions of devotees for darshan at the Samadhi Mandir complex.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Modest traditional attire; footwear removed in sanctum queues.",
        "opening_time": "04:00",
        "closing_time": "23:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "06:00 AM - 12:00 PM & Festival days",
        "entry_fee_domestic": "Free (VIP darshan slots paid)",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "https://sai.org.in",
        "metrics": {"crime_index": 14.0, "scam_index": 28.0, "weather_risk": 20.0, "health_risk": 14.0, "night_safety": 80.0, "crowd_density": 90.0, "transport_safety": 78.0},
        "tips": [
            "Use official Shri Saibaba Sansthan queue booking for darshan slots.",
            "Beware of agents selling fake VIP passes outside the complex.",
            "Keep valuables secure in dense festival crowds."
        ],
        "emergency": [
            {"name": "Shirdi Police Station", "type": "Police", "phone": "+91-2423-255100", "address": "Shirdi", "lat": 19.7650, "lng": 74.4780},
            {"name": "Saibaba Hospital Shirdi", "type": "Hospital", "phone": "+91-2423-258500", "address": "Shirdi", "lat": 19.7660, "lng": 74.4760}
        ],
        "advisory": {"title": "Festival Crowd Notice", "level": "Advisory", "summary": "Extremely high footfall on Thursdays and Guru Purnima — arrive early."}
    },
    {
        "name": "Alibaug Beaches",
        "state": "Maharashtra",
        "region": "West India",
        "category": "Beach & Coastal",
        "lat": 18.6414,
        "lng": 72.8722,
        "overall_safety_score": 83,
        "risk_tier": "Low Risk (Safe)",
        "description": "Coastal getaway across Mumbai harbour with Alibaug Beach, Kolaba Fort, and nearby Mandwa–Kihim stretches popular for weekend escapes.",
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to March",
        "dress_code_etiquette": "Casual beachwear; cover-ups in village markets.",
        "opening_time": "06:00",
        "closing_time": "19:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "11:00 AM - 05:00 PM (Weekends)",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 16.0, "scam_index": 20.0, "weather_risk": 26.0, "health_risk": 12.0, "night_safety": 74.0, "crowd_density": 65.0, "transport_safety": 72.0},
        "tips": [
            "Swim only in lifeguard-patrolled zones; undertow common.",
            "Ferry + road combo via Mandwa is often faster than full road drive from Mumbai.",
            "Hire only registered water-sports operators."
        ],
        "emergency": [
            {"name": "Alibaug Police Station", "type": "Police", "phone": "+91-2141-222033", "address": "Alibaug", "lat": 18.6420, "lng": 72.8730},
            {"name": "Civil Hospital Alibaug", "type": "Hospital", "phone": "+91-2141-222244", "address": "Alibaug", "lat": 18.6400, "lng": 72.8710}
        ],
        "advisory": {"title": "Rip Current Caution", "level": "Warning", "summary": "Monsoon and high-tide swimming discouraged without lifeguard clearance."}
    },
    {
        "name": "Sanjay Gandhi National Park",
        "state": "Maharashtra",
        "region": "West India",
        "category": "Wildlife & Nature",
        "lat": 19.2147,
        "lng": 72.9106,
        "overall_safety_score": 82,
        "risk_tier": "Low Risk (Safe)",
        "description": "Protected forest within Mumbai city limits featuring Kanheri Caves, nature trails, and leopard habitat — a unique urban wilderness experience.",
        "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Comfortable trekking clothes; closed shoes mandatory on trails.",
        "opening_time": "07:30",
        "closing_time": "17:30",
        "weekly_off_day": "Monday",
        "peak_rush_hours": "09:00 AM - 12:00 PM",
        "entry_fee_domestic": "Rs 53 (approx)",
        "entry_fee_foreign": "Rs 53 (approx)",
        "booking_portal_url": "",
        "metrics": {"crime_index": 18.0, "scam_index": 12.0, "weather_risk": 16.0, "health_risk": 14.0, "night_safety": 55.0, "crowd_density": 50.0, "transport_safety": 80.0},
        "tips": [
            "Stay on marked trails; leopards inhabit deeper forest zones.",
            "Kanheri Caves ticket is separate — carry cash/UPI.",
            "Park closes before dusk; plan return early."
        ],
        "emergency": [
            {"name": "Borivali Police Station", "type": "Police", "phone": "+91-22-28921213", "address": "Borivali East, Mumbai", "lat": 19.2300, "lng": 72.8600},
            {"name": "Bhagwati Hospital Borivali", "type": "Hospital", "phone": "+91-22-28932461", "address": "Borivali West", "lat": 19.2350, "lng": 72.8500}
        ],
        "advisory": {"title": "Wildlife Buffer Notice", "level": "Advisory", "summary": "Do not litter or feed animals; report wildlife sightings to forest staff."}
    },

    # =========================================================================
    # DELHI NCR
    # =========================================================================
    {
        "name": "India Gate & Rajpath",
        "state": "Delhi",
        "region": "North India",
        "category": "Urban & Culture",
        "lat": 28.6129,
        "lng": 77.2295,
        "overall_safety_score": 86,
        "risk_tier": "Low Risk (Safe)",
        "description": "Iconic war memorial arch on Kartavya Path (formerly Rajpath), a central gathering space for evening walks and national ceremonies in New Delhi.",
        "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Casual; respectful behaviour near memorial flame.",
        "opening_time": "05:00",
        "closing_time": "23:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "06:00 PM - 09:00 PM",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 22.0, "scam_index": 20.0, "weather_risk": 18.0, "health_risk": 12.0, "night_safety": 78.0, "crowd_density": 75.0, "transport_safety": 82.0},
        "tips": [
            "Use Metro Central Secretariat / Khan Market for easier access.",
            "Secure bags in evening crowds; avoid unmarked guides.",
            "Lawn areas may have temporary restrictions during events."
        ],
        "emergency": [
            {"name": "Parliament Street Police Station", "type": "Police", "phone": "112", "address": "New Delhi", "lat": 28.6200, "lng": 77.2100},
            {"name": "Dr Ram Manohar Lohia Hospital", "type": "Hospital", "phone": "+91-11-23365525", "address": "Baba Kharak Singh Marg", "lat": 28.6250, "lng": 77.2050}
        ],
        "advisory": {"title": "Event Closure Notice", "level": "Advisory", "summary": "Access may be restricted during Republic Day rehearsals and VVIP movements."}
    },
    {
        "name": "Lotus Temple",
        "state": "Delhi",
        "region": "North India",
        "category": "Spiritual & Sacred",
        "lat": 28.5535,
        "lng": 77.2588,
        "overall_safety_score": 90,
        "risk_tier": "Low Risk (Safe)",
        "description": "Baháʼí House of Worship shaped like a lotus, renowned for silent meditation, architectural beauty, and open access to all faiths.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Modest clothing; absolute silence inside the prayer hall.",
        "opening_time": "09:00",
        "closing_time": "17:30",
        "weekly_off_day": "Monday",
        "peak_rush_hours": "10:00 AM - 01:00 PM",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 12.0, "scam_index": 10.0, "weather_risk": 14.0, "health_risk": 8.0, "night_safety": 80.0, "crowd_density": 55.0, "transport_safety": 84.0},
        "tips": [
            "Photography inside the prayer hall is prohibited.",
            "Closed Mondays — verify hours on public holidays.",
            "Nearest Metro: Kalkaji Mandir / Nehru Place."
        ],
        "emergency": [
            {"name": "Kalkaji Police Station", "type": "Police", "phone": "112", "address": "South Delhi", "lat": 28.5500, "lng": 77.2600},
            {"name": "AIIMS New Delhi", "type": "Hospital", "phone": "+91-11-26588500", "address": "Ansari Nagar", "lat": 28.5672, "lng": 77.2100}
        ],
        "advisory": {"title": "Silence Protocol", "level": "Advisory", "summary": "Mobile phones must be silent; staff may request exit for disturbances."}
    },
    {
        "name": "Humayun's Tomb",
        "state": "Delhi",
        "region": "North India",
        "category": "Heritage & Forts",
        "lat": 28.5933,
        "lng": 77.2507,
        "overall_safety_score": 88,
        "risk_tier": "Low Risk (Safe)",
        "description": "UNESCO World Heritage Mughal garden-tomb that inspired later architecture including the Taj Mahal; set in landscaped charbagh gardens in Nizamuddin.",
        "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Comfortable walking shoes; modest attire preferred.",
        "opening_time": "06:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:00 AM - 02:00 PM",
        "entry_fee_domestic": "Rs 35",
        "entry_fee_foreign": "Rs 550",
        "booking_portal_url": "https://asi.payumoney.com",
        "metrics": {"crime_index": 14.0, "scam_index": 16.0, "weather_risk": 16.0, "health_risk": 10.0, "night_safety": 72.0, "crowd_density": 50.0, "transport_safety": 82.0},
        "tips": [
            "Combine with nearby Hazrat Nizamuddin Dargah if time allows.",
            "Buy tickets via ASI counters or official portal.",
            "Sunrise light is best for photography."
        ],
        "emergency": [
            {"name": "Nizamuddin Police Station", "type": "Police", "phone": "112", "address": "Nizamuddin", "lat": 28.5910, "lng": 77.2430},
            {"name": "Holy Family Hospital", "type": "Hospital", "phone": "+91-11-26845900", "address": "Okhla Road", "lat": 28.5600, "lng": 77.2700}
        ],
        "advisory": {"title": "Heat Advisory", "level": "Advisory", "summary": "Limited shade in gardens during peak summer afternoons."}
    },
    {
        "name": "Akshardham Temple Delhi",
        "state": "Delhi",
        "region": "North India",
        "category": "Spiritual & Sacred",
        "lat": 28.6127,
        "lng": 77.2773,
        "overall_safety_score": 91,
        "risk_tier": "Low Risk (Safe)",
        "description": "Vast Swaminarayan complex on the Yamuna banks featuring intricate stone carvings, exhibitions, and evening water shows with strict security screening.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Modest clothing covering shoulders and knees; no bags/phones inside main complex (lockers available).",
        "opening_time": "10:00",
        "closing_time": "20:00",
        "weekly_off_day": "Monday",
        "peak_rush_hours": "04:00 PM - 07:30 PM",
        "entry_fee_domestic": "Free entry (shows ticketed)",
        "entry_fee_foreign": "Free entry (shows ticketed)",
        "booking_portal_url": "https://akshardham.com",
        "metrics": {"crime_index": 8.0, "scam_index": 8.0, "weather_risk": 14.0, "health_risk": 8.0, "night_safety": 88.0, "crowd_density": 70.0, "transport_safety": 86.0},
        "tips": [
            "Leave large bags at hotel — security forbids most electronics inside.",
            "Arrive 2+ hours before evening show for security queues.",
            "Metro: Akshardham station on Blue Line."
        ],
        "emergency": [
            {"name": "Akshardham Police Post", "type": "Police", "phone": "112", "address": "Noida Mor", "lat": 28.6130, "lng": 77.2780},
            {"name": "Max Super Speciality Hospital Patparganj", "type": "Hospital", "phone": "+91-11-43033333", "address": "Patparganj", "lat": 28.6200, "lng": 77.3000}
        ],
        "advisory": {"title": "Security Screening", "level": "Advisory", "summary": "Cameras and phones are not permitted beyond the first checkpoint."}
    },

    # =========================================================================
    # UTTAR PRADESH / RAJASTHAN / MP
    # =========================================================================
    {
        "name": "Fatehpur Sikri",
        "state": "Uttar Pradesh",
        "region": "North India",
        "category": "Heritage & Forts",
        "lat": 27.0945,
        "lng": 77.6610,
        "overall_safety_score": 84,
        "risk_tier": "Low Risk (Safe)",
        "description": "UNESCO-listed abandoned Mughal capital near Agra featuring Buland Darwaza, Panch Mahal, and the marble tomb of Salim Chishti.",
        "image_url": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Modest attire; cover head optionally at dargah.",
        "opening_time": "06:00",
        "closing_time": "18:00",
        "weekly_off_day": "Friday",
        "peak_rush_hours": "10:00 AM - 02:00 PM",
        "entry_fee_domestic": "Rs 50",
        "entry_fee_foreign": "Rs 610",
        "booking_portal_url": "https://asi.payumoney.com",
        "metrics": {"crime_index": 16.0, "scam_index": 30.0, "weather_risk": 18.0, "health_risk": 12.0, "night_safety": 70.0, "crowd_density": 55.0, "transport_safety": 76.0},
        "tips": [
            "Combine with Taj Mahal day trip but allow 2–3 hours on site.",
            "Decline unsolicited 'guides' at parking; hire ASI-approved guides only.",
            "Carry water — exposed sandstone courtyards get hot."
        ],
        "emergency": [
            {"name": "Fatehpur Sikri Police Outpost", "type": "Police", "phone": "112", "address": "Fatehpur Sikri", "lat": 27.0950, "lng": 77.6620},
            {"name": "SN Medical College Hospital Agra", "type": "Hospital", "phone": "+91-562-2260353", "address": "Agra", "lat": 27.1850, "lng": 78.0120}
        ],
        "advisory": {"title": "Friday Closure", "level": "Advisory", "summary": "Complex typically closed Fridays similar to other ASI monuments in the circuit."}
    },
    {
        "name": "Sarnath",
        "state": "Uttar Pradesh",
        "region": "North India",
        "category": "Spiritual & Sacred",
        "lat": 25.3800,
        "lng": 83.0214,
        "overall_safety_score": 87,
        "risk_tier": "Low Risk (Safe)",
        "description": "Sacred Buddhist site where Buddha delivered his first sermon; home to the Dhamek Stupa, Ashoka Pillar remnant, and Sarnath Museum.",
        "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Quiet, respectful demeanour; modest clothing.",
        "opening_time": "06:00",
        "closing_time": "18:00",
        "weekly_off_day": "Friday",
        "peak_rush_hours": "09:00 AM - 12:00 PM",
        "entry_fee_domestic": "Rs 25 (excavation site)",
        "entry_fee_foreign": "Rs 300",
        "booking_portal_url": "",
        "metrics": {"crime_index": 12.0, "scam_index": 18.0, "weather_risk": 16.0, "health_risk": 12.0, "night_safety": 78.0, "crowd_density": 45.0, "transport_safety": 76.0},
        "tips": [
            "Visit museum for the original Ashokan lion capital (national emblem).",
            "Auto from Varanasi takes ~30–40 minutes — agree fare beforehand.",
            "Early morning is calmest for meditation gardens."
        ],
        "emergency": [
            {"name": "Sarnath Police Outpost", "type": "Police", "phone": "112", "address": "Sarnath", "lat": 25.3810, "lng": 83.0220},
            {"name": "Sir Sunderlal Hospital (BHU)", "type": "Hospital", "phone": "+91-542-2369291", "address": "Varanasi", "lat": 25.2750, "lng": 82.9980}
        ],
        "advisory": {"title": "Museum Timing", "level": "Advisory", "summary": "Museum closed on Fridays; verify excavation site hours seasonally."}
    },
    {
        "name": "Jodhpur: Mehrangarh Fort",
        "state": "Rajasthan",
        "region": "West India",
        "category": "Heritage & Forts",
        "lat": 26.2983,
        "lng": 73.0184,
        "overall_safety_score": 86,
        "risk_tier": "Low Risk (Safe)",
        "description": "Imposing hill fort overlooking the Blue City of Jodhpur, with palaces, museums, and panoramic views of the old town below.",
        "image_url": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Comfortable shoes for steep approaches; light cottons.",
        "opening_time": "09:00",
        "closing_time": "17:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:30 AM - 02:00 PM",
        "entry_fee_domestic": "Rs 100 (approx)",
        "entry_fee_foreign": "Rs 600 (approx)",
        "booking_portal_url": "https://www.mehrangarh.org",
        "metrics": {"crime_index": 14.0, "scam_index": 22.0, "weather_risk": 22.0, "health_risk": 12.0, "night_safety": 80.0, "crowd_density": 55.0, "transport_safety": 78.0},
        "tips": [
            "Audio guide is worthwhile inside palace museums.",
            "Blue City lanes are photogenic but narrow — watch for bikes.",
            "Summer afternoons exceed 40°C; visit early."
        ],
        "emergency": [
            {"name": "Jodhpur Kotwali", "type": "Police", "phone": "112", "address": "Jodhpur", "lat": 26.2900, "lng": 73.0300},
            {"name": "MDM Hospital Jodhpur", "type": "Hospital", "phone": "+91-291-2549400", "address": "Jodhpur", "lat": 26.2800, "lng": 73.0200}
        ],
        "advisory": {"title": "Heat Warning", "level": "Advisory", "summary": "Exposed fort ramparts — carry water and sun protection April–June."}
    },
    {
        "name": "Pushkar Lake & Brahma Temple",
        "state": "Rajasthan",
        "region": "West India",
        "category": "Spiritual & Sacred",
        "lat": 26.4899,
        "lng": 74.5511,
        "overall_safety_score": 83,
        "risk_tier": "Low Risk (Safe)",
        "description": "Sacred town around Pushkar Lake with the rare Brahma Temple, camel fair fame, and a relaxed backpacker atmosphere near Ajmer.",
        "image_url": "https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March (Kartik Purnima fair)",
        "dress_code_etiquette": "Cover shoulders/knees at temples; remove shoes.",
        "opening_time": "05:00",
        "closing_time": "21:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "06:00 AM - 09:00 AM & Fair week",
        "entry_fee_domestic": "Free (donations customary)",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 14.0, "scam_index": 32.0, "weather_risk": 18.0, "health_risk": 14.0, "night_safety": 76.0, "crowd_density": 65.0, "transport_safety": 74.0},
        "tips": [
            "Politely decline flower/tikka sellers who demand high 'donations' after the fact.",
            "Book months ahead for Pushkar Camel Fair week.",
            "Lake ghats can be slippery — watch your step."
        ],
        "emergency": [
            {"name": "Pushkar Police Station", "type": "Police", "phone": "112", "address": "Pushkar", "lat": 26.4900, "lng": 74.5520},
            {"name": "Government Hospital Ajmer", "type": "Hospital", "phone": "+91-145-2626505", "address": "Ajmer", "lat": 26.4500, "lng": 74.6400}
        ],
        "advisory": {"title": "Fair Crowd Advisory", "level": "Advisory", "summary": "Extreme crowding during Kartik Purnima — secure belongings."}
    },
    {
        "name": "Sanchi Stupa",
        "state": "Madhya Pradesh",
        "region": "West India",
        "category": "Heritage & Forts",
        "lat": 23.4793,
        "lng": 77.7398,
        "overall_safety_score": 89,
        "risk_tier": "Low Risk (Safe)",
        "description": "UNESCO Buddhist monument complex near Bhopal with the Great Stupa commissioned by Emperor Ashoka and finely carved toranas.",
        "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Quiet, respectful behaviour around stupas.",
        "opening_time": "06:30",
        "closing_time": "18:30",
        "weekly_off_day": "Friday",
        "peak_rush_hours": "10:00 AM - 01:00 PM",
        "entry_fee_domestic": "Rs 30",
        "entry_fee_foreign": "Rs 500",
        "booking_portal_url": "https://asi.payumoney.com",
        "metrics": {"crime_index": 8.0, "scam_index": 10.0, "weather_risk": 16.0, "health_risk": 10.0, "night_safety": 80.0, "crowd_density": 35.0, "transport_safety": 80.0},
        "tips": [
            "Easy day trip from Bhopal (~50 km).",
            "Visit museum for excavated relics and models.",
            "Midday heat is strong — carry water."
        ],
        "emergency": [
            {"name": "Sanchi Police Outpost", "type": "Police", "phone": "112", "address": "Sanchi", "lat": 23.4800, "lng": 77.7400},
            {"name": "AIIMS Bhopal", "type": "Hospital", "phone": "+91-755-2672300", "address": "Bhopal", "lat": 23.2500, "lng": 77.4600}
        ],
        "advisory": {"title": "Friday Closure", "level": "Advisory", "summary": "ASI site typically closed Fridays."}
    },
    {
        "name": "Ujjain: Mahakaleshwar Temple",
        "state": "Madhya Pradesh",
        "region": "West India",
        "category": "Spiritual & Sacred",
        "lat": 23.1828,
        "lng": 75.7682,
        "overall_safety_score": 84,
        "risk_tier": "Low Risk (Safe)",
        "description": "One of the twelve Jyotirlinga shrines, famed for the pre-dawn Bhasma Aarti at Mahakaleshwar in the ancient city of Ujjain.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Traditional modest dress; men may need dhoti for certain aartis.",
        "opening_time": "04:00",
        "closing_time": "23:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "04:00 AM - 07:00 AM (Bhasma Aarti)",
        "entry_fee_domestic": "Free (special aarti tickets online)",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "https://shrimahakaleshwar.com",
        "metrics": {"crime_index": 14.0, "scam_index": 24.0, "weather_risk": 18.0, "health_risk": 14.0, "night_safety": 78.0, "crowd_density": 88.0, "transport_safety": 76.0},
        "tips": [
            "Book Bhasma Aarti online well in advance.",
            "Follow temple queue instructions; avoid agents.",
            "Simhastha Kumbh years bring extreme crowds."
        ],
        "emergency": [
            {"name": "Ujjain Kotwali", "type": "Police", "phone": "112", "address": "Ujjain", "lat": 23.1830, "lng": 75.7800},
            {"name": "RD Gardi Medical College Hospital", "type": "Hospital", "phone": "+91-734-2535555", "address": "Ujjain", "lat": 23.1700, "lng": 75.7900}
        ],
        "advisory": {"title": "Aarti Crowd Notice", "level": "Advisory", "summary": "Pre-dawn queues are dense — arrive as per pass timing."}
    },

    # =========================================================================
    # HIMACHAL / J&K
    # =========================================================================
    {
        "name": "Dharamshala & McLeod Ganj",
        "state": "Himachal Pradesh",
        "region": "North India",
        "category": "Mountain & Adventure",
        "lat": 32.2190,
        "lng": 76.3234,
        "overall_safety_score": 88,
        "risk_tier": "Low Risk (Safe)",
        "description": "Hill town and seat of the Tibetan government-in-exile, with Tsuglagkhang complex, Triund trek base, and panoramic Dhauladhar views.",
        "image_url": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "March to June & September to November",
        "dress_code_etiquette": "Modest attire at monasteries; layers for altitude.",
        "opening_time": "07:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:00 AM - 03:00 PM",
        "entry_fee_domestic": "Free (monastery donations welcome)",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 10.0, "scam_index": 14.0, "weather_risk": 30.0, "health_risk": 14.0, "night_safety": 86.0, "crowd_density": 50.0, "transport_safety": 72.0},
        "tips": [
            "Triund trek needs weather check — avoid during thunderstorms.",
            "Respect photography rules inside temples.",
            "Narrow McLeod lanes — walk or use local taxis."
        ],
        "emergency": [
            {"name": "McLeod Ganj Police Station", "type": "Police", "phone": "+91-1892-221346", "address": "McLeod Ganj", "lat": 32.2360, "lng": 76.3240},
            {"name": "Delek Hospital", "type": "Hospital", "phone": "+91-1892-222053", "address": "Gangchen Kyishong", "lat": 32.2250, "lng": 76.3200}
        ],
        "advisory": {"title": "Landslide Season", "level": "Advisory", "summary": "Monsoon roadblocks possible on Kangra approaches — check HP alerts."}
    },
    {
        "name": "Dalhousie",
        "state": "Himachal Pradesh",
        "region": "North India",
        "category": "Mountain & Adventure",
        "lat": 32.5387,
        "lng": 75.9710,
        "overall_safety_score": 87,
        "risk_tier": "Low Risk (Safe)",
        "description": "Colonial-era hill station in Chamba district with pine forests, Khajjiar meadows nearby, and quiet mall roads.",
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "March to June & September to November",
        "dress_code_etiquette": "Warm layers; sturdy shoes for walks.",
        "opening_time": "06:00",
        "closing_time": "19:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "11:00 AM - 03:00 PM",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 8.0, "scam_index": 12.0, "weather_risk": 28.0, "health_risk": 12.0, "night_safety": 88.0, "crowd_density": 40.0, "transport_safety": 70.0},
        "tips": [
            "Khajjiar day trip is popular — roads are winding.",
            "ATMs can run dry on long weekends — carry cash.",
            "Evenings get cold even in summer."
        ],
        "emergency": [
            {"name": "Dalhousie Police Station", "type": "Police", "phone": "+91-1899-242227", "address": "Dalhousie", "lat": 32.5390, "lng": 75.9710},
            {"name": "Civil Hospital Dalhousie", "type": "Hospital", "phone": "+91-1899-240234", "address": "Dalhousie", "lat": 32.5370, "lng": 75.9700}
        ],
        "advisory": {"title": "Winter Road Ice", "level": "Advisory", "summary": "Icy patches Dec–Feb — prefer daytime hill driving."}
    },
    {
        "name": "Kasol & Parvati Valley",
        "state": "Himachal Pradesh",
        "region": "North India",
        "category": "Mountain & Adventure",
        "lat": 32.0115,
        "lng": 77.3152,
        "overall_safety_score": 80,
        "risk_tier": "Low Risk (Safe)",
        "description": "Riverside village gateway to Parvati Valley treks (Kheerganga, Tosh) popular with backpackers amid pine forests and Himalayan streams.",
        "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "April to June & September to November",
        "dress_code_etiquette": "Trek-ready layers; respect local villages.",
        "opening_time": "06:00",
        "closing_time": "20:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "Weekends year-round",
        "entry_fee_domestic": "Free (trek permits where applicable)",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 14.0, "scam_index": 18.0, "weather_risk": 36.0, "health_risk": 16.0, "night_safety": 74.0, "crowd_density": 55.0, "transport_safety": 68.0},
        "tips": [
            "Register with local police for overnight treks when advised.",
            "River currents are strong — do not swim after rains.",
            "Stay in registered guesthouses."
        ],
        "emergency": [
            {"name": "Jari / Kasol Police Post", "type": "Police", "phone": "112", "address": "Parvati Valley", "lat": 32.0100, "lng": 77.3200},
            {"name": "Civil Hospital Bhuntar", "type": "Hospital", "phone": "+91-1902-265033", "address": "Bhuntar", "lat": 31.8750, "lng": 77.1500}
        ],
        "advisory": {"title": "River & Trail Safety", "level": "Warning", "summary": "Flash floods and trail slips possible in monsoon — check local advisories."}
    },
    {
        "name": "Pahalgam",
        "state": "Jammu & Kashmir",
        "region": "North India",
        "category": "Mountain & Adventure",
        "lat": 34.0161,
        "lng": 75.3150,
        "overall_safety_score": 81,
        "risk_tier": "Low Risk (Safe)",
        "description": "Lidder Valley town famous as a base for Amarnath Yatra, Betaab Valley, Aru, and scenic meadows of Kashmir.",
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "April to October",
        "dress_code_etiquette": "Warm layers; modest dress in local areas.",
        "opening_time": "07:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:00 AM - 03:00 PM",
        "entry_fee_domestic": "Free (valley taxi packages extra)",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 12.0, "scam_index": 20.0, "weather_risk": 34.0, "health_risk": 14.0, "night_safety": 78.0, "crowd_density": 50.0, "transport_safety": 70.0},
        "tips": [
            "Use only registered pony/taxi unions for Aru–Betaab circuits.",
            "Check latest travel advisories before planning.",
            "Carry ID — checkpoints are common on approach roads."
        ],
        "emergency": [
            {"name": "Pahalgam Police Station", "type": "Police", "phone": "112", "address": "Pahalgam", "lat": 34.0160, "lng": 75.3150},
            {"name": "Sub-District Hospital Pahalgam", "type": "Hospital", "phone": "108", "address": "Pahalgam", "lat": 34.0150, "lng": 75.3140}
        ],
        "advisory": {"title": "Travel Advisory Check", "level": "Advisory", "summary": "Verify current security and weather notices before travel."}
    },

    # =========================================================================
    # SOUTH INDIA
    # =========================================================================
    {
        "name": "Charminar Hyderabad",
        "state": "Telangana",
        "region": "South India",
        "category": "Heritage & Forts",
        "lat": 17.3616,
        "lng": 78.4747,
        "overall_safety_score": 82,
        "risk_tier": "Low Risk (Safe)",
        "description": "16th-century monument and mosque at the heart of Hyderabad's old city, surrounded by Laad Bazaar and the iconic Char Kaman arches.",
        "image_url": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Modest dress to enter upper mosque levels.",
        "opening_time": "09:00",
        "closing_time": "17:30",
        "weekly_off_day": "Friday",
        "peak_rush_hours": "10:00 AM - 01:00 PM & Evenings in bazaar",
        "entry_fee_domestic": "Rs 25",
        "entry_fee_foreign": "Rs 300",
        "booking_portal_url": "",
        "metrics": {"crime_index": 20.0, "scam_index": 26.0, "weather_risk": 18.0, "health_risk": 14.0, "night_safety": 72.0, "crowd_density": 80.0, "transport_safety": 76.0},
        "tips": [
            "Keep valuables secure in dense bazaar lanes.",
            "Combine with Mecca Masjid and Chowmahalla nearby.",
            "Friday prayer times affect access."
        ],
        "emergency": [
            {"name": "Charminar Police Station", "type": "Police", "phone": "112", "address": "Old City, Hyderabad", "lat": 17.3620, "lng": 78.4750},
            {"name": "Osmania General Hospital", "type": "Hospital", "phone": "+91-40-24600146", "address": "Afzalgunj", "lat": 17.3750, "lng": 78.4750}
        ],
        "advisory": {"title": "Crowd & Pickpocket Caution", "level": "Advisory", "summary": "High footfall evenings — use zipped bags."}
    },
    {
        "name": "Golconda Fort",
        "state": "Telangana",
        "region": "South India",
        "category": "Heritage & Forts",
        "lat": 17.3833,
        "lng": 78.4011,
        "overall_safety_score": 85,
        "risk_tier": "Low Risk (Safe)",
        "description": "Historic Qutb Shahi fort west of Hyderabad, famous for acoustic architecture, rampart views, and evening sound-and-light shows.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Walking shoes; light clothing.",
        "opening_time": "09:00",
        "closing_time": "17:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:00 AM - 01:00 PM",
        "entry_fee_domestic": "Rs 25",
        "entry_fee_foreign": "Rs 300",
        "booking_portal_url": "",
        "metrics": {"crime_index": 14.0, "scam_index": 16.0, "weather_risk": 20.0, "health_risk": 12.0, "night_safety": 70.0, "crowd_density": 55.0, "transport_safety": 78.0},
        "tips": [
            "Climb early to avoid midday heat on the citadel.",
            "Book sound-and-light tickets separately if offered.",
            "Carry water — limited vendors inside upper levels."
        ],
        "emergency": [
            {"name": "Golconda Police Station", "type": "Police", "phone": "112", "address": "Golconda", "lat": 17.3840, "lng": 78.4020},
            {"name": "Care Hospitals Banjara Hills", "type": "Hospital", "phone": "+91-40-30418888", "address": "Hyderabad", "lat": 17.4150, "lng": 78.4480}
        ],
        "advisory": {"title": "Heat Advisory", "level": "Advisory", "summary": "Exposed stone climbs — avoid noon in summer."}
    },
    {
        "name": "Coorg (Kodagu)",
        "state": "Karnataka",
        "region": "South India",
        "category": "Wildlife & Nature",
        "lat": 12.3375,
        "lng": 75.8069,
        "overall_safety_score": 88,
        "risk_tier": "Low Risk (Safe)",
        "description": "Coffee-country hill region of Karnataka with Abbey Falls, Raja's Seat (Madikeri), and misty plantation stays.",
        "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Light woolens evenings; rain gear in monsoon.",
        "opening_time": "06:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:00 AM - 03:00 PM",
        "entry_fee_domestic": "Free (falls/park fees vary)",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 8.0, "scam_index": 12.0, "weather_risk": 30.0, "health_risk": 12.0, "night_safety": 88.0, "crowd_density": 45.0, "transport_safety": 74.0},
        "tips": [
            "Book homestays early for December weekends.",
            "Leeches common on monsoon trails — wear socks over pants.",
            "Self-drive roads are winding; avoid night ghat driving."
        ],
        "emergency": [
            {"name": "Madikeri Police Station", "type": "Police", "phone": "112", "address": "Madikeri", "lat": 12.4240, "lng": 75.7380},
            {"name": "District Hospital Madikeri", "type": "Hospital", "phone": "+91-8272-228370", "address": "Madikeri", "lat": 12.4200, "lng": 75.7400}
        ],
        "advisory": {"title": "Monsoon Landslides", "level": "Advisory", "summary": "Heavy rain can close plantation roads — check local updates."}
    },
    {
        "name": "Gokarna Beach",
        "state": "Karnataka",
        "region": "South India",
        "category": "Beach & Coastal",
        "lat": 14.5479,
        "lng": 74.3188,
        "overall_safety_score": 85,
        "risk_tier": "Low Risk (Safe)",
        "description": "Temple town and beach circuit (Om, Kudle, Half Moon) offering a quieter coastal alternative to Goa along the Arabian Sea.",
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to February",
        "dress_code_etiquette": "Modest dress in temple town; beachwear on beaches only.",
        "opening_time": "06:00",
        "closing_time": "19:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "11:00 AM - 04:00 PM",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 10.0, "scam_index": 14.0, "weather_risk": 24.0, "health_risk": 12.0, "night_safety": 78.0, "crowd_density": 50.0, "transport_safety": 72.0},
        "tips": [
            "Cliff paths to Om Beach can be slippery after rain.",
            "Respect temple town norms near Mahabaleshwar Temple.",
            "Swim with caution — limited lifeguard coverage."
        ],
        "emergency": [
            {"name": "Gokarna Police Station", "type": "Police", "phone": "112", "address": "Gokarna", "lat": 14.5480, "lng": 74.3190},
            {"name": "Community Health Centre Gokarna", "type": "Hospital", "phone": "108", "address": "Gokarna", "lat": 14.5460, "lng": 74.3170}
        ],
        "advisory": {"title": "Cliff Path Caution", "level": "Warning", "summary": "Use marked trails between beaches; avoid night cliff walks."}
    },
    {
        "name": "Fort Kochi",
        "state": "Kerala",
        "region": "South India",
        "category": "Urban & Culture",
        "lat": 9.9658,
        "lng": 76.2422,
        "overall_safety_score": 89,
        "risk_tier": "Low Risk (Safe)",
        "description": "Historic harbour quarter of Kochi with Chinese fishing nets, colonial churches, spice markets, and waterfront promenades.",
        "image_url": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Casual; modest dress in churches.",
        "opening_time": "06:00",
        "closing_time": "21:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "04:00 PM - 07:00 PM",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 12.0, "scam_index": 16.0, "weather_risk": 20.0, "health_risk": 12.0, "night_safety": 84.0, "crowd_density": 60.0, "transport_safety": 82.0},
        "tips": [
            "Sunset at Chinese nets is crowded — arrive early for photos.",
            "Use prepaid autos or Metro where available from Ernakulam.",
            "Ferry hops are scenic and cheap."
        ],
        "emergency": [
            {"name": "Fort Kochi Police Station", "type": "Police", "phone": "112", "address": "Fort Kochi", "lat": 9.9660, "lng": 76.2430},
            {"name": "General Hospital Ernakulam", "type": "Hospital", "phone": "+91-484-2361120", "address": "Ernakulam", "lat": 9.9800, "lng": 76.2800}
        ],
        "advisory": {"title": "Monsoon Squalls", "level": "Advisory", "summary": "Harbour winds strengthen in June–September evenings."}
    },
    {
        "name": "Varkala Cliff Beach",
        "state": "Kerala",
        "region": "South India",
        "category": "Beach & Coastal",
        "lat": 8.7379,
        "lng": 76.7163,
        "overall_safety_score": 84,
        "risk_tier": "Low Risk (Safe)",
        "description": "Dramatic laterite cliffs above the Arabian Sea with Papanasam Beach, cliff-top cafes, and Janardanaswamy Temple nearby.",
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to February",
        "dress_code_etiquette": "Modest near temple; beachwear on beach only.",
        "opening_time": "06:00",
        "closing_time": "19:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "04:00 PM - 06:30 PM",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 12.0, "scam_index": 16.0, "weather_risk": 26.0, "health_risk": 12.0, "night_safety": 76.0, "crowd_density": 55.0, "transport_safety": 74.0},
        "tips": [
            "Cliff edges can crumble — stay behind railings.",
            "Strong currents — swim only in allowed zones.",
            "Stairs to beach are steep after rain."
        ],
        "emergency": [
            {"name": "Varkala Police Station", "type": "Police", "phone": "112", "address": "Varkala", "lat": 8.7380, "lng": 76.7170},
            {"name": "Government Hospital Varkala", "type": "Hospital", "phone": "108", "address": "Varkala", "lat": 8.7400, "lng": 76.7200}
        ],
        "advisory": {"title": "Cliff Safety", "level": "Warning", "summary": "Do not sit on unprotected cliff lips for photos."}
    },
    {
        "name": "Kovalam Beach",
        "state": "Kerala",
        "region": "South India",
        "category": "Beach & Coastal",
        "lat": 8.4004,
        "lng": 76.9787,
        "overall_safety_score": 85,
        "risk_tier": "Low Risk (Safe)",
        "description": "Crescent beaches south of Thiruvananthapuram with Lighthouse Beach, Ayurveda resorts, and a lively promenade.",
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Beachwear on shore; cover-ups in markets.",
        "opening_time": "06:00",
        "closing_time": "19:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "04:00 PM - 06:30 PM",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 12.0, "scam_index": 18.0, "weather_risk": 24.0, "health_risk": 12.0, "night_safety": 78.0, "crowd_density": 60.0, "transport_safety": 76.0},
        "tips": [
            "Swim between lifeguard flags only.",
            "Negotiate auto fares from Trivandrum airport beforehand.",
            "Lighthouse viewpoint has a small entry fee."
        ],
        "emergency": [
            {"name": "Kovalam Police Station", "type": "Police", "phone": "112", "address": "Kovalam", "lat": 8.4010, "lng": 76.9790},
            {"name": "KIMS Hospital Trivandrum", "type": "Hospital", "phone": "+91-471-3041000", "address": "Thiruvananthapuram", "lat": 8.5200, "lng": 76.9400}
        ],
        "advisory": {"title": "Rip Current Notice", "level": "Warning", "summary": "Monsoon seas are rough — heed red flags."}
    },
    {
        "name": "Marina Beach Chennai",
        "state": "Tamil Nadu",
        "region": "South India",
        "category": "Beach & Coastal",
        "lat": 13.0500,
        "lng": 80.2824,
        "overall_safety_score": 78,
        "risk_tier": "Low Risk (Safe)",
        "description": "One of the world's longest urban beaches along the Bay of Bengal, with promenade walks, memorials, and evening street food culture.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to February",
        "dress_code_etiquette": "Casual; avoid isolated stretches late night.",
        "opening_time": "05:00",
        "closing_time": "22:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "05:00 PM - 09:00 PM",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 24.0, "scam_index": 22.0, "weather_risk": 22.0, "health_risk": 14.0, "night_safety": 68.0, "crowd_density": 85.0, "transport_safety": 78.0},
        "tips": [
            "Swimming is often prohibited due to undertow — obey boards.",
            "Keep phones secure in evening crowds.",
            "Prefer lit promenade zones after dark."
        ],
        "emergency": [
            {"name": "Marina Police Station", "type": "Police", "phone": "112", "address": "Chennai", "lat": 13.0550, "lng": 80.2800},
            {"name": "Rajiv Gandhi Government General Hospital", "type": "Hospital", "phone": "+91-44-25305000", "address": "Park Town", "lat": 13.0800, "lng": 80.2750}
        ],
        "advisory": {"title": "No-Swim Zones", "level": "Warning", "summary": "Strong currents — swimming often banned; follow police notices."}
    },
    {
        "name": "Mahabalipuram (Mamallapuram)",
        "state": "Tamil Nadu",
        "region": "South India",
        "category": "Heritage & Forts",
        "lat": 12.6208,
        "lng": 80.1945,
        "overall_safety_score": 86,
        "risk_tier": "Low Risk (Safe)",
        "description": "UNESCO Group of Monuments including Shore Temple and Pancha Rathas along the Coromandel Coast near Chennai.",
        "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to February",
        "dress_code_etiquette": "Comfortable shoes; modest clothing at temples.",
        "opening_time": "06:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "09:00 AM - 12:00 PM",
        "entry_fee_domestic": "Rs 40",
        "entry_fee_foreign": "Rs 600",
        "booking_portal_url": "https://asi.payumoney.com",
        "metrics": {"crime_index": 12.0, "scam_index": 18.0, "weather_risk": 18.0, "health_risk": 12.0, "night_safety": 76.0, "crowd_density": 55.0, "transport_safety": 78.0},
        "tips": [
            "ASI combo ticket covers major monuments.",
            "Sunrise at Shore Temple is popular with photographers.",
            "Stone carvers' streets — agree prices before buying."
        ],
        "emergency": [
            {"name": "Mahabalipuram Police Station", "type": "Police", "phone": "112", "address": "Mamallapuram", "lat": 12.6210, "lng": 80.1950},
            {"name": "Government Hospital Chengalpattu", "type": "Hospital", "phone": "108", "address": "Chengalpattu", "lat": 12.6900, "lng": 79.9700}
        ],
        "advisory": {"title": "Coastal Heat", "level": "Advisory", "summary": "Limited shade at open monuments — visit early morning."}
    },
    {
        "name": "Kodaikanal",
        "state": "Tamil Nadu",
        "region": "South India",
        "category": "Mountain & Adventure",
        "lat": 10.2381,
        "lng": 77.4892,
        "overall_safety_score": 87,
        "risk_tier": "Low Risk (Safe)",
        "description": "Palani Hills resort town with Kodai Lake, Coaker's Walk, Pillar Rocks, and cool climate escapes from the plains.",
        "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "April to June & September to November",
        "dress_code_etiquette": "Light woolens; rain jacket in monsoon.",
        "opening_time": "06:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:00 AM - 03:00 PM",
        "entry_fee_domestic": "Free (viewpoint fees vary)",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 10.0, "scam_index": 14.0, "weather_risk": 28.0, "health_risk": 10.0, "night_safety": 86.0, "crowd_density": 55.0, "transport_safety": 72.0},
        "tips": [
            "Ghat roads from plains are hairpin-heavy — prefer daylight arrival.",
            "Boating on Kodai Lake via licensed operators only.",
            "Weekend traffic around the lake is heavy."
        ],
        "emergency": [
            {"name": "Kodaikanal Police Station", "type": "Police", "phone": "112", "address": "Kodaikanal", "lat": 10.2380, "lng": 77.4900},
            {"name": "Van Allen Hospital", "type": "Hospital", "phone": "+91-4542-241242", "address": "Kodaikanal", "lat": 10.2360, "lng": 77.4880}
        ],
        "advisory": {"title": "Fog & Ghat Caution", "level": "Advisory", "summary": "Dense fog reduces visibility on approach roads in monsoon."}
    },

    # =========================================================================
    # EAST / NORTH-EAST
    # =========================================================================
    {
        "name": "Konark Sun Temple",
        "state": "Odisha",
        "region": "East & North-East India",
        "category": "Heritage & Forts",
        "lat": 19.8876,
        "lng": 86.0945,
        "overall_safety_score": 86,
        "risk_tier": "Low Risk (Safe)",
        "description": "13th-century UNESCO chariot temple dedicated to the Sun God, renowned for intricate stone wheels and erotic sculptures near the Odisha coast.",
        "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Modest attire; respectful photography.",
        "opening_time": "06:00",
        "closing_time": "20:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "09:00 AM - 12:00 PM",
        "entry_fee_domestic": "Rs 40",
        "entry_fee_foreign": "Rs 600",
        "booking_portal_url": "https://asi.payumoney.com",
        "metrics": {"crime_index": 10.0, "scam_index": 14.0, "weather_risk": 18.0, "health_risk": 12.0, "night_safety": 78.0, "crowd_density": 50.0, "transport_safety": 76.0},
        "tips": [
            "Combine with Puri Jagannath Temple (already in dataset) as a day circuit.",
            "Evening light-and-sound shows run seasonally.",
            "Guides should be ASI-approved."
        ],
        "emergency": [
            {"name": "Konark Police Station", "type": "Police", "phone": "112", "address": "Konark", "lat": 19.8880, "lng": 86.0950},
            {"name": "District Headquarters Hospital Puri", "type": "Hospital", "phone": "+91-6752-222062", "address": "Puri", "lat": 19.8100, "lng": 85.8300}
        ],
        "advisory": {"title": "Cyclone Season", "level": "Advisory", "summary": "Coastal storms possible May–November — check IMD alerts."}
    },
    {
        "name": "Victoria Memorial Kolkata",
        "state": "West Bengal",
        "region": "East & North-East India",
        "category": "Urban & Culture",
        "lat": 22.5448,
        "lng": 88.3426,
        "overall_safety_score": 85,
        "risk_tier": "Low Risk (Safe)",
        "description": "White marble museum-memorial in the heart of Kolkata set in formal gardens, showcasing colonial-era art and history exhibitions.",
        "image_url": "https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Casual; no loud behaviour in galleries.",
        "opening_time": "10:00",
        "closing_time": "17:00",
        "weekly_off_day": "Monday",
        "peak_rush_hours": "11:00 AM - 02:00 PM",
        "entry_fee_domestic": "Rs 30",
        "entry_fee_foreign": "Rs 500",
        "booking_portal_url": "",
        "metrics": {"crime_index": 18.0, "scam_index": 16.0, "weather_risk": 16.0, "health_risk": 12.0, "night_safety": 74.0, "crowd_density": 60.0, "transport_safety": 80.0},
        "tips": [
            "Gardens open earlier than the museum building.",
            "Closed Mondays — plan accordingly.",
            "Use Metro Maidan / Esplanade and walk or short cab."
        ],
        "emergency": [
            {"name": "New Market Police Station", "type": "Police", "phone": "112", "address": "Kolkata", "lat": 22.5600, "lng": 88.3500},
            {"name": "SSKM Hospital", "type": "Hospital", "phone": "+91-33-22041100", "address": "Kolkata", "lat": 22.5400, "lng": 88.3400}
        ],
        "advisory": {"title": "Monday Closure", "level": "Advisory", "summary": "Museum closed Mondays; gardens may remain open with separate rules."}
    },
    {
        "name": "Gangtok",
        "state": "Sikkim",
        "region": "East & North-East India",
        "category": "Mountain & Adventure",
        "lat": 27.3389,
        "lng": 88.6065,
        "overall_safety_score": 90,
        "risk_tier": "Low Risk (Safe)",
        "description": "Capital of Sikkim with MG Marg pedestrian street, monasteries, and gateway access to high-altitude lakes and passes.",
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "March to June & September to November",
        "dress_code_etiquette": "Warm layers; modest dress at monasteries.",
        "opening_time": "07:00",
        "closing_time": "20:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:00 AM - 04:00 PM",
        "entry_fee_domestic": "Free (inner-line permits for some circuits)",
        "entry_fee_foreign": "Permit rules apply for restricted areas",
        "booking_portal_url": "",
        "metrics": {"crime_index": 6.0, "scam_index": 10.0, "weather_risk": 28.0, "health_risk": 14.0, "night_safety": 92.0, "crowd_density": 45.0, "transport_safety": 74.0},
        "tips": [
            "Shared taxis from Siliguri/NJP are the usual approach.",
            "Plastic bans are strict — carry reusable bottles.",
            "Altitude day trips need permits — book via registered travel agents."
        ],
        "emergency": [
            {"name": "Gangtok Sadar Police Station", "type": "Police", "phone": "112", "address": "Gangtok", "lat": 27.3390, "lng": 88.6070},
            {"name": "STNM Hospital", "type": "Hospital", "phone": "+91-3592-202944", "address": "Gangtok", "lat": 27.3300, "lng": 88.6100}
        ],
        "advisory": {"title": "Permit Requirements", "level": "Advisory", "summary": "Protected Area Permits needed for Nathula / some north Sikkim routes."}
    },
    {
        "name": "Tsomgo (Changu) Lake",
        "state": "Sikkim",
        "region": "East & North-East India",
        "category": "Mountain & Adventure",
        "lat": 27.3753,
        "lng": 88.7630,
        "overall_safety_score": 82,
        "risk_tier": "Low Risk (Safe)",
        "description": "Glacial lake at about 3,750 m on the Gangtok–Nathula road, popular for day trips with yak rides and snow in winter.",
        "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "April to June & October to December",
        "dress_code_etiquette": "Heavy warm clothing; sunglasses for snow glare.",
        "opening_time": "08:00",
        "closing_time": "15:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:00 AM - 01:00 PM",
        "entry_fee_domestic": "Permit + vehicle package",
        "entry_fee_foreign": "Restricted — check permit rules",
        "booking_portal_url": "",
        "metrics": {"crime_index": 4.0, "scam_index": 12.0, "weather_risk": 40.0, "health_risk": 22.0, "night_safety": 70.0, "crowd_density": 55.0, "transport_safety": 68.0},
        "tips": [
            "Book only through registered Gangtok travel agents for permits.",
            "Altitude sickness possible — ascend slowly, avoid alcohol.",
            "Roads may close after heavy snow or landslides."
        ],
        "emergency": [
            {"name": "Kyongnosla Check Post", "type": "Police", "phone": "112", "address": "East Sikkim", "lat": 27.3700, "lng": 88.7500},
            {"name": "STNM Hospital Gangtok", "type": "Hospital", "phone": "+91-3592-202944", "address": "Gangtok", "lat": 27.3300, "lng": 88.6100}
        ],
        "advisory": {"title": "High Altitude Caution", "level": "Warning", "summary": "Carry warm layers; report dizziness to drivers immediately."}
    },
    {
        "name": "Kamakhya Temple",
        "state": "Assam",
        "region": "East & North-East India",
        "category": "Spiritual & Sacred",
        "lat": 26.1664,
        "lng": 91.7055,
        "overall_safety_score": 83,
        "risk_tier": "Low Risk (Safe)",
        "description": "Revered Shakti Peetha on Nilachal Hill in Guwahati, especially thronged during Ambubachi Mela.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Traditional modest attire; footwear removed.",
        "opening_time": "05:30",
        "closing_time": "22:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "Ambubachi Mela & mornings",
        "entry_fee_domestic": "Free (special darshan tickets vary)",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 14.0, "scam_index": 20.0, "weather_risk": 22.0, "health_risk": 14.0, "night_safety": 76.0, "crowd_density": 85.0, "transport_safety": 74.0},
        "tips": [
            "Ambubachi week is extremely crowded — book stays early.",
            "Use prepaid taxis from Guwahati airport/railway.",
            "Hill approach road is steep and narrow."
        ],
        "emergency": [
            {"name": "Jalukbari Police Station", "type": "Police", "phone": "112", "address": "Guwahati", "lat": 26.1500, "lng": 91.6800},
            {"name": "GMCH Guwahati", "type": "Hospital", "phone": "+91-361-2529457", "address": "Bhangagarh", "lat": 26.1600, "lng": 91.7700}
        ],
        "advisory": {"title": "Festival Crowd Notice", "level": "Advisory", "summary": "Expect multi-hour queues during Ambubachi Mela."}
    },
    {
        "name": "Ranthambore National Park",
        "state": "Rajasthan",
        "region": "West India",
        "category": "Wildlife & Nature",
        "lat": 26.0173,
        "lng": 76.5026,
        "overall_safety_score": 84,
        "risk_tier": "Low Risk (Safe)",
        "description": "Premier tiger reserve around Ranthambore Fort near Sawai Madhopur, offering jeep and canter safaris through dry deciduous forest.",
        "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to April",
        "dress_code_etiquette": "Earth-tone clothing; quiet behaviour on safari.",
        "opening_time": "06:00",
        "closing_time": "16:30",
        "weekly_off_day": "Wednesday",
        "peak_rush_hours": "Morning safari slots",
        "entry_fee_domestic": "Safari permit required",
        "entry_fee_foreign": "Safari permit required (higher fee)",
        "booking_portal_url": "https://www.rajasthanwildlife.in",
        "metrics": {"crime_index": 8.0, "scam_index": 16.0, "weather_risk": 22.0, "health_risk": 14.0, "night_safety": 80.0, "crowd_density": 50.0, "transport_safety": 76.0},
        "tips": [
            "Book safari zones online well ahead of weekends.",
            "Do not stand up or shout during jeep rides.",
            "Park closed in peak monsoon — verify season dates."
        ],
        "emergency": [
            {"name": "Sawai Madhopur Police", "type": "Police", "phone": "112", "address": "Sawai Madhopur", "lat": 26.0200, "lng": 76.3500},
            {"name": "Government Hospital Sawai Madhopur", "type": "Hospital", "phone": "108", "address": "Sawai Madhopur", "lat": 26.0180, "lng": 76.3400}
        ],
        "advisory": {"title": "Wildlife Buffer Rules", "level": "Advisory", "summary": "Stay inside vehicles; feeding animals is illegal."}
    },
    {
        "name": "Jim Corbett National Park",
        "state": "Uttarakhand",
        "region": "North India",
        "category": "Wildlife & Nature",
        "lat": 29.5300,
        "lng": 78.7747,
        "overall_safety_score": 85,
        "risk_tier": "Low Risk (Safe)",
        "description": "India's oldest national park in the foothills of the Himalayas, renowned for Bengal tigers, elephants, and the Ramganga river landscape.",
        "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to June",
        "dress_code_etiquette": "Muted colours on safari; no plastics littering.",
        "opening_time": "06:00",
        "closing_time": "16:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "Morning safari",
        "entry_fee_domestic": "Safari permit required",
        "entry_fee_foreign": "Safari permit required",
        "booking_portal_url": "https://www.corbettonline.uk.gov.in",
        "metrics": {"crime_index": 8.0, "scam_index": 14.0, "weather_risk": 24.0, "health_risk": 14.0, "night_safety": 78.0, "crowd_density": 50.0, "transport_safety": 74.0},
        "tips": [
            "Book Dhikala / Bijrani zones via official portal only.",
            "Night driving inside core zones is restricted.",
            "Carry mosquito repellent for lodge stays."
        ],
        "emergency": [
            {"name": "Ramnagar Police Station", "type": "Police", "phone": "112", "address": "Ramnagar", "lat": 29.4000, "lng": 79.1300},
            {"name": "Government Hospital Ramnagar", "type": "Hospital", "phone": "108", "address": "Ramnagar", "lat": 29.3950, "lng": 79.1250}
        ],
        "advisory": {"title": "Safari Rules", "level": "Advisory", "summary": "Follow guide instructions; alighting in core zones is prohibited."}
    },
    {
        "name": "Pondicherry (Puducherry) Promenade",
        "state": "Puducherry (UT)",
        "region": "South India",
        "category": "Urban & Culture",
        "lat": 11.9338,
        "lng": 79.8298,
        "overall_safety_score": 88,
        "risk_tier": "Low Risk (Safe)",
        "description": "French Quarter seaside boulevard with colourful colonial streets, cafes, and the Sri Aurobindo Ashram nearby.",
        "image_url": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to February",
        "dress_code_etiquette": "Casual; modest dress at ashram.",
        "opening_time": "06:00",
        "closing_time": "22:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "05:00 PM - 08:00 PM",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 12.0, "scam_index": 14.0, "weather_risk": 20.0, "health_risk": 10.0, "night_safety": 84.0, "crowd_density": 55.0, "transport_safety": 80.0},
        "tips": [
            "Promenade is pedestrian-friendly at evenings.",
            "Rent cycles to explore White Town lanes.",
            "Swimming on main beach is often unsafe — use designated areas."
        ],
        "emergency": [
            {"name": "Grand Bazaar Police Station", "type": "Police", "phone": "112", "address": "Puducherry", "lat": 11.9350, "lng": 79.8300},
            {"name": "IGGH Puducherry", "type": "Hospital", "phone": "+91-413-2336082", "address": "Puducherry", "lat": 11.9400, "lng": 79.8200}
        ],
        "advisory": {"title": "Cyclone Watch", "level": "Advisory", "summary": "Bay of Bengal cyclones can affect the coast Oct–Dec."}
    },
    {
        "name": "Somnath Temple",
        "state": "Gujarat",
        "region": "West India",
        "category": "Spiritual & Sacred",
        "lat": 20.8880,
        "lng": 70.4012,
        "overall_safety_score": 86,
        "risk_tier": "Low Risk (Safe)",
        "description": "Sacred Jyotirlinga temple on the Arabian Sea coast at Prabhas Patan, rebuilt in the 20th century with a striking seafront setting.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Traditional modest attire; security screening mandatory.",
        "opening_time": "06:00",
        "closing_time": "21:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "06:00 AM - 10:00 AM & Evenings",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "https://somnath.org",
        "metrics": {"crime_index": 10.0, "scam_index": 14.0, "weather_risk": 20.0, "health_risk": 12.0, "night_safety": 84.0, "crowd_density": 70.0, "transport_safety": 78.0},
        "tips": [
            "Mobile phones restricted in inner sanctum — use lockers.",
            "Sound-and-light show tickets sell out on holidays.",
            "Combine with nearby Veraval / Gir circuits if wildlife interests you."
        ],
        "emergency": [
            {"name": "Prabhas Patan Police", "type": "Police", "phone": "112", "address": "Somnath", "lat": 20.8880, "lng": 70.4010},
            {"name": "Government Hospital Veraval", "type": "Hospital", "phone": "108", "address": "Veraval", "lat": 20.9100, "lng": 70.3700}
        ],
        "advisory": {"title": "Security Screening", "level": "Advisory", "summary": "Arrive early on Mondays and festivals for darshan queues."}
    },
    {
        "name": "Dwarka: Dwarkadhish Temple",
        "state": "Gujarat",
        "region": "West India",
        "category": "Spiritual & Sacred",
        "lat": 22.2376,
        "lng": 68.9674,
        "overall_safety_score": 85,
        "risk_tier": "Low Risk (Safe)",
        "description": "Ancient Krishna temple town on Gujarat's western tip, one of the Char Dham pilgrimage sites with Gomti Ghat and Bet Dwarka ferry access.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Traditional dress preferred; footwear outside temple.",
        "opening_time": "06:30",
        "closing_time": "21:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "Morning & evening aarti",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "",
        "metrics": {"crime_index": 10.0, "scam_index": 16.0, "weather_risk": 22.0, "health_risk": 12.0, "night_safety": 82.0, "crowd_density": 75.0, "transport_safety": 76.0},
        "tips": [
            "Bet Dwarka requires ferry — check last return boat timing.",
            "Janmashtami crowds are extreme; book lodging early.",
            "Sea breeze is strong — secure hats/scarves on ghat."
        ],
        "emergency": [
            {"name": "Dwarka Police Station", "type": "Police", "phone": "112", "address": "Dwarka", "lat": 22.2380, "lng": 68.9680},
            {"name": "Government Hospital Dwarka", "type": "Hospital", "phone": "108", "address": "Dwarka", "lat": 22.2400, "lng": 68.9700}
        ],
        "advisory": {"title": "Ferry Timing", "level": "Advisory", "summary": "Bet Dwarka ferries pause in rough seas — confirm with port staff."}
    },
]
