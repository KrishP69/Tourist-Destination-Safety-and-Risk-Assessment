"""
OLAP + K-Means Clustering Service for Tourist Destination Safety & Risk Assessment.

Implements:
  - OLAP cube: multi-dimensional aggregation of safety/crowd metrics
    across Region × Category × RiskTier dimensions.
  - K-Means clustering: groups destinations by safety profile using
    pure-Python implementation (no heavy ML deps — only stdlib + math).
  - Cluster characterization: labels clusters with human-readable names.
  - API-ready payloads for the frontend analytics dashboard.
"""
from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Tuple

from app.database import get_db


# ---------------------------------------------------------------------------
# OLAP Cube
# ---------------------------------------------------------------------------

OLAP_DIMENSIONS = ["region", "category", "risk_tier"]
OLAP_MEASURES = [
    "avg_safety_score",
    "avg_crime_index",
    "avg_scam_index",
    "avg_weather_risk",
    "avg_night_safety",
    "avg_crowd_density",
    "destination_count",
]


def build_olap_cube(
    dimensions: Optional[List[str]] = None,
    filters: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Build an OLAP cube aggregating destination safety metrics.

    Args:
        dimensions: subset of OLAP_DIMENSIONS to group by (default: all).
        filters:    {dimension_col: value} pairs to restrict the slice.

    Returns:
        {
          "dimensions": [...],
          "cells": [{dim_values..., measures...}, ...],
          "totals": {measure: value, ...},
          "metadata": {...}
        }
    """
    dims = dimensions or OLAP_DIMENSIONS
    # Validate dimensions
    valid = set(OLAP_DIMENSIONS)
    dims = [d for d in dims if d in valid]
    if not dims:
        dims = list(OLAP_DIMENSIONS)

    # Build GROUP BY clause
    dim_cols = ", ".join(f"d.{c}" for c in dims)
    group_by = ", ".join(f"d.{c}" for c in dims)

    # WHERE clause for drill-down / slicing
    where_parts = ["1=1"]
    where_vals: List[Any] = []
    if filters:
        for col, val in filters.items():
            if col in valid:
                where_parts.append(f"d.{col} = ?")
                where_vals.append(val)

    where_clause = " AND ".join(where_parts)

    query = f"""
        SELECT
            {dim_cols},
            COUNT(d.id)                  AS destination_count,
            ROUND(AVG(d.overall_safety_score), 2)  AS avg_safety_score,
            ROUND(AVG(m.crime_index), 2)            AS avg_crime_index,
            ROUND(AVG(m.scam_index), 2)             AS avg_scam_index,
            ROUND(AVG(m.weather_risk), 2)           AS avg_weather_risk,
            ROUND(AVG(m.night_safety), 2)           AS avg_night_safety,
            ROUND(AVG(m.crowd_density), 2)          AS avg_crowd_density,
            ROUND(AVG(m.transport_safety), 2)       AS avg_transport_safety
        FROM destinations d
        JOIN risk_metrics m ON m.destination_id = d.id
        WHERE {where_clause}
        GROUP BY {group_by}
        ORDER BY {group_by}
    """

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, where_vals)
        rows = [dict(r) for r in cursor.fetchall()]

        # Grand totals
        cursor.execute(
            f"""
            SELECT
                COUNT(d.id)                          AS destination_count,
                ROUND(AVG(d.overall_safety_score), 2) AS avg_safety_score,
                ROUND(AVG(m.crime_index), 2)           AS avg_crime_index,
                ROUND(AVG(m.scam_index), 2)            AS avg_scam_index,
                ROUND(AVG(m.weather_risk), 2)          AS avg_weather_risk,
                ROUND(AVG(m.night_safety), 2)          AS avg_night_safety,
                ROUND(AVG(m.crowd_density), 2)         AS avg_crowd_density,
                ROUND(AVG(m.transport_safety), 2)      AS avg_transport_safety
            FROM destinations d
            JOIN risk_metrics m ON m.destination_id = d.id
            WHERE {where_clause}
            """,
            where_vals,
        )
        totals_row = cursor.fetchone()
        totals = dict(totals_row) if totals_row else {}

    return {
        "dimensions": dims,
        "cells": rows,
        "totals": totals,
        "filters_applied": filters or {},
        "metadata": {
            "measures": OLAP_MEASURES,
            "cell_count": len(rows),
            "label": "OLAP aggregation — safety & crowd intelligence cube",
        },
    }


def olap_drill_down(
    parent_dim: str,
    parent_value: str,
    child_dim: str,
) -> Dict[str, Any]:
    """Drill down from one OLAP dimension value into another child dimension."""
    return build_olap_cube(
        dimensions=[parent_dim, child_dim],
        filters={parent_dim: parent_value},
    )


def olap_slice(dimension: str, value: str) -> Dict[str, Any]:
    """Fix one dimension and aggregate the remaining two (OLAP slice)."""
    remaining_dims = [d for d in OLAP_DIMENSIONS if d != dimension]
    return build_olap_cube(dimensions=remaining_dims, filters={dimension: value})


def olap_dice(filters: Dict[str, str]) -> Dict[str, Any]:
    """Restrict multiple dimensions simultaneously (OLAP dice)."""
    remaining_dims = [d for d in OLAP_DIMENSIONS if d not in filters]
    return build_olap_cube(dimensions=remaining_dims or OLAP_DIMENSIONS, filters=filters)


# ---------------------------------------------------------------------------
# Pure-Python K-Means (no sklearn / numpy required)
# ---------------------------------------------------------------------------

def _euclidean(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _mean_vector(vectors: List[List[float]]) -> List[float]:
    n = len(vectors)
    if n == 0:
        return []
    dim = len(vectors[0])
    return [sum(v[i] for v in vectors) / n for i in range(dim)]


def _normalize(vectors: List[List[float]]) -> Tuple[List[List[float]], List[float], List[float]]:
    """Min-max normalize each feature to [0, 1]."""
    if not vectors:
        return [], [], []
    dim = len(vectors[0])
    mins = [min(v[i] for v in vectors) for i in range(dim)]
    maxs = [max(v[i] for v in vectors) for i in range(dim)]
    ranges = [mx - mn if mx != mn else 1.0 for mn, mx in zip(mins, maxs)]
    normed = [
        [(v[i] - mins[i]) / ranges[i] for i in range(dim)]
        for v in vectors
    ]
    return normed, mins, maxs


def kmeans(
    data: List[Dict[str, Any]],
    feature_keys: List[str],
    k: int = 4,
    max_iter: int = 100,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """
    K-Means clustering over data records.

    Args:
        data:         list of dicts, each containing `feature_keys`.
        feature_keys: list of numeric feature columns to cluster on.
        k:            number of clusters.
        max_iter:     maximum iterations.
        seed:         random seed for centroid initialisation.

    Returns:
        data with added keys: cluster_id, cluster_label, distance_to_centroid.
    """
    if not data or k < 1:
        return data

    k = min(k, len(data))  # can't have more clusters than points

    # Extract feature vectors
    vectors = []
    for row in data:
        vec = []
        for key in feature_keys:
            val = row.get(key)
            try:
                vec.append(float(val) if val is not None else 0.0)
            except (TypeError, ValueError):
                vec.append(0.0)
        vectors.append(vec)

    normed, mins_, maxs_ = _normalize(vectors)

    # Initialise centroids via k-means++ style (deterministic seed)
    rng = random.Random(seed)
    centroids: List[List[float]] = [normed[rng.randint(0, len(normed) - 1)]]
    while len(centroids) < k:
        # Pick point furthest from nearest existing centroid
        dists = [
            min(_euclidean(v, c) for c in centroids)
            for v in normed
        ]
        total = sum(dists)
        if total == 0:
            centroids.append(normed[rng.randint(0, len(normed) - 1)])
        else:
            probs = [d / total for d in dists]
            # Weighted selection
            r = rng.random()
            cumul = 0.0
            chosen = 0
            for i, p in enumerate(probs):
                cumul += p
                if r <= cumul:
                    chosen = i
                    break
            centroids.append(list(normed[chosen]))

    # Iterate
    assignments = [0] * len(normed)
    for _ in range(max_iter):
        new_assignments = []
        for v in normed:
            dists = [_euclidean(v, c) for c in centroids]
            new_assignments.append(dists.index(min(dists)))

        if new_assignments == assignments:
            break
        assignments = new_assignments

        # Recompute centroids
        for ci in range(k):
            members = [normed[i] for i, a in enumerate(assignments) if a == ci]
            if members:
                centroids[ci] = _mean_vector(members)

    # Compute distances and annotate data
    results = []
    for idx, (row, vec, assign) in enumerate(zip(data, normed, assignments)):
        dist = round(_euclidean(vec, centroids[assign]), 4)
        results.append({**row, "cluster_id": assign, "distance_to_centroid": dist})

    return results


def _characterize_clusters(
    clustered: List[Dict[str, Any]],
    k: int,
    feature_keys: List[str],
) -> List[Dict[str, Any]]:
    """
    Summarize each cluster with centroid statistics and a human label.
    """
    clusters: Dict[int, List[Dict]] = {i: [] for i in range(k)}
    for row in clustered:
        clusters[row["cluster_id"]].append(row)

    summaries = []
    for cid, members in clusters.items():
        if not members:
            continue
        centroid_vals = {}
        for key in feature_keys:
            vals = [float(m.get(key) or 0) for m in members]
            centroid_vals[f"avg_{key}"] = round(sum(vals) / len(vals), 2) if vals else 0.0

        # Heuristic label
        safety = centroid_vals.get("avg_overall_safety_score", 0)
        crime = centroid_vals.get("avg_crime_index", 50)
        crowd = centroid_vals.get("avg_crowd_density", 50)

        if safety >= 80 and crime <= 25:
            label = "High Safety — Low Risk"
        elif safety >= 65 and crime <= 40:
            label = "Moderate Safety"
        elif crime >= 55 or crowd >= 75:
            label = "High Risk — Crowded / Unsafe"
        else:
            label = "Moderate Risk — Mixed Profile"

        summaries.append(
            {
                "cluster_id": cid,
                "label": label,
                "member_count": len(members),
                "centroid": centroid_vals,
                "destination_names": [m.get("name", "") for m in members],
            }
        )

    summaries.sort(key=lambda x: x["cluster_id"])
    return summaries


def run_destination_clustering(k: int = 4) -> Dict[str, Any]:
    """
    Fetch all destinations + metrics, run K-Means, return enriched payload.

    Feature space:
      overall_safety_score, crime_index, scam_index, weather_risk,
      night_safety, crowd_density, transport_safety
    """
    feature_keys = [
        "overall_safety_score",
        "crime_index",
        "scam_index",
        "weather_risk",
        "night_safety",
        "crowd_density",
        "transport_safety",
    ]

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                d.id, d.name, d.state, d.region, d.category, d.risk_tier,
                d.overall_safety_score, d.lat, d.lng,
                m.crime_index, m.scam_index, m.weather_risk,
                m.night_safety, m.crowd_density, m.transport_safety
            FROM destinations d
            JOIN risk_metrics m ON m.destination_id = d.id
            ORDER BY d.name
            """
        )
        data = [dict(r) for r in cursor.fetchall()]

    if not data:
        return {"clusters": [], "destinations": [], "k": k, "error": "No destination data found"}

    k = min(k, len(data))
    clustered = kmeans(data, feature_keys=feature_keys, k=k)
    cluster_summaries = _characterize_clusters(clustered, k, feature_keys)

    return {
        "k": k,
        "total_destinations": len(data),
        "feature_keys": feature_keys,
        "clusters": cluster_summaries,
        "destinations": clustered,
        "label": "K-Means destination safety clustering",
        "model_version": "kmeans-v1-stdlib",
        "disclaimer": (
            "Clusters group destinations by safety profile. "
            "This is an analytical tool, not a real-time safety assessment."
        ),
    }


# ---------------------------------------------------------------------------
# Combined Analytics
# ---------------------------------------------------------------------------

def full_analytics_report(k: int = 4) -> Dict[str, Any]:
    """Combined OLAP cube + K-Means clustering for the analytics dashboard."""
    olap = build_olap_cube()
    clustering = run_destination_clustering(k=k)
    return {
        "olap": olap,
        "clustering": clustering,
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }
