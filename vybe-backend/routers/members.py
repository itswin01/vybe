from fastapi import APIRouter
from pydantic import BaseModel
from database import get_connection

router = APIRouter()

class MemberJoin(BaseModel):
    invite_code: str
    name: str
    budget: int
    vibe: str

@router.post("/members/join")
def join_group(data: MemberJoin):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT group_id FROM groups WHERE invite_code = %s", (data.invite_code,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return {"error": "Invalid invite code"}
        
        group_id = row[0]

        cur.execute(
            "INSERT INTO members (group_id, name) VALUES (%s, %s) RETURNING member_id",
            (group_id, data.name)
        )
        member_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO preferences (member_id, budget, vibe) VALUES (%s, %s, %s)",
            (member_id, data.budget, data.vibe)
        )

        conn.commit()
        conn.close()
        return {"member_id": str(member_id), "group_id": str(group_id)}
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return {"error": str(e)}