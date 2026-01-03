import os
from openai import OpenAI

from app.llm.base import LLMClient


class OpenAILLMClient(LLMClient):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = "gpt-4o-mini"

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model_name,
            input=prompt,
            max_output_tokens=150,
            temperature=0.2,
        )

        return response.output_text.strip()
