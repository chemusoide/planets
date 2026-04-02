from app.repositories.planet_repository import SQLitePlanetRepository
from app.repositories.sync_repository import SQLiteSyncRepository


class AdminService:
    def __init__(
        self,
        planet_repository: SQLitePlanetRepository,
        sync_repository: SQLiteSyncRepository,
    ) -> None:
        self._planet_repository = planet_repository
        self._sync_repository = sync_repository

    def get_overview(self) -> dict[str, object]:
        sync_status = self._sync_repository.get_status()
        planets = self._planet_repository.list_planets()

        return {
            "sync": sync_status,
            "runtime": {
                "planet_total": len(planets),
                "serving_from_cache": bool(sync_status["using_cached_data"]),
            },
            "architecture": [
                {
                    "name": "Frontend",
                    "responsibility": "Presenta una vista infantil y un modo técnico desplegable.",
                    "technologies": ["HTML", "CSS", "JavaScript"],
                },
                {
                    "name": "Proxy web",
                    "responsibility": "Nginx sirve archivos estáticos y reenvía /api al backend.",
                    "technologies": ["Nginx"],
                },
                {
                    "name": "Backend",
                    "responsibility": "FastAPI coordina rutas, servicios, sincronización y observabilidad.",
                    "technologies": ["FastAPI", "Uvicorn", "Pydantic"],
                },
                {
                    "name": "Persistencia",
                    "responsibility": "SQLite guarda el catálogo local y actúa como caché estable.",
                    "technologies": ["SQLite", "Docker volume"],
                },
                {
                    "name": "Fuente externa",
                    "responsibility": "Wikipedia REST en español aporta extractos, descripciones e imágenes públicas.",
                    "technologies": [sync_status["source_name"]],
                },
            ],
            "flow": [
                "La aplicación consulta la fuente externa cuando sincroniza.",
                "Los datos enriquecidos se guardan en SQLite.",
                "El frontend siempre lee del backend y el backend sirve desde la base local.",
                "Si la fuente externa falla, la app continúa usando la caché persistente.",
            ],
        }