import sys
from app.database import Base, engine, SessionLocal
from app.seed_data import seed_database
from app.models.well import Well
from app.models.report import DailyMudReport
from app.schemas.rheology import RheologyInput
from app.services.rheology_engine import calculate_rheology
from app.schemas.hydraulics import HydraulicsInput
from app.services.hydraulics_engine import calculate_hydraulics
from app.services.pdf_generator import generate_daily_mud_report_pdf

print("1. Creating database tables...")
Base.metadata.create_all(bind=engine)

db = SessionLocal()
print("2. Seeding database...")
seed_database(db)

wells_count = db.query(Well).count()
reports_count = db.query(DailyMudReport).count()
print(f"-> Wells in DB: {wells_count}, Reports in DB: {reports_count}")

print("3. Testing Rheology Engine...")
rheo_in = RheologyInput(
    rpm_600=65.0,
    rpm_300=42.0,
    rpm_200=31.0,
    rpm_100=20.0,
    rpm_6=7.0,
    rpm_3=5.0,
    gel_10s=7.0,
    gel_10m=12.0,
    gel_30m=15.0,
    mud_weight=12.5
)
rheo_out = calculate_rheology(rheo_in)
print(f"-> PV: {rheo_out.pv} cP, YP: {rheo_out.yp} lb/100ft2, AV: {rheo_out.av} cP, n: {rheo_out.n_index}, K: {rheo_out.k_index}, Tau0: {rheo_out.tau_0_hb}")

print("4. Testing Hydraulics Engine...")
hyd_in = HydraulicsInput(
    mud_weight=12.5,
    tvd=10000.0,
    md=11500.0,
    flow_rate=500.0,
    hole_id=8.5,
    drill_pipe_od=5.0,
    drill_collar_od=6.5,
    nozzles=[14, 14, 14],
    annular_pressure_loss=150.0
)
hyd_out = calculate_hydraulics(hyd_in)
print(f"-> Hydrostatic: {hyd_out.hydrostatic_pressure} psi, ECD: {hyd_out.ecd} ppg, TFA: {hyd_out.tfa} sq in, HHP: {hyd_out.hhp} hp, Flow: {hyd_out.flow_regime}")

print("5. Testing PDF Generator...")
rep = db.query(DailyMudReport).first()
well = db.query(Well).filter(Well.id == rep.well_id).first()
pdf_buf = generate_daily_mud_report_pdf(rep, well)
pdf_bytes = pdf_buf.getvalue()
print(f"-> Generated Daily Mud Report PDF: {len(pdf_bytes)} bytes!")

print("6. Testing AI Mud Doctor Engine...")
from app.main import MudDoctorQuery, ai_mud_doctor, KillSheetInput, calculate_kill_sheet

doc_res = ai_mud_doctor(MudDoctorQuery(pv=32.0, yp=16.0, mw=12.8, lgs_pct=5.8))
print(f"-> AI Mud Doctor Urgency: {doc_res['urgency']}, Recs: {len(doc_res['recommendations'])}, Ratio: {doc_res['yp_pv_ratio']}")
assert doc_res['urgency'] == "WARNING"

print("7. Testing Well Control Kill Sheet Engine...")
ks_res = calculate_kill_sheet(KillSheetInput(
    current_mw=12.0,
    tvd=10000.0,
    sidpp=500.0,
    sicp=750.0,
    slow_pump_press=800.0
))
print(f"-> KWM: {ks_res['kill_mud_weight']} ppg, ICP: {ks_res['initial_circulating_pressure']} psi, FCP: {ks_res['final_circulating_pressure']} psi")
assert ks_res['kill_mud_weight'] == 12.96
assert ks_res['initial_circulating_pressure'] == 1300.0
assert ks_res['final_circulating_pressure'] == 864.1

db.close()
print("BACKEND VERIFICATION COMPLETE: ALL SYSTEMS NOMINAL!")
