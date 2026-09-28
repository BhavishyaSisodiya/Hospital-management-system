from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Integer,
    Numeric,
    String,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class InvoiceItemDB(Base):
    __tablename__ = "invoice_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_invoice_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_invoice_items_unit_price_nonnegative",
        ),
        CheckConstraint(
            "amount >= 0",
            name="ck_invoice_items_amount_nonnegative",
        ),
        Index(
            "ix_invoice_items_invoice_id",
            "invoice_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey(
            "invoices.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    invoice: Mapped["InvoiceDB"] = relationship(
        "InvoiceDB",
        back_populates="items",
    )