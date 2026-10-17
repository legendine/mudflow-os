from pydantic import BaseModel, Field
from typing import List, Optional

class HydraulicsInput(BaseModel):
    mud_weight: float = Field(..., description="Mud Weight (ppg)", gt=0)
    tvd: float = Field(..., description="True Vertical Depth (ft)", gt=0)
    md: float = Field(..., description="Measured Depth (ft)", gt=0)
    flow_rate: float = Field(..., description="Flow Rate (GPM)", gt=0)
    hole_id: float = Field(default=8.5, description="Hole / Casing Inner Diameter (in)", gt=0)
    drill_pipe_od: float = Field(default=5.0, description="Drill Pipe Outer Diameter (in)", gt=0)
    drill_collar_od: float = Field(default=6.5, description="Drill Collar Outer Diameter (in)", gt=0)
    nozzles: List[float] = Field(default=[14, 14, 14], description="Bit nozzle sizes in 32nds of an inch (e.g. [14, 14, 14])")
    annular_pressure_loss: Optional[float] = Field(default=None, description="Annular pressure loss in psi. If None, calculated via rheology.")
    pump_pressure: Optional[float] = Field(default=3200.0, description="Surface Standpipe Pressure (psi)")
    pv: Optional[float] = Field(default=22.0, description="Plastic Viscosity (cP)")
    yp: Optional[float] = Field(default=16.0, description="Yield Point (lb/100 ft2)")

class HydraulicsOutput(BaseModel):
    hydrostatic_pressure: float = Field(..., description="Hydrostatic pressure at TVD (psi)")
    annular_pressure_loss: float = Field(..., description="Annular pressure loss (psi)")
    ecd: float = Field(..., description="Equivalent Circulating Density (ppg)")
    annular_velocity_dp: float = Field(..., description="Annular Velocity around Drill Pipe (ft/min)")
    annular_velocity_dc: float = Field(..., description="Annular Velocity around Drill Collars (ft/min)")
    tfa: float = Field(..., description="Total Flow Area of Bit Nozzles (sq in)")
    bit_velocity: float = Field(..., description="Jet Nozzle Velocity (ft/sec)")
    bit_pressure_drop: float = Field(..., description="Pressure Drop across Bit Nozzles (psi)")
    hhp: float = Field(..., description="Bit Hydraulic Horsepower (HHP)")
    hsi: float = Field(..., description="Hydraulic Horsepower per Square Inch of Bit Area (HSI)")
    impact_force: float = Field(..., description="Jet Impact Force (lbf)")
    reynolds_number: float = Field(..., description="Effective Annular Reynolds Number")
    flow_regime: str = Field(..., description="Laminar, Transitional, or Turbulent")
    percent_pressure_at_bit: float = Field(..., description="Percentage of pump pressure consumed at bit")
    hole_cleaning_status: str = Field(..., description="Evaluation of cutting transport efficiency")
