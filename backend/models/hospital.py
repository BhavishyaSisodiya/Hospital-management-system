from sqlalchemy import (
    Integer,
    String,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class HospitalDB(Base):
    __tablename__ = "hospitals"

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_hospitals_name_not_empty",
        ),
        CheckConstraint(
            "length(trim(address)) > 0",
            name="ck_hospitals_address_not_empty",
        ),
        Index(
            "ix_hospitals_name",
            "name",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    departments: Mapped[list["DepartmentDB"]] = relationship(
        "DepartmentDB",
        back_populates="hospital",
    )

    rooms: Mapped[list["RoomDB"]] = relationship(
        "RoomDB",
        back_populates="hospital",
    )

    pharmacies: Mapped[list["PharmacyDB"]] = relationship(
        "PharmacyDB",
        back_populates="hospital",
    )