from fastapi import APIRouter
from database import get_connection
import requests
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

VIBE_TO_TYPE = {
    "cafe": "cafe",
    "food": "restaurant",
    "study": "library",
    "hangout": "park"
}

def fetch_places(lat, lng, radius_km, place_type):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": int(radius_km * 1000),
        "type": place_type,
        "key": os.getenv("GOOGLE_API_KEY")
    }
    res = requests.get(url, params=params)
    return res.json().get("results", [])

def calculate_score(place, avg_budget, vibe_counts):
    score = 0

    # Budget match (40%)
    place_price = place.get("price_level", 2)
    budget_diff = abs(place_price - avg_budget)
    budget_score = max(0, 100 - (budget_diff * 25))
    score += 0.4 * budget_score

    # Vibe match (40%)
    place_types = place.get("types", [])
    dominant_vibe = max(vibe_counts, key=vibe_counts.get)
    mapped_type = VIBE_TO_TYPE.get(dominant_vibe, "restaurant")
    vibe_score = 100 if mapped_type in place_types else 0
    score += 0.4 * vibe_score

    # Rating match (20%)
    rating = place.get("rating", 3)
    rating_score = (rating / 5) * 100
    score += 0.2 * rating_score

    return round(score, 2)

@router.post("/recommendations/{group_id}")
def generate_recommendations(group_id: str):
    conn = get_connection()
    cur = conn.cursor()

    # Get group info
    cur.execute(
        "SELECT meeting_point_lat, meeting_point_lng, search_radius_km FROM groups WHERE group_id = %s",
        (group_id,)
    )
    group = cur.fetchone()
    if not group:
        conn.close()
        return {"error": "Group not found"}

    lat, lng, radius = group

    # Get all preferences for this group
    cur.execute(
        """
        SELECT p.budget, p.vibe FROM preferences p
        JOIN members m ON p.member_id = m.member_id
        WHERE m.group_id = %s
        """,
        (group_id,)
    )
    prefs = cur.fetchall()
    if not prefs:
        conn.close()
        return {"error": "No preferences found"}

    budgets = [p[0] for p in prefs]
    vibes = [p[1] for p in prefs]

    avg_budget = sum(budgets) / len(budgets)
    vibe_counts = {v: vibes.count(v) for v in set(vibes)}
    dominant_vibe = max(vibe_counts, key=vibe_counts.get)
    place_type = VIBE_TO_TYPE.get(dominant_vibe, "restaurant")

    # Fetch places
    places = fetch_places(lat, lng, radius, place_type)
    if not places:
        conn.close()
        return {"error": "No places found nearby"}

    # Score places
    scored = []
    for place in places:
        s = calculate_score(place, avg_budget, vibe_counts)
        scored.append({
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "rating": place.get("rating"),
            "price_level": place.get("price_level"),
            "score": s
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top3 = scored[:3]

    # Save to recommendations table
    cur.execute("DELETE FROM recommendations WHERE group_id = %s", (group_id,))
    for i, place in enumerate(top3):
        cur.execute(
            """
            INSERT INTO recommendations (group_id, place_id, score, rank)
            VALUES (%s, %s, %s, %s)
            """,
            (group_id, place["name"], place["score"], i + 1)
        )

    conn.commit()
    conn.close()

    return {"recommendations": top3}