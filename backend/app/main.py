import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.database import initialize_database
from app.middleware.logging import RequestLoggingMiddleware
from app.repositories.planet_repository import SQLitePlanetRepository
from app.repositories.sync_repository import SQLiteSyncRepository
from app.routes.admin import router as admin_router
from app.routes.planets import router as planets_router
from app.services.admin_service import AdminService
from app.services.external_planet_source import WikipediaPlanetSource
from app.services.log_buffer import InMemoryLogHandler
from app.services.planet_sync_service import PlanetSyncService
from app.services.planet_service import PlanetService


def configure_logging() -> None:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    memory_handler = InMemoryLogHandler()
    memory_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if not root_logger.handlers:
        root_logger.addHandler(stream_handler)
        root_logger.addHandler(memory_handler)


configure_logging()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    repository = SQLitePlanetRepository(settings.database_path)
    sync_repository = SQLiteSyncRepository(settings.database_path)
    source_client = WikipediaPlanetSource(
        settings.source_api_base_url,
        settings.source_request_timeout_seconds,
    )
    planet_service = PlanetService(repository)
    sync_service = PlanetSyncService(
        settings=settings,
        planet_repository=repository,
        sync_repository=sync_repository,
        source_client=source_client,
    )
    admin_service = AdminService(repository, sync_repository)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        initialize_database(
            settings.database_path,
            settings.source_name,
            settings.source_api_base_url,
        )
        app.state.settings = settings
        app.state.planet_service = planet_service
        app.state.sync_service = sync_service
        app.state.admin_service = admin_service
        if settings.auto_sync_on_startup:
            sync_service.sync_planets()
        logger.info("application.startup database=%s", settings.database_path)
        yield
        logger.info("application.shutdown")

    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(planets_router)
    app.include_router(admin_router)

    @app.get("/health", tags=["system"])
    def healthcheck() -> dict[str, str]:
        logger.info("healthcheck.executed")
        return {"status": "ok"}

    return app


app = create_app()
