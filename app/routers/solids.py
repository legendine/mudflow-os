from fastapi import APIRouter
from app.schemas.solids import RetortInput, RetortOutput
from app.services.solids_engine import analyze_solids

router = APIRouter(prefix="/api/solids", tags=["Retort & Solids Control"])

@router.post("/analyze", response_model=RetortOutput)
def analyze_solids_endpoint(payload: RetortInput):
    """
    Computes Retort Phase Distribution, Average Specific Gravity of Solids (ASG),
    % HGS vs % LGS partitioning, active bentonite/clay content from MBT,
    and solids control equipment efficiency recommendations.
    """
    return analyze_solids(payload)
