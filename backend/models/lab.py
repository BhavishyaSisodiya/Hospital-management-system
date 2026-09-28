from datetime import datetime, timezone

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


class LabTestDB(Base):
    __tablename__ = "lab_tests"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'cancelled')",
            name="ck_lab_tests_status",
        ),
        Index(
            "ix_lab_tests_patient_id",
            "patient_id",
        ),
        Index(
            "ix_lab_tests_doctor_id",
            "doctor_id",
        ),
        Index(
            "ix_lab_tests_technician_id",
            "technician_id",
        ),
        Index(
            "ix_lab_tests_test_type_id",
            "test_type_id",
        ),
        Index(
            "ix_lab_tests_test_date",
            "test_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    test_type_id: Mapped[int] = mapped_column(
        ForeignKey(
            "test_types.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
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

    technician_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    test_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )

    test_type: Mapped["TestTypeDB"] = relationship(
        "TestTypeDB",
        back_populates="lab_tests",
    )

    patient: Mapped["PatientDB"] = relationship(
        "PatientDB",
        back_populates="lab_tests",
    )

    doctor: Mapped["DoctorDB"] = relationship(
        "DoctorDB",
        back_populates="lab_tests",
    )

    technician: Mapped["EmployeeDB"] = relationship(
        "EmployeeDB",
        back_populates="lab_tests",
    )

    result: Mapped["LabResultDB | None"] = relationship(
        "LabResultDB",
        back_populates="lab_test",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    prescriptions: Mapped[list["PrescriptionDB"]] = relationship(
        "PrescriptionDB",
        back_populates="lab_test",
    )