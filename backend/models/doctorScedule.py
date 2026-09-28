from datetime import time

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Time,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class DoctorScheduleDB(Base):
    __tablename__ = "doctor_schedules"

    __table_args__ = (
        CheckConstraint(
            "day_of_week IN ('monday', 'tuesday', 'wednesday', "
            "'thursday', 'friday', 'saturday', 'sunday')",
            name="ck_doctor_schedules_day",
        ),
        CheckConstraint(
            "end_time > start_time",
            name="ck_doctor_schedules_time",
        ),
        Index(
            "ix_doctor_schedules_doctor_id",
            "doctor_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey(
            "doctors.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    day_of_week: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    doctor: Mapped["DoctorDB"] = relationship(
        "DoctorDB",
        back_populates="schedules",
    )