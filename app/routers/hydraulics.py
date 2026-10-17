from fastapi import APIRouter
from app.schemas.hydraulics import HydraulicsInput, HydraulicsOutput
from app.services.hydraulics_engine import calculate_hydraulics

router = APIRouter(prefix="/api/hydraulics", tags=["Hydraulics Engine"])

@router.post("/calculate", response_model=HydraulicsOutput)
def calculate_hydraulics_endpoint(payload: HydraulicsInput):
    """
    Computes Hydrostatic Pressure, ECD, Bit Nozzle TFA, Jet Velocity, Bit Pressure Drop,
    HHP, HSI, Jet Impact Force, and Annular Velocity with Flow Regime classification.
    """
    return calculate_hydraulics(payload)

@router.post("/pressure-profile")
def get_pressure_profile(payload: HydraulicsInput):
    """
    Generates depth step profile (0 to TD) showing Hydrostatic Pressure, Annular Friction,
    and Dynamic Circulating Pressure (ECD equivalent pressure).
    """
    base_res = calculate_hydraulics(payload)
    tvd_max = payload.tvd
    steps = 10
    profile = []
    
    for i in range(1, steps + 1):
        depth_step = round((tvd_max / steps) * i, 1)
        p_hyd_step = 0.052 * payload.mud_weight * depth_step
        p_ann_step = (base_res.annular_pressure_loss / tvd_max) * depth_step
        p_circ_step = p_hyd_step + p_ann_step
        ecd_step = p_circ_step / (0.052 * depth_step) if depth_step > 0 else payload.mud_weight
        
        profile.append({
            "depth_tvd": depth_step,
            "hydrostatic_pressure": round(p_hyd_step, 1),
            "annular_friction": round(p_ann_step, 1),
            "total_circulating_pressure": round(p_circ_step, 1),
            "local_ecd": round(ecd_step, 2)
        })
        
    return {
        "summary": base_res,
        "profile": profile
    }
