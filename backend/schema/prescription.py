from datetime import date

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# PRESCRIPTION BASE SCHEMA
# ============================================================

class PrescriptionBase(BaseModel):
    patient_id: int = Field(
        ...,
        gt=0,
    )

    doctor_id: int | None = Field(
        default=None,
        gt=0,
    )

    pharmacy_id: int | None = Field(
        default=None,
        gt=0,
    )

    lab_test_id: int | None = Field(
        default=None,
        gt=0,
    )

    prescription_date: date


# ============================================================
# CREATE PRESCRIPTION
# ============================================================

class PrescriptionCreate(PrescriptionBase):
    test_type_id: int | None = Field(
        default=None,
        gt=0,
    )


# ============================================================
# UPDATE PRESCRIPTION
# ============================================================

class PrescriptionUpdate(BaseModel):
    patient_id: int | None = Field(
        default=None,
        gt=0,
    )

    doctor_id: int | None = Field(
        default=None,
        gt=0,
    )

    pharmacy_id: int | None = Field(
        default=None,
        gt=0,
    )

    lab_test_id: int | None = Field(
        default=None,
        gt=0,
    )

    prescription_date: date | None = None


# ============================================================
# PRESCRIPTION RESPONSE
# ============================================================

class PrescriptionResponse(PrescriptionBase):
    id: int

    doctor_id: int = Field(
        ...,
        gt=0,
    )

    model_config = ConfigDict(
        from_attributes=True,
    )