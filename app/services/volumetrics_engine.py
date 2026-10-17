from typing import Dict, Any
from app.schemas.volumetrics import (
    HoleVolumeInput, HoleVolumeOutput,
    WeightUpInput, WeightUpOutput,
    DilutionInput, DilutionOutput
)

BASE_FLUID_DENSITIES: Dict[str, float] = {
    "fresh_water": 8.33,
    "sea_water": 8.60,
    "diesel": 7.00,
    "base_oil": 6.80
}

WEIGHTING_AGENTS = {
    "barite": {
        "sg": 4.20,
        "density_ppg": 35.0,
        "constant": 1470.0,
        "sack_weight_lb": 100.0,
        "cost_per_sack_usd": 18.50
    },
    "hematite": {
        "sg": 5.00,
        "density_ppg": 41.7,
        "constant": 1751.0,
        "sack_weight_lb": 100.0,
        "cost_per_sack_usd": 28.00
    }
}

def calculate_hole_volumes(data: HoleVolumeInput) -> HoleVolumeOutput:
    # Capacity formulas: bbl/ft = ID^2 / 1029.4
    # Annular capacity formulas: bbl/ft = (Hole_ID^2 - OD^2) / 1029.4
    
    dp_len = max(0.0, data.drill_pipe_length)
    dc_len = max(0.0, data.drill_collar_length)
    
    dp_cap = (data.drill_pipe_id ** 2 / 1029.4) * dp_len
    dc_cap = (data.drill_collar_id ** 2 / 1029.4) * dc_len
    total_string_cap = dp_cap + dc_cap
    
    dp_ann_diff = max(0.0, (data.hole_id ** 2) - (data.drill_pipe_od ** 2))
    dc_ann_diff = max(0.0, (data.hole_id ** 2) - (data.drill_collar_od ** 2))
    
    dp_ann_cap = (dp_ann_diff / 1029.4) * dp_len
    dc_ann_cap = (dc_ann_diff / 1029.4) * dc_len
    total_ann_vol = dp_ann_cap + dc_ann_cap
    
    total_hole_vol = total_string_cap + total_ann_vol
    active_circulating = data.active_pits + total_hole_vol
    total_system = data.active_pits + data.reserve_pits + data.trip_tank + total_hole_vol
    
    return HoleVolumeOutput(
        drill_pipe_capacity=round(dp_cap, 1),
        drill_collar_capacity=round(dc_cap, 1),
        total_string_capacity=round(total_string_cap, 1),
        annular_capacity_dp=round(dp_ann_cap, 1),
        annular_capacity_dc=round(dc_ann_cap, 1),
        total_annular_volume=round(total_ann_vol, 1),
        total_hole_volume=round(total_hole_vol, 1),
        active_surface_volume=round(data.active_pits, 1),
        reserve_surface_volume=round(data.reserve_pits, 1),
        trip_tank_volume=round(data.trip_tank, 1),
        total_active_circulating_volume=round(active_circulating, 1),
        total_system_volume=round(total_system, 1)
    )

def calculate_weight_up(data: WeightUpInput) -> WeightUpOutput:
    agent_key = data.weighting_agent.lower()
    props = WEIGHTING_AGENTS.get(agent_key, WEIGHTING_AGENTS["barite"])
    
    mw1 = data.initial_mud_weight
    mw2 = data.target_mud_weight
    v1 = data.initial_volume
    rho_w = props["density_ppg"]
    
    if mw2 <= mw1:
        return WeightUpOutput(
            weighting_agent=agent_key.capitalize(),
            weighting_material_density_ppg=rho_w,
            weighting_agent_sg=props["sg"],
            sacks_per_100_bbl=0.0,
            total_sacks=0.0,
            total_metric_tons=0.0,
            volume_increase_bbl=0.0,
            final_volume_bbl=round(v1, 1),
            cost_estimate_usd=0.0
        )
        
    denom = max(0.1, rho_w - mw2)
    sacks_per_100 = (props["constant"] * (mw2 - mw1)) / denom
    total_sacks = sacks_per_100 * (v1 / 100.0)
    total_mt = (total_sacks * props["sack_weight_lb"]) / 2204.62
    
    # Volume expansion: V_w = Total_Weight / (SG * 8.337 * 42)
    vol_increase = (total_sacks * props["sack_weight_lb"]) / (props["sg"] * 8.337 * 42.0)
    final_vol = v1 + vol_increase
    cost = total_sacks * props["cost_per_sack_usd"]
    
    return WeightUpOutput(
        weighting_agent=agent_key.capitalize(),
        weighting_material_density_ppg=rho_w,
        weighting_agent_sg=props["sg"],
        sacks_per_100_bbl=round(sacks_per_100, 1),
        total_sacks=round(total_sacks, 0),
        total_metric_tons=round(total_mt, 2),
        volume_increase_bbl=round(vol_increase, 1),
        final_volume_bbl=round(final_vol, 1),
        cost_estimate_usd=round(cost, 2)
    )

def calculate_dilution(data: DilutionInput) -> DilutionOutput:
    base_dens = data.base_fluid_density or BASE_FLUID_DENSITIES.get(data.base_fluid, 8.33)
    mw1 = data.initial_mud_weight
    mw2 = data.target_mud_weight
    v1 = data.initial_volume
    
    # 1. Dilution to lower density
    # V_dil = V1 * (MW1 - MW2) / (MW2 - MW_base)
    if mw2 < mw1 and mw2 > base_dens:
        denom = mw2 - base_dens
        dil_vol_dens = v1 * (mw1 - mw2) / denom
    else:
        dil_vol_dens = 0.0
        
    final_vol_dens = v1 + dil_vol_dens
    
    # 2. Dilution to cut LGS
    dil_vol_lgs = None
    barite_for_lgs = None
    if data.current_lgs_pct and data.target_lgs_pct and data.current_lgs_pct > data.target_lgs_pct:
        # V_dil_lgs = V1 * (LGS1 - LGS2) / LGS2
        dil_vol_lgs = v1 * (data.current_lgs_pct - data.target_lgs_pct) / data.target_lgs_pct
        
        # To maintain target MW1 on the newly diluted mud:
        # Sacks needed for dil_vol_lgs
        sacks_per_100 = (1470.0 * (mw1 - base_dens)) / max(0.1, (35.0 - mw1))
        barite_for_lgs = sacks_per_100 * (dil_vol_lgs / 100.0)
        
    notes = (
        f"Base fluid selected: {data.base_fluid.replace('_', ' ').title()} ({base_dens} ppg). "
        f"Always verify active pit room prior to large surface transfers."
    )
    
    return DilutionOutput(
        base_fluid=data.base_fluid.replace("_", " ").title(),
        base_fluid_density_ppg=round(base_dens, 2),
        dilution_volume_for_density_bbl=round(dil_vol_dens, 1),
        final_volume_after_density_dilution_bbl=round(final_vol_dens, 1),
        dilution_volume_for_lgs_bbl=round(dil_vol_lgs, 1) if dil_vol_lgs is not None else None,
        barite_needed_to_maintain_mw_sacks=round(barite_for_lgs, 0) if barite_for_lgs is not None else None,
        notes=notes
    )
