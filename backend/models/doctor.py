from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


from database import Base

class DoctorDB(Base):
    __tablename__ = "doctors"

    __table_args__ = (
        CheckConstraint(
            "length(trim(specialization)) > 0",
            name="ck_doctors_specialization_not_empty",
        ),
        CheckConstraint(
            "experience_years IS NULL OR experience_years >= 0",
            name="ck_doctors_experience_nonnegative",
        ),
        Index(
            "ix_doctors_employee_id",
            "employee_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="RESTRICT",
        ),
        unique=True,
        nullable=False,
    )

    specialization: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    experience_years: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    employee: Mapped["EmployeeDB"] = relationship(
        "EmployeeDB",
        back_populates="doctor",
    )

    appointments: Mapped[list["AppointmentDB"]] = relationship(
        "AppointmentDB",
        back_populates="doctor",
    )

    schedules: Mapped[list["DoctorScheduleDB"]] = relationship(
        "DoctorScheduleDB",
        back_populates="doctor",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    medical_records: Mapped[list["MedicalRecordDB"]] = relationship(
        "MedicalRecordDB",
        back_populates="doctor",
    )

    admissions: Mapped[list["AdmissionDB"]] = relationship(
        "AdmissionDB",
        back_populates="doctor",
    )

    lab_tests: Mapped[list["LabTestDB"]] = relationship(
        "LabTestDB",
        back_populates="doctor",
    )

    prescriptions: Mapped[list["PrescriptionDB"]] = relationship(
        "PrescriptionDB",
        back_populates="doctor",
    )