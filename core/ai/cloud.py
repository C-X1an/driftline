from __future__ import annotations

import os
from typing import Dict, Any

from openai import OpenAI


# ---------------------------------------------------------
# Constants
# ---------------------------------------------------------

DEFAULT_CLOUD_MODEL = "gpt-4o-mini"


# ---------------------------------------------------------
# OpenAI pricing (USD per 1K tokens)
# Keep minimal — expand later for paid tiers.
# ---------------------------------------------------------

OPENAI_PRICING = {
    "gpt-4o-mini": {
        "input_per_1k": 0.00015,
        "output_per_1k": 0.0006,
    },
}


def _calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Exact USD cost using official pricing.
    """
    if model not in OPENAI_PRICING:
        return 0.0

    pricing = OPENAI_PRICING[model]

    input_cost = (input_tokens / 1000) * pricing["input_per_1k"]
    output_cost = (output_tokens / 1000) * pricing["output_per_1k"]

    return round(input_cost + output_cost, 8)


# ---------------------------------------------------------
# Client (DEV ONLY — will be replaced by Driftline backend)
# ---------------------------------------------------------

def _get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set.\n"
            "This is required for local development.\n"
            "In production, Driftline will route through its own backend."
        )

    return OpenAI(api_key=api_key)


# ---------------------------------------------------------
# Cloud prompt execution
# ---------------------------------------------------------

def run_cloud_prompt(
    prompt: str,
    model: str = DEFAULT_CLOUD_MODEL,
) -> Dict[str, Any]:
    """
    Executes prompt on OpenAI (DEV MODE).

    Returns:
    {
        text: str
        model: str
        input_tokens: int
        output_tokens: int
        cost_usd: float
        confidence: float  # placeholder until evaluator layer
    }
    """

    client = _get_openai_client()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content or ""

    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    cost_usd = _calculate_cost(model, input_tokens, output_tokens)

    return {
        "text": text.strip(),
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost_usd,
    }