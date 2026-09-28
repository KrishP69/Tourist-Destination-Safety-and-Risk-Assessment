"""
Analytics router — exposes OLAP cube and K-Means clustering endpoints.
All endpoints are read-only and publicly accessible (no auth required).
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from app.services.olap_kmeans import (
    build_olap_cube,
    olap_drill_down,
    olap_slice,
    olap_dice,
    run_destination_clustering,
    full_analytics_report,
    OLAP_DIMENSIONS,
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics — OLAP & Clustering"])


@router.get("/olap/cube")
def get_olap_cube(
    dimensions: Optional[str] = Query(
        None,
        description="Comma-separated dimensions to group by. "
                    f"Valid: {', '.join(OLAP_DIMENSIONS)}. "
                    "Default: all three.",
    ),
    region: Optional[str] = Query(None, description="Filter by region"),
    category: Optional[str] = Query(None, description="Filter by destination category"),
    risk_tier: Optional[str] = Query(None, description="Filter by risk tier"),
):
    """
    OLAP Cube — multi-dimensional aggregation of safety & crowd metrics.

    Aggregate dimensions: **region**, **category**, **risk_tier**

    Measures: avg_safety_score, avg_crime_index, avg_scam_index,
              avg_weather_risk, avg_night_safety, avg_crowd_density,
              destination_count
    """
    dims = None
    if dimensions:
        dims = [d.strip() for d in dimensions.split(",") if d.strip()]
        invalid = [d for d in dims if d not in OLAP_DIMENSIONS]
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid dimensions: {invalid}. Valid: {OLAP_DIMENSIONS}",
            )

    filters = {}
    if region:
        filters["region"] = region
    if category:
        filters["category"] = category
    if risk_tier:
        filters["risk_tier"] = risk_tier

    try:
        return build_olap_cube(dimensions=dims, filters=filters or None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OLAP cube error: {str(e)}")


@router.get("/olap/drill-down")
def get_olap_drill_down(
    parent_dim: str = Query(..., description=f"Parent dimension. Valid: {OLAP_DIMENSIONS}"),
    parent_value: str = Query(..., description="Parent dimension value to drill into"),
    child_dim: str = Query(..., description=f"Child dimension. Valid: {OLAP_DIMENSIONS}"),
):
    """
    OLAP Drill-Down — fix a parent dimension value and break down by a child dimension.

    Example: parent_dim=region&parent_value=North India&child_dim=category
    """
    for d in [parent_dim, child_dim]:
        if d not in OLAP_DIMENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"'{d}' is not a valid dimension. Valid: {OLAP_DIMENSIONS}",
            )
    if parent_dim == child_dim:
        raise HTTPException(status_code=400, detail="parent_dim and child_dim must differ")
    try:
        return olap_drill_down(parent_dim, parent_value, child_dim)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drill-down error: {str(e)}")


@router.get("/olap/slice")
def get_olap_slice(
    dimension: str = Query(..., description=f"Dimension to fix. Valid: {OLAP_DIMENSIONS}"),
    value: str = Query(..., description="Value to fix the dimension to"),
):
    """
    OLAP Slice — fix one dimension to a value, aggregate the remaining two.

    Example: dimension=risk_tier&value=Low Risk (Safe)
    """
    if dimension not in OLAP_DIMENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"'{dimension}' is not a valid dimension. Valid: {OLAP_DIMENSIONS}",
        )
    try:
        return olap_slice(dimension, value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Slice error: {str(e)}")


@router.get("/olap/dice")
def get_olap_dice(
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    risk_tier: Optional[str] = Query(None),
):
    """
    OLAP Dice — restrict two or more dimensions simultaneously.

    Example: region=South India&category=Beach & Coastal
    """
    filters = {}
    if region:
        filters["region"] = region
    if category:
        filters["category"] = category
    if risk_tier:
        filters["risk_tier"] = risk_tier
    if not filters:
        raise HTTPException(
            status_code=400, detail="Provide at least one filter (region / category / risk_tier)"
        )
    try:
        return olap_dice(filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dice error: {str(e)}")


@router.get("/cluster")
def get_destination_clusters(
    k: int = Query(4, ge=2, le=10, description="Number of clusters (2–10)"),
):
    """
    K-Means Clustering — groups destinations by safety profile.

    Features: overall_safety_score, crime_index, scam_index, weather_risk,
              night_safety, crowd_density, transport_safety

    Returns cluster summaries + per-destination cluster assignments.
    """
    try:
        return run_destination_clustering(k=k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering error: {str(e)}")


@router.get("/report")
def get_full_analytics_report(
    k: int = Query(4, ge=2, le=10, description="Number of K-Means clusters"),
):
    """
    Full Analytics Report — OLAP cube + K-Means clustering in one response.
    Useful for dashboard initialisation.
    """
    try:
        return full_analytics_report(k=k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics report error: {str(e)}")
