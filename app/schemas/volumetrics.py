from pydantic import BaseModel, Field
from typing import Optional, Literal

class HoleVolumeInput(BaseModel):
    hole_id: float = Field(default=8.5, gt=0, description="Hole ID (in)")
    hole_length: float = Field(..., gt=0, description="Total Well Measured Depth (ft)")
    drill_pipe_od: float = Field(default=5.0, gt=0, description="Drill Pipe OD (in)")
    drill_pipe_id: float = Field(default=4.276, gt=0, description="Drill Pipe ID (in)")
    drill_pipe_length: float = Field(..., ge=0, description="Drill Pipe Length (ft)")
    drill_collar_od: float = Field(default=6.5, gt=0, description="Drill Collar OD (in)")
    drill_collar_id: float = Field(default=2.813, gt=0, description="Drill Collar ID (in)")
    drill_collar_length: float = Field(default=600.0, ge=0, description="Drill Collar Length (ft)")
    active_pits: float = Field(default=650.0, ge=0, description="Active Surface Pit Volume (bbl)")
    reserve_pits: float = Field(default=400.0, ge=0, description="Reserve Surface Pit Volume (bbl)")
    trip_tank: float = Field(default=45.0, ge=0, description="Trip Tank Volume (bbl)")

class HoleVolumeOutput(BaseModel):
    drill_pipe_capacity: float = Field(..., description="Internal DP Capacity (bbl)")
    drill_collar_capacity: float = Field(..., description="Internal DC Capacity (bbl)")
    total_string_capacity: float = Field(..., description="Total Drill String Capacity (bbl)")
    annular_capacity_dp: float = Field(..., description="Annulus around DP (bbl)")
    annular_capacity_dc: float = Field(..., description="Annulus around DC (bbl)")
    total_annular_volume: float = Field(..., description="Total Annular Volume (bbl)")
    total_hole_volume: float = Field(..., description="Total In-Hole Volume (bbl)")
    active_surface_volume: float = Field(..., description="Active Pits Volume (bbl)")
    reserve_surface_volume: float = Field(..., description="Reserve Pits Volume (bbl)")
    trip_tank_volume: float = Field(..., description="Trip Tank (bbl)")
    total_active_circulating_volume: float = Field(..., description="Active Pits + Hole Volume (bbl)")
    total_system_volume: float = Field(..., description="Entire Mud System on Location (bbl)")

class WeightUpInput(BaseModel):
    initial_mud_weight: float = Field(..., gt=6.0, lt=22.0, description="Current Mud Weight (ppg)")
    target_mud_weight: float = Field(..., gt=6.0, lt=23.0, description="Desired Mud Weight (ppg)")
    initial_volume: float = Field(..., gt=0, description="Mud Volume to Weight Up (bbl)")
    weighting_agent: Literal["barite", "hematite"] = Field(default="barite", description="Weighting material type")

class WeightUpOutput(BaseModel):
    weighting_agent: str
    weighting_material_density_ppg: float
    weighting_agent_sg: float
    sacks_per_100_bbl: float = Field(..., description="100-lb sacks required per 100 bbl mud")
    total_sacks: float = Field(..., description="Total 100-lb sacks required")
    total_metric_tons: float = Field(..., description="Total metric tons")
    volume_increase_bbl: float = Field(..., description="Volume expansion due to added solids (bbl)")
    final_volume_bbl: float = Field(..., description="Final volume after weighting up (bbl)")
    cost_estimate_usd: float = Field(..., description="Approximate material cost in USD")

class DilutionInput(BaseModel):
    initial_mud_weight: float = Field(..., gt=6.0, description="Current Mud Weight (ppg)")
    target_mud_weight: float = Field(..., gt=6.0, description="Desired Reduced Mud Weight (ppg)")
    initial_volume: float = Field(..., gt=0, description="Current System Volume (bbl)")
    base_fluid: Literal["fresh_water", "sea_water", "diesel", "base_oil"] = Field(default="fresh_water")
    base_fluid_density: Optional[float] = Field(default=None, description="Base fluid density (ppg)")
    current_lgs_pct: Optional[float] = Field(default=None, ge=0, le=50, description="Current LGS (% vol)")
    target_lgs_pct: Optional[float] = Field(default=None, ge=0, le=50, description="Desired Target LGS (% vol)")

class DilutionOutput(BaseModel):
    base_fluid: str
    base_fluid_density_ppg: float
    dilution_volume_for_density_bbl: float = Field(..., description="Base fluid required to reduce density (bbl)")
    final_volume_after_density_dilution_bbl: float
    dilution_volume_for_lgs_bbl: Optional[float] = Field(None, description="Base fluid required to cut LGS to target (bbl)")
    barite_needed_to_maintain_mw_sacks: Optional[float] = Field(None, description="Barite sacks to restore density after LGS dilution")
    notes: str
