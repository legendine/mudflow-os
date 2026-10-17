from pydantic import BaseModel, Field
from typing import Optional

class RetortInput(BaseModel):
    water_pct: float = Field(..., ge=0, le=100, description="Retort Water Volume %")
    oil_pct: float = Field(default=0.0, ge=0, le=100, description="Retort Oil Volume %")
    solids_pct: Optional[float] = Field(default=None, ge=0, le=100, description="Retort Solids Volume % (if None, calculated as 100 - W% - O%)")
    mud_weight: float = Field(..., gt=6.0, lt=23.0, description="Mud Weight (ppg)")
    mbt_ppb: float = Field(default=15.0, ge=0, description="Methylene Blue Capacity (ppb bentonite eq)")
    chlorides_mg_l: float = Field(default=15000.0, ge=0, description="Chlorides concentration (mg/L)")
    oil_sg: float = Field(default=0.84, gt=0.6, lt=1.1, description="Base oil specific gravity")

class RetortOutput(BaseModel):
    water_pct: float
    oil_pct: float
    total_solids_pct: float
    oil_water_ratio: str
    
    # Solids Partitioning
    asg: float = Field(..., description="Average Specific Gravity of Solids (ASG)")
    hgs_pct: float = Field(..., description="High Gravity Solids (Barite/Hematite) % by volume")
    lgs_pct: float = Field(..., description="Low Gravity Solids (Drill Solids + Bentonite) % by volume")
    hgs_ppb: float = Field(..., description="High Gravity Solids (ppb)")
    lgs_ppb: float = Field(..., description="Low Gravity Solids (ppb)")
    
    # Clay and Active Solids
    active_clay_pct: float = Field(..., description="Active Smectite Clay (% by volume)")
    active_clay_ppb: float = Field(..., description="Active Clay (ppb bentonite eq)")
    inactive_drill_solids_pct: float = Field(..., description="Inactive Drill Solids (% by volume)")
    active_clay_ratio: float = Field(..., description="Active Clay to Total LGS Ratio")
    
    # Thresholds and alerts
    excess_lgs: bool = Field(..., description="True if LGS exceeds recommended operational limits (> 4-5% in HPHT, > 6% standard)")
    lgs_recommendation: str
    solids_control_efficiency: str
