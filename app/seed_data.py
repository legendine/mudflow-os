import json
from sqlalchemy.orm import Session
from app.models.well import Well
from app.models.report import DailyMudReport

def seed_database(db: Session):
    # Check if wells already exist
    if db.query(Well).count() > 0:
        return

    # 1. Create Wells
    well1 = Well(
        well_name="Castberg 7220/8-1",
        operator="Equinor Energy",
        rig_name="Deepsea Nordkapp",
        field_name="Johan Castberg",
        country="Norway",
        spud_date="2026-09-01",
        target_depth=14200.0,
        well_type="Exploration / HPHT",
        status="Active Drilling"
    )
    well2 = Well(
        well_name="Thunder Horse MC-778",
        operator="BP America Production",
        rig_name="Thunder Horse PDQ",
        field_name="Mississippi Canyon",
        country="USA - Deepwater GOM",
        spud_date="2026-07-20",
        target_depth=28500.0,
        well_type="Deepwater Subsea HPHT",
        status="Drilling 12-1/4 Intermediate"
    )
    well3 = Well(
        well_name="Wolfcamp A-102H",
        operator="Pioneer Natural Resources",
        rig_name="H&P FlexRig 582",
        field_name="Midland Basin",
        country="USA - Texas",
        spud_date="2026-10-05",
        target_depth=19800.0,
        well_type="Horizontal Unconventional",
        status="Drilling Lateral Section"
    )
    db.add_all([well1, well2, well3])
    db.commit()
    db.refresh(well1)
    db.refresh(well2)
    db.refresh(well3)

    # 2. Add sequential Daily Mud Reports for Well 1
    chems_rep14 = json.dumps([
        {"product": "Barite (API 4.2 SG)", "unit": "100 lb Sack", "added": 120, "initial": 1400, "ending": 1280},
        {"product": "EDC 99-DW Base Oil", "unit": "BBL", "added": 35, "initial": 400, "ending": 365},
        {"product": "Invermul Primary Emulsifier", "unit": "55 Gal Drum", "added": 2, "initial": 24, "ending": 22},
        {"product": "EZ-MUL NT Secondary Emulsifier", "unit": "55 Gal Drum", "added": 2, "initial": 20, "ending": 18},
        {"product": "Geltone V Organophilic Clay", "unit": "50 lb Sack", "added": 15, "initial": 150, "ending": 135}
    ])

    report14 = DailyMudReport(
        well_id=well1.id,
        report_no=14,
        report_date="2026-10-14",
        depth_md=11250.0,
        depth_tvd=9820.0,
        daily_footage=420.0,
        current_operation="Drilling 8-1/2 section through Stø sandstone",
        formation="Stø Formation",
        mud_type="Synthetic OBM (Versaclean)",
        mud_weight=12.4,
        pv=21.0,
        yp=15.0,
        av=31.0,
        yp_pv_ratio=0.71,
        gel_10s=6.0,
        gel_10m=11.0,
        gel_30m=14.0,
        rpm_600=63.0,
        rpm_300=42.0,
        rpm_200=32.0,
        rpm_100=20.0,
        rpm_6=7.0,
        rpm_3=5.0,
        n_index=0.584,
        k_index=1.124,
        tau_0=4.26,
        flow_rate=520.0,
        pump_pressure=3150.0,
        annular_pressure_loss=145.0,
        hydrostatic_pressure=6332.0,
        ecd=12.68,
        hole_id=8.5,
        drill_pipe_od=5.0,
        drill_collar_od=6.5,
        bit_size=8.5,
        nozzles_str="3x14",
        tfa=0.451,
        bit_velocity=370.1,
        bit_pressure_drop=1328.0,
        hhp=402.9,
        hsi=7.10,
        impact_force=1240.2,
        annular_velocity_dp=134.2,
        flow_regime="Laminar Flow (Optimal Wellbore Stability)",
        active_volume=680.0,
        reserve_volume=450.0,
        trip_tank_volume=42.0,
        hole_volume=512.0,
        total_volume=1684.0,
        retort_water=14.5,
        retort_oil=66.5,
        retort_solids=19.0,
        asg=3.82,
        hgs_pct=14.49,
        lgs_pct=4.51,
        mbt=12.0,
        chlorides=18500.0,
        chemical_additions_json=chems_rep14,
        remarks="Properties within target specifications. Good shaker performance on 170 mesh. Maintained ECD below fracture gradient window (13.1 ppg).",
        engineer_name="Erik Lindqvist (Senior Drilling Fluids Specialist)"
    )

    chems_rep15 = json.dumps([
        {"product": "Barite (API 4.2 SG)", "unit": "100 lb Sack", "added": 160, "initial": 1280, "ending": 1120},
        {"product": "EDC 99-DW Base Oil", "unit": "BBL", "added": 40, "initial": 365, "ending": 325},
        {"product": "Duratone HT Fluid Loss Reducer", "unit": "50 lb Sack", "added": 12, "initial": 90, "ending": 78},
        {"product": "Lime (Calcium Hydroxide)", "unit": "50 lb Sack", "added": 20, "initial": 160, "ending": 140}
    ])

    report15 = DailyMudReport(
        well_id=well1.id,
        report_no=15,
        report_date="2026-10-15",
        depth_md=11730.0,
        depth_tvd=10180.0,
        daily_footage=480.0,
        current_operation="Drilling 8-1/2 section at 42 ft/hr with PDC Bit",
        formation="Nordmela Formation",
        mud_type="Synthetic OBM (Versaclean)",
        mud_weight=12.6,
        pv=23.0,
        yp=17.0,
        av=33.5,
        yp_pv_ratio=0.74,
        gel_10s=7.0,
        gel_10m=12.0,
        gel_30m=15.0,
        rpm_600=67.0,
        rpm_300=44.0,
        rpm_200=34.0,
        rpm_100=21.0,
        rpm_6=8.0,
        rpm_3=6.0,
        n_index=0.607,
        k_index=1.045,
        tau_0=4.80,
        flow_rate=530.0,
        pump_pressure=3280.0,
        annular_pressure_loss=156.0,
        hydrostatic_pressure=6670.0,
        ecd=12.89,
        hole_id=8.5,
        drill_pipe_od=5.0,
        drill_collar_od=6.5,
        bit_size=8.5,
        nozzles_str="3x14",
        tfa=0.451,
        bit_velocity=377.2,
        bit_pressure_drop=1402.0,
        hhp=433.5,
        hsi=7.64,
        impact_force=1306.8,
        annular_velocity_dp=136.8,
        flow_regime="Laminar Flow (Optimal Wellbore Stability)",
        active_volume=695.0,
        reserve_volume=430.0,
        trip_tank_volume=45.0,
        hole_volume=535.0,
        total_volume=1705.0,
        retort_water=14.0,
        retort_oil=66.0,
        retort_solids=20.0,
        asg=3.85,
        hgs_pct=15.62,
        lgs_pct=4.38,
        mbt=11.5,
        chlorides=19200.0,
        chemical_additions_json=chems_rep15,
        remarks="Weighted active system up from 12.4 to 12.6 ppg as planned. Centrifuges running continuous duty to control reactive fines from Nordmela siltstones.",
        engineer_name="Erik Lindqvist (Senior Drilling Fluids Specialist)"
    )

    chems_rep16 = json.dumps([
        {"product": "Barite (API 4.2 SG)", "unit": "100 lb Sack", "added": 180, "initial": 1120, "ending": 940},
        {"product": "EDC 99-DW Base Oil", "unit": "BBL", "added": 45, "initial": 325, "ending": 280},
        {"product": "Primary Emulsifier", "unit": "55 Gal Drum", "added": 3, "initial": 22, "ending": 19},
        {"product": "Rheflat Rheology Modifier", "unit": "55 Gal Drum", "added": 1, "initial": 14, "ending": 13}
    ])

    report16 = DailyMudReport(
        well_id=well1.id,
        report_no=16,
        report_date="2026-10-16",
        depth_md=12240.0,
        depth_tvd=10550.0,
        daily_footage=510.0,
        current_operation="Drilling ahead smoothly towards Tubåen reservoir target",
        formation="Tubåen Formation",
        mud_type="Synthetic OBM (Versaclean)",
        mud_weight=12.8,
        pv=24.0,
        yp=18.0,
        av=35.0,
        yp_pv_ratio=0.75,
        gel_10s=7.0,
        gel_10m=13.0,
        gel_30m=16.0,
        rpm_600=70.0,
        rpm_300=46.0,
        rpm_200=35.0,
        rpm_100=22.0,
        rpm_6=8.0,
        rpm_3=6.0,
        n_index=0.605,
        k_index=1.092,
        tau_0=5.00,
        flow_rate=540.0,
        pump_pressure=3390.0,
        annular_pressure_loss=168.0,
        hydrostatic_pressure=7022.0,
        ecd=13.11,
        hole_id=8.5,
        drill_pipe_od=5.0,
        drill_collar_od=6.5,
        bit_size=8.5,
        nozzles_str="3x14",
        tfa=0.451,
        bit_velocity=384.3,
        bit_pressure_drop=1479.0,
        hhp=465.7,
        hsi=8.21,
        impact_force=1379.8,
        annular_velocity_dp=139.4,
        flow_regime="Laminar Flow (Optimal Wellbore Stability)",
        active_volume=710.0,
        reserve_volume=410.0,
        trip_tank_volume=46.0,
        hole_volume=558.0,
        total_volume=1724.0,
        retort_water=13.8,
        retort_oil=65.2,
        retort_solids=21.0,
        asg=3.88,
        hgs_pct=16.80,
        lgs_pct=4.20,
        mbt=10.0,
        chlorides=19800.0,
        chemical_additions_json=chems_rep16,
        remarks="Approaching Tubåen sand tops. Flow checks confirmed negative. Mud properties in pristine condition: LGS suppressed to 4.2% vol. Flat gels maintained.",
        engineer_name="Erik Lindqvist (Senior Drilling Fluids Specialist)"
    )

    db.add_all([report14, report15, report16])
    db.commit()
