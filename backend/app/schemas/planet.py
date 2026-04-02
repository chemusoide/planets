from typing import Literal

from pydantic import BaseModel


PlanetCategory = Literal["solar-system", "exoplanets"]


class Planet(BaseModel):
    id: int
    position: int
    category: PlanetCategory
    name: str
    emoji: str
    climate: str
    terrain: str
    population: str
    description: str
    kid_summary: str
    fun_fact: str
    moons: int
    day_length_hours: float
    distance_from_sun_million_km: float
    wikipedia_title: str = ""
    source_summary: str = ""
    source_description: str = ""
    source_page_url: str = ""
    image_url: str = ""
    last_synced_at: str | None = None


class PlanetListResponse(BaseModel):
    items: list[Planet]
    total: int
