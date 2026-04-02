import logging

from app.repositories.planet_repository import PlanetRepository
from app.schemas.planet import Planet, PlanetCategory


logger = logging.getLogger("app.services.planets")


class PlanetService:
    def __init__(self, repository: PlanetRepository) -> None:
        self._repository = repository

    def list_planets(self, category: PlanetCategory | None = None) -> list[Planet]:
        planets = self._repository.list_planets(category=category)
        logger.info("planets.data.loaded total=%s", len(planets))
        return planets

    def get_planet(self, planet_id: int) -> Planet | None:
        logger.info("planet.data.search planet_id=%s", planet_id)
        planet = self._repository.get_planet(planet_id)
        if planet is None:
            logger.info("planet.data.missing planet_id=%s", planet_id)
            return None

        logger.info("planet.data.found planet_id=%s", planet_id)
        return planet
