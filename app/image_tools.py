"""Image generation and Cloud Storage upload tools for ApexCoach."""

import datetime
import uuid
from typing import Any, Dict

from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import Client, types

BUCKET_NAME = "apex-coach-media-5389"
PROJECT_ID = "qwiklabs-gcp-04-01f0eaa1a1af"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"


def generate_workout_visual(
    prompt: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generates an athletic workout visual, milestone poster, or exercise illustration, saves it as an artifact, and uploads it to Cloud Storage.

    Args:
        prompt: Description of the fitness visual or motivational poster to generate (e.g. 'A dynamic motivational poster celebrating a new personal record of 315 lb deadlift in a modern gym').
        tool_context: ADK ToolContext for saving the artifact in the dev UI / playground.

    Returns:
        A dictionary containing the image generation status, public storage URL, and filename.
    """
    try:
        # Initialize Google GenAI client for global location
        client = Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
        )

        image_bytes = None
        mime_type = "image/png"

        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/png"
                    break

        if not image_bytes:
            return {"error": "No image data was returned by the model."}

        ext = "png" if "png" in mime_type else "jpg"
        filename = f"poster_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.{ext}"

        # 1. Save artifact with tool_context
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename, artifact_part)

        # 2. Upload to Cloud Storage bucket and return public URL
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "filename": filename,
            "public_url": public_url,
            "prompt": prompt,
            "message": f"Image generated and uploaded successfully. Public URL: {public_url}",
        }
    except Exception as e:
        return {"error": f"Failed to generate and upload image: {str(e)}"}
