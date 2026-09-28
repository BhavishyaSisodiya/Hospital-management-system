from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# PHARMACY BASE SCHEMA
# ============================================================

class PharmacyBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    location: str = Field(
        ...,
        min_length=1,
        max_length=150,
    )

    hospital_id: int = Field(
        ...,
        gt=0,
    )


# ============================================================
# CREATE PHARMACY
# ============================================================

class PharmacyCreate(PharmacyBase):
    pass


# ============================================================
# UPDATE PHARMACY
# ============================================================

class PharmacyUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    location: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    hospital_id: int | None = Field(
        default=None,
        gt=0,
    )


# ============================================================
# PHARMACY RESPONSE
# ============================================================

class PharmacyResponse(PharmacyBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )