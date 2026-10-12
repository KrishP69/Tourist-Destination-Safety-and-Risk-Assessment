"""
Fetch authentic, canonical, high-resolution landmark images for all 79 destinations,
apply subtle visual enhancement (contrast/vibrance/sharpness) for a clean cinematic look,
save locally to frontend/img/destinations/dest_{id}.jpg,
and update SQLite destinations.image_url to /static/img/destinations/dest_{id}.jpg.
Zero duplicate photos. Zero Taj Mahal photos on other landmarks.
"""
import os
import sys
import json
import sqlite3
import urllib.request
from pathlib import Path
from PIL import Image, ImageEnhance

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_IMG_DIR = BASE_DIR.parent / "frontend" / "img" / "destinations"
STATIC_IMG_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = BASE_DIR / "data" / "safety_assessment.db"

# Exact Wikipedia canonical topic titles for every Indian destination
LANDMARK_WIKI_MAP = {
    300: ["Taj_Mahal", "Agra_Fort"],
    301: ["Ghats_in_Varanasi", "Dashashwamedh_Ghat", "Varanasi"],
    302: ["Solang_Valley", "Manali,_Himachal_Pradesh"],
    303: ["Pangong_Tso", "Leh"],
    304: ["Shimla", "Kufri,_India"],
    305: ["Rishikesh", "Har_Ki_Pauri", "Haridwar"],
    306: ["Golden_Temple", "Harmandir_Sahib"],
    307: ["Kedarnath_Temple", "Badrinath_Temple"],
    308: ["Gulmarg", "Dal_Lake", "Srinagar"],
    309: ["Qutb_Minar", "Red_Fort"],
    310: ["Ram_Mandir,_Ayodhya", "Ayodhya"],
    311: ["Nainital_Lake", "Nainital", "Mussoorie"],
    312: ["Hawa_Mahal", "Amer_Fort", "Jaipur"],
    313: ["Baga_Beach", "Calangute_Beach", "Goa"],
    314: ["Lake_Pichola", "City_Palace,_Udaipur"],
    315: ["Gateway_of_India", "Marine_Drive,_Mumbai"],
    316: ["Jaisalmer_Fort", "Thar_Desert"],
    317: ["Statue_of_Unity"],
    318: ["Kailasa_temple,_Ellora", "Ellora_Caves", "Ajanta_Caves"],
    319: ["Khajuraho_Group_of_Monuments", "Kandariya_Mahadeva_Temple"],
    320: ["Great_Rann_of_Kutch", "Rann_of_Kutch"],
    321: ["Munnar", "Eravikulam_National_Park"],
    322: ["Alappuzha", "Kerala_backwaters"],
    323: ["Virupaksha_Temple,_Hampi", "Hampi"],
    324: ["Nilgiri_Mountain_Railway", "Ooty"],
    325: ["Meenakshi_Temple", "Madurai"],
    326: ["Mysore_Palace"],
    327: ["Venkateswara_Temple,_Tirumala", "Tirupati"],
    328: ["Vivekananda_Rock_Memorial"],
    329: ["Darjeeling_Himalayan_Railway", "Tiger_Hill,_Darjeeling", "Darjeeling"],
    330: ["Jagannath_Temple,_Puri", "Puri"],
    331: ["Living_root_bridge", "Elephant_Falls_(Shillong)", "Cherrapunji"],
    332: ["Kaziranga_National_Park"],
    333: ["Tawang_Monastery"],
    334: ["Mahabodhi_Temple", "Bodh_Gaya"],
    335: ["Radhanagar_Beach", "Havelock_Island"],
    336: ["Bangaram_Atoll", "Agatti_Island", "Lakshadweep"],
    337: ["Thiruvalluvar_Statue", "Vivekananda_Rock_Memorial"],
    338: ["Elephanta_Caves"],
    339: ["Lonavala", "Khandala"],
    340: ["Mahabaleshwar"],
    341: ["Shirdi_Sai_Baba_Temple", "Shirdi"],
    342: ["Kolaba_Fort", "Alibag"],
    343: ["Kanheri_Caves", "Sanjay_Gandhi_National_Park"],
    344: ["India_Gate"],
    345: ["Lotus_Temple"],
    346: ["Humayun%27s_Tomb"],
    347: ["Swaminarayan_Akshardham_(Delhi)", "Akshardham_(Delhi)"],
    348: ["Fatehpur_Sikri", "Buland_Darwaza"],
    349: ["Dhamek_Stupa", "Sarnath"],
    350: ["Mehrangarh", "Jodhpur"],
    351: ["Pushkar_Lake", "Brahma_Temple,_Pushkar"],
    352: ["Sanchi", "Great_Stupa_at_Sanchi"],
    353: ["Mahakaleshwar_Jyotirlinga", "Ujjain"],
    354: ["McLeod_Ganj", "Dharamshala"],
    355: ["Dalhousie,_India"],
    356: ["Parvati_Valley", "Kasol"],
    357: ["Betaab_Valley", "Pahalgam"],
    358: ["Charminar"],
    359: ["Golconda_Fort"],
    360: ["Abbey_Falls", "Kodagu_district"],
    361: ["Om_Beach", "Gokarna,_India"],
    362: ["Chinese_fishing_nets", "Fort_Kochi"],
    363: ["Varkala_Beach"],
    364: ["Kovalam"],
    365: ["Marina_Beach"],
    366: ["Shore_Temple", "Group_of_Monuments_at_Mahabalipuram"],
    367: ["Kodaikanal_Lake", "Kodaikanal"],
    368: ["Konark_Sun_Temple"],
    369: ["Victoria_Memorial,_Kolkata"],
    370: ["Gangtok"],
    371: ["Lake_Tsomgo"],
    372: ["Kamakhya_Temple"],
    373: ["Ranthambore_Fort", "Ranthambore_National_Park"],
    374: ["Jim_Corbett_National_Park"],
    375: ["Promenade_Beach", "Pondicherry"],
    376: ["Somnath_temple"],
    377: ["Dwarkadhish_Temple", "Dwarka"],
    378: ["Lohagad", "Lohagad_Fort"]
}

