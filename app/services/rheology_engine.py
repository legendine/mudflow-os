import math
from typing import List, Dict, Tuple
from app.schemas.rheology import RheologyInput, RheologyOutput, RheologyCurvePoint

# Standard viscometer RPMs and their exact shear rates (sec^-1)
# Factor: 1 RPM = 1.7034 sec^-1
RPM_MAP = {
    600: 1022.04,
    300: 511.02,
    200: 340.68,
    100: 170.34,
    6: 10.22,
    3: 5.11
}

# 1 dial degree (deg) = 1.066 lb / 100 sq ft = 0.511 Pa
DIAL_TO_FIELD_STRESS = 1.066

def calculate_rheology(data: RheologyInput) -> RheologyOutput:
    r600 = max(0.0, data.rpm_600)
    r300 = max(0.0, data.rpm_300)
    r200 = max(0.0, data.rpm_200)
    r100 = max(0.0, data.rpm_100)
    r6 = max(0.0, data.rpm_6)
    r3 = max(0.0, data.rpm_3)

    # 1. Bingham Plastic Model
    # PV = R600 - R300 (cP)
    pv = max(0.0, r600 - r300)
    # YP = R300 - PV = 2*R300 - R600 (lb/100 ft2)
    yp = max(0.0, r300 - pv)
    # AV = R600 / 2 (cP)
    av = r600 / 2.0
    yp_pv_ratio = (yp / pv) if pv > 0 else 0.0

    # 2. Power Law Model (Ostwald-de Waele)
    # n = 3.322 * log10(R600 / R300)
    if r300 > 0 and r600 > 0:
        n_index = 3.3219 * math.log10(r600 / r300)
        # K = 511 * R300 / 511^n (or in field units lb*s^n / 100 ft2)
        # In field units: tau = K * gamma^n. At gamma=511, tau=R300*1.066
        k_index = (r300 * DIAL_TO_FIELD_STRESS) / (511.02 ** n_index) if n_index > 0 else 0.0
    else:
        n_index = 0.8
        k_index = 0.5

    # 3. Herschel-Bulkley (Yield Power Law, API RP 13D)
    # Tau = Tau_0 + K_hb * gamma^n_hb
    # Tau_0 estimation via API 13D formula: Tau_0 = 2*R3 - R6 (in dial units, then * 1.066)
    tau_0_dial = 2.0 * r3 - r6
    if tau_0_dial < 0 or r3 == 0:
        tau_0_dial = max(0.0, r3 * 0.75)
    
    # If tau_0_dial >= r300, clamp it so log is valid
    if tau_0_dial >= r300:
        tau_0_dial = max(0.0, r300 * 0.4)

    tau_0_field = tau_0_dial * DIAL_TO_FIELD_STRESS

    # Calculate n_hb and K_hb
    num = r600 - tau_0_dial
    den = r300 - tau_0_dial
    if num > 0 and den > 0 and num > den:
        n_hb = 3.3219 * math.log10(num / den)
    else:
        n_hb = max(0.2, n_index * 0.9)

    # Consistency factor K_hb (lb*s^n / 100 ft2)
    k_hb = ((r300 - tau_0_dial) * DIAL_TO_FIELD_STRESS) / (511.02 ** n_hb) if n_hb > 0 else 0.1

    # 4. Gel Strength Analysis
    g10s = data.gel_10s
    g10m = data.gel_10m
    g30m = data.gel_30m

    if g30m >= 2.5 * max(1.0, g10s) and g10m >= 1.8 * max(1.0, g10s):
        gel_structure_type = "Progressive (High Sag / Swab Risk)"
    elif (g30m - g10s <= 5.0) and (g10m - g10s <= 3.0):
        gel_structure_type = "Flat / Stable (Optimal for Thixotropy)"
    else:
        gel_structure_type = "Moderate Thixotropic (Normal)"

    # 5. Measure vs Models Goodness of Fit (R^2)
    # Gather actual points
    data_points = [
        (3, RPM_MAP[3], r3 * DIAL_TO_FIELD_STRESS),
        (6, RPM_MAP[6], r6 * DIAL_TO_FIELD_STRESS),
        (100, RPM_MAP[100], r100 * DIAL_TO_FIELD_STRESS),
        (200, RPM_MAP[200], r200 * DIAL_TO_FIELD_STRESS),
        (300, RPM_MAP[300], r300 * DIAL_TO_FIELD_STRESS),
        (600, RPM_MAP[600], r600 * DIAL_TO_FIELD_STRESS),
    ]

    # Filter out 0 readings if not entered
    valid_points = [p for p in data_points if p[2] > 0]
    if not valid_points:
        valid_points = data_points

    mean_measured = sum(p[2] for p in valid_points) / len(valid_points)
    ss_tot = sum((p[2] - mean_measured) ** 2 for p in valid_points) or 1.0

    def bingham_predict(gamma: float) -> float:
        # field units: tau = YP + PV * (gamma / 1022.04 * 1.066)
        # In field units, PV (cP) * gamma / 478.8 = lb/100ft2
        return yp + (pv * gamma * 0.002088)

    def powerlaw_predict(gamma: float) -> float:
        return k_index * (gamma ** n_index)

    def hb_predict(gamma: float) -> float:
        return tau_0_field + k_hb * (gamma ** n_hb)

    ss_res_bp = sum((p[2] - bingham_predict(p[1])) ** 2 for p in valid_points)
    ss_res_pl = sum((p[2] - powerlaw_predict(p[1])) ** 2 for p in valid_points)
    ss_res_hb = sum((p[2] - hb_predict(p[1])) ** 2 for p in valid_points)

    r2_bingham = max(0.0, min(0.999, 1.0 - (ss_res_bp / ss_tot)))
    r2_powerlaw = max(0.0, min(0.999, 1.0 - (ss_res_pl / ss_tot)))
    r2_hb = max(0.0, min(0.999, 1.0 - (ss_res_hb / ss_tot)))

    # 6. Generate curve points for Chart.js rendering
    # Include all 6 measured RPM points plus intermediate points for smooth curve
    rpms_for_curve = [3, 6, 20, 50, 100, 150, 200, 250, 300, 400, 500, 600]
    measured_dict = {
        3: r3 * DIAL_TO_FIELD_STRESS,
        6: r6 * DIAL_TO_FIELD_STRESS,
        100: r100 * DIAL_TO_FIELD_STRESS,
        200: r200 * DIAL_TO_FIELD_STRESS,
        300: r300 * DIAL_TO_FIELD_STRESS,
        600: r600 * DIAL_TO_FIELD_STRESS,
    }

    curve_data: List[RheologyCurvePoint] = []
    for rpm in rpms_for_curve:
        gamma = rpm * 1.7034
        m_stress = measured_dict.get(rpm, -1.0)
        curve_data.append(
            RheologyCurvePoint(
                rpm=float(rpm),
                shear_rate=round(gamma, 2),
                measured_stress=round(m_stress, 2) if m_stress >= 0 else -1.0,
                bingham_stress=round(bingham_predict(gamma), 2),
                powerlaw_stress=round(powerlaw_predict(gamma), 2),
                herschel_bulkley_stress=round(hb_predict(gamma), 2),
            )
        )

    return RheologyOutput(
        pv=round(pv, 2),
        yp=round(yp, 2),
        av=round(av, 2),
        yp_pv_ratio=round(yp_pv_ratio, 2),
        n_index=round(n_index, 4),
        k_index=round(k_index, 4),
        tau_0_hb=round(tau_0_field, 2),
        n_hb=round(n_hb, 4),
        k_hb=round(k_hb, 4),
        gel_10s=round(g10s, 1),
        gel_10m=round(g10m, 1),
        gel_30m=round(g30m, 1),
        gel_structure_type=gel_structure_type,
        r2_bingham=round(r2_bingham, 3),
        r2_powerlaw=round(r2_powerlaw, 3),
        r2_hb=round(r2_hb, 3),
        curve_data=curve_data
    )
