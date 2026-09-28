from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class EmployeeDB(Base):
    __tablename__ = "employees"

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_employees_name_not_empty",
        ),
        CheckConstraint(
            "salary IS NULL OR salary >= 0",
            name="ck_employees_salary_nonnegative",
        ),
        CheckConstraint(
            "employment_status IN ('active', 'inactive', 'on_leave', 'terminated')",
            name="ck_employees_status",
        ),
       
        Index(
            "ix_employees_role_id",
            "role_id",
        ),
        Index(
            "ix_employees_department_id",
            "department_id",
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

    role_id: Mapped[int] = mapped_column(
        ForeignKey(
            "roles.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey(
            "departments.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    dob: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(150),
        unique=True,
        nullable=True,
        index=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    hire_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    salary: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )


    employment_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    role: Mapped["RoleDB"] = relationship(
        "RoleDB",
        back_populates="employees",
    )

    department: Mapped["DepartmentDB"] = relationship(
        "DepartmentDB",
        back_populates="employees",
    )

    doctor: Mapped["DoctorDB | None"] = relationship(
        "DoctorDB",
        back_populates="employee",
        uselist=False,
    )

    lab_tests: Mapped[list["LabTestDB"]] = relationship(
        "LabTestDB",
        back_populates="technician",
    )

    vitals_recorded: Mapped[list["VitalDB"]] = relationship(
        "VitalDB",
        back_populates="recorded_by_employee",
    )

    nurse_assignments: Mapped[list["NurseAssignmentDB"]] = relationship(
        "NurseAssignmentDB",
        back_populates="nurse",
    )