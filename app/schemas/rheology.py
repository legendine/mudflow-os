from pydantic import BaseModel, Field
from typing import List, Optional

class RheologyInput(BaseModel):
    rpm_600: float = Field(..., description="600 RPM viscometer dial reading", ge=0)
    rpm_300: float = Field(..., description="300 RPM viscometer dial reading", ge=0)
    rpm_200: float = Field(default=0.0, ge=0)
    rpm_100: float = Field(default=0.0, ge=0)
    rpm_6: float = Field(default=0.0, ge=0)
    rpm_3: float = Field(default=0.0, ge=0)
    gel_10s: float = Field(default=0.0, description="10-second gel strength (lb/100 ft2)", ge=0)
    gel_10m: float = Field(default=0.0, description="10-minute gel strength (lb/100 ft2)", ge=0)
    gel_30m: float = Field(default=0.0, description="30-minute gel strength (lb/100 ft2)", ge=0)
    mud_weight: Optional[float] = Field(default=12.0, ge=6.0, le=22.0)

class RheologyCurvePoint(BaseModel):
    rpm: float
    shear_rate: float
    measured_stress: float
    bingham_stress: float
    powerlaw_stress: float
    herschel_bulkley_stress: float

class RheologyOutput(BaseModel):
    pv: float = Field(..., description="Plastic Viscosity (cP)")
    yp: float = Field(..., description="Yield Point (lb/100 ft2)")
    av: float = Field(..., description="Apparent Viscosity (cP)")
    yp_pv_ratio: float = Field(..., description="YP/PV Ratio")
    
    # Power Law Model
    n_index: float = Field(..., description="Power Law Flow Behavior Index n")
    k_index: float = Field(..., description="Power Law Consistency Index K (lb*s^n / 100 ft2)")
    
    # Herschel-Bulkley (Yield Power Law) Model
    tau_0_hb: float = Field(..., description="Herschel-Bulkley Yield Stress Tau0 (lb/100 ft2)")
    n_hb: float = Field(..., description="Herschel-Bulkley Flow Behavior Index n_hb")
    k_hb: float = Field(..., description="Herschel-Bulkley Consistency Index K_hb")
    
    # Gel Strengths
    gel_10s: float
    gel_10m: float
    gel_30m: float
    gel_structure_type: str = Field(..., description="Flat, Progressive, or Fragile")
    
    # Statistical model fit
    r2_bingham: float
    r2_powerlaw: float
    r2_hb: float
    
    curve_data: List[RheologyCurvePoint]
