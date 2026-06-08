from fastapi import APIRouter
from pydantic import BaseModel
from database import get_connection
import uuid

router = APIRouter()

class GroupCreate(BaseModel):
    name: str
    meeting_point_lat: float
    meeting_point_lng: float
    search_radius_km: float

@router.post("/groups")
def create_group(data: GroupCreate):
    conn = get_connection()
    cur = conn.cursor()
    invite_code = str(uuid.uuid4())[:8]
    cur.execute(
        """
        INSERT INTO groups (group_name, meeting_point_lat, meeting_point_lng, search_radius_km, invite_code)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING group_id
        """,
        (data.name, data.meeting_point_lat, data.meeting_point_lng, data.search_radius_km, invite_code)
    )
    group_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return {"group_id": str(group_id), "invite_code": invite_code}

@router.get("/groups/invite/{invite_code}")
def get_group_by_invite(invite_code: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT group_id, group_name FROM groups WHERE invite_code = %s",
        (invite_code,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"error": "Invalid invite code"}
    return {"group_id": str(row[0]), "group_name": row[1]}