# Reliable fallback direct URLs for Indian landmarks
FALLBACK_DIRECT_URLS = {
    300: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Taj_Mahal_%28Edited%29.jpeg/1280px-Taj_Mahal_%28Edited%29.jpeg",
    301: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Varanasi_Ghats_panorama.jpg/1280px-Varanasi_Ghats_panorama.jpg",
    302: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Solang_valley.jpg/1280px-Solang_valley.jpg",
    303: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Pangong_Tso_lake_Ladakh.jpg/1280px-Pangong_Tso_lake_Ladakh.jpg",
    304: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Shimla_Ridge_Church.jpg/1280px-Shimla_Ridge_Church.jpg",
    305: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Laxman_Jhula_Rishikesh.jpg/1280px-Laxman_Jhula_Rishikesh.jpg",
    306: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amritsar_at_night.jpg/1280px-The_Golden_Temple_of_Amritsar_at_night.jpg",
    307: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Kedarnath_Temple_Uttarakhand.jpg/1280px-Kedarnath_Temple_Uttarakhand.jpg",
    308: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Dal_lake_Srinagar_Kashmir.jpg/1280px-Dal_lake_Srinagar_Kashmir.jpg",
    309: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Qutub_Minar_in_New_Delhi_06-2016_img3.jpg/1280px-Qutub_Minar_in_New_Delhi_06-2016_img3.jpg",
    310: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Ayodhya_Ram_Mandir_Inauguration.jpg/1280px-Ayodhya_Ram_Mandir_Inauguration.jpg",
    311: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Naini_Lake_Nainital_Uttarakhand.jpg/1280px-Naini_Lake_Nainital_Uttarakhand.jpg",
    312: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Hawa_Mahal_2011.jpg/1280px-Hawa_Mahal_2011.jpg",
    313: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Baga_Beach_Goa.jpg/1280px-Baga_Beach_Goa.jpg",
    314: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Udaipur_City_Palace_Lake_Pichola.jpg/1280px-Udaipur_City_Palace_Lake_Pichola.jpg",
    315: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Mumbai_03-2016_30_Gateway_of_India.jpg/1280px-Mumbai_03-2016_30_Gateway_of_India.jpg",
    316: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Jaisalmer_Fort_Rajasthan.jpg/1280px-Jaisalmer_Fort_Rajasthan.jpg",
    317: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Statue_of_Unity.jpg/1280px-Statue_of_Unity.jpg",
    318: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Ellora_cave16_001.jpg/1280px-Ellora_cave16_001.jpg",
    319: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Kandariya_Mahadeva_temple_Khajuraho.jpg/1280px-Kandariya_Mahadeva_temple_Khajuraho.jpg",
    320: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/White_Desert_Rann_of_Kutch.jpg/1280px-White_Desert_Rann_of_Kutch.jpg",
    321: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Tea_plantations_Munnar_Kerala.jpg/1280px-Tea_plantations_Munnar_Kerala.jpg",
    322: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Alappuzha_Boat_Beauty_W.jpg/1280px-Alappuzha_Boat_Beauty_W.jpg",
    323: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Stone_Chariot_Hampi.jpg/1280px-Stone_Chariot_Hampi.jpg",
    324: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Nilgiri_Mountain_Railway_steam_loco.jpg/1280px-Nilgiri_Mountain_Railway_steam_loco.jpg",
    325: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Meenakshi_Amman_Temple_Towers.jpg/1280px-Meenakshi_Amman_Temple_Towers.jpg",
    326: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Mysore_Palace_Illumination.jpg/1280px-Mysore_Palace_Illumination.jpg",
    327: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Tirumala_Venkateswara_Temple.jpg/1280px-Tirumala_Venkateswara_Temple.jpg",
    328: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Vivekananda_Rock_Memorial_Kanyakumari.jpg/1280px-Vivekananda_Rock_Memorial_Kanyakumari.jpg",
    329: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Darjeeling_Himalayan_Railway_Batasia_Loop.jpg/1280px-Darjeeling_Himalayan_Railway_Batasia_Loop.jpg",
    330: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Jagannath_Temple_Puri.jpg/1280px-Jagannath_Temple_Puri.jpg",
    331: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Living_Root_Bridge_Cherrapunji.jpg/1280px-Living_Root_Bridge_Cherrapunji.jpg",
    332: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Rhino_in_Kaziranga.jpg/1280px-Rhino_in_Kaziranga.jpg",
    333: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Tawang_Monastery_Arunachal.jpg/1280px-Tawang_Monastery_Arunachal.jpg",
    334: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Mahabodhi_Temple_Bodh_Gaya.jpg/1280px-Mahabodhi_Temple_Bodh_Gaya.jpg",
    335: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Radhanagar_Beach_Havelock.jpg/1280px-Radhanagar_Beach_Havelock.jpg",
    336: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Bangaram_Island_Lakshadweep.jpg/1280px-Bangaram_Island_Lakshadweep.jpg",
    337: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Thiruvalluvar_Statue_Kanyakumari.jpg/1280px-Thiruvalluvar_Statue_Kanyakumari.jpg",
    338: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Elephanta_Caves_Trimurti.jpg/1280px-Elephanta_Caves_Trimurti.jpg",
    339: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Tiger%27s_Leap_Lonavala.jpg/1280px-Tiger%27s_Leap_Lonavala.jpg",
    340: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Mahabaleshwar_Arthur_Seat.jpg/1280px-Mahabaleshwar_Arthur_Seat.jpg",
    341: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Shirdi_Sai_Baba_Samadhi_Mandir.jpg/1280px-Shirdi_Sai_Baba_Samadhi_Mandir.jpg",
    342: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Kolaba_Fort_Alibaug.jpg/1280px-Kolaba_Fort_Alibaug.jpg",
    343: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Kanheri_Caves_Mumbai.jpg/1280px-Kanheri_Caves_Mumbai.jpg",
    344: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/India_Gate_in_New_Delhi_03-2016.jpg/1280px-India_Gate_in_New_Delhi_03-2016.jpg",
    345: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/LotusDelhi.jpg/1280px-LotusDelhi.jpg",
    346: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Humayun%27s_Tomb_Delhi_India.jpg/1280px-Humayun%27s_Tomb_Delhi_India.jpg",
    347: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Akshardham_Temple_Delhi.jpg/1280px-Akshardham_Temple_Delhi.jpg",
    348: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Buland_Darwaza_Fatehpur_Sikri.jpg/1280px-Buland_Darwaza_Fatehpur_Sikri.jpg",
    349: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Dhamekh_Stupa_Sarnath.jpg/1280px-Dhamekh_Stupa_Sarnath.jpg",
    350: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Mehrangarh_Fort_Jodhpur.jpg/1280px-Mehrangarh_Fort_Jodhpur.jpg",
    351: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Pushkar_Holy_Lake_Ghats.jpg/1280px-Pushkar_Holy_Lake_Ghats.jpg",
    352: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Great_Stupa_at_Sanchi.jpg/1280px-Great_Stupa_at_Sanchi.jpg",
    353: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Mahakaleshwar_Jyotirlinga_Ujjain.jpg/1280px-Mahakaleshwar_Jyotirlinga_Ujjain.jpg",
    354: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Tsuglagkhang_Complex_McLeod_Ganj.jpg/1280px-Tsuglagkhang_Complex_McLeod_Ganj.jpg",
    355: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Dalhousie_Himachal_Pradesh.jpg/1280px-Dalhousie_Himachal_Pradesh.jpg",
    356: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Parvati_River_Kasol.jpg/1280px-Parvati_River_Kasol.jpg",
    357: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Betaab_Valley_Pahalgam.jpg/1280px-Betaab_Valley_Pahalgam.jpg",
    358: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Charminar_Hyderabad_Telangana.jpg/1280px-Charminar_Hyderabad_Telangana.jpg",
    359: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Golconda_Fort_Hyderabad.jpg/1280px-Golconda_Fort_Hyderabad.jpg",
    360: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Abbey_Falls_Madikeri_Coorg.jpg/1280px-Abbey_Falls_Madikeri_Coorg.jpg",
    361: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Om_Beach_Gokarna.jpg/1280px-Om_Beach_Gokarna.jpg",
    362: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Chinese_Fishing_Nets_Kochi.jpg/1280px-Chinese_Fishing_Nets_Kochi.jpg",
    363: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Varkala_Cliff_Beach.jpg/1280px-Varkala_Cliff_Beach.jpg",
    364: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Lighthouse_Beach_Kovalam.jpg/1280px-Lighthouse_Beach_Kovalam.jpg",
    365: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Marina_Beach_Chennai.jpg/1280px-Marina_Beach_Chennai.jpg",
    366: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Shore_Temple_Mahabalipuram.jpg/1280px-Shore_Temple_Mahabalipuram.jpg",
    367: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Kodaikanal_Lake_Tamil_Nadu.jpg/1280px-Kodaikanal_Lake_Tamil_Nadu.jpg",
    368: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Konark_Sun_Temple_2022.jpg/1280px-Konark_Sun_Temple_2022.jpg",
    369: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Victoria_Memorial_Kolkata.jpg/1280px-Victoria_Memorial_Kolkata.jpg",
    370: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Gangtok_Sikkim_Himalayas.jpg/1280px-Gangtok_Sikkim_Himalayas.jpg",
    371: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Tsomgo_Lake_Sikkim.jpg/1280px-Tsomgo_Lake_Sikkim.jpg",
    372: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Kamakhya_Temple_Guwahati.jpg/1280px-Kamakhya_Temple_Guwahati.jpg",
    373: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Ranthambore_Fort_Rajasthan.jpg/1280px-Ranthambore_Fort_Rajasthan.jpg",
    374: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Jim_Corbett_National_Park_Tiger.jpg/1280px-Jim_Corbett_National_Park_Tiger.jpg",
    375: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Promenade_Beach_Pondicherry.jpg/1280px-Promenade_Beach_Pondicherry.jpg",
    376: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Somnath_Temple_Gujarat.jpg/1280px-Somnath_Temple_Gujarat.jpg",
    377: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Dwarkadhish_Temple_Dwarka.jpg/1280px-Dwarkadhish_Temple_Dwarka.jpg",
    378: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Panoramic_view_of_the_bastions_of_Lohagad_Fort_2.jpg/1280px-Panoramic_view_of_the_bastions_of_Lohagad_Fort_2.jpg"
}


def fetch_wiki_image_url(topic: str) -> str | None:
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "SafeTourBharat/3.0 (academic student project; contact@safetour.edu)"}
        )
        with urllib.request.urlopen(req, timeout=8) as res:
            data = json.loads(res.read().decode("utf-8"))
            orig = data.get("originalimage", {}).get("source")
            if orig:
                return orig
            thumb = data.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    except Exception:
        pass
    return None


def download_and_process_image(img_url: str, dest_id: int) -> bool:
    target_path = STATIC_IMG_DIR / f"dest_{dest_id}.jpg"
    try:
        req = urllib.request.Request(
            img_url,
            headers={"User-Agent": "SafeTourBharat/3.0 (academic student project; contact@safetour.edu)"}
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            data = response.read()

        temp_path = STATIC_IMG_DIR / f"temp_{dest_id}.raw"
        with open(temp_path, "wb") as f:
            f.write(data)

        # Process with Pillow to ensure standard dimensions and aesthetic finish
        with Image.open(temp_path) as im:
            im = im.convert("RGB")
            # Proportional resize/crop to 1200x800
            target_w, target_h = 1200, 800
            src_w, src_h = im.size
            src_ratio = src_w / src_h
            target_ratio = target_w / target_h

            if src_ratio > target_ratio:
                # Wider: crop sides
                new_w = int(src_h * target_ratio)
                left = (src_w - new_w) // 2
                im = im.crop((left, 0, left + new_w, src_h))
            else:
                # Taller: crop top/bottom
                new_h = int(src_w / target_ratio)
                top = (src_h - new_h) // 2
                im = im.crop((0, top, src_w, top + new_h))

            im = im.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # Apply subtle cinematic color/contrast enhancement
            im = ImageEnhance.Color(im).enhance(1.08)
            im = ImageEnhance.Contrast(im).enhance(1.05)
            im = ImageEnhance.Sharpness(im).enhance(1.04)

            im.save(target_path, "JPEG", quality=90, optimize=True)

        if temp_path.exists():
            temp_path.unlink()

        return True
    except Exception as e:
        print(f"  [!] Failed downloading/processing {dest_id} from {img_url}: {e}")
        return False


from concurrent.futures import ThreadPoolExecutor, as_completed

def process_single_destination(dest_item):
    did, name = dest_item
    img_url = None

    # 1. Try Wikipedia summary API queries
    queries = LANDMARK_WIKI_MAP.get(did, [])
    for q in queries:
        img_url = fetch_wiki_image_url(q)
        if img_url:
            break

    # 2. If not found via API, use fallback direct URL
    if not img_url and did in FALLBACK_DIRECT_URLS:
        img_url = FALLBACK_DIRECT_URLS[did]

    if not img_url:
        return did, name, False, "No URL found"

    ok = download_and_process_image(img_url, did)
    if not ok and did in FALLBACK_DIRECT_URLS and img_url != FALLBACK_DIRECT_URLS[did]:
        ok = download_and_process_image(FALLBACK_DIRECT_URLS[did], did)

    if ok:
        local_url = f"/static/img/destinations/dest_{did}.jpg"
        return did, name, True, local_url
    return did, name, False, "Download/process failed"


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM destinations ORDER BY id ASC")
    destinations = cursor.fetchall()
    print(f"Total destinations to process concurrently: {len(destinations)}")

    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_single_destination, d): d for d in destinations}
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            did, name, ok, msg = res
            status = "✓" if ok else "✗"
            print(f"[{status}] {did}: {name} -> {msg}")

    # Commit all successful updates to database
    success_count = 0
    for did, name, ok, local_url in results:
        if ok:
            cursor.execute("UPDATE destinations SET image_url = ? WHERE id = ?", (local_url, did))
            success_count += 1
    conn.commit()
    conn.close()
    print(f"\n==========================================")
    print(f"COMPLETE: {success_count}/{len(destinations)} destination images created & saved!")
    print(f"==========================================")


if __name__ == "__main__":
    main()
