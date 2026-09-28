from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class VitalBase(BaseModel):
    patient_id: int
    recorded_by: int

    recorded_at: datetime | None = None

    temperature: Decimal | None = Field(
        default=None,
        gt=0,
    )

    heart_rate: int | None = Field(
        default=None,
        gt=0,
    )

    blood_pressure_systolic: int | None = Field(
        default=None,
        gt=0,
    )

    blood_pressure_diastolic: int | None = Field(
        default=None,
        gt=0,
    )

    respiratory_rate: int | None = Field(
        default=None,
        gt=0,
    )

    oxygen_saturation: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    weight: Decimal | None = Field(
        default=None,
        gt=0,
    )


class VitalCreate(VitalBase):
    pass


class VitalUpdate(BaseModel):
    patient_id: int | None = None

    recorded_by: int | None = None

    recorded_at: datetime | None = None

    temperature: Decimal | None = Field(
        default=None,
        gt=0,
    )

    heart_rate: int | None = Field(
        default=None,
        gt=0,
    )

    blood_pressure_systolic: int | None = Field(
        default=None,
        gt=0,
    )

    blood_pressure_diastolic: int | None = Field(
        default=None,
        gt=0,
    )

    respiratory_rate: int | None = Field(
        default=None,
        gt=0,
    )

    oxygen_saturation: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    weight: Decimal | None = Field(
        default=None,
        gt=0,
    )


class VitalResponse(BaseModel):
    id: int
    patient_id: int
    recorded_by: int
    recorded_at: datetime

    temperature: Decimal | None
    heart_rate: int | None

    blood_pressure_systolic: int | None
    blood_pressure_diastolic: int | None

    respiratory_rate: int | None

    oxygen_saturation: Decimal | None
    weight: Decimal | None

    model_config = ConfigDict(
        from_attributes=True
    )