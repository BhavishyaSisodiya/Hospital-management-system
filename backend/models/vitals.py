from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class VitalDB(Base):
    __tablename__ = "vitals"

    __table_args__ = (
        CheckConstraint(
            "temperature IS NULL OR temperature > 0",
            name="ck_vitals_temperature_positive",
        ),
        CheckConstraint(
            "heart_rate IS NULL OR heart_rate > 0",
            name="ck_vitals_heart_rate_positive",
        ),
        CheckConstraint(
            "blood_pressure_systolic IS NULL OR blood_pressure_systolic > 0",
            name="ck_vitals_bp_systolic_positive",
        ),
        CheckConstraint(
            "blood_pressure_diastolic IS NULL OR blood_pressure_diastolic > 0",
            name="ck_vitals_bp_diastolic_positive",
        ),
        CheckConstraint(
            "respiratory_rate IS NULL OR respiratory_rate > 0",
            name="ck_vitals_respiratory_rate_positive",
        ),
        CheckConstraint(
            "oxygen_saturation IS NULL OR "
            "(oxygen_saturation >= 0 AND oxygen_saturation <= 100)",
            name="ck_vitals_oxygen_saturation",
        ),
        CheckConstraint(
            "weight IS NULL OR weight > 0",
            name="ck_vitals_weight_positive",
        ),
        Index(
            "ix_vitals_patient_recorded_at",
            "patient_id",
            "recorded_at",
        ),
        Index(
            "ix_vitals_recorded_by",
            "recorded_by",
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

    recorded_by: Mapped[int] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    temperature: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )

    heart_rate: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    blood_pressure_systolic: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    blood_pressure_diastolic: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    respiratory_rate: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    oxygen_saturation: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    weight: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    patient: Mapped["PatientDB"] = relationship(
        "PatientDB",
        back_populates="vitals",
    )

    recorded_by_employee: Mapped["EmployeeDB"] = relationship(
        "EmployeeDB",
        back_populates="vitals_recorded",
    )