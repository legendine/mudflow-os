from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class WellBase(BaseModel):
    well_name: str
    operator: str = "Equinor Energy"
    rig_name: str = "Deepsea Nordkapp"
    field_name: str = "Johan Castberg"
    country: str = "Norway"
    spud_date: str = "2026-08-15"
    target_depth: float = 14500.0
    well_type: str = "Exploration / HPHT"
    status: str = "Active Drilling"

class WellCreate(WellBase):
    pass

class WellResponse(WellBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DailyMudReportBase(BaseModel):
    well_id: int
    report_no: int
    report_date: str
    depth_md: float
    depth_tvd: float
    daily_footage: float = 0.0
    current_operation: str = "Drilling 8-1/2 inch section"
    formation: str = "Stø Formation"

    # Rheology
    mud_type: str = "Synthetic OBM"
    mud_weight: float
    pv: float = 0.0
    yp: float = 0.0
    av: float = 0.0
    yp_pv_ratio: float = 0.0
    gel_10s: float = 0.0
    gel_10m: float = 0.0
    gel_30m: float = 0.0
    rpm_600: float = 0.0
    rpm_300: float = 0.0
    rpm_200: float = 0.0
    rpm_100: float = 0.0
    rpm_6: float = 0.0
    rpm_3: float = 0.0
    n_index: float = 0.0
    k_index: float = 0.0
    tau_0: float = 0.0

    # Hydraulics
    flow_rate: float = 0.0
    pump_pressure: float = 0.0
    annular_pressure_loss: float = 0.0
    hydrostatic_pressure: float = 0.0
    ecd: float = 0.0
    hole_id: float = 8.5
    drill_pipe_od: float = 5.0
    drill_collar_od: float = 6.5
    bit_size: float = 8.5
    nozzles_str: str = "3x14"
    tfa: float = 0.0
    bit_velocity: float = 0.0
    bit_pressure_drop: float = 0.0
    hhp: float = 0.0
    hsi: float = 0.0
    impact_force: float = 0.0
    annular_velocity_dp: float = 0.0
    flow_regime: str = "Laminar"

    # Volumes
    active_volume: float = 0.0
    reserve_volume: float = 0.0
    trip_tank_volume: float = 0.0
    hole_volume: float = 0.0
    total_volume: float = 0.0

    # Retort
    retort_water: float = 0.0
    retort_oil: float = 0.0
    retort_solids: float = 0.0
    asg: float = 0.0
    hgs_pct: float = 0.0
    lgs_pct: float = 0.0
    mbt: float = 0.0
    chlorides: float = 0.0

    # Meta
    chemical_additions_json: str = "[]"
    remarks: str = ""
    engineer_name: str = "Senior Mud Engineer"

class DailyMudReportCreate(DailyMudReportBase):
    pass

class DailyMudReportResponse(DailyMudReportBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
