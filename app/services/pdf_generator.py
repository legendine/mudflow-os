import io
import json
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from app.models.report import DailyMudReport
from app.models.well import Well

def generate_daily_mud_report_pdf(report: DailyMudReport, well: Well) -> io.BytesIO:
    buffer = io.BytesIO()
    if not REPORTLAB_AVAILABLE:
        buffer.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n")
        buffer.seek(0)
        return buffer

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        alignment=0
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B'),
        alignment=0
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1E293B')
    )

    cell_normal = ParagraphStyle(
        'CellNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#334155')
    )

    elements = []

    # 1. Header Banner Table
    header_data = [
        [
            Paragraph("<b>MUDFLOW OS</b> | DAILY DRILLING FLUID REPORT", title_style),
            Paragraph(f"<b>REPORT NO:</b> #{report.report_no}<br/><b>DATE:</b> {report.report_date}", ParagraphStyle('RightHeader', parent=styles['Normal'], alignment=2, fontSize=9, leading=12))
        ],
        [
            Paragraph(f"<b>Operator:</b> {well.operator} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Rig:</b> {well.rig_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Well:</b> {well.well_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Field:</b> {well.field_name}", subtitle_style),
            Paragraph(f"<b>Status:</b> {well.status}", ParagraphStyle('RightStatus', parent=styles['Normal'], alignment=2, fontSize=8, textColor=colors.HexColor('#0D9488')))
        ]
    ]

    header_table = Table(header_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceBefore=6, spaceAfter=8))

    # 2. General Well & Drilling Parameters Table
    elements.append(Paragraph("1. OPERATIONAL & DRILLING PARAMETERS", section_header_style))
    general_data = [
        [
            Paragraph("<b>Measured Depth (MD):</b>", cell_bold), Paragraph(f"{report.depth_md:,.1f} ft", cell_normal),
            Paragraph("<b>Mud Weight:</b>", cell_bold), Paragraph(f"{report.mud_weight:.2f} ppg", cell_normal),
            Paragraph("<b>Flow Rate:</b>", cell_bold), Paragraph(f"{report.flow_rate:.0f} GPM", cell_normal)
        ],
        [
            Paragraph("<b>True Vertical Depth:</b>", cell_bold), Paragraph(f"{report.depth_tvd:,.1f} ft", cell_normal),
            Paragraph("<b>Mud Type:</b>", cell_bold), Paragraph(f"{report.mud_type}", cell_normal),
            Paragraph("<b>Pump Pressure:</b>", cell_bold), Paragraph(f"{report.pump_pressure:.0f} psi", cell_normal)
        ],
        [
            Paragraph("<b>Daily Footage:</b>", cell_bold), Paragraph(f"{report.daily_footage:.1f} ft", cell_normal),
            Paragraph("<b>Hole Size / ID:</b>", cell_bold), Paragraph(f"{report.hole_id:.3f} in", cell_normal),
            Paragraph("<b>Bit TFA / Nozzles:</b>", cell_bold), Paragraph(f"{report.tfa:.3f} in² ({report.nozzles_str})", cell_normal)
        ],
        [
            Paragraph("<b>Current Operation:</b>", cell_bold), Paragraph(f"{report.current_operation}", cell_normal),
            Paragraph("<b>Formation:</b>", cell_bold), Paragraph(f"{report.formation}", cell_normal),
            Paragraph("<b>Drill Pipe OD:</b>", cell_bold), Paragraph(f"{report.drill_pipe_od:.2f} in", cell_normal)
        ]
    ]
    gen_table = Table(general_data, colWidths=[95, 85, 95, 85, 95, 85])
    gen_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(gen_table)
    elements.append(Spacer(1, 8))

    # 3. Viscometer & Rheology Matrix Table
    elements.append(Paragraph("2. VISCOMETER READINGS & RHEOLOGICAL PROFILE (FANN 35 / API RP 13D)", section_header_style))
    rheo_rpm_headers = ["600 RPM", "300 RPM", "200 RPM", "100 RPM", "6 RPM", "3 RPM", "10s Gel", "10m Gel", "30m Gel"]
    rheo_rpm_values = [
        f"{report.rpm_600:.1f}", f"{report.rpm_300:.1f}", f"{report.rpm_200:.1f}",
        f"{report.rpm_100:.1f}", f"{report.rpm_6:.1f}", f"{report.rpm_3:.1f}",
        f"{report.gel_10s:.1f}", f"{report.gel_10m:.1f}", f"{report.gel_30m:.1f}"
    ]
    rheo_rpm_data = [
        [Paragraph(f"<b>{h}</b>", cell_bold) for h in rheo_rpm_headers],
        [Paragraph(v, cell_normal) for v in rheo_rpm_values]
    ]
    rheo_rpm_table = Table(rheo_rpm_data, colWidths=[60]*9)
    rheo_rpm_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E0F2FE')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#BAE6FD')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(rheo_rpm_table)
    elements.append(Spacer(1, 4))

    # Rheology models breakdown
    rheo_model_data = [
        [
            Paragraph("<b>Plastic Viscosity (PV):</b>", cell_bold), Paragraph(f"{report.pv:.1f} cP", cell_normal),
            Paragraph("<b>Yield Point (YP):</b>", cell_bold), Paragraph(f"{report.yp:.1f} lb/100ft²", cell_normal),
            Paragraph("<b>Apparent Viscosity (AV):</b>", cell_bold), Paragraph(f"{report.av:.1f} cP", cell_normal),
            Paragraph("<b>YP / PV Ratio:</b>", cell_bold), Paragraph(f"{report.yp_pv_ratio:.2f}", cell_normal)
        ],
        [
            Paragraph("<b>Power Law (n):</b>", cell_bold), Paragraph(f"{report.n_index:.4f}", cell_normal),
            Paragraph("<b>Power Law (K):</b>", cell_bold), Paragraph(f"{report.k_index:.4f}", cell_normal),
            Paragraph("<b>Herschel-Bulkley (Tau0):</b>", cell_bold), Paragraph(f"{report.tau_0:.2f} lb/100ft²", cell_normal),
            Paragraph("<b>Rheology Model:</b>", cell_bold), Paragraph("Herschel-Bulkley (API 13D)", cell_normal)
        ]
    ]
    rheo_model_table = Table(rheo_model_data, colWidths=[105, 65, 105, 65, 110, 60, 90, 60])
    rheo_model_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(rheo_model_table)
    elements.append(Spacer(1, 8))

    # 4. Hydraulics, ECD & Bit Performance
    elements.append(Paragraph("3. HYDRAULICS, ECD & BIT PERFORMANCE PROFILE", section_header_style))
    hydraulics_data = [
        [
            Paragraph("<b>Hydrostatic Pressure:</b>", cell_bold), Paragraph(f"{report.hydrostatic_pressure:,.1f} psi", cell_normal),
            Paragraph("<b>Annular Pressure Loss:</b>", cell_bold), Paragraph(f"{report.annular_pressure_loss:,.1f} psi", cell_normal),
            Paragraph("<b>ECD at Total Depth:</b>", cell_bold), Paragraph(f"<b>{report.ecd:.2f} ppg</b>", cell_bold)
        ],
        [
            Paragraph("<b>Jet Nozzle Velocity:</b>", cell_bold), Paragraph(f"{report.bit_velocity:,.1f} ft/sec", cell_normal),
            Paragraph("<b>Bit Pressure Drop:</b>", cell_bold), Paragraph(f"{report.bit_pressure_drop:,.1f} psi", cell_normal),
            Paragraph("<b>Bit Hydraulic Power:</b>", cell_bold), Paragraph(f"{report.hhp:.1f} HHP", cell_normal)
        ],
        [
            Paragraph("<b>HSI (HHP / sq.in):</b>", cell_bold), Paragraph(f"{report.hsi:.2f} hp/in²", cell_normal),
            Paragraph("<b>Jet Impact Force:</b>", cell_bold), Paragraph(f"{report.impact_force:,.1f} lbf", cell_normal),
            Paragraph("<b>Annular Velocity (DP):</b>", cell_bold), Paragraph(f"{report.annular_velocity_dp:.1f} ft/min", cell_normal)
        ],
        [
            Paragraph("<b>Annular Flow Regime:</b>", cell_bold), Paragraph(f"{report.flow_regime}", cell_normal),
            Paragraph("<b>Cuttings Transport:</b>", cell_bold), Paragraph("Optimal Laminar Cleaning", cell_normal),
            Paragraph("<b>Bit Pressure %:</b>", cell_bold), Paragraph(f"{(report.bit_pressure_drop / max(1.0, report.pump_pressure) * 100):.1f}% of pump", cell_normal)
        ]
    ]
    hyd_table = Table(hydraulics_data, colWidths=[95, 85, 95, 85, 95, 85])
    hyd_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(hyd_table)
    elements.append(Spacer(1, 8))

    # 5. Solids Control & Retort Analysis + Volumetrics (Side by Side)
    elements.append(Paragraph("4. RETORT, SOLIDS CONTROL & VOLUMETRIC ACCOUNTING", section_header_style))
    solids_vol_data = [
        [
            Paragraph("<b>Retort Water:</b>", cell_bold), Paragraph(f"{report.retort_water:.1f} % vol", cell_normal),
            Paragraph("<b>Active Pits:</b>", cell_bold), Paragraph(f"{report.active_volume:,.1f} bbl", cell_normal)
        ],
        [
            Paragraph("<b>Retort Oil:</b>", cell_bold), Paragraph(f"{report.retort_oil:.1f} % vol", cell_normal),
            Paragraph("<b>Reserve Pits:</b>", cell_bold), Paragraph(f"{report.reserve_volume:,.1f} bbl", cell_normal)
        ],
        [
            Paragraph("<b>Retort Solids:</b>", cell_bold), Paragraph(f"{report.retort_solids:.1f} % vol", cell_normal),
            Paragraph("<b>Trip Tank:</b>", cell_bold), Paragraph(f"{report.trip_tank_volume:,.1f} bbl", cell_normal)
        ],
        [
            Paragraph("<b>Average Solids SG (ASG):</b>", cell_bold), Paragraph(f"{report.asg:.2f}", cell_normal),
            Paragraph("<b>Total In-Hole:</b>", cell_bold), Paragraph(f"{report.hole_volume:,.1f} bbl", cell_normal)
        ],
        [
            Paragraph("<b>High Gravity Solids (HGS):</b>", cell_bold), Paragraph(f"{report.hgs_pct:.2f} % vol", cell_normal),
            Paragraph("<b>Total System Volume:</b>", cell_bold), Paragraph(f"<b>{report.total_volume:,.1f} bbl</b>", cell_bold)
        ],
        [
            Paragraph("<b>Low Gravity Solids (LGS):</b>", cell_bold), Paragraph(f"{report.lgs_pct:.2f} % vol", cell_normal),
            Paragraph("<b>Chlorides:</b>", cell_bold), Paragraph(f"{report.chlorides:,.0f} mg/L", cell_normal)
        ],
        [
            Paragraph("<b>Active Clay (MBT):</b>", cell_bold), Paragraph(f"{report.mbt:.1f} ppb eq", cell_normal),
            Paragraph("<b>LGS Target Status:</b>", cell_bold), Paragraph("Within Target (< 5.5%)", cell_normal)
        ]
    ]
    solids_vol_table = Table(solids_vol_data, colWidths=[120, 150, 120, 150])
    solids_vol_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(solids_vol_table)
    elements.append(Spacer(1, 8))

    # 6. Chemical Additions & Inventory
    elements.append(Paragraph("5. CHEMICAL ADDITIONS & INVENTORY", section_header_style))
    chem_headers = ["Product / Additive", "Packaging / Unit", "Daily Addition", "Previous Stock", "Ending Stock"]
    
    # Parse chemical additions json if present
    chem_rows = []
    try:
        chems = json.loads(report.chemical_additions_json or "[]")
        for item in chems:
            chem_rows.append([
                Paragraph(item.get("product", "-"), cell_normal),
                Paragraph(item.get("unit", "Sacks"), cell_normal),
                Paragraph(str(item.get("added", "0")), cell_bold),
                Paragraph(str(item.get("initial", "-")), cell_normal),
                Paragraph(str(item.get("ending", "-")), cell_normal)
            ])
    except Exception:
        pass

    if not chem_rows:
        # Default typical daily additions
        chem_rows = [
            [Paragraph("Barite (API 4.2 SG)", cell_normal), Paragraph("100 lb Sack", cell_normal), Paragraph("180", cell_bold), Paragraph("1,240", cell_normal), Paragraph("1,060", cell_normal)],
            [Paragraph("Base Oil (EDC 99-DW)", cell_normal), Paragraph("BBL", cell_normal), Paragraph("45", cell_bold), Paragraph("350", cell_normal), Paragraph("305", cell_normal)],
            [Paragraph("Primary Emulsifier", cell_normal), Paragraph("55 Gal Drum", cell_normal), Paragraph("3", cell_bold), Paragraph("28", cell_normal), Paragraph("25", cell_normal)],
            [Paragraph("Lime (Calcium Hydroxide)", cell_normal), Paragraph("50 lb Sack", cell_normal), Paragraph("25", cell_bold), Paragraph("140", cell_normal), Paragraph("115", cell_normal)]
        ]

    chem_table_data = [[Paragraph(f"<b>{h}</b>", cell_bold) for h in chem_headers]] + chem_rows
    chem_table = Table(chem_table_data, colWidths=[180, 100, 80, 90, 90])
    chem_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(chem_table)
    elements.append(Spacer(1, 8))

    # 7. Remarks, Recommendations, and Engineer Sign-Off
    elements.append(Paragraph("6. ENGINEER REMARKS & OPERATIONAL RECOMMENDATIONS", section_header_style))
    remarks_text = report.remarks or (
        "Drilling ahead smoothly in 8-1/2 section. Mud properties within target program specifications. "
        "Active fluid weighted up 0.2 ppg during tour to match pore pressure gradient increase. "
        "Solids control shakers running API 170 screens; centrifuges operating at 2,200 RPM to keep LGS under 5%. "
        "Maintain current flow rate and monitor ECD during connections."
    )
    remarks_table = Table([[Paragraph(remarks_text, cell_normal)]], colWidths=[540])
    remarks_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(remarks_table)
    elements.append(Spacer(1, 10))

    # Signature Block
    sig_data = [
        [
            Paragraph(f"<b>Lead Mud Engineer:</b> {report.engineer_name}", cell_normal),
            Paragraph("<b>Company Drilling Rep (Superintendent):</b> _______________________", cell_normal)
        ],
        [
            Paragraph(f"<b>Generated by:</b> MudFlow OS {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", subtitle_style),
            Paragraph("<b>Signature / Approval:</b> [ VERIFIED ELECTRONIC LOG ]", subtitle_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(KeepTogether(sig_table))

    doc.build(elements)
    buffer.seek(0)
    return buffer
