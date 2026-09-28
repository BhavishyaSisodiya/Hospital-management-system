from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class InvoiceDB(Base):
    __tablename__ = "invoices"

    __table_args__ = (
        CheckConstraint(
            "status IN ('unpaid', 'partially_paid', 'paid', 'cancelled')",
            name="ck_invoices_status",
        ),
        Index(
            "ix_invoices_patient_id",
            "patient_id",
        ),
        Index(
            "ix_invoices_invoice_date",
            "invoice_date",
        ),
        Index(
            "ix_invoices_status",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "patients.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    invoice_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="unpaid",
    )

    patient: Mapped["PatientDB"] = relationship(
        "PatientDB",
        back_populates="invoices",
    )

    items: Mapped[list["InvoiceItemDB"]] = relationship(
        "InvoiceItemDB",
        back_populates="invoice",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    payments: Mapped[list["PaymentDB"]] = relationship(
        "PaymentDB",
        back_populates="invoice",
    )