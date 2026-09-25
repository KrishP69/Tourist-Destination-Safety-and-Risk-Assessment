import json
from .database import get_db, init_db
from .auth import hash_password
from .seed_destinations_extra import ADDITIONAL_INDIA_DESTINATIONS

INDIA_DESTINATIONS = [
    # =========================================================================
    # NORTH INDIA
    # =========================================================================
    {
        "name": "Taj Mahal & Agra Fort",
        "state": "Uttar Pradesh",
        "region": "North India",
        "category": "Heritage & Forts",
        "lat": 27.1751,
        "lng": 78.0421,
        "overall_safety_score": 82,
        "risk_tier": "Low Risk (Safe)",
        "description": "UNESCO World Heritage wonder of pristine ivory-white marble commissioned in 1632 by Mughal Emperor Shah Jahan. One of the Seven Wonders of the World.",
        "image_url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Modest clothing required. Shoe covers mandatory on main mausoleum plinth.",
        "opening_time": "06:00",
        "closing_time": "18:30",
        "weekly_off_day": "Friday",
        "peak_rush_hours": "10:00 AM - 03:30 PM",
        "entry_fee_domestic": "Rs 50 (+ Rs 200 for mausoleum)",
        "entry_fee_foreign": "Rs 1100 (+ Rs 200 for mausoleum)",
        "booking_portal_url": "https://asi.payumoney.com",
        "metrics": {"crime_index": 24.0, "scam_index": 35.0, "weather_risk": 15.0, "health_risk": 14.0, "night_safety": 78.0, "crowd_density": 85.0, "transport_safety": 80.0},
        "tips": [
            "Book tickets exclusively via official ASI portal (asi.payumoney.com) to avoid invalid paper barcodes.",
            "Taj Mahal is closed every Friday for prayers. Plan your schedule accordingly.",
            "Sunrise slot (06:00 AM) provides lowest crowds and best natural photography light."
        ],
        "emergency": [
            {"name": "Taj Tourist Police Station", "type": "Police", "phone": "+91-562-2421204", "address": "East Gate, Taj Mahal, Agra", "lat": 27.1730, "lng": 78.0450},
            {"name": "SN Medical College Hospital Agra", "type": "Hospital", "phone": "+91-562-2260353", "address": "Hospital Road, Agra", "lat": 27.1850, "lng": 78.0120}
        ],
        "advisory": {"title": "Friday Closure & Sunrise Peak Notice", "level": "Advisory", "summary": "Closed on all Fridays. High tourist queues between 11 AM and 3 PM."}
    },
    {
        "name": "Varanasi Ghats & Kashi Vishwanath",
        "state": "Uttar Pradesh",
        "region": "North India",
        "category": "Spiritual & Sacred",
        "lat": 25.3109,
        "lng": 83.0107,
        "overall_safety_score": 79,
        "risk_tier": "Low Risk (Safe)",
        "description": "The spiritual capital of India on the sacred River Ganges. Famous for evening Ganga Aarti at Dashashwamedh Ghat and the ancient Kashi Vishwanath Jyotirlinga corridor.",
        "image_url": "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to February",
        "dress_code_etiquette": "Traditional Indian attire. Modest clothing covering shoulders and knees; footwear forbidden near ghat steps.",
        "opening_time": "03:00",
        "closing_time": "23:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "05:30 PM - 08:30 PM (Ganga Aarti)",
        "entry_fee_domestic": "Free (Sugam Darshan Rs 300)",
        "entry_fee_foreign": "Free (Sugam Darshan Rs 600)",
        "booking_portal_url": "https://shrikashivishwanath.org",
        "metrics": {"crime_index": 22.0, "scam_index": 38.0, "weather_risk": 16.0, "health_risk": 20.0, "night_safety": 76.0, "crowd_density": 92.0, "transport_safety": 74.0},
        "tips": [
            "Hold onto railings during evening Ganga Aarti; ghat steps become slippery from river silt.",
            "Hire only government-licensed boats with functional orange life jackets.",
            "Keep cash in inner zipped pockets when navigating congested Godowlia alleys."
        ],
        "emergency": [
            {"name": "Varanasi Tourist Police Post", "type": "Police", "phone": "+91-542-2508000", "address": "Dashashwamedh Ghat, Varanasi", "lat": 25.3080, "lng": 83.0110},
            {"name": "Sir Sunderlal Hospital (BHU)", "type": "Hospital", "phone": "+91-542-2369291", "address": "BHU Campus, Varanasi", "lat": 25.2750, "lng": 82.9980}
        ],
        "advisory": {"title": "River Undertow Caution", "level": "Warning", "summary": "Do not venture into mid-river deep channels outside designated bathing barricades."}
    },
    {
        "name": "Manali & Solang Valley",
        "state": "Himachal Pradesh",
        "region": "North India",
        "category": "Mountain & Adventure",
        "lat": 32.2396,
        "lng": 77.1887,
        "overall_safety_score": 78,
        "risk_tier": "Low Risk (Safe)",
        "description": "High-altitude Himalayan resort town nestled in the Beas River valley. Gateway for Rohtang Pass, Solang adventure sports, and the Atal Tunnel.",
        "image_url": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to June (Snow: Dec-Feb)",
        "dress_code_etiquette": "Heavy layered woolens in winter; comfortable trekking gear in summer.",
        "opening_time": "08:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:30 AM - 03:00 PM",
        "entry_fee_domestic": "Free (Activity charges vary)",
        "entry_fee_foreign": "Free (Activity charges vary)",
        "booking_portal_url": "https://rohtangpermits.nic.in",
        "metrics": {"crime_index": 12.0, "scam_index": 24.0, "weather_risk": 38.0, "health_risk": 18.0, "night_safety": 85.0, "crowd_density": 65.0, "transport_safety": 72.0},
        "tips": [
            "Obtain official Green Rohtang Pass permits in advance online.",
            "Check HP State Disaster Authority (HPSDMA) alerts for landslides during heavy monsoon rains.",
            "Paragliding operators must display valid HP Tourism licensing tags."
        ],
        "emergency": [
            {"name": "Manali Police Station", "type": "Police", "phone": "+91-1902-252322", "address": "Mall Road, Manali", "lat": 32.2420, "lng": 77.1890},
            {"name": "Civil Hospital Manali", "type": "Hospital", "phone": "+91-1902-253385", "address": "Model Town, Manali", "lat": 32.2410, "lng": 77.1870}
        ],
        "advisory": {"title": "Monsoon Landslide Preparedness", "level": "Warning", "summary": "Monitor NH-3 highway status during rains. Carry warm blankets and emergency food."}
    },
    {
        "name": "Leh & Pangong Tso",
        "state": "Ladakh (UT)",
        "region": "North India",
        "category": "Mountain & Adventure",
        "lat": 34.1526,
        "lng": 77.5771,
        "overall_safety_score": 75,
        "risk_tier": "Low Risk (Safe)",
        "description": "High-desert moonscape at 11,500+ feet with Tibetan Buddhist gompas, Khardung La pass, and the endorheic cobalt waters of Pangong Tso.",
        "image_url": "https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "May to September",
        "dress_code_etiquette": "Strictly modest clothing in Buddhist monasteries. Walk clockwise around chortens and mani stone walls.",
        "opening_time": "06:00",
        "closing_time": "19:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "11:00 AM - 02:30 PM",
        "entry_fee_domestic": "ILP Environmental Fee Rs 400",
        "entry_fee_foreign": "Protected Area Permit Fee Rs 500",
        "booking_portal_url": "https://lahdclehpermit.in",
        "metrics": {"crime_index": 8.0, "scam_index": 15.0, "weather_risk": 44.0, "health_risk": 42.0, "night_safety": 92.0, "crowd_density": 40.0, "transport_safety": 68.0},
        "tips": [
            "Mandatory 48-hour rest upon arrival by air for AMS acclimatization.",
            "Carry a portable pulse oximeter; consult a doctor for preventive Diamox.",
            "Inner Line Permit (ILP) required for Pangong, Nubra Valley, and Hanle."
        ],
        "emergency": [
            {"name": "Leh Tourist Police Desk", "type": "Police", "phone": "+91-1982-252018", "address": "Airport Road, Leh", "lat": 34.1500, "lng": 77.5750},
            {"name": "SNM Hospital Leh (Hyperbaric Chamber)", "type": "Hospital", "phone": "+91-1982-252014", "address": "Hospital Road, Leh", "lat": 34.1560, "lng": 77.5810}
        ],
        "advisory": {"title": "High Altitude AMS Medical Advisory", "level": "Warning", "summary": "Oxygen levels are ~35% lower than sea level. Avoid alcohol and heavy physical exertion during the first 48 hours."}
    },
    {
        "name": "Shimla & Kufri",
        "state": "Himachal Pradesh",
        "region": "North India",
        "category": "Mountain & Adventure",
        "lat": 31.1048,
        "lng": 77.1734,
        "overall_safety_score": 84,
        "risk_tier": "Low Risk (Safe)",
        "description": "Former summer capital of British India, celebrated for Mall Road, colonial Christ Church, pine-covered ridges, and the UNESCO Kalka-Shimla toy train.",
        "image_url": "https://images.unsplash.com/photo-1597074866923-dc0589150358?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "March to June & December to January",
        "dress_code_etiquette": "Smart casuals with sturdy walking footwear for pedestrian hill slopes.",
        "opening_time": "08:00",
        "closing_time": "22:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "04:30 PM - 08:30 PM (Mall Road)",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "https://himachaltourism.gov.in",
        "metrics": {"crime_index": 14.0, "scam_index": 20.0, "weather_risk": 25.0, "health_risk": 15.0, "night_safety": 88.0, "crowd_density": 80.0, "transport_safety": 78.0},
        "tips": [
            "Conceal shiny spectacles and food packets on Jakhoo Temple trail from rhesus monkeys.",
            "Vehicles are completely banned on Mall Road; use municipal elevator lifts.",
            "Winter roads around Kufri experience black ice; travel only with experienced mountain drivers."
        ],
        "emergency": [
            {"name": "Shimla Tourist Police Post", "type": "Police", "phone": "+91-177-2812344", "address": "Mall Road, Shimla", "lat": 31.1050, "lng": 77.1740},
            {"name": "Indira Gandhi Medical College (IGMC)", "type": "Hospital", "phone": "+91-177-2804251", "address": "Ridge Road, Shimla", "lat": 31.1100, "lng": 77.1800}
        ],
        "advisory": {"title": "Municipal Cleanliness Bylaws", "level": "Advisory", "summary": "Smoking and littering are strictly punishable by spot fines on Mall Road."}
    },
    {
        "name": "Rishikesh & Haridwar",
        "state": "Uttarakhand",
        "region": "North India",
        "category": "Spiritual & Sacred",
        "lat": 30.0869,
        "lng": 78.2676,
        "overall_safety_score": 81,
        "risk_tier": "Low Risk (Safe)",
        "description": "Yoga Capital of the World along the emerald Ganges, renowned for Ram Jhula suspension bridges, white-water rafting, and Parmarth Niketan aarti.",
        "image_url": "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "September to November & February to May",
        "dress_code_etiquette": "Loose cotton yoga wear; modest clothing in ashrams. Alcohol and non-vegetarian food strictly banned.",
        "opening_time": "05:00",
        "closing_time": "21:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "05:30 PM - 07:30 PM (Triveni Ghat Aarti)",
        "entry_fee_domestic": "Free (Rafting Rs 600 - 1500)",
        "entry_fee_foreign": "Free (Rafting Rs 600 - 1500)",
        "booking_portal_url": "https://uttarakhandtourism.gov.in",
        "metrics": {"crime_index": 16.0, "scam_index": 28.0, "weather_risk": 22.0, "health_risk": 16.0, "night_safety": 82.0, "crowd_density": 78.0, "transport_safety": 80.0},
        "tips": [
            "White-water rafting permitted only with operators certified by UTDB.",
            "Strong undertows exist outside designated bathing ghats; never swim in deep channels without life vests."
        ],
        "emergency": [
            {"name": "Rishikesh Police Station", "type": "Police", "phone": "+91-135-2430030", "address": "Haridwar Road, Rishikesh", "lat": 30.0900, "lng": 78.2700},
            {"name": "AIIMS Rishikesh Trauma Center", "type": "Hospital", "phone": "+91-135-2462940", "address": "Virbhadra Road, Rishikesh", "lat": 30.0750, "lng": 78.2850}
        ],
        "advisory": {"title": "River Safety Notice", "level": "Warning", "summary": "Rafting suspended when river discharge exceeds safety limits during heavy rainfall."}
    },
    {
        "name": "Amritsar: Golden Temple & Wagah",
        "state": "Punjab",
        "region": "North India",
        "category": "Spiritual & Sacred",
        "lat": 31.6200,
        "lng": 74.8765,
        "overall_safety_score": 89,
        "risk_tier": "Low Risk (Safe)",
        "description": "Sri Harmandir Sahib, the holiest Gurdwara of Sikhism covered in real gold leaf, famous for round-the-clock Langar serving 100,000+ meals daily with selfless hospitality.",
        "image_url": "https://images.unsplash.com/photo-1588096344356-9b57a1599557?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Head must be completely covered with cloth/scarf (rumal). Wash feet and hands in foot bath before entering the holy parikrama.",
        "opening_time": "00:00",
        "closing_time": "23:59",
        "weekly_off_day": "None",
        "peak_rush_hours": "04:30 AM (Palki Sahib) & 04:30 PM - 06:30 PM (Wagah Border)",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free",
        "booking_portal_url": "https://sgpc.net",
        "metrics": {"crime_index": 12.0, "scam_index": 16.0, "weather_risk": 15.0, "health_risk": 12.0, "night_safety": 92.0, "crowd_density": 88.0, "transport_safety": 85.0},
        "tips": [
            "Arrive 2 hours prior to Wagah Border Beating Retreat ceremony; grandstands fill rapidly.",
            "Free shoe deposit counters operate efficiently 24/7."
        ],
        "emergency": [
            {"name": "Amritsar Tourist Police Desk", "type": "Police", "phone": "+91-183-2550100", "address": "Heritage Street, Amritsar", "lat": 31.6210, "lng": 74.8780},
            {"name": "Sri Guru Ram Das Charitable Hospital", "type": "Hospital", "phone": "+91-183-2870200", "address": "Mehta Road, Amritsar", "lat": 31.6250, "lng": 74.8820}
        ],
        "advisory": {"title": "Langar Dining Protocol", "level": "Advisory", "summary": "All visitors dine equally seated on floor mats. Accept Karah Prasad with both hands held together."}
    },
    {
        "name": "Kedarnath & Badrinath (Char Dham)",
        "state": "Uttarakhand",
        "region": "North India",
        "category": "Spiritual & Sacred",
        "lat": 30.7346,
        "lng": 79.0669,
        "overall_safety_score": 68,
        "risk_tier": "Moderate Risk",
        "description": "Sacred Himalayan pilgrimage shrine situated at 11,755 ft amidst snow-capped peaks of the Garhwal Himalayas, revered by millions across India.",
        "image_url": "https://images.unsplash.com/photo-1626595639780-60a62453fbca?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "May to June & September to October (Closed winter)",
        "dress_code_etiquette": "Heavy sub-zero winter wear, waterproof raincoats, sturdy ankle-support trekking boots.",
        "opening_time": "04:00",
        "closing_time": "21:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "05:00 AM - 11:00 AM (Morning Darshan)",
        "entry_fee_domestic": "Biometric Registration Free",
        "entry_fee_foreign": "Biometric Registration Free",
        "booking_portal_url": "https://registrationandtouristcare.uk.gov.in",
        "metrics": {"crime_index": 6.0, "scam_index": 22.0, "weather_risk": 58.0, "health_risk": 48.0, "night_safety": 70.0, "crowd_density": 85.0, "transport_safety": 55.0},
        "tips": [
            "Mandatory biometric Char Dham registration before starting journey.",
            "16-km trek from Gaurikund to Kedarnath requires sound cardio fitness.",
            "Helicopter passes must only be booked through official IRCTC portal (heliyatra.irctc.co.in)."
        ],
        "emergency": [
            {"name": "SDRF Kedarnath Base Camp", "type": "Rescue", "phone": "+91-135-2410197", "address": "Kedarnath Temple Complex", "lat": 30.7350, "lng": 79.0670},
            {"name": "District Emergency Control Rudraprayag", "type": "Government", "phone": "+91-1364-233727", "address": "Rudraprayag Control Room", "lat": 30.2850, "lng": 78.9800}
        ],
        "advisory": {"title": "Sub-Zero Weather & Trekking Cutoff", "level": "Warning", "summary": "Trek beyond Lincholi closed after 4:30 PM for safety. Sudden hail and temperature drops under -2°C occur regularly."}
    },
    {
        "name": "Srinagar & Gulmarg",
        "state": "Jammu & Kashmir",
        "region": "North India",
        "category": "Mountain & Adventure",
        "lat": 34.0837,
        "lng": 74.7973,
        "overall_safety_score": 76,
        "risk_tier": "Low Risk (Safe)",
        "description": "Crown of Kashmir: iconic Dal Lake shikaras, floating vegetable markets, Mughal Nishat gardens, and Asia's highest cable car Gulmarg Gondola reaching 13,780 feet.",
        "image_url": "https://images.unsplash.com/photo-1598091383021-15ddea10925d?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "April to October (Spring/Summer), Dec to Feb (Skiing)",
        "dress_code_etiquette": "Modest clothing when visiting shrines like Hazratbal. Pheran and thermals in winter.",
        "opening_time": "09:00",
        "closing_time": "17:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:00 AM - 02:00 PM (Gondola Base)",
        "entry_fee_domestic": "Gondola Ph 1: Rs 740, Ph 2: Rs 950",
        "entry_fee_foreign": "Gondola Ph 1: Rs 740, Ph 2: Rs 950",
        "booking_portal_url": "https://www.jksaltc.com",
        "metrics": {"crime_index": 18.0, "scam_index": 32.0, "weather_risk": 35.0, "health_risk": 20.0, "night_safety": 78.0, "crowd_density": 65.0, "transport_safety": 75.0},
        "tips": [
            "Book Gulmarg Gondola Phase 1 & 2 passes weeks ahead via official portal.",
            "Pre-paid SIM cards from other states do not work in J&K; buy a local post-paid SIM or BSNL connection."
        ],
        "emergency": [
            {"name": "J&K Tourist Police Station Srinagar", "type": "Police", "phone": "+91-194-2452224", "address": "TRC Ground, Srinagar", "lat": 34.0750, "lng": 74.8100},
            {"name": "SMHS Hospital Srinagar", "type": "Hospital", "phone": "+91-194-2452013", "address": "Karan Nagar, Srinagar", "lat": 34.0900, "lng": 74.7950}
        ],
        "advisory": {"title": "Winter Ski Hazard Notice", "level": "Advisory", "summary": "Skiers heading to Apharwat peak must carry avalanche transceivers and hire certified snow guides."}
    },
    {
        "name": "Delhi: Red Fort & Qutub Minar",
        "state": "Delhi NCR",
        "region": "North India",
        "category": "Heritage & Forts",
        "lat": 28.6562,
        "lng": 77.2410,
        "overall_safety_score": 80,
        "risk_tier": "Low Risk (Safe)",
        "description": "The monumental capital of India, featuring Mughal red sandstone fortresses, UNESCO Qutub Minar complex, Humayun's Tomb, and legendary Old Delhi culinary lanes.",
        "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Smart casuals. Cover head and remove shoes at Gurdwara Bangla Sahib and Jama Masjid.",
        "opening_time": "07:00",
        "closing_time": "17:30",
        "weekly_off_day": "Monday",
        "peak_rush_hours": "11:00 AM - 04:00 PM",
        "entry_fee_domestic": "Rs 35 (Online) / Rs 50 (Cash)",
        "entry_fee_foreign": "Rs 550 (Online) / Rs 600 (Cash)",
        "booking_portal_url": "https://asi.payumoney.com",
        "metrics": {"crime_index": 28.0, "scam_index": 34.0, "weather_risk": 18.0, "health_risk": 22.0, "night_safety": 74.0, "crowd_density": 88.0, "transport_safety": 88.0},
        "tips": [
            "Use Delhi Metro (DMRC) for fast, air-conditioned, and traffic-free travel across all monuments.",
            "Red Fort is closed on Mondays for weekly maintenance."
        ],
        "emergency": [
            {"name": "Delhi Tourist Police Helpline", "type": "Police", "phone": "1031 / +91-11-23311231", "address": "Paharganj / CP, New Delhi", "lat": 28.6320, "lng": 77.2180},
            {"name": "AIIMS Delhi Emergency Trauma", "type": "Hospital", "phone": "+91-11-26588500", "address": "Ansari Nagar, New Delhi", "lat": 28.5670, "lng": 77.2100}
        ],
        "advisory": {"title": "Monday Monument Closure", "level": "Advisory", "summary": "Red Fort, Akshardham, and National Museum are closed every Monday."}
    },
    {
        "name": "Ayodhya: Shri Ram Mandir",
        "state": "Uttar Pradesh",
        "region": "North India",
        "category": "Spiritual & Sacred",
        "lat": 26.7956,
        "lng": 82.1943,
        "overall_safety_score": 85,
        "risk_tier": "Low Risk (Safe)",
        "description": "Grand Nagara-style stone temple on the banks of Saryu River, dedicated to Lord Rama at his sacred birthplace in Ayodhya.",
        "image_url": "https://images.unsplash.com/photo-1600100397608-f010f4439c7f?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Traditional Indian attire. Electronic gadgets, mobile phones, and leather items forbidden in sanctum.",
        "opening_time": "06:30",
        "closing_time": "21:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "07:00 AM - 11:30 AM & 05:00 PM - 08:30 PM",
        "entry_fee_domestic": "Free (Aarti Pass online)",
        "entry_fee_foreign": "Free (Aarti Pass online)",
        "booking_portal_url": "https://srjbtkshetra.org",
        "metrics": {"crime_index": 12.0, "scam_index": 20.0, "weather_risk": 16.0, "health_risk": 14.0, "night_safety": 85.0, "crowd_density": 90.0, "transport_safety": 82.0},
        "tips": [
            "Book Aarti passes free on official trust portal (srjbtkshetra.org) in advance.",
            "Free electronic cloakrooms available at the Pilgrimage Facilitation Centre."
        ],
        "emergency": [
            {"name": "Ayodhya Temple Security Cell", "type": "Police", "phone": "+91-5278-232043", "address": "Ram Janmabhoomi Complex", "lat": 26.7950, "lng": 82.1940},
            {"name": "District Hospital Ayodhya", "type": "Hospital", "phone": "+91-5278-222224", "address": "Civil Lines, Ayodhya", "lat": 26.7800, "lng": 82.1800}
        ],
        "advisory": {"title": "Devotee Security Queue Protocol", "level": "Advisory", "summary": "Multi-tier security frisking. Deposit smart watches, earphones, and powerbanks prior to entry."}
    },
    {
        "name": "Nainital & Mussoorie",
        "state": "Uttarakhand",
        "region": "North India",
        "category": "Mountain & Adventure",
        "lat": 29.3919,
        "lng": 79.4542,
        "overall_safety_score": 83,
        "risk_tier": "Low Risk (Safe)",
        "description": "Scenic lake district surrounded by seven pine hills (Sapta-Shring), featuring Naini Lake yacht boating, Mallital market, and snow viewpoint.",
        "image_url": "https://images.unsplash.com/photo-1597074866923-dc0589150358?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "March to June & September to November",
        "dress_code_etiquette": "Light woolens for summer evenings; heavy jackets in winter.",
        "opening_time": "06:00",
        "closing_time": "21:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "04:00 PM - 07:30 PM (Mall Road Promenade)",
        "entry_fee_domestic": "Free (Boating Rs 210 - 420)",
        "entry_fee_foreign": "Free (Boating Rs 210 - 420)",
        "booking_portal_url": "https://uttarakhandtourism.gov.in",
        "metrics": {"crime_index": 12.0, "scam_index": 22.0, "weather_risk": 26.0, "health_risk": 14.0, "night_safety": 84.0, "crowd_density": 78.0, "transport_safety": 78.0},
        "tips": [
            "Vehicular parking is strictly regulated in Nainital; use municipal shuttle parking at Sukhatal.",
            "Life jackets mandatory for all Naini Lake rowboat and pedal-boat rides."
        ],
        "emergency": [
            {"name": "Nainital Police Station Mallital", "type": "Police", "phone": "+91-5942-235552", "address": "Mallital, Nainital", "lat": 29.3930, "lng": 79.4530},
            {"name": "BD Pandey District Hospital", "type": "Hospital", "phone": "+91-5942-235022", "address": "Mallital, Nainital", "lat": 29.3950, "lng": 79.4510}
        ],
        "advisory": {"title": "Ghat Traffic Restriction", "level": "Advisory", "summary": "Heavy tourist traffic during long weekends. Follow police diversion signs from Kaladhungi route."}
    },

    # =========================================================================
    # WEST & CENTRAL INDIA
    # =========================================================================
    {
        "name": "Jaipur: Amer Fort & Hawa Mahal",
        "state": "Rajasthan",
        "region": "West India",
        "category": "Heritage & Forts",
        "lat": 26.9239,
        "lng": 75.8267,
        "overall_safety_score": 83,
        "risk_tier": "Low Risk (Safe)",
        "description": "The royal Pink City: hilltop fortress of Amer with mirror-inlaid Sheesh Mahal, honeycomb facade of Hawa Mahal, and royal courtyards of City Palace.",
        "image_url": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Comfortable cotton attire, broad-brimmed sun hats, and walking shoes for fort ramparts.",
        "opening_time": "08:00",
        "closing_time": "17:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:30 AM - 03:00 PM",
        "entry_fee_domestic": "Rs 100 (Composite Ticket Rs 300)",
        "entry_fee_foreign": "Rs 500 (Composite Ticket Rs 1000)",
        "booking_portal_url": "https://artandculture.rajasthan.gov.in",
        "metrics": {"crime_index": 20.0, "scam_index": 36.0, "weather_risk": 18.0, "health_risk": 14.0, "night_safety": 82.0, "crowd_density": 82.0, "transport_safety": 82.0},
        "tips": [
            "Use the composite monument entry ticket to avoid standing in separate ticket queues.",
            "Hire only Department of Tourism licensed guides wearing government photo badges.",
            "Beware of touts claiming special jewelry export tax refunds."
        ],
        "emergency": [
            {"name": "Rajasthan Tourist Police Desk Jaipur", "type": "Police", "phone": "+91-141-2600324", "address": "Amer Road / Hawa Mahal, Jaipur", "lat": 26.9240, "lng": 75.8270},
            {"name": "SMS Medical College & Hospital", "type": "Hospital", "phone": "+91-141-2560291", "address": "JLN Marg, Jaipur", "lat": 26.8920, "lng": 75.8150}
        ],
        "advisory": {"title": "Midday Sun Caution", "level": "Advisory", "summary": "Amer Fort ascent can be strenuous during noon hours. Electric buggies and jeeps are available from the base."}
    },
    {
        "name": "Goa: Baga, Calangute & Old Goa",
        "state": "Goa",
        "region": "West India",
        "category": "Beach & Coastal",
        "lat": 15.5553,
        "lng": 73.7517,
        "overall_safety_score": 85,
        "risk_tier": "Low Risk (Safe)",
        "description": "Golden Arabian Sea shores, beach shacks, lively coastal culture, water sports, and UNESCO World Heritage Portuguese churches of Old Goa.",
        "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to February",
        "dress_code_etiquette": "Casual beachwear on shores. Modest clothing covering shoulders and knees strictly enforced inside churches and temples.",
        "opening_time": "06:00",
        "closing_time": "23:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "04:30 PM - 09:00 PM",
        "entry_fee_domestic": "Free (Churches Free)",
        "entry_fee_foreign": "Free (Churches Free)",
        "booking_portal_url": "https://goatourism.gov.in",
        "metrics": {"crime_index": 16.0, "scam_index": 26.0, "weather_risk": 20.0, "health_risk": 12.0, "night_safety": 85.0, "crowd_density": 85.0, "transport_safety": 84.0},
        "tips": [
            "Strictly adhere to red flags posted by Drishti Marine lifeguards; riptides are hazardous.",
            "Zero tolerance for driving under the influence; Goa Police conduct frequent breathalyzer checkpoints.",
            "Rent two-wheelers only with valid yellow-on-black commercial rental plates."
        ],
        "emergency": [
            {"name": "Goa Tourist Police Calangute", "type": "Police", "phone": "+91-832-2278299", "address": "Tito's Lane Junction, Baga", "lat": 15.5520, "lng": 73.7530},
            {"name": "Drishti Marine Lifeguard Helpline", "type": "Rescue", "phone": "9911001122", "address": "All Goa Beaches", "lat": 15.5553, "lng": 73.7517}
        ],
        "advisory": {"title": "Public Beach Alcohol Ban", "level": "Advisory", "summary": "Drinking alcohol on open public beaches is banned under Goa Tourism Act and carries spot police fines."}
    },
    {
        "name": "Udaipur: Lake Pichola & City Palace",
        "state": "Rajasthan",
        "region": "West India",
        "category": "Heritage & Forts",
        "lat": 24.5764,
        "lng": 73.6835,
        "overall_safety_score": 87,
        "risk_tier": "Low Risk (Safe)",
        "description": "Venice of the East, surrounded by the Aravalli hills, floating Taj Lake Palace, grand City Palace museum, and romantic sunset boat rides.",
        "image_url": "https://images.unsplash.com/photo-1615836245337-f5b9b2303f10?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Smart casuals; modest dress inside Jagdish Temple.",
        "opening_time": "09:00",
        "closing_time": "17:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "03:30 PM - 06:00 PM (Sunset Cruise)",
        "entry_fee_domestic": "Rs 300 (Palace Museum)",
        "entry_fee_foreign": "Rs 300 (Palace Museum)",
        "booking_portal_url": "https://citypalacemuseum.org",
        "metrics": {"crime_index": 14.0, "scam_index": 22.0, "weather_risk": 15.0, "health_risk": 12.0, "night_safety": 88.0, "crowd_density": 70.0, "transport_safety": 84.0},
        "tips": [
            "Sunset boat cruise tickets at Lake Pichola sell out early; purchase passes at City Palace jetty by 2:00 PM.",
            "Old city streets are narrow; hire auto-rickshaws or explore on foot rather than large SUVs."
        ],
        "emergency": [
            {"name": "Udaipur Tourist Assistance Booth", "type": "Police", "phone": "+91-294-2411535", "address": "City Palace Entrance, Udaipur", "lat": 24.5770, "lng": 73.6840},
            {"name": "MB General Hospital Udaipur", "type": "Hospital", "phone": "+91-294-2528811", "address": "Hospital Road, Udaipur", "lat": 24.5880, "lng": 73.6950}
        ],
        "advisory": {"title": "Boat Safety Regulations", "level": "Advisory", "summary": "Wearing life jackets is mandatory on all Lake Pichola and Fateh Sagar boat tours."}
    },
    {
        "name": "Mumbai: Marine Drive & Gateway",
        "state": "Maharashtra",
        "region": "West India",
        "category": "Urban & Culture",
        "lat": 18.9220,
        "lng": 72.8347,
        "overall_safety_score": 86,
        "risk_tier": "Low Risk (Safe)",
        "description": "Financial capital of India, featuring Victorian Gothic UNESCO architecture, the historic Gateway of India arch, and Queen's Necklace promenade.",
        "image_url": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to February",
        "dress_code_etiquette": "Cosmopolitan casuals.",
        "opening_time": "00:00",
        "closing_time": "23:59",
        "weekly_off_day": "None",
        "peak_rush_hours": "05:30 PM - 09:30 PM (Promenade Evening)",
        "entry_fee_domestic": "Free (Ferry to Elephanta Rs 260)",
        "entry_fee_foreign": "Free (Ferry to Elephanta Rs 260)",
        "booking_portal_url": "https://maharashtratourism.gov.in",
        "metrics": {"crime_index": 20.0, "scam_index": 25.0, "weather_risk": 22.0, "health_risk": 14.0, "night_safety": 88.0, "crowd_density": 90.0, "transport_safety": 90.0},
        "tips": [
            "During high-tide monsoon surges, do not cross tetrapod wave-breakers along Marine Drive.",
            "Local train rush hours (08:30-11:00 AM, 06:00-09:00 PM) carry extreme crowds; travel off-peak.",
            "Metered Kaali-Peeli cabs strictly charge according to official tariff meters."
        ],
        "emergency": [
            {"name": "Mumbai Tourist Police Branch", "type": "Police", "phone": "+91-22-22620826", "address": "Colaba / Gateway, Mumbai", "lat": 18.9230, "lng": 72.8350},
            {"name": "Bombay Hospital & Medical Research", "type": "Hospital", "phone": "+91-22-22067676", "address": "Marine Lines, Mumbai", "lat": 18.9400, "lng": 72.8280}
        ],
        "advisory": {"title": "Monsoon High Tide Warnings", "level": "Warning", "summary": "Avoid sitting on seawalls when municipal warnings for high tides (>4.5m) coincide with heavy rain."}
    },
    {
        "name": "Jaisalmer: Golden Fort & Thar Desert",
        "state": "Rajasthan",
        "region": "West India",
        "category": "Heritage & Forts",
        "lat": 26.9124,
        "lng": 70.9127,
        "overall_safety_score": 82,
        "risk_tier": "Low Risk (Safe)",
        "description": "Golden sandstone citadel rising from the Thar Desert dunes, featuring India's only fully inhabited living fort, intricate havelis, and Sam Desert camps.",
        "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Sun protective cottons by day, heavy woolens and jackets for desert nights.",
        "opening_time": "09:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "04:00 PM - 07:00 PM (Sam Dune Sunset)",
        "entry_fee_domestic": "Fort Free (Palace Museum Rs 100)",
        "entry_fee_foreign": "Fort Free (Palace Museum Rs 500)",
        "booking_portal_url": "https://artandculture.rajasthan.gov.in",
        "metrics": {"crime_index": 12.0, "scam_index": 30.0, "weather_risk": 25.0, "health_risk": 15.0, "night_safety": 85.0, "crowd_density": 60.0, "transport_safety": 80.0},
        "tips": [
            "Ensure desert safari camps provide bottled mineral water and have verified security staff.",
            "Temperatures drop drastically after sunset in Thar desert; keep warm clothing ready.",
            "Never venture off marked desert roads without a certified local desert navigator."
        ],
        "emergency": [
            {"name": "Jaisalmer Police Control", "type": "Police", "phone": "+91-2992-252233", "address": "Fort Road, Jaisalmer", "lat": 26.9150, "lng": 70.9100},
            {"name": "Jawahir Hospital Jaisalmer", "type": "Hospital", "phone": "+91-2992-252343", "address": "Station Road, Jaisalmer", "lat": 26.9100, "lng": 70.9200}
        ],
        "advisory": {"title": "Desert Dehydration Warning", "level": "Advisory", "summary": "Drink at least 3-4 liters of water daily during daytime desert excursions."}
    },
    {
        "name": "Statue of Unity & Kevadia",
        "state": "Gujarat",
        "region": "West India",
        "category": "Urban & Culture",
        "lat": 21.8380,
        "lng": 73.7191,
        "overall_safety_score": 93,
        "risk_tier": "Low Risk (Safe)",
        "description": "The world's tallest statue (182m) honoring Sardar Vallabhbhai Patel on the Narmada River, featuring high-speed elevators and panoramic viewing galleries.",
        "image_url": "https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Smart casuals with sun protection.",
        "opening_time": "08:00",
        "closing_time": "18:00",
        "weekly_off_day": "Monday",
        "peak_rush_hours": "11:00 AM - 03:30 PM",
        "entry_fee_domestic": "Rs 150 (Viewing Gallery Rs 380)",
        "entry_fee_foreign": "Rs 150 (Viewing Gallery Rs 380)",
        "booking_portal_url": "https://sot.gujarat.gov.in",
        "metrics": {"crime_index": 6.0, "scam_index": 10.0, "weather_risk": 15.0, "health_risk": 10.0, "night_safety": 94.0, "crowd_density": 75.0, "transport_safety": 95.0},
        "tips": [
            "Closed on Mondays for weekly maintenance. Book viewing gallery slot online via sot.gujarat.gov.in.",
            "Internal transit is seamless via the centralized electric bus fleet."
        ],
        "emergency": [
            {"name": "Statue of Unity Visitor Helpdesk", "type": "Government", "phone": "1800-233-6600", "address": "Kevadia Colony, Narmada", "lat": 21.8390, "lng": 73.7200},
            {"name": "Kevadia Sub-District Hospital", "type": "Hospital", "phone": "+91-2640-235025", "address": "Garudeshwar Road, Kevadia", "lat": 21.8300, "lng": 73.7100}
        ],
        "advisory": {"title": "Monday Maintenance Closure", "level": "Advisory", "summary": "The entire Statue of Unity complex is strictly closed on Mondays."}
    },
    {
        "name": "Ajanta & Ellora Caves",
        "state": "Maharashtra",
        "region": "West India",
        "category": "Heritage & Forts",
        "lat": 20.0268,
        "lng": 75.1792,
        "overall_safety_score": 88,
        "risk_tier": "Low Risk (Safe)",
        "description": "UNESCO World Heritage rock-cut temples dating from 2nd century BCE to 10th century CE, including the breathtaking monolithic Kailasa Temple.",
        "image_url": "https://images.unsplash.com/photo-1609137144813-7d9921338f24?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Comfortable non-skid walking shoes for climbing ancient rock-cut staircases.",
        "opening_time": "09:00",
        "closing_time": "17:30",
        "weekly_off_day": "Tuesday (Ellora) / Monday (Ajanta)",
        "peak_rush_hours": "11:00 AM - 03:00 PM",
        "entry_fee_domestic": "Rs 40 (ASI Online)",
        "entry_fee_foreign": "Rs 600 (ASI Online)",
        "booking_portal_url": "https://asi.payumoney.com",
        "metrics": {"crime_index": 10.0, "scam_index": 16.0, "weather_risk": 16.0, "health_risk": 12.0, "night_safety": 86.0, "crowd_density": 65.0, "transport_safety": 85.0},
        "tips": [
            "Ajanta Caves closed on Mondays; Ellora Caves closed on Tuesdays.",
            "Flash photography prohibited inside cave paintings to preserve vegetable dyes.",
            "Use eco-friendly electric shuttle buses from T-junction parking."
        ],
        "emergency": [
            {"name": "Chhatrapati Sambhajinagar Tourist Police", "type": "Police", "phone": "+91-240-2331513", "address": "Station Road, Aurangabad", "lat": 19.8760, "lng": 75.3430},
            {"name": "Government Medical College Hospital", "type": "Hospital", "phone": "+91-240-2402412", "address": "Panchakki Road, Aurangabad", "lat": 19.8900, "lng": 75.3200}
        ],
        "advisory": {"title": "Alternating Weekly Closure", "level": "Advisory", "summary": "Ajanta closed Monday; Ellora closed Tuesday. Do not plan single-day visits without checking calendar."}
    },
    {
        "name": "Khajuraho: Western Group of Temples",
        "state": "Madhya Pradesh",
        "region": "West India",
        "category": "Heritage & Forts",
        "lat": 24.8517,
        "lng": 79.9200,
        "overall_safety_score": 87,
        "risk_tier": "Low Risk (Safe)",
        "description": "UNESCO World Heritage medieval Hindu and Jain temples renowned for exquisite Nagara-style architecture and sensuous sandstone sculptures of the Chandela dynasty.",
        "image_url": "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Respectful smart casuals; sun protection.",
        "opening_time": "06:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "09:30 AM - 01:00 PM",
        "entry_fee_domestic": "Rs 40 (Online)",
        "entry_fee_foreign": "Rs 600 (Online)",
        "booking_portal_url": "https://asi.payumoney.com",
        "metrics": {"crime_index": 10.0, "scam_index": 22.0, "weather_risk": 18.0, "health_risk": 12.0, "night_safety": 85.0, "crowd_density": 55.0, "transport_safety": 84.0},
        "tips": [
            "Attend the Western Group evening Sound & Light show narrated by Amitabh Bachchan.",
            "Hire only certified MP Tourism guides wearing official badges."
        ],
        "emergency": [
            {"name": "Khajuraho Police Station", "type": "Police", "phone": "+91-7686-274022", "address": "Main Road, Khajuraho", "lat": 24.8520, "lng": 79.9210},
            {"name": "Primary Health Centre Khajuraho", "type": "Hospital", "phone": "+91-7686-274033", "address": "Hospital Square, Khajuraho", "lat": 24.8500, "lng": 79.9180}
        ],
        "advisory": {"title": "Sound & Light Timings", "level": "Advisory", "summary": "English show at 6:30 PM; Hindi show at 7:40 PM in winter."}
    },
    {
        "name": "Rann of Kutch & White Desert",
        "state": "Gujarat",
        "region": "West India",
        "category": "Wildlife & Nature",
        "lat": 23.8340,
        "lng": 69.8378,
        "overall_safety_score": 86,
        "risk_tier": "Low Risk (Safe)",
        "description": "The world's largest salt desert spanning over 7,500 sq km, coming alive under moonlight during the vibrant Rann Utsav with folk music and artisan handicraft villages.",
        "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to February (Full Moon nights)",
        "dress_code_etiquette": "Sun protection during day; heavy woolens and windcheaters for chilly salt desert nights.",
        "opening_time": "06:00",
        "closing_time": "20:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "05:00 PM - 08:30 PM (Sunset to Full Moon)",
        "entry_fee_domestic": "White Rann Permit Rs 100",
        "entry_fee_foreign": "White Rann Permit Rs 100",
        "booking_portal_url": "https://www.rannpermit.com",
        "metrics": {"crime_index": 6.0, "scam_index": 12.0, "weather_risk": 22.0, "health_risk": 15.0, "night_safety": 90.0, "crowd_density": 70.0, "transport_safety": 85.0},
        "tips": [
            "Mandatory online permit from rannpermit.com before crossing the Bhirandiyara police checkpoint.",
            "Full moon nights provide the most mesmerizing surreal white glow."
        ],
        "emergency": [
            {"name": "Khavda Police Station", "type": "Police", "phone": "+91-2803-277222", "address": "Khavda Junction, Kutch", "lat": 23.8400, "lng": 69.7500},
            {"name": "Bhuj General Hospital", "type": "Hospital", "phone": "+91-2832-250100", "address": "Hospital Road, Bhuj", "lat": 23.2500, "lng": 69.6700}
        ],
        "advisory": {"title": "Border Proximity Checkpoint", "level": "Warning", "summary": "Do not wander beyond demarcated white salt pedestrian pathways towards the international border."}
    },

    # =========================================================================
    # SOUTH INDIA
    # =========================================================================
    {
        "name": "Munnar & Eravikulam National Park",
        "state": "Kerala",
        "region": "South India",
        "category": "Mountain & Adventure",
        "lat": 10.0889,
        "lng": 77.0595,
        "overall_safety_score": 87,
        "risk_tier": "Low Risk (Safe)",
        "description": "Rolling emerald hills carpeted with tea plantations, misty waterfalls, and the habitat of the endangered Nilgiri Tahr mountain goat in the Western Ghats.",
        "image_url": "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "September to May",
        "dress_code_etiquette": "Light woolens for misty mornings, rain gear, comfortable walking shoes.",
        "opening_time": "07:30",
        "closing_time": "16:00",
        "weekly_off_day": "None (Calving closure Feb-Mar)",
        "peak_rush_hours": "09:00 AM - 01:00 PM",
        "entry_fee_domestic": "Rs 200 (Eravikulam entry)",
        "entry_fee_foreign": "Rs 500 (Eravikulam entry)",
        "booking_portal_url": "https://eravikulamnationalpark.in",
        "metrics": {"crime_index": 10.0, "scam_index": 18.0, "weather_risk": 24.0, "health_risk": 12.0, "night_safety": 86.0, "crowd_density": 65.0, "transport_safety": 78.0},
        "tips": [
            "Gap Road (NH-85) has sharp hairpin bends and frequent mist; drive cautiously in low gear.",
            "Eravikulam National Park closes for calving season from February to March each year.",
            "Do not step off marked trails into dense tea bushes due to pit vipers."
        ],
        "emergency": [
            {"name": "Munnar Tourist Police Desk", "type": "Police", "phone": "+91-4865-230022", "address": "Munnar Town, Idukki", "lat": 10.0890, "lng": 77.0600},
            {"name": "Tata General Hospital Munnar", "type": "Hospital", "phone": "+91-4865-230222", "address": "Mattupetty Road, Munnar", "lat": 10.0920, "lng": 77.0650}
        ],
        "advisory": {"title": "Zero Plastic Municipality", "level": "Advisory", "summary": "Single-use plastic bottles and carry bags are prohibited across the Munnar tourism zone."}
    },
    {
        "name": "Alleppey (Alappuzha) Backwaters",
        "state": "Kerala",
        "region": "South India",
        "category": "Beach & Coastal",
        "lat": 9.4981,
        "lng": 76.3388,
        "overall_safety_score": 88,
        "risk_tier": "Low Risk (Safe)",
        "description": "Venice of the East: tranquil palm-fringed lagoons, traditional Kettuvallam houseboats, and serene inland canals on Vembanad Lake.",
        "image_url": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Casual, airy cotton clothing and mosquito repellent lotion for evening cruises.",
        "opening_time": "06:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "11:30 AM - 04:00 PM (Day Cruise Boarding)",
        "entry_fee_domestic": "Houseboat Rs 6,000 - 15,000 / night",
        "entry_fee_foreign": "Houseboat Rs 6,000 - 15,000 / night",
        "booking_portal_url": "https://alappuzhatourism.com",
        "metrics": {"crime_index": 10.0, "scam_index": 22.0, "weather_risk": 18.0, "health_risk": 14.0, "night_safety": 88.0, "crowd_density": 70.0, "transport_safety": 86.0},
        "tips": [
            "Hire houseboats only with official DTPC safety license stickers.",
            "Verify life jackets and fire extinguishers before sailing.",
            "Houseboats prohibited from cruising after 5:30 PM to preserve night fishing nets."
        ],
        "emergency": [
            {"name": "Alleppey Tourist Police Station", "type": "Police", "phone": "+91-477-2243441", "address": "Boat Jetty Road, Alappuzha", "lat": 9.4990, "lng": 76.3400},
            {"name": "Alappuzha General Hospital", "type": "Hospital", "phone": "+91-477-2253324", "address": "Hospital Road, Alappuzha", "lat": 9.4950, "lng": 76.3350}
        ],
        "advisory": {"title": "Certified Houseboat Verification", "level": "Advisory", "summary": "Check for green/gold tourism category classification plaques inside the boat saloon."}
    },
    {
        "name": "Hampi: Vijayanagara Ruins",
        "state": "Karnataka",
        "region": "South India",
        "category": "Heritage & Forts",
        "lat": 15.3350,
        "lng": 76.4600,
        "overall_safety_score": 84,
        "risk_tier": "Low Risk (Safe)",
        "description": "UNESCO World Heritage ruins of the magnificent 14th-century Vijayanagara Empire, featuring the Stone Chariot at Vittala Temple and Virupaksha Temple.",
        "image_url": "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to February",
        "dress_code_etiquette": "Modest clothing covering shoulders and knees when visiting active temple sites like Virupaksha.",
        "opening_time": "06:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "09:30 AM - 01:00 PM & 04:30 PM - 06:00 PM",
        "entry_fee_domestic": "Rs 40 (ASI Online)",
        "entry_fee_foreign": "Rs 600 (ASI Online)",
        "booking_portal_url": "https://asi.payumoney.com",
        "metrics": {"crime_index": 12.0, "scam_index": 20.0, "weather_risk": 20.0, "health_risk": 15.0, "night_safety": 80.0, "crowd_density": 65.0, "transport_safety": 82.0},
        "tips": [
            "Drink plenty of water and wear sun hats; granite boulders trap high heat during the day.",
            "Rent bicycles or electric buggies for traveling between monument clusters.",
            "Avoid swimming in Tungabhadra River near Kodandarama Temple due to submerged rocky whirlpools."
        ],
        "emergency": [
            {"name": "Hampi Police Station", "type": "Police", "phone": "+91-8394-241244", "address": "Near Bus Stand, Hampi", "lat": 15.3340, "lng": 76.4610},
            {"name": "Government Hospital Hospet", "type": "Hospital", "phone": "+91-8394-224444", "address": "College Road, Hospet", "lat": 15.2700, "lng": 76.3900}
        ],
        "advisory": {"title": "River Undertow Warning", "level": "Warning", "summary": "Coracle rides must operate strictly with life jackets. Never venture into river rapids."}
    },
    {
        "name": "Ooty & Nilgiri Mountain Railway",
        "state": "Tamil Nadu",
        "region": "South India",
        "category": "Mountain & Adventure",
        "lat": 11.4102,
        "lng": 76.6950,
        "overall_safety_score": 86,
        "risk_tier": "Low Risk (Safe)",
        "description": "Queen of Hill Stations in the Blue Mountains, featuring the Government Botanical Garden, Ooty Lake, tea estates, and the UNESCO Nilgiri Toy Train.",
        "image_url": "https://images.unsplash.com/photo-1589308078059-be1415eab4c3?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to June",
        "dress_code_etiquette": "Warm woolen clothing for evening temperatures dropping sharply year-round.",
        "opening_time": "07:00",
        "closing_time": "18:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:30 AM - 03:30 PM",
        "entry_fee_domestic": "Botanical Garden Rs 40",
        "entry_fee_foreign": "Botanical Garden Rs 100",
        "booking_portal_url": "https://epass.tnega.org",
        "metrics": {"crime_index": 12.0, "scam_index": 20.0, "weather_risk": 22.0, "health_risk": 12.0, "night_safety": 86.0, "crowd_density": 80.0, "transport_safety": 80.0},
        "tips": [
            "Obtain mandatory e-Pass (epass.tnega.org) before driving up the Nilgiri hills.",
            "Kalhatty Ghat has 36 hairpin bends; descending vehicles must use 2nd gear engine braking."
        ],
        "emergency": [
            {"name": "Ooty Tourist Police Desk", "type": "Police", "phone": "+91-423-2444003", "address": "Commercial Road, Ooty", "lat": 11.4110, "lng": 76.6960},
            {"name": "Government Headquarter Hospital Ooty", "type": "Hospital", "phone": "+91-423-2442212", "address": "Hospital Road, Ooty", "lat": 11.4080, "lng": 76.7020}
        ],
        "advisory": {"title": "Nilgiri Plastic Ban", "level": "Advisory", "summary": "Plastic water bottles and thermocol items are strictly prohibited throughout Nilgiri district."}
    },
    {
        "name": "Madurai: Meenakshi Amman Temple",
        "state": "Tamil Nadu",
        "region": "South India",
        "category": "Spiritual & Sacred",
        "lat": 9.9195,
        "lng": 78.1193,
        "overall_safety_score": 88,
        "risk_tier": "Low Risk (Safe)",
        "description": "Historic Dravidian architecture masterpiece with 14 towering gopurams encrusted with thousands of colorful mythological stucco figures.",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Strict traditional dress code: dhoti/pyjama with shirt for men; saree or salwar kameez with dupatta for women.",
        "opening_time": "05:00",
        "closing_time": "22:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "07:00 AM - 11:00 AM & 06:00 PM - 08:30 PM",
        "entry_fee_domestic": "Free (Special Darshan Rs 100)",
        "entry_fee_foreign": "Free (Special Darshan Rs 100)",
        "booking_portal_url": "https://maduraimeenakshi.hrce.tn.gov.in",
        "metrics": {"crime_index": 14.0, "scam_index": 24.0, "weather_risk": 18.0, "health_risk": 14.0, "night_safety": 84.0, "crowd_density": 88.0, "transport_safety": 86.0},
        "tips": [
            "Mobile phones, cameras, smart watches, and electronic gadgets are strictly banned inside temple.",
            "Secure your belongings at official temple cloakrooms near East or West Gopuram gates."
        ],
        "emergency": [
            {"name": "Madurai Temple Police Wing", "type": "Police", "phone": "+91-452-2344360", "address": "East Chithirai Street, Madurai", "lat": 9.9200, "lng": 78.1200},
            {"name": "Government Rajaji Hospital Madurai", "type": "Hospital", "phone": "+91-452-2532535", "address": "Panagal Road, Madurai", "lat": 9.9280, "lng": 78.1300}
        ],
        "advisory": {"title": "Temple Gadget Prohibition", "level": "Advisory", "summary": "Do not carry electronics to queue gates; metal detector baggage screening is mandatory."}
    },
    {
        "name": "Mysore Palace & Chamundi Hill",
        "state": "Karnataka",
        "region": "South India",
        "category": "Heritage & Forts",
        "lat": 12.3051,
        "lng": 76.6551,
        "overall_safety_score": 90,
        "risk_tier": "Low Risk (Safe)",
        "description": "Magnificent seat of the Wadiyar dynasty, famous for 100,000 illumination bulbs on Sunday evenings, golden royal throne, and world-famous Mysore Dasara.",
        "image_url": "https://images.unsplash.com/photo-1600684388091-62730f4b0f9f?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "September to March",
        "dress_code_etiquette": "Respectful smart casuals. Shoes must be deposited at designated Varaha Gate counters.",
        "opening_time": "10:00",
        "closing_time": "17:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "01:30 PM - 05:00 PM (Sunday Illumination 7-8 PM)",
        "entry_fee_domestic": "Rs 100",
        "entry_fee_foreign": "Rs 300",
        "booking_portal_url": "https://mysorepalace.karnataka.gov.in",
        "metrics": {"crime_index": 10.0, "scam_index": 18.0, "weather_risk": 14.0, "health_risk": 12.0, "night_safety": 90.0, "crowd_density": 82.0, "transport_safety": 88.0},
        "tips": [
            "Palace illumination happens every Sunday and public holiday from 7:00 PM to 7:45 PM; reach by 6:15 PM.",
            "Buy Mysore silk only from certified government KSIC showrooms with official Silk Mark tags."
        ],
        "emergency": [
            {"name": "Mysore Palace Security Desk", "type": "Police", "phone": "+91-821-2421051", "address": "Varaha Gate, Mysore", "lat": 12.3050, "lng": 76.6550},
            {"name": "KR Hospital Mysore", "type": "Hospital", "phone": "+91-821-2423300", "address": "Sayyaji Rao Road, Mysore", "lat": 12.3150, "lng": 76.6500}
        ],
        "advisory": {"title": "Drone Flying Prohibition", "level": "Advisory", "summary": "Flying civilian drones over the palace grounds is strictly prohibited under security regulations."}
    },
    {
        "name": "Tirupati: Sri Venkateswara Swamy",
        "state": "Andhra Pradesh",
        "region": "South India",
        "category": "Spiritual & Sacred",
        "lat": 13.6833,
        "lng": 79.3500,
        "overall_safety_score": 91,
        "risk_tier": "Low Risk (Safe)",
        "description": "World's most visited sacred pilgrimage shrine situated atop the Seven Seshachalam Hills at Tirumala, dedicated to Lord Venkateswara (Balaji).",
        "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "September to February",
        "dress_code_etiquette": "Strict Traditional Dress Code: Dhoti/Kurta for men; Saree or Half-Saree/Churidar with Dupatta for women. Jeans strictly forbidden.",
        "opening_time": "03:00",
        "closing_time": "23:59",
        "weekly_off_day": "None",
        "peak_rush_hours": "07:00 AM - 02:00 PM & 05:00 PM - 09:00 PM",
        "entry_fee_domestic": "Free (Special Entry Darshan Rs 300)",
        "entry_fee_foreign": "Free (Special Entry Darshan Rs 300)",
        "booking_portal_url": "https://ttdevasthanams.ap.gov.in",
        "metrics": {"crime_index": 8.0, "scam_index": 15.0, "weather_risk": 16.0, "health_risk": 10.0, "night_safety": 94.0, "crowd_density": 95.0, "transport_safety": 92.0},
        "tips": [
            "Book the Rs 300 Special Entry Darshan pass months ahead exclusively through ttdevasthanams.ap.gov.in.",
            "Tirumala Ghat Road is speed-monitored; descending in under 28 minutes attracts automatic fines at the toll gate."
        ],
        "emergency": [
            {"name": "TTD Vigilance & Security Office", "type": "Police", "phone": "+91-877-2263777", "address": "Tirumala, Andhra Pradesh", "lat": 13.6840, "lng": 79.3510},
            {"name": "SVIMS Super Specialty Hospital", "type": "Hospital", "phone": "+91-877-2287777", "address": "Alipiri Road, Tirupati", "lat": 13.6300, "lng": 79.4100}
        ],
        "advisory": {"title": "Ghat Road Speed & Time Regulation", "level": "Advisory", "summary": "Strict 28-minute minimum transit time enforced between Alipiri Toll and Tirumala for passenger safety."}
    },
    {
        "name": "Kanyakumari & Vivekananda Rock",
        "state": "Tamil Nadu",
        "region": "South India",
        "category": "Beach & Coastal",
        "lat": 8.0883,
        "lng": 77.5385,
        "overall_safety_score": 87,
        "risk_tier": "Low Risk (Safe)",
        "description": "The southernmost tip of mainland India, where the Indian Ocean, Arabian Sea, and Bay of Bengal converge. Famous for sunrise and sunset over the tri-sea.",
        "image_url": "https://images.unsplash.com/photo-1590766940554-634a7ed41450?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Comfortable breezy cottons. Footwear deposited before entering Vivekananda Memorial.",
        "opening_time": "08:00",
        "closing_time": "16:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "05:45 AM - 07:00 AM (Sunrise) & 03:00 PM - 05:30 PM",
        "entry_fee_domestic": "Ferry Rs 50 + Memorial Rs 20",
        "entry_fee_foreign": "Ferry Rs 50 + Memorial Rs 20",
        "booking_portal_url": "https://tamilnadutourism.tn.gov.in",
        "metrics": {"crime_index": 10.0, "scam_index": 18.0, "weather_risk": 20.0, "health_risk": 12.0, "night_safety": 88.0, "crowd_density": 75.0, "transport_safety": 85.0},
        "tips": [
            "Ferry rides to Vivekananda Rock operate subject to calm sea conditions; reach jetty before 3:00 PM.",
            "Triveni Sangam steps can be extremely slippery during high tide."
        ],
        "emergency": [
            {"name": "Kanyakumari Coastal Police", "type": "Police", "phone": "+91-4652-246224", "address": "Beach Road, Kanyakumari", "lat": 8.0890, "lng": 77.5390},
            {"name": "Government Medical College Asaripallam", "type": "Hospital", "phone": "+91-4652-223201", "address": "Asaripallam, Nagercoil", "lat": 8.1800, "lng": 77.4200}
        ],
        "advisory": {"title": "Tri-Sea Convergence Currents", "level": "Warning", "summary": "Swimming strictly barred at Triveni Sangam rocky beach due to cross-wave undertows."}
    },

    # =========================================================================
    # EAST & NORTHEAST INDIA
    # =========================================================================
    {
        "name": "Darjeeling & Tiger Hill",
        "state": "West Bengal",
        "region": "East & North-East India",
        "category": "Mountain & Adventure",
        "lat": 27.0410,
        "lng": 88.2663,
        "overall_safety_score": 83,
        "risk_tier": "Low Risk (Safe)",
        "description": "The Queen of the Hills offering breathtaking views of Mount Kangchenjunga, UNESCO Darjeeling Himalayan Railway, and world-renowned tea gardens.",
        "image_url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "March to May & October to December",
        "dress_code_etiquette": "Warm woolen clothing even during summer for early dawn sunrise tours.",
        "opening_time": "04:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "04:00 AM - 06:30 AM (Tiger Hill Sunrise)",
        "entry_fee_domestic": "Tiger Hill Entry Rs 50",
        "entry_fee_foreign": "Tiger Hill Entry Rs 50",
        "booking_portal_url": "https://wbtourism.gov.in",
        "metrics": {"crime_index": 12.0, "scam_index": 20.0, "weather_risk": 28.0, "health_risk": 14.0, "night_safety": 84.0, "crowd_density": 78.0, "transport_safety": 76.0},
        "tips": [
            "Tiger Hill sunrise trips start at 3:30 AM; hire pre-arranged cabs the previous afternoon.",
            "Landslides can occur along Hill Cart Road during intense monsoon showers.",
            "Buy authentic Darjeeling tea only from certified Tea Board of India outlets."
        ],
        "emergency": [
            {"name": "Darjeeling Sadar Police Station", "type": "Police", "phone": "+91-354-2252622", "address": "Laden La Road, Darjeeling", "lat": 27.0420, "lng": 78.2670},
            {"name": "Darjeeling District Hospital", "type": "Hospital", "phone": "+91-354-2254218", "address": "Hospital Road, Darjeeling", "lat": 27.0450, "lng": 88.2600}
        ],
        "advisory": {"title": "Tiger Hill Traffic Bottleneck", "level": "Advisory", "summary": "Heavy traffic bottlenecks occur on the Ghoom-Tiger Hill ascent between 4:00 AM and 5:00 AM."}
    },
    {
        "name": "Puri: Jagannath Temple & Golden Beach",
        "state": "Odisha",
        "region": "East & North-East India",
        "category": "Spiritual & Sacred",
        "lat": 19.8135,
        "lng": 85.8312,
        "overall_safety_score": 81,
        "risk_tier": "Low Risk (Safe)",
        "description": "Abode of Lord Jagannath famous for the annual Ratha Yatra festival, centuries-old Mahaprasad culinary tradition, and certified Blue Flag Golden Beach.",
        "image_url": "https://images.unsplash.com/photo-1628107082933-07b235e4646c?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to February",
        "dress_code_etiquette": "Traditional Indian temple wear. Strictly no leather belts, wallets, shoes, or phones past the Singhadwara gate.",
        "opening_time": "05:30",
        "closing_time": "22:30",
        "weekly_off_day": "None",
        "peak_rush_hours": "06:00 AM - 10:00 AM & 05:00 PM - 09:00 PM",
        "entry_fee_domestic": "Free",
        "entry_fee_foreign": "Free (Temple outer precinct)",
        "booking_portal_url": "https://shrijagannatha.odisha.gov.in",
        "metrics": {"crime_index": 16.0, "scam_index": 30.0, "weather_risk": 25.0, "health_risk": 15.0, "night_safety": 80.0, "crowd_density": 88.0, "transport_safety": 82.0},
        "tips": [
            "Swim only in designated lifeguard-patrolled zones of Blue Flag Beach.",
            "Only Hindus are permitted inside the core Jagannath Temple according to ancient customs."
        ],
        "emergency": [
            {"name": "Puri Beach Police Station", "type": "Police", "phone": "+91-6752-223400", "address": "Chakratirtha Road, Puri", "lat": 19.8150, "lng": 85.8350},
            {"name": "District Headquarters Hospital Puri", "type": "Hospital", "phone": "+91-6752-222018", "address": "Grand Road, Puri", "lat": 19.8100, "lng": 85.8250}
        ],
        "advisory": {"title": "Sea Bathing Safety Caution", "level": "Warning", "summary": "Do not enter the sea after sunset. Follow lifeguard whistle instructions immediately."}
    },
    {
        "name": "Shillong & Cherrapunji (Sohra)",
        "state": "Meghalaya",
        "region": "East & North-East India",
        "category": "Mountain & Adventure",
        "lat": 25.5788,
        "lng": 91.8933,
        "overall_safety_score": 86,
        "risk_tier": "Low Risk (Safe)",
        "description": "Scotland of the East with dramatic Nohkalikai Falls, indigenous Khasi bio-engineered Living Root Bridges, and limestone caves in the wettest region on Earth.",
        "image_url": "https://images.unsplash.com/photo-1626014303757-65644775be70?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to May",
        "dress_code_etiquette": "Rainproof jackets, hiking shoes with rubber grip.",
        "opening_time": "06:00",
        "closing_time": "17:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "10:00 AM - 02:30 PM",
        "entry_fee_domestic": "Living Root Bridge Rs 50",
        "entry_fee_foreign": "Living Root Bridge Rs 100",
        "booking_portal_url": "https://meghalayatourism.in",
        "metrics": {"crime_index": 10.0, "scam_index": 14.0, "weather_risk": 32.0, "health_risk": 14.0, "night_safety": 86.0, "crowd_density": 55.0, "transport_safety": 78.0},
        "tips": [
            "Double Decker Living Root Bridge trek (Nongriat) involves descending and climbing 3,500+ steep steps; carry electrolyte water.",
            "Dense mountain fog can reduce road visibility to under 5 meters along the Shillong-Sohra highway."
        ],
        "emergency": [
            {"name": "Shillong Sadar Police Station", "type": "Police", "phone": "+91-364-2224818", "address": "Police Bazar, Shillong", "lat": 25.5790, "lng": 91.8940},
            {"name": "NEIGRIHMS Super-Specialty Hospital", "type": "Hospital", "phone": "+91-364-2538011", "address": "Mawdiangdiang, Shillong", "lat": 25.6000, "lng": 91.9300}
        ],
        "advisory": {"title": "Khasi Community Etiquette", "level": "Advisory", "summary": "Zero littering strictly enforced in Mawlynnong and Sohra village reserves. Carry all wrappers back."}
    },
    {
        "name": "Kaziranga National Park",
        "state": "Assam",
        "region": "East & North-East India",
        "category": "Wildlife & Nature",
        "lat": 26.5775,
        "lng": 93.1711,
        "overall_safety_score": 85,
        "risk_tier": "Low Risk (Safe)",
        "description": "World stronghold of the Great Indian One-Horned Rhinoceros, tigers, elephants, and wild water buffalo along the mighty Brahmaputra river floodplains.",
        "image_url": "https://images.unsplash.com/photo-1575550959106-5a7defe28b56?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "November to April (Closed during monsoon)",
        "dress_code_etiquette": "Neutral khaki, olive green, or earthy brown clothing. Bright reds and fluorescents are strictly discouraged.",
        "opening_time": "07:00",
        "closing_time": "16:30",
        "weekly_off_day": "Closed May-Oct (Flood Season)",
        "peak_rush_hours": "07:30 AM - 10:00 AM & 01:30 PM - 03:30 PM (Safari)",
        "entry_fee_domestic": "Jeep Safari Entry Rs 100 + Jeep charge",
        "entry_fee_foreign": "Jeep Safari Entry Rs 650 + Jeep charge",
        "booking_portal_url": "https://kaziranga.assam.gov.in",
        "metrics": {"crime_index": 8.0, "scam_index": 12.0, "weather_risk": 28.0, "health_risk": 15.0, "night_safety": 82.0, "crowd_density": 55.0, "transport_safety": 80.0},
        "tips": [
            "Park is open only from November to April; completely closed during monsoon flood season.",
            "Always follow forest range officer instructions during jeep safaris; maintain safe distance from rhinos."
        ],
        "emergency": [
            {"name": "Bokakhat Forest Range Office", "type": "Rescue", "phone": "+91-3776-268095", "address": "Bokakhat, Golaghat", "lat": 26.6000, "lng": 93.1800},
            {"name": "Kohora Civil Hospital", "type": "Hospital", "phone": "+91-3776-262444", "address": "Kohora, Kaziranga", "lat": 26.5800, "lng": 93.1700}
        ],
        "advisory": {"title": "Wildlife Proximity Rules", "level": "Warning", "summary": "Never stand up or make sudden movements when rhinos or wild elephants approach safari tracks."}
    },
    {
        "name": "Tawang Monastery & Sela Pass",
        "state": "Arunachal Pradesh",
        "region": "East & North-East India",
        "category": "Mountain & Adventure",
        "lat": 27.5861,
        "lng": 91.8594,
        "overall_safety_score": 77,
        "risk_tier": "Low Risk (Safe)",
        "description": "India's largest Buddhist monastery founded in 1681, perched dramatically at 10,000 ft in western Arunachal Pradesh near high-altitude Sela Pass.",
        "image_url": "https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "April to October",
        "dress_code_etiquette": "Respectful attire inside the monastery. Heavy woolens for Sela Pass crossing.",
        "opening_time": "07:00",
        "closing_time": "19:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "09:00 AM - 12:30 PM",
        "entry_fee_domestic": "ILP Rs 100",
        "entry_fee_foreign": "PAP USD 50",
        "booking_portal_url": "https://arunachalilp.com",
        "metrics": {"crime_index": 6.0, "scam_index": 10.0, "weather_risk": 45.0, "health_risk": 28.0, "night_safety": 88.0, "crowd_density": 35.0, "transport_safety": 68.0},
        "tips": [
            "Inner Line Permit (ILP) is required for all domestic Indian travelers visiting Arunachal Pradesh.",
            "Sela Pass (13,700 ft) often experiences heavy snowfall and icing; use high-clearance 4WD vehicles."
        ],
        "emergency": [
            {"name": "Tawang Police Station", "type": "Police", "phone": "+91-3794-222221", "address": "Old Market, Tawang", "lat": 27.5870, "lng": 91.8600},
            {"name": "Khandro Drowa Tsangmu Hospital", "type": "Hospital", "phone": "+91-3794-222214", "address": "Hospital Road, Tawang", "lat": 27.5850, "lng": 91.8550}
        ],
        "advisory": {"title": "Sela Pass Weather Window", "level": "Warning", "summary": "Cross Sela Pass before 2:00 PM to avoid severe evening blizzard conditions and road icing."}
    },
    {
        "name": "Bodh Gaya: Mahabodhi Temple",
        "state": "Bihar",
        "region": "East & North-East India",
        "category": "Spiritual & Sacred",
        "lat": 24.6959,
        "lng": 84.9914,
        "overall_safety_score": 85,
        "risk_tier": "Low Risk (Safe)",
        "description": "UNESCO World Heritage site marking the location where Siddhartha Gautama attained supreme enlightenment under the sacred Bodhi Tree.",
        "image_url": "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to March",
        "dress_code_etiquette": "Modest clothing covering shoulders and legs. Footwear deposited at outer counter.",
        "opening_time": "05:00",
        "closing_time": "21:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "07:00 AM - 10:00 AM & 05:00 PM - 07:30 PM",
        "entry_fee_domestic": "Free (Camera fee Rs 100)",
        "entry_fee_foreign": "Free (Camera fee Rs 100)",
        "booking_portal_url": "https://mahabodhi.org",
        "metrics": {"crime_index": 14.0, "scam_index": 20.0, "weather_risk": 18.0, "health_risk": 16.0, "night_safety": 84.0, "crowd_density": 70.0, "transport_safety": 82.0},
        "tips": [
            "Meditation permitted around the Bodhi Tree in serene silence.",
            "Mobile phones must be kept on silent or deposited."
        ],
        "emergency": [
            {"name": "Bodh Gaya Police Station", "type": "Police", "phone": "+91-631-2200727", "address": "Near Temple Gate, Bodh Gaya", "lat": 24.6960, "lng": 84.9920},
            {"name": "Anugrah Narayan Magadh Medical College", "type": "Hospital", "phone": "+91-631-2400371", "address": "Gaya", "lat": 24.7800, "lng": 85.0000}
        ],
        "advisory": {"title": "Bodhi Tree Sanctum Protocol", "level": "Advisory", "summary": "Do not pluck or break leaves from the sacred Bodhi Tree; fallen leaves may be accepted from ground."}
    },

    # =========================================================================
    # ISLANDS
    # =========================================================================
    {
        "name": "Andaman: Havelock & Radhanagar Beach",
        "state": "Andaman & Nicobar (UT)",
        "region": "South India",
        "category": "Beach & Coastal",
        "lat": 11.9840,
        "lng": 92.9876,
        "overall_safety_score": 91,
        "risk_tier": "Low Risk (Safe)",
        "description": "Voted Time Magazine's Best Beach in Asia, famous for powdered white sands, turquoise sea, scuba diving at Elephant Beach, and pristine coral reefs.",
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to May",
        "dress_code_etiquette": "Tropical beachwear on beaches. Swimwear restricted to shore areas.",
        "opening_time": "06:00",
        "closing_time": "18:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "03:30 PM - 05:45 PM (Radhanagar Sunset)",
        "entry_fee_domestic": "Free (Ferry Port Blair to Havelock Rs 1200 - 2500)",
        "entry_fee_foreign": "Free (Ferry Port Blair to Havelock Rs 1200 - 2500)",
        "booking_portal_url": "https://dss.andaman.gov.in",
        "metrics": {"crime_index": 6.0, "scam_index": 12.0, "weather_risk": 20.0, "health_risk": 12.0, "night_safety": 92.0, "crowd_density": 50.0, "transport_safety": 88.0},
        "tips": [
            "Book Makruzz or government DSS ferry tickets well ahead of peak season.",
            "Only dive with certified PADI/SSI dive masters carrying emergency pure oxygen on dive vessels.",
            "Do not touch coral reefs or attempt taking seashells through airport security."
        ],
        "emergency": [
            {"name": "Havelock Police Station", "type": "Police", "phone": "+91-3192-282405", "address": "Village No. 3, Havelock", "lat": 11.9850, "lng": 92.9880},
            {"name": "Primary Health Centre Havelock", "type": "Hospital", "phone": "+91-3192-282245", "address": "Village No. 1, Havelock", "lat": 11.9820, "lng": 92.9850},
            {"name": "Coast Guard Search & Rescue", "type": "Rescue", "phone": "1554", "address": "Port Blair Headquarters", "lat": 11.6667, "lng": 92.7500}
        ],
        "advisory": {"title": "Marine Coral Protection", "level": "Advisory", "summary": "Collecting live or dead corals is strictly illegal under Wildlife Protection Act."}
    },
    {
        "name": "Lakshadweep: Agatti, Bangaram & Kavaratti Islands",
        "state": "Lakshadweep (UT)",
        "region": "South India",
        "category": "Beach & Coastal",
        "lat": 10.8530,
        "lng": 72.1949,
        "overall_safety_score": 94,
        "risk_tier": "Low Risk (Safe)",
        "description": "India's breathtaking coral archipelago in the Arabian Sea, featuring crystal-clear turquoise lagoons, pristine coral reefs, dolphin pods, and white powdery beaches at Bangaram, Agatti, and Kavaratti.",
        "image_url": "https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?auto=format&fit=crop&w=1200&q=80",
        "best_visit_time": "October to May",
        "dress_code_etiquette": "Modest casuals on inhabited islands (Agatti, Kavaratti). Respect delicate coral ecosystems; touching or extracting corals or seashells is strictly prohibited.",
        "opening_time": "06:00",
        "closing_time": "20:00",
        "weekly_off_day": "None",
        "peak_rush_hours": "09:00 AM - 04:30 PM (Water Sports & Lagoon Diving)",
        "entry_fee_domestic": "₹300 (e-Permit Heritage Fee)",
        "entry_fee_foreign": "₹500 (Foreign Registration Fee)",
        "booking_portal_url": "https://epermit.lakshadweep.gov.in",
        "metrics": {"crime_index": 2.0, "scam_index": 5.0, "weather_risk": 24.0, "health_risk": 16.0, "night_safety": 96.0, "crowd_density": 20.0, "transport_safety": 85.0},
        "tips": [
            "Mandatory e-Permit must be obtained online via epermit.lakshadweep.gov.in prior to flight departure.",
            "Regular commercial flights operate from Kochi (COK) to Agatti Island (AGX) via Alliance Air.",
            "Carry adequate cash as digital payment terminals can experience connectivity delays on outer atolls.",
            "Only dive with certified PADI/SSI instructors holding valid maritime permits."
        ],
        "emergency": [
            {"name": "Agatti Island Police Station", "type": "Police", "phone": "+91-4894-242226", "address": "Airport Road, Agatti Island", "lat": 10.8540, "lng": 72.1950},
            {"name": "Rajiv Gandhi Specialty Government Hospital", "type": "Hospital", "phone": "+91-4894-242234", "address": "Main Road, Agatti Island", "lat": 10.8510, "lng": 72.1930},
            {"name": "Kavaratti Police Headquarters", "type": "Police", "phone": "+91-4896-262225", "address": "Secretariat Road, Kavaratti", "lat": 10.5670, "lng": 72.6420},
            {"name": "Indira Gandhi General Hospital Kavaratti", "type": "Hospital", "phone": "+91-4896-262234", "address": "Hospital Road, Kavaratti", "lat": 10.5650, "lng": 72.6400}
        ],
        "advisory": {"title": "Coral Reef Conservation & Maritime Monsoon Advisory", "level": "Advisory", "summary": "Strict environmental protection enforced under the Wildlife Protection Act. Snorkeling and boat diving restricted to authorized marine corridors."}
    },
]

