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


class PharmacyDB(Base):
    __tablename__ = "pharmacies"

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "name",
            name="uq_pharmacies_hospital_name",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_pharmacies_name_not_empty",
        ),
        Index(
            "ix_pharmacies_hospital_id",
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

    location: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
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
        back_populates="pharmacies",
    )

    stock: Mapped[list["PharmacyStockDB"]] = relationship(
        "PharmacyStockDB",
        back_populates="pharmacy",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    prescriptions: Mapped[list["PrescriptionDB"]] = relationship(
        "PrescriptionDB",
        back_populates="pharmacy",
    )