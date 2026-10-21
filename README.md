# ApexCoach — AI Fitness & Athletic Training Coach

ApexCoach is an elite AI-powered athletic training and fitness coaching agent built on the Google Agent Development Kit (ADK) and Google Cloud Vertex AI Agent Platform.

It delivers personalized workout recommendations, 1-Rep Max (1RM) estimations and percentage calculations, exercises from both a managed Firestore catalog and the global open-source wger database, motivational workout milestone visuals via Gemini image generation, long-term memory across sessions, and custom Python execution in a secure sandbox.

---

## Key Features & Wired Google Cloud Integrations

- **Vertex AI Agent Platform & Gemini 3.8 Flash**: Core reasoning engine for coaching conversations, athletic training design, and tool orchestration.
- **Vertex AI Memory Bank (`PreloadMemoryTool`)**: Persistent cross-session long-term memory that automatically tracks and remembers user goals, preferences, personal records, and health conditions / allergies across conversations.
- **Google Cloud Firestore Database**: Managed exercise catalog database and workout logging backend (`list_exercises`, `get_exercise_details`, `log_workout`, `get_recent_workout_logs`).
- **Google Cloud Storage & Image Generation**: Generates athletic milestone posters and visual badges using `gemini-3.1-flash-lite-image` and uploads them directly to a public Cloud Storage bucket (`apex-coach-media-5389`).
- **Agent Engine Sandbox Code Execution (`AgentEngineSandboxCodeExecutor`)**: Secure Python code sandbox for running complex periodization algorithms, fatigue models, and training load calculations.
- **A2UI Visual UI Components (v0.8)**: Generates structured A2UI visual cards (Card, Column, Row, Text, Image) rendered natively in the ADK Dev UI and custom frontend.
- **Free Public Fitness API Integration**: Direct integration with the wger open-source workout database (`search_wger_exercises`) for global exercise search.
- **Deterministic 1RM Calculator**: Epley formula calculation for estimated 1-Rep Max and percentage-based training zones.

---

## Architecture

```
                       ┌─────────────────────────┐
                       │     Browser / UI        │
                       │   (Chat UI + A2UI)      │
                       └────────────┬────────────┘
                                    │ HTTP
                       ┌────────────▼────────────┐
                       │   FastAPI Proxy Server  │
                       │       (Cloud Run)       │
                       └────────────┬────────────┘
                                    │ A2A Protocol
                       ┌────────────▼────────────┐
                       │   Vertex AI Agent Engine│
                       │       (ApexCoach)       │
                       └─────┬──────────────┬────┘
                             │              │
      ┌──────────────────────┼──────────────┼──────────────────────┐
      │                      │              │                      │
┌─────▼──────────┐    ┌──────▼──────┐ ┌─────▼────────┐      ┌──────▼──────┐
│  Firestore DB  │    │ Memory Bank │ │ Cloud Storage│      │Code Sandbox │
│(Catalog & Logs)│    │(Long-Term)  │ │ (Media & Img)│      │(Python Exec)│
└────────────────┘    └─────────────┘ └──────────────┘      └─────────────┘
```

---

## Local Development & Setup

### Prerequisites

- Python 3.11+
- `uv` package manager
- Google Cloud SDK (`gcloud`) with authenticated credentials

### 1. Setup Environment

```bash
cd apex-coach
uv sync
```

### 2. Run the Agent Locally (with ADK Web & Memory Bank)

```bash
uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://6625968230768836608
```

### 3. Run the Custom Frontend Locally

From the `frontend/` directory:

```bash
cd frontend
pip install -r requirements.txt
export AGENT_ENGINE_RESOURCE_NAME="projects/569786897679/locations/us-east1/reasoningEngines/6625968230768836608"
export AGENT_DIRECTORY="app"
python main.py
```

---

## Deployment

### Deploy Agent to Vertex AI Agent Platform

```bash
agents-cli deploy --project <GCP_PROJECT_ID>
```

### Deploy Frontend to Cloud Run

```bash
gcloud run deploy apex-coach-frontend \
  --source frontend \
  --region us-east1 \
  --project <GCP_PROJECT_ID> \
  --allow-unauthenticated \
  --set-env-vars="AGENT_ENGINE_RESOURCE_NAME=<AGENT_ENGINE_RESOURCE_NAME>,AGENT_DIRECTORY=app"
```
