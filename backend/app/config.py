import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    data_dir: Path
    database_path: Path
    source_api_base_url: str
    source_name: str
    auto_sync_on_startup: bool
    source_request_timeout_seconds: float


@lru_cache
def get_settings() -> Settings:
    backend_dir = Path(__file__).resolve().parents[1]
    data_dir = Path(os.getenv("DATA_DIR", backend_dir / "data")).expanduser()
    database_path = data_dir / "planets.db"
    return Settings(
        app_name="Planets Demo API",
        app_version="3.0.0",
        data_dir=data_dir,
        database_path=database_path,
        source_api_base_url=os.getenv(
            "SOURCE_API_BASE_URL", "https://es.wikipedia.org/api/rest_v1/page/summary"
        ),
        source_name=os.getenv("SOURCE_NAME", "Wikipedia REST ES"),
        auto_sync_on_startup=_get_bool_env("AUTO_SYNC_ON_STARTUP", True),
        source_request_timeout_seconds=float(
            os.getenv("SOURCE_REQUEST_TIMEOUT_SECONDS", "8")
        ),
    )