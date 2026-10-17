import math
from typing import List, Optional
from app.schemas.hydraulics import HydraulicsInput, HydraulicsOutput

def calculate_hydraulics(data: HydraulicsInput) -> HydraulicsOutput:
    mw = max(6.0, data.mud_weight)
    tvd = max(10.0, data.tvd)
    md = max(tvd, data.md)
    q = max(1.0, data.flow_rate)
    hole_id = max(3.0, data.hole_id)
    dp_od = min(hole_id - 0.25, max(2.375, data.drill_pipe_od))
    dc_od = min(hole_id - 0.1, max(3.5, data.drill_collar_od))
    pv = max(1.0, data.pv or 20.0)
    yp = max(0.0, data.yp or 15.0)
    p_pump = max(100.0, data.pump_pressure or 3000.0)

    # 1. Hydrostatic Pressure: P_hyd = 0.052 * MW * TVD (psi)
    p_hyd = 0.052 * mw * tvd

    # 2. Annular Velocities
    # AV = 24.5 * Q / (ID^2 - OD^2)  [ft/min]
    diff_dp = max(0.5, (hole_id ** 2) - (dp_od ** 2))
    av_dp = (24.5 * q) / diff_dp

    diff_dc = max(0.2, (hole_id ** 2) - (dc_od ** 2))
    av_dc = (24.5 * q) / diff_dc

    # 3. Annular Pressure Loss Calculation
    # If not provided, calculate using Bingham plastic annular friction model
    annular_clearance = hole_id - dp_od
    if data.annular_pressure_loss is not None and data.annular_pressure_loss > 0:
        p_ann = data.annular_pressure_loss
    else:
        # Field formula: dP/dL = (PV * AV / 60000 / (ID - OD)^2) + (YP / 200 / (ID - OD))
        grad = ((pv * av_dp) / (60000.0 * (annular_clearance ** 2))) + (yp / (200.0 * annular_clearance))
        p_ann = max(10.0, grad * md)

    # 4. Equivalent Circulating Density (ECD)
    # ECD = MW + (dP_ann / (0.052 * TVD))
    ecd = mw + (p_ann / (0.052 * tvd))

    # 5. Bit Nozzle Hydraulics
    nozzle_list = data.nozzles if data.nozzles and len(data.nozzles) > 0 else [14, 14, 14]
    
    # TFA (in^2) = sum(N_i^2) / 1303.8
    sum_sq = sum(float(n) ** 2 for n in nozzle_list)
    tfa = max(0.05, sum_sq / 1303.8)

    # Jet Nozzle Velocity: Vn = Q / (3.117 * TFA)  [ft/sec]
    v_n = q / (3.117 * tfa)

    # Bit Pressure Drop: dP_b = (MW * Q^2) / (10858 * TFA^2)  [psi]
    # (Assuming discharge coefficient Cd = 0.95: 11140 * 0.95^2 approx 10858)
    dp_bit = (mw * (q ** 2)) / (10858.0 * (tfa ** 2))

    # Bit Hydraulic Horsepower: HHP = (dP_bit * Q) / 1714  [hp]
    hhp = (dp_bit * q) / 1714.0

    # HSI = HHP / (pi/4 * BitSize^2)  [hp / in^2]
    bit_area = (math.pi / 4.0) * (hole_id ** 2)
    hsi = hhp / bit_area if bit_area > 0 else 0.0

    # Jet Impact Force: IF = (MW * Q * Vn) / 1930  [lbf]
    impact_force = (mw * q * v_n) / 1930.0

    # 6. Flow Regime in Annulus
    # Effective viscosity in annulus (cP)
    mu_e = pv + (300.0 * yp * annular_clearance / av_dp) if av_dp > 0 else pv
    # Annular Reynolds Number
    re = (2.96 * mw * av_dp * annular_clearance) / mu_e if mu_e > 0 else 1000.0

    # Critical Velocity (ft/min)
    inside_sqrt = max(0.0, (pv ** 2) + 8.2 * mw * (annular_clearance ** 2) * yp)
    v_c = (97.0 * pv + 97.0 * math.sqrt(inside_sqrt)) / (mw * annular_clearance)

    if re < 2100 or av_dp < v_c:
        flow_regime = "Laminar Flow (Optimal Wellbore Stability)"
    elif re <= 3200:
        flow_regime = "Transitional Flow (Monitor Hole Erosion)"
    else:
        flow_regime = "Turbulent Flow (High Erosion & Surge Risk)"

    # Bit Pressure Percentage vs Pump
    pct_bit = min(100.0, (dp_bit / p_pump) * 100.0)

    # Hole Cleaning Assessment
    if av_dp >= 140.0:
        hole_cleaning_status = "Excellent Cutting Transport (>140 ft/min)"
    elif av_dp >= 110.0:
        hole_cleaning_status = "Adequate Cutting Transport (110 - 140 ft/min)"
    else:
        hole_cleaning_status = "Sub-optimal Annular Velocity (<110 ft/min, Cuttings Bed Risk)"

    return HydraulicsOutput(
        hydrostatic_pressure=round(p_hyd, 1),
        annular_pressure_loss=round(p_ann, 1),
        ecd=round(ecd, 2),
        annular_velocity_dp=round(av_dp, 1),
        annular_velocity_dc=round(av_dc, 1),
        tfa=round(tfa, 3),
        bit_velocity=round(v_n, 1),
        bit_pressure_drop=round(dp_bit, 1),
        hhp=round(hhp, 1),
        hsi=round(hsi, 2),
        impact_force=round(impact_force, 1),
        reynolds_number=round(re, 0),
        flow_regime=flow_regime,
        percent_pressure_at_bit=round(pct_bit, 1),
        hole_cleaning_status=hole_cleaning_status
    )
