from app.llm.base import LLMClient


class MockLLMClient(LLMClient):
    model_name = "mock-v1"

    def generate(self, prompt: str) -> str:
        return (
            "The system configuration has deviated from its baseline. "
            "This change may affect runtime behavior or reliability. "
            "Review the modified settings and confirm they align with current operational intent."
        )
