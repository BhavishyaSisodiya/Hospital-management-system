from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    CheckConstraint,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class MedicineBatchDB(Base):
    __tablename__ = "medicine_batches"

    __table_args__ = (
        UniqueConstraint(
            "medicine_id",
            "batch_number",
            name="uq_medicine_batches_medicine_batch",
        ),
        CheckConstraint(
            "unit_cost >= 0",
            name="ck_medicine_batches_unit_cost_nonnegative",
        ),
        Index(
            "ix_medicine_batches_medicine_id",
            "medicine_id",
        ),
        Index(
            "ix_medicine_batches_expiry_date",
            "expiry_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    medicine_id: Mapped[int] = mapped_column(
        ForeignKey(
            "medicines.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    batch_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    expiry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    medicine: Mapped["MedicineDB"] = relationship(
        "MedicineDB",
        back_populates="batches",
    )

    pharmacy_stocks: Mapped[list["PharmacyStockDB"]] = relationship(
        "PharmacyStockDB",
        back_populates="batch",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )