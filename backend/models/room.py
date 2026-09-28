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


class RoomDB(Base):
    __tablename__ = "rooms"

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "room_number",
            name="uq_rooms_hospital_room_number",
        ),
        CheckConstraint(
            "status IN ('available', 'occupied', 'maintenance', 'inactive')",
            name="ck_rooms_status",
        ),
        Index(
            "ix_rooms_hospital_id",
            "hospital_id",
        ),
        Index(
            "ix_rooms_department_id",
            "department_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    room_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    room_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="available",
    )

    hospital_id: Mapped[int] = mapped_column(
        ForeignKey(
            "hospitals.id",
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

    hospital: Mapped["HospitalDB"] = relationship(
        "HospitalDB",
        back_populates="rooms",
    )

    department: Mapped["DepartmentDB"] = relationship(
        "DepartmentDB",
        back_populates="rooms",
    )

    beds: Mapped[list["BedDB"]] = relationship(
        "BedDB",
        back_populates="room",
    )