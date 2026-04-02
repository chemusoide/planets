import logging
from datetime import UTC, datetime

from app.config import Settings
from app.repositories.planet_repository import SQLitePlanetRepository
from app.repositories.sync_repository import SQLiteSyncRepository
from app.services.external_planet_source import WikipediaPlanetSource


logger = logging.getLogger("app.services.sync")


class PlanetSyncService:
    def __init__(
        self,
        *,
        settings: Settings,
        planet_repository: SQLitePlanetRepository,
        sync_repository: SQLiteSyncRepository,
        source_client: WikipediaPlanetSource,
    ) -> None:
        self._settings = settings
        self._planet_repository = planet_repository
        self._sync_repository = sync_repository
        self._source_client = source_client

    def sync_planets(self) -> dict[str, object]:
        attempted_at = datetime.now(UTC).isoformat()
        planets = self._planet_repository.list_planets()
        updates: list[dict[str, str]] = []

        try:
            for planet in planets:
                source_payload = self._source_client.fetch_planet_details(planet.wikipedia_title)
                updates.append({"id": planet.id, **source_payload})

            self._planet_repository.update_source_fields(updates)
            message = f"Sincronización completada con {len(updates)} planetas." 
            self._sync_repository.update_status(
                source_name=self._settings.source_name,
                source_url=self._settings.source_api_base_url,
                last_attempted_at=attempted_at,
                last_success_at=attempted_at,
                last_status="success",
                last_message=message,
                records_processed=len(updates),
                using_cached_data=False,
            )
            logger.info("sync.success records=%s", len(updates))
        except Exception as exc:
            message = f"No se pudo actualizar la fuente externa: {exc}" 
            self._sync_repository.update_status(
                source_name=self._settings.source_name,
                source_url=self._settings.source_api_base_url,
                last_attempted_at=attempted_at,
                last_success_at=self._sync_repository.get_status().get("last_success_at"),
                last_status="error",
                last_message=message,
                records_processed=0,
                using_cached_data=True,
            )
            logger.warning("sync.error message=%s", message)

        return self._sync_repository.get_status()