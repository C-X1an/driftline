from abc import ABC, abstractmethod


class LLMClient(ABC):
    model_name: str

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass
