# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-3.8-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


import json
from pathlib import Path
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

from .firestore_tools import (
    get_exercise_details,
    get_recent_workout_logs,
    list_exercises,
    log_workout,
)
from .image_tools import generate_workout_visual
from .wger_tools import search_wger_exercises


# Load Agent Engine resource from deployment_metadata.json if available
def _get_agent_engine_resource() -> str:
    metadata_path = Path(__file__).resolve().parent.parent / "deployment_metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("remote_agent_runtime_id", "")
        except Exception:
            pass
    return "projects/569786897679/locations/us-east1/reasoningEngines/6625968230768836608"


agent_engine_resource = _get_agent_engine_resource()
sandbox_code_executor = (
    AgentEngineSandboxCodeExecutor(agent_engine_resource_name=agent_engine_resource)
    if agent_engine_resource
    else None
)


def calculate_one_rep_max(weight_lbs: float, reps: int) -> dict:
    """Calculates estimated 1-Rep Max (1RM) using the Epley formula and returns training percentages.

    Args:
        weight_lbs: The weight lifted in pounds.
        reps: The number of completed repetitions (must be >= 1).

    Returns:
        A dictionary with estimated 1RM and percentage-based training loads.
    """
    if reps <= 0 or weight_lbs <= 0:
        return {"error": "Weight and reps must both be greater than 0."}
    
    # Epley formula
    one_rm = weight_lbs if reps == 1 else round(weight_lbs * (1 + (reps / 30.0)), 1)
    
    return {
        "input_weight_lbs": weight_lbs,
        "input_reps": reps,
        "estimated_1rm_lbs": one_rm,
        "training_zones": {
            "90%_heavy_strength": round(one_rm * 0.90, 1),
            "85%_strength": round(one_rm * 0.85, 1),
            "80%_hypertrophy_heavy": round(one_rm * 0.80, 1),
            "75%_hypertrophy_medium": round(one_rm * 0.75, 1),
            "70%_endurance_volume": round(one_rm * 0.70, 1),
            "65%_speed_power": round(one_rm * 0.65, 1),
        },
    }


from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from .a2ui_utils import a2ui_callback


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are ApexCoach, an elite AI fitness and athletic training coach. "
        "You remember and track the user's stated allergies, dietary restrictions, health conditions, fitness goals, injury history, preferences, and workout personal records across conversations and use them to personalize your coaching and nutritional advice. "
        "Pay special attention to any allergies mentioned by the user and ensure they are preserved in memory and never violated in recommendations. "
        "You help athletes and fitness enthusiasts discover exercises, get technique instructions, "
        "calculate 1RM and training percentages, log training sessions, and generate motivational milestone posters. "
        "You can execute Python code in your secure sandbox to perform complex calculations, simulations, periodization models, and data analyses. "
        "Use your Firestore tools to inspect your saved exercise catalog and log workouts, your "
        "search_wger_exercises tool to search the global open-source exercise database, your "
        "calculation tools to compute training loads, and your generate_workout_visual tool to create posters and milestone visuals."
    ),
    workflow_description="Analyze the user request, call any appropriate tools (Firestore, calculation, API search, image generator, code sandbox), and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=sandbox_code_executor,
    tools=[
        PreloadMemoryTool(),
        list_exercises,
        get_exercise_details,
        log_workout,
        get_recent_workout_logs,
        calculate_one_rep_max,
        search_wger_exercises,
        generate_workout_visual,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)






