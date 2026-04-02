import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Request

from app.schemas.planet import Planet, PlanetListResponse
from app.services.log_buffer import get_recent_logs


router = APIRouter(tags=["planets"])
logger = logging.getLogger("app.routes.planets")


def get_planet_service(request: Request):
    return request.app.state.planet_service


@router.get("/planets", response_model=PlanetListResponse)
def list_planets(
    request: Request,
    category: Literal["solar-system", "exoplanets"] | None = Query(
        default=None,
        description="solar-system o exoplanets",
    ),
) -> PlanetListResponse:
    logger.info("planets.list.processing category=%s", category or "all")
    planet_service = get_planet_service(request)
    planets = planet_service.list_planets(category=category)
    logger.info("planets.list.response count=%s", len(planets))
    return PlanetListResponse(items=planets, total=len(planets))


@router.get("/planets/{planet_id}", response_model=Planet)
def get_planet(planet_id: int, request: Request) -> Planet:
    logger.info("planets.detail.processing planet_id=%s", planet_id)
    planet_service = get_planet_service(request)
    planet = planet_service.get_planet(planet_id)
    if planet is None:
        logger.warning("planets.detail.not_found planet_id=%s", planet_id)
        raise HTTPException(status_code=404, detail="Planet not found")

    logger.info("planets.detail.response planet_id=%s name=%s", planet.id, planet.name)
    return planet


@router.get("/logs/recent", tags=["system"])
def recent_logs(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, list[str] | int]:
    logs = get_recent_logs(limit=limit)
    logger.info("logs.recent.response count=%s", len(logs))
    return {"items": logs, "total": len(logs)}
