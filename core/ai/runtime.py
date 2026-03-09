from __future__ import annotations

import subprocess
import shutil
import time
import json
import re

from core.ai.installer import install_ollama_interactive
from core.ai.cloud import run_cloud_prompt


# ---------------------------------------------------------
# Constants
# ---------------------------------------------------------

LOCAL_RUNTIME_CMD = "ollama"

PRIMARY_MODEL = "qwen2.5:14b-instruct"
FALLBACK_MODEL = "deepseek-coder:6.7b-test"


# ---------------------------------------------------------
# Runtime detection
# ---------------------------------------------------------

def is_runtime_installed() -> bool:
    return shutil.which(LOCAL_RUNTIME_CMD) is not None


def ensure_runtime_installed() -> None:
    if is_runtime_installed():
        return

    print("Ollama is not installed.")
    print("Driftline will now launch the Ollama installer.")
    print("Please complete the installation process.")
    print("This may take up to 1–2 minutes.\n")

    install_ollama_interactive()

    # Wait up to 60 seconds
    for _ in range(30):
        if is_runtime_installed():
            print("Ollama installation detected.")
            return
        time.sleep(2)

    print("\nOllama installation completed, but CLI not detected.")
    print("Please restart your terminal and run 'driftline init' again.")
    raise RuntimeError("Ollama CLI not detected after installation.")


# ---------------------------------------------------------
# Model management
# ---------------------------------------------------------

def is_model_available(model: str) -> bool:
    try:
        result = subprocess.run(
            [LOCAL_RUNTIME_CMD, "list"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return model in result.stdout
    except Exception:
        return False


def download_model(model: str) -> None:
    subprocess.run(
        [LOCAL_RUNTIME_CMD, "pull", model],
        check=True,
    )


def ensure_best_local_model() -> str:
    ensure_runtime_installed()

    if not is_model_available(PRIMARY_MODEL):
        try:
            download_model(PRIMARY_MODEL)
        except Exception:
            pass

    if is_model_available(PRIMARY_MODEL):
        return PRIMARY_MODEL

    if not is_model_available(FALLBACK_MODEL):
        download_model(FALLBACK_MODEL)

    return FALLBACK_MODEL


# ---------------------------------------------------------
# Prompt execution
# ---------------------------------------------------------

def run_local_prompt(prompt: str) -> tuple[str, str]:
    model = ensure_best_local_model()

    try:
        process = subprocess.Popen(
            [LOCAL_RUNTIME_CMD, "run", model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        stdout, stderr = process.communicate(prompt)

        if process.returncode != 0:
            raise RuntimeError(stderr)

        return stdout.strip(), model

    except Exception:
        if model != FALLBACK_MODEL:
            process = subprocess.Popen(
                [LOCAL_RUNTIME_CMD, "run", FALLBACK_MODEL],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            stdout, stderr = process.communicate(prompt)

            if process.returncode != 0:
                raise RuntimeError(stderr)

            return stdout.strip(), FALLBACK_MODEL

        raise RuntimeError("Local AI execution failed on all models.")


def get_active_plan() -> str:
    # TEMPORARY: until backend auth implemented
    return "free"


def normalize_json_output(raw: str):
    """
    Attempts to extract valid JSON from LLM output.

    Handles cases like:
    - ```json ... ```
    - markdown fences
    - extra explanation text
    """

    if not isinstance(raw, str):
        return None

    text = raw.strip()

    # Remove markdown fences
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text)
        text = text.rstrip("`").strip()

    # Attempt direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try extracting first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    return None


# ---------------------------------------------------------
# Public reasoning entrypoint
# ---------------------------------------------------------
def run_reasoning(prompt: str) -> dict:
    plan = get_active_plan()

    used_cloud = False
    cost_usd = 0.0
    model_used = None
    raw_text = ""

    if plan == "paid":
        cloud = run_cloud_prompt(prompt)

        raw_text = cloud.get("text", "")
        model_used = cloud.get("model")
        cost_usd = cloud.get("cost_usd", 0.0)
        used_cloud = True
    else:
        raw_text, model_used = run_local_prompt(prompt)

    # ----------------------------------------
    # Normalize JSON safely
    # ----------------------------------------
    parsed = normalize_json_output(raw_text)

    # retry once for local models if JSON invalid
    if parsed is None and plan != "paid":
        raw_text, model_used = run_local_prompt(prompt)
        parsed = normalize_json_output(raw_text)

    if parsed is None:
        raise RuntimeError(
            "AI returned invalid JSON. Please retry."
            f"DEBUG AI RAW OUTPUT:{raw_text}"
        )

    return {
        "text": parsed,
        "model": model_used,
        "used_cloud": used_cloud,
        "cost_usd": round(cost_usd, 8),
    }