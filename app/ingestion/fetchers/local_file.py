from pathlib import Path


def fetch_local_file(fetch_spec: dict) -> str:
    """
    fetch_spec example:
    {
        "type": "LOCAL_FILE",
        "path": "C:/configs/app.yaml"
    }
    """
    path = fetch_spec.get("path")
    if not path:
        raise ValueError("fetch_spec missing 'path'")

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path.read_text(encoding="utf-8")
