"""Seed Firestore with exercises and sample workout templates for ApexCoach."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-01f0eaa1a1af"

EXERCISES = [
    {
        "id": "barbell-back-squat",
        "name": "Barbell Back Squat",
        "category": "strength",
        "muscle_groups": ["quadriceps", "glutes", "core"],
        "equipment": "barbell",
        "difficulty": "intermediate",
        "instructions": "Place barbell across upper traps. Squat down until hips are below parallel, keeping chest high and knees tracking over toes. Drive back up through midfoot.",
        "default_sets": 4,
        "default_reps": "6-8",
    },
    {
        "id": "barbell-bench-press",
        "name": "Barbell Bench Press",
        "category": "strength",
        "muscle_groups": ["chest", "anterior deltoids", "triceps"],
        "equipment": "barbell",
        "difficulty": "intermediate",
        "instructions": "Lie flat on bench, retract shoulder blades, grip bar slightly wider than shoulder-width. Lower bar with control to lower chest, then press back up explosively.",
        "default_sets": 4,
        "default_reps": "8-10",
    },
    {
        "id": "conventional-deadlift",
        "name": "Conventional Deadlift",
        "category": "strength",
        "muscle_groups": ["hamstrings", "glutes", "lower back", "lats"],
        "equipment": "barbell",
        "difficulty": "advanced",
        "instructions": "Stand with feet hip-width under bar. Hinge hips back, grip bar outside shins, brace core, and drive the floor away to lockout at hips and knees.",
        "default_sets": 3,
        "default_reps": "5",
    },
    {
        "id": "pull-up",
        "name": "Pull-Up",
        "category": "calisthenics",
        "muscle_groups": ["lats", "upper back", "biceps"],
        "equipment": "pull-up bar",
        "difficulty": "intermediate",
        "instructions": "Hang from bar with overhand grip wider than shoulders. Pull elbows down and back until chin clears the bar, then lower with full control.",
        "default_sets": 3,
        "default_reps": "8-12",
    },
    {
        "id": "dumbbell-bulgarian-split-squat",
        "name": "Dumbbell Bulgarian Split Squat",
        "category": "hypertrophy",
        "muscle_groups": ["quadriceps", "glutes", "hamstrings"],
        "equipment": "dumbbells",
        "difficulty": "intermediate",
        "instructions": "Place rear foot laces-down on bench. Hold dumbbells at sides. Descend until front thigh is parallel to floor, then press back through front heel.",
        "default_sets": 3,
        "default_reps": "10-12 each leg",
    },
    {
        "id": "kettlebell-swing",
        "name": "Kettlebell Swing",
        "category": "conditioning",
        "muscle_groups": ["hamstrings", "glutes", "core", "shoulders"],
        "equipment": "kettlebell",
        "difficulty": "beginner",
        "instructions": "Hinge hips back and hike kettlebell between legs. Snap hips forward explosively to swing bell to chest height. Guide bell back down into next hinge.",
        "default_sets": 4,
        "default_reps": "15-20",
    },
    {
        "id": "romanian-deadlift",
        "name": "Romanian Deadlift (RDL)",
        "category": "strength",
        "muscle_groups": ["hamstrings", "glutes"],
        "equipment": "barbell",
        "difficulty": "intermediate",
        "instructions": "Hold bar at hips with soft knees. Push hips back while keeping back flat and bar glued to legs. Reverse movement when you feel deep hamstring stretch.",
        "default_sets": 3,
        "default_reps": "8-10",
    },
]

def seed():
    db = firestore.Client(project=PROJECT_ID)
    print(f"Connecting to Firestore for project: {PROJECT_ID}")
    
    collection_ref = db.collection("exercises")
    count = 0
    for item in EXERCISES:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"  ✓ Seeded exercise: {item['name']} ({doc_id})")
        count += 1
    
    print(f"Done! Successfully seeded {count} items into collection 'exercises'.")

if __name__ == "__main__":
    seed()
