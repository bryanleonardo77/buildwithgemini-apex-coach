"""Public fitness API integration using wger Workout Manager."""

import html
import re
import urllib.parse
import urllib.request
import json
from typing import Any, Dict, List, Optional

WGER_API_BASE = "https://wger.de/api/v2"

def _clean_html(raw_html: str) -> str:
    clean = re.sub(r"<[^>]+>", " ", raw_html)
    return html.unescape(clean).strip()

def search_wger_exercises(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Searches the open-source wger global exercise database for movements matching a keyword.

    Args:
        query: Search term for the exercise (e.g. 'curl', 'squat', 'bench', 'press', 'shoulder').
        limit: Maximum number of results to return (default: 5).

    Returns:
        A list of exercise details including name, category, target muscles, equipment, and instructions.
    """
    try:
        url = f"{WGER_API_BASE}/exerciseinfo/?limit=100"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ApexCoach-ADK-Agent/1.0", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                return [{"error": f"Failed to fetch from wger API (HTTP {response.status})"}]
            data = json.loads(response.read().decode("utf-8"))

        query_clean = query.strip().lower()
        matched = []

        for item in data.get("results", []):
            name = None
            description = ""
            for trans in item.get("translations", []):
                if trans.get("language") == 2:  # English
                    name = trans.get("name")
                    description = _clean_html(trans.get("description", ""))
                    break
            
            if not name:
                continue

            category = item.get("category", {}).get("name", "General")
            muscles = [
                m.get("name_en") or m.get("name")
                for m in item.get("muscles", [])
                if m.get("name_en") or m.get("name")
            ]
            equipment = [
                e.get("name") for e in item.get("equipment", []) if e.get("name")
            ]

            # Check if query matches name, category, muscle, or equipment
            match_target = f"{name} {category} {' '.join(muscles)} {' '.join(equipment)}".lower()
            if query_clean in match_target:
                matched.append({
                    "id": item.get("id"),
                    "name": name,
                    "category": category,
                    "primary_muscles": muscles,
                    "equipment": equipment or ["Bodyweight"],
                    "instructions": description[:300] if description else "Standard form applies.",
                })
                if len(matched) >= limit:
                    break

        return matched or [{"message": f"No public exercises found matching '{query}'."}]
    except Exception as e:
        return [{"error": f"Error querying wger exercise database: {str(e)}"}]
