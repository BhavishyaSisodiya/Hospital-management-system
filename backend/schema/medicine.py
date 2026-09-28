from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# MEDICINE BASE SCHEMA
# ============================================================

class MedicineBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    manufacturer: str | None = Field(
        default=None,
        max_length=100,
    )

    unit_price: Decimal = Field(
        ...,
        ge=Decimal("0.00"),
        decimal_places=2,
        max_digits=10,
    )


# ============================================================
# CREATE MEDICINE
# ============================================================

class MedicineCreate(MedicineBase):
    pass


# ============================================================
# UPDATE MEDICINE
# ============================================================

class MedicineUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    manufacturer: str | None = Field(
        default=None,
        max_length=100,
    )

    unit_price: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        decimal_places=2,
        max_digits=10,
    )


# ============================================================
# MEDICINE RESPONSE
# ============================================================

class MedicineResponse(MedicineBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )

