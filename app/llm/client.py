from app.llm.mock import MockLLMClient
# from app.llm.openai_client import OpenAILLMClient


def get_llm_client():
    return MockLLMClient()
