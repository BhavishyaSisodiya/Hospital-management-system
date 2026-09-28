from datetime import date

from sqlalchemy import (
    Date,
    Integer,
    String,
    CheckConstraint,
    Index,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class PatientDB(Base):
    __tablename__ = "patients"

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_patients_name_not_empty",
        ),
        Index(
            "ix_patients_phone",
            "phone",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    gender: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True,
        index=True
    )

    appointments: Mapped[list["AppointmentDB"]] = relationship(
        "AppointmentDB",
        back_populates="patient",
    )

    medical_records: Mapped[list["MedicalRecordDB"]] = relationship(
        "MedicalRecordDB",
        back_populates="patient",
    )

    vitals: Mapped[list["VitalDB"]] = relationship(
        "VitalDB",
        back_populates="patient",
    )

    admissions: Mapped[list["AdmissionDB"]] = relationship(
        "AdmissionDB",
        back_populates="patient",
    )

    lab_tests: Mapped[list["LabTestDB"]] = relationship(
        "LabTestDB",
        back_populates="patient",
    )

    prescriptions: Mapped[list["PrescriptionDB"]] = relationship(
        "PrescriptionDB",
        back_populates="patient",
    )

    invoices: Mapped[list["InvoiceDB"]] = relationship(
        "InvoiceDB",
        back_populates="patient",
    )
    user:Mapped["UserDB"]=relationship(
        "UserDB",
        back_populates="patient"
    )