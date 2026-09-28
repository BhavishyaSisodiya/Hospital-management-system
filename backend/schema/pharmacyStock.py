from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# PHARMACY STOCK BASE SCHEMA
# ============================================================

class PharmacyStockBase(BaseModel):
    pharmacy_id: int = Field(
        ...,
        gt=0,
    )

    batch_id: int = Field(
        ...,
        gt=0,
    )

    quantity: int = Field(
        ...,
        ge=0,
    )


# ============================================================
# CREATE PHARMACY STOCK
# ============================================================

class PharmacyStockCreate(PharmacyStockBase):
    pass


# ============================================================
# UPDATE PHARMACY STOCK
# ============================================================

class PharmacyStockUpdate(BaseModel):
    quantity: int = Field(
        ...,
        ge=0,
    )


# ============================================================
# PHARMACY STOCK RESPONSE
# ============================================================

class PharmacyStockResponse(PharmacyStockBase):

    model_config = ConfigDict(
        from_attributes=True,
    )