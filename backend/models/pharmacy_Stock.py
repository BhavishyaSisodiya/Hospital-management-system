from sqlalchemy import (
    ForeignKey,
    Integer,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class PharmacyStockDB(Base):
    __tablename__ = "pharmacy_stock"

    __table_args__ = (
        CheckConstraint(
            "quantity >= 0",
            name="ck_pharmacy_stock_quantity_nonnegative",
        ),
        Index(
            "ix_pharmacy_stock_batch_id",
            "batch_id",
        ),
    )

    pharmacy_id: Mapped[int] = mapped_column(
        ForeignKey(
            "pharmacies.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    batch_id: Mapped[int] = mapped_column(
        ForeignKey(
            "medicine_batches.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    pharmacy: Mapped["PharmacyDB"] = relationship(
        "PharmacyDB",
        back_populates="stock",
    )

    batch: Mapped["MedicineBatchDB"] = relationship(
        "MedicineBatchDB",
        back_populates="pharmacy_stocks",
    )