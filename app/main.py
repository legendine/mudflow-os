from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from pathlib import Path

from app.config import APP_TITLE, APP_VERSION, BASE_DIR
from app.database import engine, Base, get_db
from app.seed_data import seed_database
from app.routers import (
    rheology_router,
    hydraulics_router,
    volumetrics_router,
    solids_router,
    reports_router
)

# Initialize tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Full-Stack Drilling Mud Engineering & Hydraulics Management Suite for Operations Engineers"
)

# Enable CORS for local testing & integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(rheology_router)
app.include_router(hydraulics_router)
app.include_router(volumetrics_router)
app.include_router(solids_router)
app.include_router(reports_router)

# Static directory setup
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Mount static directory for JS/CSS assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ==========================================
# PYDANTIC MODELS FOR AI MUD DOCTOR & KILL SHEET
# ==========================================

class MudDoctorQuery(BaseModel):
    pv: float = Field(..., description="Plastic Viscosity in cP")
    yp: float = Field(..., description="Yield Point in lb/100ft²")
    mw: float = Field(..., description="Mud Weight in ppg")
    lgs_pct: float = Field(..., description="Low Gravity Solids percentage (% vol)")


class KillSheetInput(BaseModel):
    current_mw: float = Field(..., description="Current Mud Weight in ppg")
    tvd: float = Field(..., description="True Vertical Depth in feet")
    sidpp: float = Field(..., description="Shut-In Drillpipe Pressure in psi")
    sicp: float = Field(..., description="Shut-In Casing Pressure in psi")
    slow_pump_press: float = Field(..., description="Slow Circulating Pump Pressure in psi")


# ==========================================
# AI MUD DOCTOR & KILL SHEET ENDPOINTS
# ==========================================

@app.post("/api/ai-mud-doctor")
def ai_mud_doctor(query: MudDoctorQuery):
    pv = query.pv
    yp = query.yp
    mw = query.mw
    lgs_pct = query.lgs_pct

    yp_pv_ratio = round(yp / pv, 2) if pv > 0 else 0.0
    recommendations = []
    urgency = "OPTIMAL"

    # 1. LGS Analysis
    if lgs_pct > 7.0:
        urgency = "CRITICAL"
        recommendations.append(
            f"CRITICAL LGS CONTAMINATION: Low Gravity Solids at {lgs_pct:.1f}% vol (safe limit <= 5.5%). "
            "High risk of differential sticking, thick filter cake, and excessive ECD. Run all high-G drying shakers, "
            "operate decanting centrifuges at maximum G-force in discard mode, and initiate base fluid dilution."
        )
    elif lgs_pct > 5.5:
        if urgency != "CRITICAL":
            urgency = "WARNING"
        recommendations.append(
            f"ELEVATED DRILL SOLIDS (LGS {lgs_pct:.1f}%): LGS exceeds 5.5% guideline. Sub-micron solids build-up causes plastic viscosity spikes. "
            "Inspect shaker screens for tears or blinding, optimize centrifuge feed rate, and plan base fluid dilution."
        )
    else:
        recommendations.append(
            f"SOLIDS CONTROL NORMAL: LGS ({lgs_pct:.1f}% vol) is well controlled below 5.5% target limit. Solids removal efficiency is nominal."
        )

    # 2. Plastic Viscosity Analysis
    if pv > 35:
        urgency = "CRITICAL"
        recommendations.append(
            f"SEVERE PLASTIC VISCOSITY ({pv:.1f} cP): Mechanical friction from ultra-fine solids is dangerously high. "
            "Annular pressure losses and swab/surge pressures are elevated. Dilute active volume with base fluid and add wetting agents/thinners."
        )
    elif pv > 30:
        if urgency != "CRITICAL":
            urgency = "WARNING"
        recommendations.append(
            f"HIGH PLASTIC VISCOSITY ({pv:.1f} cP): Fluid resistance due to colloidal solids volume is above normal operating window (>30 cP). "
            "Increase solids discard rate and condition active system with thinners/dispersants."
        )
    elif pv < 10 and mw > 12.0:
        if urgency != "CRITICAL":
            urgency = "WARNING"
        recommendations.append(
            f"LOW VISCOSITY ALERT ({pv:.1f} cP for {mw:.1f} ppg): Plastic viscosity is unusually low for this mud density. "
            "Verify solids suspension and monitor for dynamic/static barite sag."
        )

    # 3. Yield Point & YP/PV Ratio Analysis
    if yp_pv_ratio < 0.5:
        if urgency != "CRITICAL":
            urgency = "WARNING"
        recommendations.append(
            f"POOR HOLE CLEANING (YP/PV = {yp_pv_ratio:.2f}): Recommended ratio is 0.50 - 1.25. "
            f"Yield point ({yp:.1f} lb/100ft²) is inadequate to support and carry drill cuttings in deviated sections. "
            "Add organophilic clay, rheological modifier, or biopolymer to raise low-shear rheology."
        )
    elif yp_pv_ratio > 1.3:
        if urgency != "CRITICAL":
            urgency = "WARNING"
        recommendations.append(
            f"PROGRESSIVE GELATION / FLOCCULATION (YP/PV = {yp_pv_ratio:.2f}): Yield point is disproportionately high. "
            "Indicates potential chemical contamination, active clay hydration, or over-treatment. High pressure will be required to break circulation. "
            "Add deflocculant/chemical thinner to restore balanced rheology."
        )
    else:
        recommendations.append(
            f"RHEOLOGY BALANCE OPTIMAL: YP/PV ratio ({yp_pv_ratio:.2f}) is in the ideal API window (0.50 - 1.25), providing superior cutting carrying capacity and manageable circulation pressures."
        )

    # 4. Additional Density & Mud Weight Context
    if mw >= 15.0:
        recommendations.append(
            f"HPHT DENSITY PROTOCOL: Mud Weight ({mw:.1f} ppg) requires tight ECD monitoring, surge pressure mitigation during tripping, and continuous trip-tank telemetry tracking."
        )

    summary_note = (
        f"AI Mud Doctor Diagnostic: Current fluid status evaluated as {urgency}. "
        f"MW: {mw:.1f} ppg | PV: {pv:.1f} cP | YP: {yp:.1f} lb/100ft² | YP/PV: {yp_pv_ratio:.2f} | LGS: {lgs_pct:.1f}% vol. "
        f"{'Immediate corrective treatment recommended to mitigate wellbore stability and ECD risks.' if urgency != 'OPTIMAL' else 'Fluid properties are within optimum specifications for active drilling operations.'}"
    )

    return {
        "urgency": urgency,
        "status": f"Diagnostic Complete: {urgency}",
        "yp_pv_ratio": yp_pv_ratio,
        "metrics": {
            "pv": pv,
            "yp": yp,
            "mw": mw,
            "lgs_pct": lgs_pct,
            "yp_pv_ratio": yp_pv_ratio
        },
        "recommendations": recommendations,
        "summary_note": summary_note
    }


