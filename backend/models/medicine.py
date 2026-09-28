from decimal import Decimal

from sqlalchemy import (
    Integer,
    Numeric,
    String,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class MedicineDB(Base):
    __tablename__ = "medicines"

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_medicines_name_not_empty",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_medicines_unit_price_nonnegative",
        ),
        Index(
            "ix_medicines_name",
            "name",
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

    manufacturer: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    batches: Mapped[list["MedicineBatchDB"]] = relationship(
        "MedicineBatchDB",
        back_populates="medicine",
    )

    prescription_items: Mapped[list["PrescriptionMedicineDB"]] = relationship(
        "PrescriptionMedicineDB",
        back_populates="medicine",
    )