# Expand with additional real destinations (unique names only)
_existing_names = {d["name"] for d in INDIA_DESTINATIONS}
for _extra in ADDITIONAL_INDIA_DESTINATIONS:
    if _extra["name"] not in _existing_names:
        INDIA_DESTINATIONS.append(_extra)
        _existing_names.add(_extra["name"])

REAL_TIME_HAZARDS = [
    {
        "dest_name": "Lakshadweep: Agatti, Bangaram & Kavaratti Islands",
        "title": "Arabian Sea Swell & Marine Corals Snorkeling Caution",
        "category": "Weather Hazard",
        "severity": "Low",
        "location_name": "Agatti Lagoon Reef Outer Edge",
        "lat_offset": 0.005,
        "lng_offset": 0.004,
        "description": "Mild tidal swells observed on outer reef edge. Water sports and snorkeling permitted exclusively inside the protected turquoise lagoon zone."
    },
    {
        "dest_name": "Manali & Solang Valley",
        "title": "NH-3 Solang Bypass Landslide Alert",
        "category": "Weather Hazard",
        "severity": "High",
        "location_name": "NH-3 Km 14 near Palchan",
        "lat_offset": 0.015,
        "lng_offset": 0.012,
        "description": "Heavy overnight hill showers caused loose rock debris and mud slip on the Solang bypass road. Border Roads Organisation (BRO) bulldozers actively clearing single lane. Expected clear by 2:00 PM."
    },
    {
        "dest_name": "Goa: Baga, Calangute & Old Goa",
        "title": "Arabian Sea High Undertow & Red Flag Alert",
        "category": "Weather Hazard",
        "severity": "Medium",
        "location_name": "Baga Beach Shoreline (Shack Sector 4)",
        "lat_offset": -0.002,
        "lng_offset": -0.003,
        "description": "Strong rip currents and 2.8m high tide swells reported by Drishti Marine lifeguards. Red danger flags posted along Baga beach. Swimming temporarily prohibited; shack dining operational."
    },
    {
        "dest_name": "Varanasi Ghats & Kashi Vishwanath",
        "title": "Maha Aarti & Darshan Corridor Pilgrim Surge",
        "category": "Road Hazard",
        "severity": "Medium",
        "location_name": "Godowlia to Dashashwamedh Corridor",
        "lat_offset": 0.001,
        "lng_offset": 0.002,
        "description": "Heavy devotee surge observed along Godowlia pedestrian gate due to festival crowd. Current queue wait time exceeding 75 minutes. Tourist police directing families towards Gate No. 4."
    },
    {
        "dest_name": "Tawang Monastery & Sela Pass",
        "title": "Sela Pass Sub-Zero Blizzard & Black Ice Warning",
        "category": "Weather Hazard",
        "severity": "Critical",
        "location_name": "Sela Pass Summit (13,700 ft)",
        "lat_offset": 0.035,
        "lng_offset": 0.020,
        "description": "Sub-zero blizzard conditions with severe road icing between Sela Lake and Jaswant Garh. Indian Army checkpoints restricting non-4WD passenger vehicles. Chains mandatory on tires."
    },
    {
        "dest_name": "Puri: Jagannath Temple & Golden Beach",
        "title": "Blue Flag Beach Sector 3 Undertow Danger",
        "category": "Weather Hazard",
        "severity": "Medium",
        "location_name": "Golden Beach Lifeguard Post 2",
        "lat_offset": -0.004,
        "lng_offset": 0.005,
        "description": "Strong seaward undertows recorded by Odisha Tourism Lifeguard Wing. Bathing allowed strictly within buoyant safety net zones. Whistles active."
    },
    {
        "dest_name": "Jaisalmer: Golden Fort & Thar Desert",
        "title": "Thar Desert Midday Heat Advisory",
        "category": "Weather Hazard",
        "severity": "Low",
        "location_name": "Sam Sand Dunes Activity Area",
        "lat_offset": 0.010,
        "lng_offset": 0.015,
        "description": "Daytime temperatures reaching 42°C with high UV index. Desert camel safaris and quad biking suspended between 11:30 AM and 3:30 PM for animal and passenger safety."
    }
]