@app.post("/api/well-control/kill-sheet")
def calculate_kill_sheet(data: KillSheetInput):
    current_mw = data.current_mw
    tvd = data.tvd
    sidpp = data.sidpp
    sicp = data.sicp
    slow_pump_press = data.slow_pump_press

    if tvd <= 0:
        raise HTTPException(status_code=400, detail="True Vertical Depth (TVD) must be greater than zero.")
    if current_mw <= 0:
        raise HTTPException(status_code=400, detail="Current Mud Weight must be greater than zero.")

    # Calculations:
    # Kill Mud Weight (KWM) = current_mw + (sidpp / (0.052 * tvd))
    # Initial Circulating Pressure (ICP) = slow_pump_press + sidpp
    # Final Circulating Pressure (FCP) = slow_pump_press * (kwm / current_mw)
    kwm = current_mw + (sidpp / (0.052 * tvd))
    icp = slow_pump_press + sidpp
    fcp = slow_pump_press * (kwm / current_mw)

    kick_intensity = kwm - current_mw
    initial_bhp = 0.052 * current_mw * tvd + sidpp

    instructions = [
        "1. SHUT-IN VERIFICATION: Confirm space-out, verify BOP pipe/annular rams closed, HCR valve open to choke manifold, choke fully closed. Record stabilized SIDPP and SICP.",
        f"2. KILL MUD PREPARATION: Calculate and mix Kill Mud Weight (KWM = {kwm:.2f} ppg). Ensure sufficient Barite stocks and active pit room for volume expansion.",
        f"3. ESTABLISH KILL RATE (SCR): Zero stroke counters. Slowly bring pump up to chosen kill rate while regulating choke to hold casing pressure constant at SICP ({sicp:.0f} psi).",
        f"4. DRILLPIPE PRESSURE TRACKING: Once kill rate is reached, observe Initial Circulating Pressure (ICP = {icp:.0f} psi). Maintain ICP on drillpipe gauge until kill mud arrives at bit.",
        f"5. STEP DOWN TO FCP: Follow drillpipe pressure step-down graph from ICP ({icp:.0f} psi) down to Final Circulating Pressure (FCP = {fcp:.0f} psi) as kill mud reaches bit nozzles.",
        f"6. MAINTAIN FCP TO SURFACE: Maintain FCP ({fcp:.0f} psi) constant on drillpipe gauge by adjusting choke until kill mud circulates from bit up to surface and gas/influx is completely vented.",
        f"7. SHUT-IN & FLOW CHECK: Shut down mud pumps and close choke. Confirm SIDPP = 0 psi and SICP = 0 psi. Perform flow check. Verify mud returns at {kwm:.2f} ppg before resuming operations."
    ]

    summary_note = (
        f"Well Control Kill Sheet: KWM = {kwm:.2f} ppg (+{kick_intensity:.2f} ppg intensity) | "
        f"ICP = {icp:.0f} psi | FCP = {fcp:.0f} psi | Initial BHP = {initial_bhp:.0f} psi."
    )

    return {
        "status": "success",
        "inputs": {
            "current_mw": current_mw,
            "tvd": tvd,
            "sidpp": sidpp,
            "sicp": sicp,
            "slow_pump_press": slow_pump_press
        },
        "kill_mud_weight": round(kwm, 2),
        "initial_circulating_pressure": round(icp, 1),
        "final_circulating_pressure": round(fcp, 1),
        "kwm": round(kwm, 2),
        "icp": round(icp, 1),
        "fcp": round(fcp, 1),
        "kick_intensity_ppg": round(kick_intensity, 2),
        "initial_bhp_psi": round(initial_bhp, 1),
        "instructions": instructions,
        "summary": summary_note
    }


@app.on_event("startup")
def on_startup():
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": APP_TITLE,
        "version": APP_VERSION,
        "engine": "active"
    }

@app.get("/")
def serve_index():
    candidates = [
        BASE_DIR / "app" / "templates" / "index.html",
        STATIC_DIR / "index.html"
    ]
    for index_file in candidates:
        if index_file.exists():
            return FileResponse(str(index_file))
    return {"message": "MudFlow OS API is active. Frontend index.html not yet generated."}
