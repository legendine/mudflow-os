from app.routers.rheology import router as rheology_router
from app.routers.hydraulics import router as hydraulics_router
from app.routers.volumetrics import router as volumetrics_router
from app.routers.solids import router as solids_router
from app.routers.reports import router as reports_router

__all__ = [
    "rheology_router",
    "hydraulics_router",
    "volumetrics_router",
    "solids_router",
    "reports_router"
]