DEMO_USERS = [
    {
        "full_name": "Chief Safety Officer (Admin)",
        "email": "admin@safetour.gov.in",
        "username": "safetour_admin",
        "password": "AdminPass#2026",
        "role": "admin",
        "reputation_xp": 5000,
        "home_city": "New Delhi"
    },
    {
        "full_name": "Inspector R. K. Verma (Police Command)",
        "email": "police.112@eoc.gov.in",
        "username": "police_112",
        "password": "PolicePass#112",
        "role": "admin",
        "reputation_xp": 4000,
        "home_city": "New Delhi"
    },
    {
        "full_name": "Dr. Meenakshi Sundaram (EMS & Trauma 108)",
        "email": "medical.108@eoc.gov.in",
        "username": "medical_108",
        "password": "MedicalPass#108",
        "role": "admin",
        "reputation_xp": 4000,
        "home_city": "New Delhi"
    },
    {
        "full_name": "Chief Fire Officer B. S. Rawat (Fire & Rescue 101)",
        "email": "fire.101@eoc.gov.in",
        "username": "fire_101",
        "password": "FirePass#101",
        "role": "admin",
        "reputation_xp": 4000,
        "home_city": "New Delhi"
    },
    {
        "full_name": "Commandant S. K. Nair (NDRF Disaster Response)",
        "email": "ndrf@eoc.gov.in",
        "username": "ndrf_command",
        "password": "NdrfPass#2026",
        "role": "admin",
        "reputation_xp": 4000,
        "home_city": "New Delhi"
    },
    {
        "full_name": "Director General (Unified Operations)",
        "email": "commander@eoc.gov.in",
        "username": "eoc_commander",
        "password": "Commander#2026",
        "role": "admin",
        "reputation_xp": 5000,
        "home_city": "New Delhi"
    },
    {
        "full_name": "Arjun Mehta",
        "email": "arjun@traveler.in",
        "username": "arjun_mehta",
        "password": "Traveler@123",
        "role": "tourist",
        "reputation_xp": 1150,
        "home_city": "Mumbai"
    },
    {
        "full_name": "Priya Sharma",
        "email": "priya@traveler.in",
        "username": "priya_sharma",
        "password": "Traveler@123",
        "reputation_xp": 650,
        "home_city": "Delhi"
    },
    {
        "full_name": "Rohit Verma",
        "email": "rohit@traveler.in",
        "username": "rohit_verma",
        "password": "Traveler@123",
        "reputation_xp": 350,
        "home_city": "Bengaluru"
    },
    {
        "full_name": "Ananya Iyer",
        "email": "ananya@traveler.in",
        "username": "ananya_iyer",
        "password": "Traveler@123",
        "reputation_xp": 150,
        "home_city": "Chennai"
    }
]

