from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# MEDICINE BATCH BASE SCHEMA
# ============================================================

class MedicineBatchBase(BaseModel):
    medicine_id: int = Field(
        ...,
        gt=0,
        description="ID of the medicine associated with this batch.",
    )

    batch_number: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique batch number for the medicine.",
    )

    expiry_date: date = Field(
        ...,
        description="Expiry date of the medicine batch.",
    )

    unit_cost: Decimal = Field(
        ...,
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
        description="Purchase cost per unit for this batch.",
    )


# ============================================================
# CREATE MEDICINE BATCH
# ============================================================

class MedicineBatchCreate(MedicineBatchBase):
    pass


# ============================================================
# UPDATE MEDICINE BATCH
# ============================================================

class MedicineBatchUpdate(BaseModel):
    medicine_id: int | None = Field(
        default=None,
        gt=0,
        description="ID of the medicine associated with this batch.",
    )

    batch_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Unique batch number for the medicine.",
    )

    expiry_date: date | None = Field(
        default=None,
        description="Expiry date of the medicine batch.",
    )

    unit_cost: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
        description="Purchase cost per unit for this batch.",
    )


# ============================================================
# MEDICINE BATCH RESPONSE
# ============================================================

class MedicineBatchResponse(MedicineBatchBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )