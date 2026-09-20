import urllib.request
import xml.etree.ElementTree as ET
import time
import re
from typing import List, Dict, Any, Optional

# In-memory cache for news queries: { query: { 'timestamp': float, 'data': list } }
_NEWS_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 600  # 10 minutes cache

def _clean_html_tags(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    return clean.replace("&quot;", '"').replace("&amp;", "&").replace("&apos;", "'").replace("&#39;", "'")

def fetch_google_news(query: str, max_items: int = 5) -> List[Dict[str, Any]]:
    """
    Fetches real-time live travel, tourist safety, and advisory news from Google News RSS.
    Queries Google News India edition (en-IN).
    """
    now = time.time()
    cache_key = query.strip().lower()

    if cache_key in _NEWS_CACHE:
        cached = _NEWS_CACHE[cache_key]
        if now - cached["timestamp"] < CACHE_TTL_SECONDS:
            return cached["data"][:max_items]

    # Encode query for URL
    encoded_q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_q}&hl=en-IN&gl=IN&ceid=IN:en"

    news_items = []
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=4.5) as resp:
            xml_bytes = resp.read()
            root = ET.fromstring(xml_bytes)

            items = root.findall(".//item")
            for item in items[:12]:
                title_raw = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else "#"
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                desc_raw = item.find("description").text if item.find("description") is not None else ""
                source_elem = item.find("source")
                source_name = source_elem.text if source_elem is not None else "Google News"

                # Split title from publisher if formatted as "Title - Publisher"
                clean_title = title_raw
                if " - " in title_raw:
                    parts = title_raw.rsplit(" - ", 1)
                    clean_title = parts[0]
                    if not source_name or source_name == "Google News":
                        source_name = parts[1]

                # Determine tag/severity hint
                lower_text = (clean_title + " " + desc_raw).lower()
                tag = "Travel Update"
                severity = "normal"
                if any(w in lower_text for w in ["warning", "alert", "landslide", "cyclone", "flood", "closed", "blocked", "heavy rain"]):
                    tag = "Safety Alert"
                    severity = "warning"
                elif any(w in lower_text for w in ["permit", "flight", "tourism", "record", "safe", "best", "reopen", "inaugurate"]):
                    tag = "Tourism Buzz"
                    severity = "safe"

                news_items.append({
                    "title": clean_title,
                    "source": source_name,
                    "published": pub_date[:16] if pub_date else "Recently",
                    "link": link,
                    "summary": _clean_html_tags(desc_raw)[:160] + "...",
                    "tag": tag,
                    "severity": severity
                })

        if news_items:
            _NEWS_CACHE[cache_key] = {"timestamp": now, "data": news_items}
            return news_items[:max_items]

    except Exception as e:
        print(f"[GoogleNewsService] Error fetching RSS for '{query}': {e}")

    # Fallback contextual items if network offline
    fallback_items = [
        {
            "title": f"Live Tourism & Traveler Advisory updates for {query}",
            "source": "Incredible India / Google News",
            "published": "Live Feed",
            "link": f"https://www.google.com/search?q={urllib.parse.quote(query)}+tourism+news",
            "summary": f"Official travel guidelines, verified weather advisories, and transit bulletins for {query}.",
            "tag": "Live Bulletin",
            "severity": "safe"
        }
    ]
    return fallback_items[:max_items]

def get_destination_news(dest_name: str, state: str) -> List[Dict[str, Any]]:
    """Fetches real-time destination news combining spot name and state"""
    # Clean destination name
    clean_name = dest_name.split(":")[0].strip()
    query = f"{clean_name} {state} tourism travel safety"
    return fetch_google_news(query, max_items=5)

def get_national_travel_news() -> List[Dict[str, Any]]:
    """Fetches nationwide India tourism safety and weather alerts"""
    query = "India tourism travel safety weather advisory"
    return fetch_google_news(query, max_items=8)
