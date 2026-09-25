"""
Fetch live disaster-related reports from GDELT (no API key) and Google News RSS.
Never returns fabricated disaster events on failure.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.config import (
    DISASTER_ALERT_API_URL,
    DISASTER_MAX_ARTICLES,
    DISASTER_TIMESPAN,
    GDELT_DOC_API_URL,
)
from app.services.disaster_taxonomy import classify_event, gdelt_query_terms


def _http_get(url: str, timeout: float = 12.0) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "SafeTourBharat/3.0 (+tourist-safety; research)",
            "Accept": "application/json, application/rss+xml, application/xml, text/xml, */*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _normalize_title(title: str) -> str:
    t = (title or "").lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:180]


def dedupe_key(title: str, url: str = "") -> str:
    base = _normalize_title(title)
    host = ""
    if url:
        try:
            host = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
        except Exception:
            host = ""
    return f"{base}|{host}"


def fetch_gdelt_articles(max_records: Optional[int] = None) -> List[Dict[str, Any]]:
    """GDELT DOC 2.0 ArtList — free, no key. India-focused disaster query."""
    max_records = max_records or DISASTER_MAX_ARTICLES
    query = gdelt_query_terms()
    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "maxrecords": str(min(250, max(10, max_records))),
        "timespan": DISASTER_TIMESPAN,
        "sort": "HybridRel",
    }
    url = GDELT_DOC_API_URL + "?" + urllib.parse.urlencode(params)
    try:
        raw = _http_get(url, timeout=15.0)
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as e:
        print(f"[DisasterIngest] GDELT fetch failed: {e}")
        return []

    articles = []
    for item in data.get("articles") or []:
        title = (item.get("title") or "").strip()
        if not title:
            continue
        text = f"{title} {item.get('seendate') or ''}"
        etype = classify_event(title)
        if not etype:
            continue
        url_art = item.get("url") or ""
        articles.append({
            "title": title,
            "summary": title,
            "source": item.get("domain") or item.get("sourceCountry") or "GDELT",
            "url": url_art,
            "published_at": item.get("seendate") or "",
            "event_type": etype,
            "provider": "gdelt",
            "official_alert": False,
            "dedupe_key": dedupe_key(title, url_art),
        })
    return articles


def fetch_google_news_disaster(max_per_query: int = 8) -> List[Dict[str, Any]]:
    """Google News RSS for India disaster topics — no API key. Empty list on failure."""
    queries = [
        "India flood OR flooding OR flash flood",
        "India landslide OR mudslide",
        "India cyclone OR storm surge",
        "India earthquake",
        "India heavy rainfall cloudburst warning",
    ]
    out: List[Dict[str, Any]] = []
    for q in queries:
        encoded = urllib.parse.quote(q)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
        try:
            xml_bytes = _http_get(url, timeout=8.0)
            root = ET.fromstring(xml_bytes)
            for item in root.findall(".//item")[:max_per_query]:
                title_raw = item.findtext("title") or ""
                link = item.findtext("link") or ""
                pub = item.findtext("pubDate") or ""
                desc = item.findtext("description") or ""
                source_el = item.find("source")
                source = source_el.text if source_el is not None else "Google News"
                clean_title = title_raw
                if " - " in title_raw:
                    parts = title_raw.rsplit(" - ", 1)
                    clean_title = parts[0]
                    if source == "Google News":
                        source = parts[1]
                etype = classify_event(clean_title + " " + desc)
                if not etype:
                    continue
                out.append({
                    "title": clean_title.strip(),
                    "summary": re.sub(r"<[^>]+>", "", desc)[:240],
                    "source": source,
                    "url": link,
                    "published_at": pub,
                    "event_type": etype,
                    "provider": "google_news_rss",
                    "official_alert": False,
                    "dedupe_key": dedupe_key(clean_title, link),
                })
        except Exception as e:
            print(f"[DisasterIngest] Google News RSS failed for '{q}': {e}")
            continue
    return out


def fetch_official_cap_alerts() -> List[Dict[str, Any]]:
    """
    Optional official CAP/SACHET-style feed if DISASTER_ALERT_API_URL is configured.
    Returns [] when unset or on failure — never fabricates alerts.
    """
    if not DISASTER_ALERT_API_URL:
        return []
    try:
        raw = _http_get(DISASTER_ALERT_API_URL, timeout=12.0)
        text = raw.decode("utf-8", errors="ignore")
        # Minimal CAP parse: look for <headline> / <description> / <areaDesc>
        root = ET.fromstring(text)
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"
        out = []
        for alert in root.findall(f".//{ns}alert") or [root]:
            for info in alert.findall(f"{ns}info"):
                headline = (info.findtext(f"{ns}headline") or "").strip()
                desc = (info.findtext(f"{ns}description") or "").strip()
                area = ""
                for a in info.findall(f"{ns}area"):
                    area = (a.findtext(f"{ns}areaDesc") or area or "").strip()
                body = f"{headline} {desc} {area}"
                etype = classify_event(body) or "extreme_weather"
                if not headline and not desc:
                    continue
                title = headline or desc[:120]
                out.append({
                    "title": title,
                    "summary": (desc or headline)[:400],
                    "source": "Official CAP Alert",
                    "url": DISASTER_ALERT_API_URL,
                    "published_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "event_type": etype,
                    "provider": "official_cap",
                    "official_alert": True,
                    "dedupe_key": dedupe_key(title, "official_cap"),
                    "area_hint": area,
                })
        return out
    except Exception as e:
        print(f"[DisasterIngest] Official CAP fetch failed: {e}")
        return []


def fetch_all_live_articles() -> List[Dict[str, Any]]:
    """Merge providers and dedupe by dedupe_key. No mock/filler articles."""
    merged: Dict[str, Dict[str, Any]] = {}
    for art in fetch_official_cap_alerts() + fetch_gdelt_articles() + fetch_google_news_disaster():
        key = art.get("dedupe_key") or dedupe_key(art.get("title", ""), art.get("url", ""))
        if key in merged:
            # Prefer official over news if duplicate
            if art.get("official_alert") and not merged[key].get("official_alert"):
                merged[key] = art
            continue
        merged[key] = art
    return list(merged.values())
