from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Well(Base):
    __tablename__ = "wells"

    id = Column(Integer, primary_key=True, index=True)
    well_name = Column(String(100), nullable=False)
    operator = Column(String(100), default="Equinor Energy")
    rig_name = Column(String(100), default="Deepsea Nordkapp")
    field_name = Column(String(100), default="Johan Castberg")
    country = Column(String(50), default="Norway")
    spud_date = Column(String(20), default="2026-08-15")
    target_depth = Column(Float, default=14500.0)
    well_type = Column(String(50), default="Exploration / HPHT")
    status = Column(String(50), default="Active Drilling")
    created_at = Column(DateTime, default=datetime.utcnow)

    reports = relationship("DailyMudReport", back_populates="well", cascade="all, delete-orphan")
