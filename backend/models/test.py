from decimal import Decimal

from sqlalchemy import (
    Integer,
    Numeric,
    String,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class TestTypeDB(Base):
    __tablename__ = "test_types"

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_test_types_name_not_empty",
        ),
        CheckConstraint(
            "price >= 0",
            name="ck_test_types_price_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    lab_tests: Mapped[list["LabTestDB"]] = relationship(
        "LabTestDB",
        back_populates="test_type",
    )