import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


class LLMClient:

    def __init__(self):
        api_key = ""

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> str:
        interaction = self.client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
        )

        return interaction.output_text