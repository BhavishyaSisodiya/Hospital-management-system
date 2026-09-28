from sqlalchemy import Column, Integer, DateTime, ForeignKey
from database import Base
from datetime import datetime


class LabTestDB(Base):
    __tablename__ = "lab_tests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    test_type_id = Column(
        Integer,
        ForeignKey("test_types.id"),
        nullable=False
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False
    )

    technician_id = Column(
        Integer,
        ForeignKey("lab_technicians.id"),
        nullable=False
    )

    test_date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )