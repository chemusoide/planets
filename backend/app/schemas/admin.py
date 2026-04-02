from pydantic import BaseModel


class SyncStatus(BaseModel):
    source_name: str
    source_url: str
    last_attempted_at: str | None
    last_success_at: str | None
    last_status: str
    last_message: str
    records_processed: int
    using_cached_data: bool


class RuntimeStatus(BaseModel):
    planet_total: int
    serving_from_cache: bool


class ArchitectureSection(BaseModel):
    name: str
    responsibility: str
    technologies: list[str]


class AdminOverview(BaseModel):
    sync: SyncStatus
    runtime: RuntimeStatus
    architecture: list[ArchitectureSection]
    flow: list[str]