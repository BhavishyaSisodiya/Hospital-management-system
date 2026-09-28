from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    CheckConstraint,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class DepartmentDB(Base):
    __tablename__ = "departments"

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "name",
            name="uq_departments_hospital_name",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_departments_name_not_empty",
        ),
        Index(
            "ix_departments_hospital_id",
            "hospital_id",
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

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    hospital_id: Mapped[int] = mapped_column(
        ForeignKey(
            "hospitals.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    hospital: Mapped["HospitalDB"] = relationship(
        "HospitalDB",
        back_populates="departments",
    )

    employees: Mapped[list["EmployeeDB"]] = relationship(
        "EmployeeDB",
        back_populates="department",
    )

    rooms: Mapped[list["RoomDB"]] = relationship(
        "RoomDB",
        back_populates="department",
    )