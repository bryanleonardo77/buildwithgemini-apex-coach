"""Firestore backend tools for ApexCoach."""

import datetime
from typing import Any, Dict, List, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-01f0eaa1a1af"

def _get_db() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)

def list_exercises(
    category: Optional[str] = None,
    muscle_group: Optional[str] = None,
    equipment: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List or search exercises from the Firestore exercise catalog.

    Args:
        category: Optional category filter (e.g. 'strength', 'hypertrophy', 'calisthenics', 'conditioning').
        muscle_group: Optional muscle group filter (e.g. 'quadriceps', 'chest', 'hamstrings', 'lats', 'glutes').
        equipment: Optional equipment filter (e.g. 'barbell', 'dumbbells', 'pull-up bar', 'kettlebell').

    Returns:
        A list of exercise dictionaries matching the criteria.
    """
    db = _get_db()
    docs = db.collection("exercises").stream()
    results = []

    for doc in docs:
        data = doc.to_dict()
        if category and data.get("category", "").lower() != category.lower():
            continue
        if equipment and data.get("equipment", "").lower() != equipment.lower():
            continue
        if muscle_group:
            groups = [g.lower() for g in data.get("muscle_groups", [])]
            if muscle_group.lower() not in groups:
                continue
        results.append(data)

    return results

def get_exercise_details(exercise_name: str) -> Dict[str, Any]:
    """Retrieve detailed information and form cues for a specific exercise.

    Args:
        exercise_name: Name or ID of the exercise (e.g. 'Barbell Back Squat' or 'pull-up').

    Returns:
        Detailed exercise dict or error message.
    """
    db = _get_db()
    docs = db.collection("exercises").stream()
    query_clean = exercise_name.strip().lower()

    for doc in docs:
        data = doc.to_dict()
        if (
            data.get("id", "").lower() == query_clean
            or query_clean in data.get("name", "").lower()
        ):
            return data

    return {"error": f"Exercise '{exercise_name}' not found in the catalog."}

def log_workout(
    exercise_name: str,
    sets: int,
    reps: int,
    weight_lbs: float,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Log a completed workout set/session into the Firestore workout_logs collection.

    Args:
        exercise_name: The name of the exercise performed (e.g., 'Barbell Back Squat').
        sets: Number of completed sets.
        reps: Number of completed reps per set.
        weight_lbs: Weight used in pounds (use 0 for bodyweight exercises).
        notes: Optional notes or reflections on RPE, form, or fatigue.

    Returns:
        A confirmation dict containing the logged record ID and timestamp.
    """
    db = _get_db()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record = {
        "exercise_name": exercise_name,
        "sets": sets,
        "reps": reps,
        "weight_lbs": weight_lbs,
        "notes": notes or "",
        "timestamp": now_str,
    }
    update_time, doc_ref = db.collection("workout_logs").add(record)
    return {
        "status": "success",
        "log_id": doc_ref.id,
        "exercise": exercise_name,
        "sets": sets,
        "reps": reps,
        "weight_lbs": weight_lbs,
        "timestamp": now_str,
    }

def get_recent_workout_logs(limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve recently logged workouts from Firestore.

    Args:
        limit: Number of recent logs to fetch (default: 5).

    Returns:
        A list of recent workout log records.
    """
    db = _get_db()
    logs_ref = (
        db.collection("workout_logs")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
    )
    results = []
    for doc in logs_ref.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results
