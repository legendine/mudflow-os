from fastapi import APIRouter
from app.schemas.rheology import RheologyInput, RheologyOutput
from app.services.rheology_engine import calculate_rheology

router = APIRouter(prefix="/api/rheology", tags=["Rheology Engine"])

@router.post("/calculate", response_model=RheologyOutput)
def calculate_rheology_endpoint(payload: RheologyInput):
    """
    Computes Bingham Plastic, Power Law, and Herschel-Bulkley flow parameters,
    gel strength profile, and shear rate vs shear stress curve datasets.
    """
    return calculate_rheology(payload)

@router.get("/defaults")
def get_rheology_defaults():
    """
    Returns baseline field rheology readings for standard Synthetic OBM and Water-Based Mud.
    """
    return {
        "synthetic_obm": {
            "rpm_600": 68.0,
            "rpm_300": 42.0,
            "rpm_200": 32.0,
            "rpm_100": 20.0,
            "rpm_6": 7.0,
            "rpm_3": 5.0,
            "gel_10s": 7.0,
            "gel_10m": 12.0,
            "gel_30m": 15.0,
            "mud_weight": 12.8
        },
        "water_based_mud": {
            "rpm_600": 55.0,
            "rpm_300": 35.0,
            "rpm_200": 26.0,
            "rpm_100": 17.0,
            "rpm_6": 5.0,
            "rpm_3": 4.0,
            "gel_10s": 5.0,
            "gel_10m": 9.0,
            "gel_30m": 11.0,
            "mud_weight": 10.5
        }
    }
