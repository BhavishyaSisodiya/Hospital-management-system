from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class PrescriptionMedicineDB(Base):
    __tablename__ = "prescription_medicines"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_prescription_medicines_quantity_positive",
        ),
        CheckConstraint(
            "length(trim(dosage)) > 0",
            name="ck_prescription_medicines_dosage_not_empty",
        ),
        Index(
            "ix_prescription_medicines_medicine_id",
            "medicine_id",
        ),
    )

    prescription_id: Mapped[int] = mapped_column(
        ForeignKey(
            "prescriptions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    medicine_id: Mapped[int] = mapped_column(
        ForeignKey(
            "medicines.id",
            ondelete="RESTRICT",
        ),
        primary_key=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    dosage: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    duration: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    instructions: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    prescription: Mapped["PrescriptionDB"] = relationship(
        "PrescriptionDB",
        back_populates="medicines",
    )

    medicine: Mapped["MedicineDB"] = relationship(
        "MedicineDB",
        back_populates="prescription_items",
    )