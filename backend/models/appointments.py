from datetime import date, time

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    String,
    Time,
    CheckConstraint,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class AppointmentDB(Base):
    __tablename__ = "appointments"

    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "appointment_date",
            "appointment_time",
            name="uq_appointments_doctor_datetime",
        ),
        CheckConstraint(
            "status IN ('scheduled', 'completed', 'cancelled', 'no_show')",
            name="ck_appointments_status",
        ),
        Index(
            "ix_appointments_patient_id",
            "patient_id",
        ),
        Index(
            "ix_appointments_doctor_date",
            "doctor_id",
            "appointment_date",
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

    appointment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    appointment_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="scheduled",
    )

    patient: Mapped["PatientDB"] = relationship(
        "PatientDB",
        back_populates="appointments",
    )

    doctor: Mapped["DoctorDB"] = relationship(
        "DoctorDB",
        back_populates="appointments",
    )