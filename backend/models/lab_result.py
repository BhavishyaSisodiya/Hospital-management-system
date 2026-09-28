from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class LabResultDB(Base):
    __tablename__ = "lab_results"

    __table_args__ = (
        CheckConstraint(
            "length(trim(result)) > 0",
            name="ck_lab_results_result_not_empty",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    lab_test_id: Mapped[int] = mapped_column(
        ForeignKey(
            "lab_tests.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    result: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    reference_range: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    lab_test: Mapped["LabTestDB"] = relationship(
        "LabTestDB",
        back_populates="result",
    )