from fastapi import APIRouter, HTTPException
from typing import Optional
from app.database import get_db
from app.models.schemas import IncidentCreate

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

@router.get("")
def get_incidents(
    destination_id: Optional[int] = None,
    category: Optional[str] = None,
    status: Optional[str] = "Active"
):
    with get_db() as conn:
        cursor = conn.cursor()
        query = """
        SELECT i.*, d.name as destination_name, d.country as destination_country
        FROM incidents i
        JOIN destinations d ON i.destination_id = d.id
        WHERE 1=1
        """
        params = []
        if destination_id:
            query += " AND i.destination_id = ?"
            params.append(destination_id)
        if category and category != "All":
            query += " AND i.category = ?"
            params.append(category)
        if status and status != "All":
            query += " AND i.status = ?"
            params.append(status)

        query += " ORDER BY i.reported_at DESC LIMIT 50"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]

@router.post("")
def report_incident(incident: IncidentCreate):
    with get_db() as conn:
        cursor = conn.cursor()
        # Verify destination exists
        cursor.execute("SELECT id FROM destinations WHERE id = ?", (incident.destination_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Destination not found")

        cursor.execute("""
        INSERT INTO incidents (destination_id, title, category, severity, location_name, lat, lng, description, upvotes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 'Active')
        """, (
            incident.destination_id, incident.title, incident.category, incident.severity,
            incident.location_name, incident.lat, incident.lng, incident.description
        ))
        incident_id = cursor.lastrowid
        return {"success": True, "incident_id": incident_id, "message": "Incident report submitted for community awareness."}

@router.post("/{incident_id}/upvote")
def upvote_incident(incident_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT upvotes FROM incidents WHERE id = ?", (incident_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")

        new_votes = row[0] + 1
        new_status = "Verified" if new_votes >= 5 else "Active"
        cursor.execute("UPDATE incidents SET upvotes = ?, status = ? WHERE id = ?", (new_votes, new_status, incident_id))
        return {"success": True, "upvotes": new_votes, "status": new_status}
