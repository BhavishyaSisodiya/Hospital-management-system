from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class MedicalRecordDB(Base):
    __tablename__ = "medical_records"

    __table_args__ = (
        CheckConstraint(
            "length(trim(diagnosis)) > 0",
            name="ck_medical_records_diagnosis_not_empty",
        ),
        Index(
            "ix_medical_records_patient_id",
            "patient_id",
        ),
        Index(
            "ix_medical_records_doctor_id",
            "doctor_id",
        ),
        Index(
            "ix_medical_records_record_date",
            "record_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "patients.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey(
            "doctors.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    diagnosis: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    record_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    patient: Mapped["PatientDB"] = relationship(
        "PatientDB",
        back_populates="medical_records",
    )

    doctor: Mapped["DoctorDB"] = relationship(
        "DoctorDB",
        back_populates="medical_records",
    )