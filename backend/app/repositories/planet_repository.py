import logging
from pathlib import Path
from typing import Protocol

from app.database import get_connection
from app.schemas.planet import Planet, PlanetCategory


logger = logging.getLogger("app.repositories.planets")


class PlanetRepository(Protocol):
    def list_planets(self, category: PlanetCategory | None = None) -> list[Planet]: ...

    def get_planet(self, planet_id: int) -> Planet | None: ...

    def update_source_fields(self, updates: list[dict[str, str]]) -> None: ...


class SQLitePlanetRepository:
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    def list_planets(self, category: PlanetCategory | None = None) -> list[Planet]:
        query = """
                SELECT id, position, category, name, emoji, climate, terrain, population,
                       description, kid_summary, fun_fact, moons,
                       day_length_hours, distance_from_sun_million_km,
                       wikipedia_title, source_summary, source_description,
                       source_page_url, image_url, last_synced_at
                FROM planets
            """
        params: tuple[object, ...] = ()
        if category:
            query += " WHERE category = ?"
            params = (category,)
        query += " ORDER BY CASE category WHEN 'solar-system' THEN 1 WHEN 'exoplanets' THEN 2 ELSE 3 END, position ASC"

        with get_connection(self._database_path) as connection:
            rows = connection.execute(query, params).fetchall()

        logger.info("planets.repository.list rows=%s", len(rows))
        return [Planet.model_validate(dict(row)) for row in rows]

    def get_planet(self, planet_id: int) -> Planet | None:
        with get_connection(self._database_path) as connection:
            row = connection.execute(
                """
                  SELECT id, position, category, name, emoji, climate, terrain, population,
                       description, kid_summary, fun_fact, moons,
                      day_length_hours, distance_from_sun_million_km,
                      wikipedia_title, source_summary, source_description,
                      source_page_url, image_url, last_synced_at
                FROM planets
                WHERE id = ?
                """,
                (planet_id,),
            ).fetchone()

        if row is None:
            logger.info("planets.repository.missing planet_id=%s", planet_id)
            return None

        logger.info("planets.repository.found planet_id=%s", planet_id)
        return Planet.model_validate(dict(row))

    def update_source_fields(self, updates: list[dict[str, str]]) -> None:
        with get_connection(self._database_path) as connection:
            connection.executemany(
                """
                UPDATE planets
                SET source_summary = :source_summary,
                    source_description = :source_description,
                    source_page_url = :source_page_url,
                    image_url = :image_url,
                    last_synced_at = :last_synced_at
                WHERE id = :id
                """,
                updates,
            )