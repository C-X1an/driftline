from typing import Callable

from app.ingestion.fetchers.local_file import fetch_local_file


FETCHER_REGISTRY: dict[str, Callable[[dict], str]] = {
    "LOCAL_FILE": fetch_local_file,
}
