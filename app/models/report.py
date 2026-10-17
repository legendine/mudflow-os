from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class DailyMudReport(Base):
    __tablename__ = "daily_mud_reports"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False)
    report_no = Column(Integer, nullable=False)
    report_date = Column(String(20), nullable=False)
    depth_md = Column(Float, nullable=False)
    depth_tvd = Column(Float, nullable=False)
    daily_footage = Column(Float, default=0.0)
    current_operation = Column(String(255), default="Drilling 8-1/2 inch hole")
    formation = Column(String(100), default="Stø Formation")

    # Mud Properties & Rheology
    mud_type = Column(String(50), default="OBM / Synthetic")
    mud_weight = Column(Float, nullable=False)  # ppg
    pv = Column(Float, default=0.0)             # cP
    yp = Column(Float, default=0.0)             # lb/100 ft2
    av = Column(Float, default=0.0)             # cP
    yp_pv_ratio = Column(Float, default=0.0)
    gel_10s = Column(Float, default=0.0)
    gel_10m = Column(Float, default=0.0)
    gel_30m = Column(Float, default=0.0)
    rpm_600 = Column(Float, default=0.0)
    rpm_300 = Column(Float, default=0.0)
    rpm_200 = Column(Float, default=0.0)
    rpm_100 = Column(Float, default=0.0)
    rpm_6 = Column(Float, default=0.0)
    rpm_3 = Column(Float, default=0.0)
    n_index = Column(Float, default=0.0)
    k_index = Column(Float, default=0.0)
    tau_0 = Column(Float, default=0.0)

    # Hydraulics
    flow_rate = Column(Float, default=0.0)              # GPM
    pump_pressure = Column(Float, default=0.0)          # psi
    annular_pressure_loss = Column(Float, default=0.0)  # psi
    hydrostatic_pressure = Column(Float, default=0.0)   # psi
    ecd = Column(Float, default=0.0)                    # ppg
    hole_id = Column(Float, default=8.5)                # in
    drill_pipe_od = Column(Float, default=5.0)          # in
    drill_collar_od = Column(Float, default=6.5)        # in
    bit_size = Column(Float, default=8.5)               # in
    nozzles_str = Column(String(50), default="3x14")
    tfa = Column(Float, default=0.0)                    # in2
    bit_velocity = Column(Float, default=0.0)           # ft/s
    bit_pressure_drop = Column(Float, default=0.0)      # psi
    hhp = Column(Float, default=0.0)                    # hp
    hsi = Column(Float, default=0.0)                    # hp/in2
    impact_force = Column(Float, default=0.0)           # lbf
    annular_velocity_dp = Column(Float, default=0.0)    # ft/min
    flow_regime = Column(String(50), default="Laminar")

    # Volumes
    active_volume = Column(Float, default=0.0)          # bbl
    reserve_volume = Column(Float, default=0.0)         # bbl
    trip_tank_volume = Column(Float, default=0.0)       # bbl
    hole_volume = Column(Float, default=0.0)            # bbl
    total_volume = Column(Float, default=0.0)           # bbl

    # Retort & Solids
    retort_water = Column(Float, default=0.0)           # % vol
    retort_oil = Column(Float, default=0.0)             # % vol
    retort_solids = Column(Float, default=0.0)          # % vol
    asg = Column(Float, default=0.0)                    # Average SG
    hgs_pct = Column(Float, default=0.0)                # % vol
    lgs_pct = Column(Float, default=0.0)                # % vol
    mbt = Column(Float, default=0.0)                    # ppb
    chlorides = Column(Float, default=0.0)              # mg/L

    # Chemicals & Remarks
    chemical_additions_json = Column(Text, default="[]")
    remarks = Column(Text, default="")
    engineer_name = Column(String(100), default="Senior Mud Engineer")
    created_at = Column(DateTime, default=datetime.utcnow)

    well = relationship("Well", back_populates="reports")
