"""Geofencing utilities — circular radius + optional polygon (ray casting)."""
from __future__ import annotations

import json
import math
from typing import Any, Dict, List, Optional, Tuple


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def validate_coordinates(lat: float, lon: float) -> None:
    if lat is None or lon is None:
        raise ValueError("Latitude and longitude are required")
    if not (-90.0 <= float(lat) <= 90.0):
        raise ValueError("Latitude must be between -90 and 90")
    if not (-180.0 <= float(lon) <= 180.0):
        raise ValueError("Longitude must be between -180 and 180")


def point_in_polygon(lat: float, lon: float, polygon: List[Tuple[float, float]]) -> bool:
    """Ray-casting. polygon = list of (lat, lon) rings; closed or open."""
    if not polygon or len(polygon) < 3:
        return False
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        yi, xi = polygon[i][0], polygon[i][1]
        yj, xj = polygon[j][0], polygon[j][1]
        intersects = ((xi > lon) != (xj > lon)) and (
            lat < (yj - yi) * (lon - xi) / ((xj - xi) or 1e-12) + yi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def parse_polygon(polygon_json: Optional[str]) -> Optional[List[Tuple[float, float]]]:
    if not polygon_json:
        return None
    try:
        data = json.loads(polygon_json) if isinstance(polygon_json, str) else polygon_json
        points = []
        for p in data:
            if isinstance(p, dict):
                points.append((float(p["lat"]), float(p["lng"])))
            else:
                points.append((float(p[0]), float(p[1])))
        return points if len(points) >= 3 else None
    except Exception:
        return None


def is_inside_destination(
    lat: float,
    lon: float,
    dest: Dict[str, Any],
) -> Tuple[bool, float]:
    """
    Returns (inside, distance_meters_from_center).
    Prefer polygon geofence when present; otherwise circular radius.
    """
    validate_coordinates(lat, lon)
    center_lat = float(dest["lat"])
    center_lng = float(dest["lng"])
    distance_m = haversine_meters(lat, lon, center_lat, center_lng)

    polygon = parse_polygon(dest.get("geofence_polygon"))
    if polygon:
        return point_in_polygon(lat, lon, polygon), round(distance_m, 1)

    radius = float(dest.get("geofence_radius_m") or 800)
    return distance_m <= radius, round(distance_m, 1)


def is_inside_zone(lat: float, lon: float, zone: Dict[str, Any]) -> bool:
    polygon = parse_polygon(zone.get("polygon_json"))
    if polygon:
        return point_in_polygon(lat, lon, polygon)
    if zone.get("center_lat") is None or zone.get("center_lng") is None:
        return False
    radius = float(zone.get("radius_m") or 150)
    dist = haversine_meters(lat, lon, float(zone["center_lat"]), float(zone["center_lng"]))
    return dist <= radius
