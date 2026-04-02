from fastapi import APIRouter, Request

from app.schemas.admin import AdminOverview


router = APIRouter(prefix="/admin", tags=["admin"])


def get_admin_service(request: Request):
    return request.app.state.admin_service


@router.get("/overview", response_model=AdminOverview)
def overview(request: Request) -> AdminOverview:
    admin_service = get_admin_service(request)
    return AdminOverview.model_validate(admin_service.get_overview())


@router.post("/sync", response_model=AdminOverview)
def sync_planets(request: Request) -> AdminOverview:
    sync_service = request.app.state.sync_service
    sync_service.sync_planets()
    admin_service = get_admin_service(request)
    return AdminOverview.model_validate(admin_service.get_overview())