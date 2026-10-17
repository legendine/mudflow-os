from app.schemas.solids import RetortInput, RetortOutput

def analyze_solids(data: RetortInput) -> RetortOutput:
    vw = max(0.0, min(100.0, data.water_pct))
    vo = max(0.0, min(100.0, data.oil_pct))
    
    if data.solids_pct is not None and data.solids_pct > 0:
        vs = data.solids_pct
    else:
        vs = max(0.0, 100.0 - (vw + vo))
        
    mw = data.mud_weight
    oil_sg = data.oil_sg or 0.84
    oil_density = oil_sg * 8.337
    water_density = 8.337
    
    # 1. Oil Water Ratio (OWR)
    liquid_total = vo + vw
    if liquid_total > 0 and vo > 0:
        oil_ratio = round((vo / liquid_total) * 100.0)
        water_ratio = 100 - oil_ratio
        owr_str = f"{oil_ratio}/{water_ratio}"
    elif vo == 0 and vw > 0:
        owr_str = "0/100 (WBM)"
    else:
        owr_str = "N/A"
        
    # 2. Average Specific Gravity of Solids (ASG)
    # Weight of 1 gallon of liquid
    w_water = (vw / 100.0) * water_density
    w_oil = (vo / 100.0) * oil_density
    w_liquid = w_water + w_oil
    w_solids = max(0.0, mw - w_liquid)
    
    solids_fraction = max(0.001, vs / 100.0)
    asg = w_solids / (solids_fraction * water_density)
    asg = max(2.60, min(4.35, asg))
    
    # 3. High Gravity Solids (HGS) and Low Gravity Solids (LGS) Partitioning
    # Standard: Barite SG = 4.20, LGS SG = 2.60
    # %HGS = %S * (ASG - 2.60) / (4.20 - 2.60)
    denom = 4.20 - 2.60
    hgs_pct = vs * max(0.0, (asg - 2.60)) / denom
    hgs_pct = max(0.0, min(vs, hgs_pct))
    lgs_pct = max(0.0, vs - hgs_pct)
    
    # Pounds per barrel: ppb = %vol * SG * 3.5
    hgs_ppb = hgs_pct * 4.20 * 3.5
    lgs_ppb = lgs_pct * 2.60 * 3.5
    
    # 4. Active Clay Concentration from MBT (Methylene Blue Test)
    # MBT is in ppb bentonite equivalent
    # Active clay % vol = MBT / (2.60 * 3.5) = MBT / 9.1
    mbt = max(0.0, data.mbt_ppb)
    active_clay_pct = mbt / 9.1
    active_clay_pct = min(lgs_pct, active_clay_pct)
    inactive_solids_pct = max(0.0, lgs_pct - active_clay_pct)
    active_clay_ratio = (active_clay_pct / lgs_pct) if lgs_pct > 0 else 0.0
    
    # 5. Engineering Assessment & Recommendations
    excess_lgs = lgs_pct > 5.5
    if lgs_pct > 7.0:
        lgs_recommendation = (
            f"CRITICAL: LGS is elevated at {round(lgs_pct, 1)}% vol (>7% threshold). "
            f"Run decanting centrifuges at maximum G-force and initiate base fluid dilution to protect ROP and prevent stuck pipe."
        )
        solids_efficiency = "Poor (Drill solids accumulation active)"
    elif lgs_pct > 5.0:
        lgs_recommendation = (
            f"WARNING: LGS is {round(lgs_pct, 1)}% vol. Optimize shaker screen meshes (switch to API 170/200) "
            f"and verify desilter / desander underflow to avoid rheological thickening."
        )
        solids_efficiency = "Fair (Centrifuge processing recommended)"
    else:
        lgs_recommendation = (
            f"OPTIMAL: LGS maintained at {round(lgs_pct, 1)}% vol (well below 5% target). "
            f"Solids control equipment operating with high efficiency."
        )
        solids_efficiency = "Excellent (Solids within target window)"
        
    return RetortOutput(
        water_pct=round(vw, 1),
        oil_pct=round(vo, 1),
        total_solids_pct=round(vs, 1),
        oil_water_ratio=owr_str,
        asg=round(asg, 2),
        hgs_pct=round(hgs_pct, 2),
        lgs_pct=round(lgs_pct, 2),
        hgs_ppb=round(hgs_ppb, 1),
        lgs_ppb=round(lgs_ppb, 1),
        active_clay_pct=round(active_clay_pct, 2),
        active_clay_ppb=round(mbt, 1),
        inactive_drill_solids_pct=round(inactive_solids_pct, 2),
        active_clay_ratio=round(active_clay_ratio, 2),
        excess_lgs=excess_lgs,
        lgs_recommendation=lgs_recommendation,
        solids_control_efficiency=solids_efficiency
    )
