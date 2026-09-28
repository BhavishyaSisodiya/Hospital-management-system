from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class NurseAssignmentDB(Base):
    __tablename__ = "nurse_assignments"

    __table_args__ = (
        CheckConstraint(
            "unassigned_at IS NULL OR unassigned_at >= assigned_at",
            name="ck_nurse_assignments_dates",
        ),
        Index(
            "ix_nurse_assignments_admission_id",
            "admission_id",
        ),
        Index(
            "ix_nurse_assignments_nurse_id",
            "nurse_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    admission_id: Mapped[int] = mapped_column(
        ForeignKey(
            "admissions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    nurse_id: Mapped[int] = mapped_column(
        ForeignKey(
            "employees.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    unassigned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    admission: Mapped["AdmissionDB"] = relationship(
        "AdmissionDB",
        back_populates="nurse_assignments",
    )

    nurse: Mapped["EmployeeDB"] = relationship(
        "EmployeeDB",
        back_populates="nurse_assignments",
    )