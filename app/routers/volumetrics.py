from fastapi import APIRouter
from app.schemas.volumetrics import (
    HoleVolumeInput, HoleVolumeOutput,
    WeightUpInput, WeightUpOutput,
    DilutionInput, DilutionOutput
)
from app.services.volumetrics_engine import (
    calculate_hole_volumes,
    calculate_weight_up,
    calculate_dilution
)

router = APIRouter(prefix="/api/volumetrics", tags=["Pit Volumes & Fluid Management"])

@router.post("/hole-volumes", response_model=HoleVolumeOutput)
def calculate_volumes_endpoint(payload: HoleVolumeInput):
    """
    Computes drill string internal capacity, annular capacity (DP & DC),
    total hole volume, active circulating volume, and total on-location volume.
    """
    return calculate_hole_volumes(payload)

@router.post("/weight-up", response_model=WeightUpOutput)
def calculate_weight_up_endpoint(payload: WeightUpInput):
    """
    Calculates Barite (4.2 SG) or Hematite (5.0 SG) sacks required, sacks per 100 bbl,
    volume expansion, metric tonnage, and cost estimate.
    """
    return calculate_weight_up(payload)

@router.post("/dilution", response_model=DilutionOutput)
def calculate_dilution_endpoint(payload: DilutionInput):
    """
    Calculates required base fluid dilution volume to lower mud weight or reduce
    Low Gravity Solids (LGS), and barite requirement to maintain weight.
    """
    return calculate_dilution(payload)