SAMPLE_PULSE_VOTES = [
    {
        "dest_name": "Lakshadweep: Agatti, Bangaram & Kavaratti Islands",
        "user_email": "arjun@traveler.in",
        "crowd_rush": "Peaceful",
        "visit_recommendation": "Recommended",
        "safety_vibe": "Very Safe",
        "ground_weather": "Pleasant",
        "clean_sanitation": "Good",
        "user_comment": "Direct flight from Kochi to Agatti was seamless. Turquoise lagoon is mesmerizing! Very safe, tranquil atmosphere and zero crime.",
        "distance_km": 0.5
    },
    {
        "dest_name": "Taj Mahal & Agra Fort",
        "user_email": "arjun@traveler.in",
        "crowd_rush": "Heavy",
        "visit_recommendation": "Recommended",
        "safety_vibe": "Very Safe",
        "ground_weather": "Pleasant",
        "clean_sanitation": "Good",
        "user_comment": "On-site at East Gate! Pre-booked ASI digital entry took only ~20 mins. Stunning morning light on marble dome.",
        "distance_km": 0.4
    },
    {
        "dest_name": "Taj Mahal & Agra Fort",
        "user_email": "priya@traveler.in",
        "crowd_rush": "Moderate",
        "visit_recommendation": "Recommended",
        "safety_vibe": "Very Safe",
        "ground_weather": "Pleasant",
        "clean_sanitation": "Good",
        "user_comment": "Visited at 6:30 AM sunrise. Highly recommend entering early; crowd picked up exponentially after 9:30 AM.",
        "distance_km": 1.2
    },
    {
        "dest_name": "Manali & Solang Valley",
        "user_email": "rohit@traveler.in",
        "crowd_rush": "Moderate",
        "visit_recommendation": "Recommended",
        "safety_vibe": "Very Safe",
        "ground_weather": "Pleasant",
        "clean_sanitation": "Good",
        "user_comment": "At Solang Valley right now. Paragliding operations running smoothly with green flag clearances. Mountain roads clear.",
        "distance_km": 3.8
    },
    {
        "dest_name": "Varanasi Ghats & Kashi Vishwanath",
        "user_email": "priya@traveler.in",
        "crowd_rush": "Heavy",
        "visit_recommendation": "Recommended",
        "safety_vibe": "Standard Vigilance",
        "ground_weather": "Pleasant",
        "clean_sanitation": "Good",
        "user_comment": "Ganga Aarti at Dashashwamedh was packed with devotees. Hold hands with your group. Spectacular spiritual atmosphere.",
        "distance_km": 0.3
    },
    {
        "dest_name": "Goa: Baga, Calangute & Old Goa",
        "user_email": "arjun@traveler.in",
        "crowd_rush": "Moderate",
        "visit_recommendation": "Recommended",
        "safety_vibe": "Very Safe",
        "ground_weather": "Pleasant",
        "clean_sanitation": "Good",
        "user_comment": "Shack food is fresh and police patrolling active along beach belt. Note the high tide warning flags at water edge.",
        "distance_km": 0.8
    },
    {
        "dest_name": "Leh & Pangong Tso",
        "user_email": "rohit@traveler.in",
        "crowd_rush": "Peaceful",
        "visit_recommendation": "Recommended",
        "safety_vibe": "Very Safe",
        "ground_weather": "Cold/Chilly",
        "clean_sanitation": "Good",
        "user_comment": "Cobalt blue waters are mesmerizing! Temperature around 6°C with brisk winds. Thermals and windbreakers mandatory.",
        "distance_km": 2.1
    }
]

