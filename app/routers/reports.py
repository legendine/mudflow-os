from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import urllib.parse

from app.database import get_db
from app.models.well import Well
from app.models.report import DailyMudReport
from app.schemas.report import (
    WellCreate, WellResponse,
    DailyMudReportCreate, DailyMudReportResponse
)
from app.services.pdf_generator import generate_daily_mud_report_pdf

router = APIRouter(prefix="/api", tags=["Daily Reports & Database"])

# --- Wells Endpoints ---
@router.get("/wells", response_model=List[WellResponse])
def get_wells(db: Session = Depends(get_db)):
    return db.query(Well).order_by(Well.id.asc()).all()

@router.post("/wells", response_model=WellResponse, status_code=status.HTTP_201_CREATED)
def create_well(payload: WellCreate, db: Session = Depends(get_db)):
    well = Well(**payload.model_dump())
    db.add(well)
    db.commit()
    db.refresh(well)
    return well

@router.get("/wells/{well_id}", response_model=WellResponse)
def get_well(well_id: int, db: Session = Depends(get_db)):
    well = db.query(Well).filter(Well.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    return well

# --- Daily Mud Reports Endpoints ---
@router.get("/reports", response_model=List[DailyMudReportResponse])
def get_reports(well_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(DailyMudReport)
    if well_id:
        query = query.filter(DailyMudReport.well_id == well_id)
    return query.order_by(DailyMudReport.report_no.desc()).all()

@router.get("/reports/{report_id}", response_model=DailyMudReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(DailyMudReport).filter(DailyMudReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Daily Mud Report not found")
    return report

@router.post("/reports", response_model=DailyMudReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(payload: DailyMudReportCreate, db: Session = Depends(get_db)):
    # Check if well exists
    well = db.query(Well).filter(Well.id == payload.well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Target well not found")
        
    report = DailyMudReport(**payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.put("/reports/{report_id}", response_model=DailyMudReportResponse)
def update_report(report_id: int, payload: DailyMudReportCreate, db: Session = Depends(get_db)):
    report = db.query(DailyMudReport).filter(DailyMudReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Daily Mud Report not found")
    
    for key, val in payload.model_dump().items():
        setattr(report, key, val)
        
    db.commit()
    db.refresh(report)
    return report

@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(DailyMudReport).filter(DailyMudReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Daily Mud Report not found")
    db.delete(report)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- PDF Export Endpoint ---
@router.get("/reports/{report_id}/pdf")
def download_report_pdf(report_id: int, db: Session = Depends(get_db)):
    report = db.query(DailyMudReport).filter(DailyMudReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Daily Mud Report not found")
        
    well = db.query(Well).filter(Well.id == report.well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Associated well not found")
        
    pdf_buffer = generate_daily_mud_report_pdf(report, well)
    
    filename = f"Daily_Mud_Report_{well.well_name.replace(' ', '_')}_Rep{report.report_no}_{report.report_date}.pdf"
    encoded_filename = urllib.parse.quote(filename)
    
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
    }
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers=headers
    )
