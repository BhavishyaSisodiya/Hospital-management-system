from datetime import date

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class PrescriptionDB(Base):
    __tablename__ = "prescriptions"

    __table_args__ = (
        Index(
            "ix_prescriptions_patient_id",
            "patient_id",
        ),
        Index(
            "ix_prescriptions_doctor_id",
            "doctor_id",
        ),
        Index(
            "ix_prescriptions_pharmacy_id",
            "pharmacy_id",
        ),
        Index(
            "ix_prescriptions_lab_test_id",
            "lab_test_id",
        ),
        Index(
            "ix_prescriptions_date",
            "prescription_date",
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

    pharmacy_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "pharmacies.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    lab_test_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "lab_tests.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    prescription_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    patient: Mapped["PatientDB"] = relationship(
        "PatientDB",
        back_populates="prescriptions",
    )

    doctor: Mapped["DoctorDB"] = relationship(
        "DoctorDB",
        back_populates="prescriptions",
    )

    pharmacy: Mapped["PharmacyDB | None"] = relationship(
        "PharmacyDB",
        back_populates="prescriptions",
    )

    lab_test: Mapped["LabTestDB | None"] = relationship(
        "LabTestDB",
        back_populates="prescriptions",
    )

    medicines: Mapped[list["PrescriptionMedicineDB"]] = relationship(
        "PrescriptionMedicineDB",
        back_populates="prescription",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )