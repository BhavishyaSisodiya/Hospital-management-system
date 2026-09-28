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


class BedDB(Base):
    __tablename__ = "beds"

    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "bed_number",
            name="uq_beds_room_bed_number",
        ),
        CheckConstraint(
            "status IN ('available', 'occupied', 'maintenance', 'inactive')",
            name="ck_beds_status",
        ),
        Index(
            "ix_beds_room_id",
            "room_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    bed_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    room_id: Mapped[int] = mapped_column(
        ForeignKey(
            "rooms.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="available",
    )

    room: Mapped["RoomDB"] = relationship(
        "RoomDB",
        back_populates="beds",
    )

    admissions: Mapped[list["AdmissionDB"]] = relationship(
        "AdmissionDB",
        back_populates="bed",
    )