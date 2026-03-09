from functools import lru_cache
import json
from pathlib import Path

PROMPT_DIR = Path(__file__).parent


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    path = PROMPT_DIR / f"{name}.txt"

    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {name}")

    return path.read_text(encoding="utf-8")


def build_prompt(template_name: str, payload: dict) -> str:
    template = load_prompt(template_name)
    data_block = json.dumps(payload, indent=2)

    return f"""{template}

INPUT DATA:
{data_block}
"""