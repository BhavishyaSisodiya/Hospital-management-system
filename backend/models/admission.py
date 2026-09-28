from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class AdmissionDB(Base):
    __tablename__ = "admissions"

    __table_args__ = (
        CheckConstraint(
            "status IN ('admitted', 'discharged', 'cancelled')",
            name="ck_admissions_status",
        ),
        CheckConstraint(
            "discharge_date IS NULL OR discharge_date >= admission_date",
            name="ck_admissions_discharge_date",
        ),
        Index(
            "ix_admissions_patient_id",
            "patient_id",
        ),
        Index(
            "ix_admissions_doctor_id",
            "doctor_id",
        ),
        Index(
            "ix_admissions_bed_id",
            "bed_id",
        ),
        Index(
            "ix_admissions_status",
            "status",
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

    bed_id: Mapped[int] = mapped_column(
        ForeignKey(
            "beds.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    admission_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    discharge_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="admitted",
    )

    patient: Mapped["PatientDB"] = relationship(
        "PatientDB",
        back_populates="admissions",
    )

    doctor: Mapped["DoctorDB"] = relationship(
        "DoctorDB",
        back_populates="admissions",
    )

    bed: Mapped["BedDB"] = relationship(
        "BedDB",
        back_populates="admissions",
    )

    nurse_assignments: Mapped[list["NurseAssignmentDB"]] = relationship(
        "NurseAssignmentDB",
        back_populates="admission",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )