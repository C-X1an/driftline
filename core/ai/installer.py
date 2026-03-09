from __future__ import annotations

import platform
import subprocess
import shutil


OLLAMA_INSTALL_URL = "https://ollama.com/download"


def is_ollama_installed() -> bool:
    """
    Check if Ollama exists in PATH.
    """
    return shutil.which("ollama") is not None


def install_ollama_interactive() -> None:
    """
    Offer automatic Ollama installation.
    """
    if is_ollama_installed():
        return

    print("\nDriftline requires a local AI runtime (Ollama).")
    choice = input("Install Ollama automatically now? [y/N]: ").strip().lower()

    if choice != "y":
        raise RuntimeError(
            f"Ollama not installed.\n"
            f"Please install manually from: {OLLAMA_INSTALL_URL}"
        )

    system = platform.system()

    try:
        if system == "Windows":
            subprocess.run(
                ["powershell", "-Command", "winget install Ollama.Ollama"],
                check=True,
            )

        elif system == "Darwin":  # macOS
            subprocess.run(
                ["brew", "install", "ollama"],
                check=True,
            )

        elif system == "Linux":
            subprocess.run(
                ["sh", "-c", "curl -fsSL https://ollama.com/install.sh | sh"],
                check=True,
            )

        else:
            raise RuntimeError("Unsupported OS for automatic Ollama install.")

    except subprocess.CalledProcessError as e:
        raise RuntimeError("Automatic Ollama install failed.") from e

    if not is_ollama_installed():
        raise RuntimeError("Ollama installation did not succeed.")

    print("Ollama installed successfully.\n")