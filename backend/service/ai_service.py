import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")

if not AI_API_KEY:
    raise ValueError(
        "AI_API_KEY was not found. "
        "Please add it to your .env file."
    )

client = genai.Client(api_key=AI_API_KEY)

MODEL_NAME = "gemini-3.5-flash"


def generate_ai_notes(prompt):

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text