def _insert_destination_bundle(cursor, d, dest_id_map):
    """Insert one destination + metrics/tips/emergency/advisory. Mutates dest_id_map."""
    cursor.execute("""
        INSERT INTO destinations (
            name, state, region, country, category, lat, lng,
            overall_safety_score, risk_tier, description, image_url,
            best_visit_time, dress_code_etiquette, opening_time, closing_time,
            weekly_off_day, peak_rush_hours, entry_fee_domestic, entry_fee_foreign, booking_portal_url
        ) VALUES (?, ?, ?, 'India', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        d["name"], d["state"], d["region"], d["category"], d["lat"], d["lng"],
        d["overall_safety_score"], d["risk_tier"], d["description"], d["image_url"],
        d["best_visit_time"], d["dress_code_etiquette"],
        d.get("opening_time", "06:00"), d.get("closing_time", "18:30"),
        d.get("weekly_off_day", "None"), d.get("peak_rush_hours", "11:00 AM - 03:30 PM"),
        d.get("entry_fee_domestic", "Free"), d.get("entry_fee_foreign", "Free"),
        d.get("booking_portal_url", "")
    ))
    dest_id = cursor.lastrowid
    dest_id_map[d["name"]] = dest_id

    m = d["metrics"]
    cursor.execute("""
        INSERT INTO risk_metrics (
            destination_id, crime_index, scam_index, weather_risk,
            health_risk, night_safety, crowd_density, transport_safety
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (dest_id, m["crime_index"], m["scam_index"], m["weather_risk"], m["health_risk"], m["night_safety"], m["crowd_density"], m["transport_safety"]))

    for tip in d.get("tips", []):
        cursor.execute("""
            INSERT INTO safety_tips (destination_id, tip_text, category)
            VALUES (?, ?, 'Local Advice')
        """, (dest_id, tip))

    for ec in d.get("emergency", []):
        cursor.execute("""
            INSERT INTO emergency_contacts (destination_id, facility_name, facility_type, phone, address, lat, lng, is_24_7)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (dest_id, ec["name"], ec["type"], ec["phone"], ec["address"], ec.get("lat", d["lat"]), ec.get("lng", d["lng"])))

    adv = d.get("advisory")
    if adv:
        cursor.execute("""
            INSERT INTO safety_advisories (destination_id, title, alert_level, summary, issued_by, is_active)
            VALUES (?, ?, ?, ?, 'Ministry of Tourism / State Police', 1)
        """, (dest_id, adv["title"], adv["level"], adv["summary"]))

    return dest_id


def seed_database(force_refresh: bool = False):
    init_db()
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM destinations WHERE country = 'India'")
        india_dest_count = cursor.fetchone()["count"]

        # Check if operational columns populated
        cursor.execute("SELECT COUNT(*) as count FROM destinations WHERE opening_time IS NOT NULL")
        has_operational_fields = cursor.fetchone()["count"]

        if has_operational_fields == 0 or force_refresh:
            print(f"[SafeTour Bharat] Initializing database with {len(INDIA_DESTINATIONS)} iconic Indian tourist destinations and real-time operational data...")
            cursor.execute("DELETE FROM ground_pulse_votes")
            cursor.execute("DELETE FROM safety_tips")
            cursor.execute("DELETE FROM emergency_contacts")
            cursor.execute("DELETE FROM safety_advisories")
            cursor.execute("DELETE FROM risk_metrics")
            cursor.execute("DELETE FROM incidents")
            cursor.execute("DELETE FROM destinations")

            dest_id_map = {}

            for d in INDIA_DESTINATIONS:
                _insert_destination_bundle(cursor, d, dest_id_map)

            # Seed Real-Time Hazards & Incidents (Landslides, High Tides, Fog, Pilgrim Rush)
            for hz in REAL_TIME_HAZARDS:
                d_id = dest_id_map.get(hz["dest_name"])
                if d_id:
                    # Lookup destination lat/lng
                    cursor.execute("SELECT lat, lng FROM destinations WHERE id = ?", (d_id,))
                    d_row = cursor.fetchone()
                    inc_lat = d_row["lat"] + hz["lat_offset"]
                    inc_lng = d_row["lng"] + hz["lng_offset"]

                    cursor.execute("""
                        INSERT INTO incidents (
                            destination_id, title, category, severity,
                            location_name, lat, lng, description, upvotes, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 8, 'Active')
                    """, (
                        d_id, hz["title"], hz["category"], hz["severity"],
                        hz["location_name"], inc_lat, inc_lng, hz["description"]
                    ))

            conn.commit()
        elif india_dest_count < len(INDIA_DESTINATIONS):
            # Additive expansion: insert only missing destinations by name (preserve existing data)
            cursor.execute("SELECT name FROM destinations WHERE country = 'India'")
            existing = {row["name"] for row in cursor.fetchall()}
            dest_id_map = {}
            added = 0
            for d in INDIA_DESTINATIONS:
                if d["name"] in existing:
                    continue
                _insert_destination_bundle(cursor, d, dest_id_map)
                added += 1
            if added:
                print(f"[SafeTour Bharat] Added {added} new destinations (total seed catalog: {len(INDIA_DESTINATIONS)}).")
                conn.commit()
                try:
                    from app.services.demo_crowd_service import seed_destination_crowd_defaults
                    seed_destination_crowd_defaults(cursor)
                    conn.commit()
                except Exception as e:
                    print(f"[SafeTour Bharat] Crowd defaults backfill note: {e}")
            else:
                print("[SafeTour Bharat] Destination catalog already up to date.")

        # Seed Demo Users
        for u in DEMO_USERS:
            cursor.execute("SELECT id FROM users WHERE email = ?", (u["email"],))
            if not cursor.fetchone():
                hashed = hash_password(u["password"])
                cursor.execute("""
                    INSERT INTO users (full_name, email, username, password_hash, role, reputation_xp, home_city)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (u["full_name"], u["email"], u["username"], hashed, u.get("role", "tourist"), u["reputation_xp"], u["home_city"]))
        conn.commit()

        # Seed Sample Pulse Votes
        cursor.execute("SELECT COUNT(*) as count FROM ground_pulse_votes")
        vote_count = cursor.fetchone()["count"]
        if vote_count == 0:
            print("[SafeTour Bharat] Seeding verified on-site Ground Pulse votes...")
            for v in SAMPLE_PULSE_VOTES:
                cursor.execute("SELECT id, lat, lng FROM destinations WHERE name = ?", (v["dest_name"],))
                d_row = cursor.fetchone()
                cursor.execute("SELECT id, full_name, home_city FROM users WHERE email = ?", (v["user_email"],))
                u_row = cursor.fetchone()
                if d_row and u_row:
                    cursor.execute("""
                        INSERT INTO ground_pulse_votes (
                            destination_id, user_id, user_name, user_city,
                            is_onsite_verified, distance_km, crowd_rush, visit_recommendation,
                            safety_vibe, ground_weather, clean_sanitation, user_comment, helpful_count
                        ) VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, 1)
                    """, (
                        d_row["id"],
                        u_row["id"],
                        u_row["full_name"],
                        u_row["home_city"],
                        v["distance_km"],
                        v["crowd_rush"],
                        v["visit_recommendation"],
                        v["safety_vibe"],
                        v["ground_weather"],
                        v["clean_sanitation"],
                        v["user_comment"]
                    ))
            conn.commit()

        # Seed Emergency Dispatches if empty
        cursor.execute("SELECT COUNT(*) as count FROM emergency_dispatches")
        dispatch_count = cursor.fetchone()["count"]
        if dispatch_count == 0:
            cursor.execute("SELECT id, title, severity FROM incidents WHERE status = 'Active' ORDER BY id ASC")
            active_incidents = cursor.fetchall()
            for inc in active_incidents:
                title = inc["title"]
                inc_id = inc["id"]
                if "Landslide" in title:
                    cursor.execute("""
                        INSERT INTO emergency_dispatches (incident_id, agency_type, unit_callsign, contact_phone, dispatch_status, eta_minutes, responder_notes)
                        VALUES (?, 'NDRF', 'NDRF-HP-CLEARANCE-03', '+91-1902-252700', 'ON_SCENE', 0, 'Heavy earthmover and disaster personnel on site. Single-lane debris clearing in progress.')
                    """, (inc_id,))
                elif "Undertow" in title or "Tide" in title:
                    cursor.execute("""
                        INSERT INTO emergency_dispatches (incident_id, agency_type, unit_callsign, contact_phone, dispatch_status, eta_minutes, responder_notes)
                        VALUES (?, 'Police', 'GOA-COASTAL-PATROL-02', '112', 'EN_ROUTE', 4, 'Coastal rescue boat responding with lifeguards to enforce red flags.')
                    """, (inc_id,))
                elif "Surge" in title or "Pilgrim" in title:
                    cursor.execute("""
                        INSERT INTO emergency_dispatches (incident_id, agency_type, unit_callsign, contact_phone, dispatch_status, eta_minutes, responder_notes)
                        VALUES (?, 'Police', 'VARANASI-PCR-09', '112', 'DISPATCHED', 6, 'Crowd stabilization unit deployed to Godowlia Gate No. 4.')
                    """, (inc_id,))
            conn.commit()

        print("[SafeTour Bharat] Database synchronized with all-India destinations, real-time operational timings, and live hazard incidents.")

        # Crowd intelligence defaults (capacity, zones) — additive, never deletes destinations
        try:
            from app.services.demo_crowd_service import seed_destination_crowd_defaults
            seed_destination_crowd_defaults(cursor)
            conn.commit()
            print("[SafeTour Bharat] Crowd capacity / zone defaults synchronized.")
        except Exception as e:
            print(f"[SafeTour Bharat] Crowd defaults note: {e}")

if __name__ == "__main__":
    seed_database(force_refresh=True)
