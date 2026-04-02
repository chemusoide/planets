from datetime import UTC, datetime
from urllib.parse import quote

import httpx


class WikipediaPlanetSource:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._headers = {
            "User-Agent": "PlanetsDemoBot/1.0 (educational homelab project)",
            "Accept": "application/json",
        }

    def fetch_planet_details(self, wikipedia_title: str) -> dict[str, str]:
        encoded_title = quote(wikipedia_title, safe="()")
        response = httpx.get(
            f"{self._base_url}/{encoded_title}",
            timeout=self._timeout,
            headers=self._headers,
        )
        response.raise_for_status()
        payload = response.json()

        return {
            "source_summary": payload.get("extract", "").strip(),
            "source_description": payload.get("description", "").strip(),
            "source_page_url": payload.get("content_urls", {})
            .get("desktop", {})
            .get("page", ""),
            "image_url": payload.get("thumbnail", {}).get("source", ""),
            "last_synced_at": datetime.now(UTC).isoformat(),
        }