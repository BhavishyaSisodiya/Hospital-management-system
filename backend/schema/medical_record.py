from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MedicalRecordBase(BaseModel):
    patient_id: int
    doctor_id: int

    diagnosis: str = Field(
        min_length=1,
        max_length=255,
    )

    notes: str | None = None
    record_date: datetime | None = None

    @field_validator("diagnosis")
    @classmethod
    def validate_diagnosis(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Diagnosis cannot be empty."
            )

        return value


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(BaseModel):
    patient_id: int | None = None
    doctor_id: int | None = None

    diagnosis: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    notes: str | None = None
    record_date: datetime | None = None

    @field_validator("diagnosis")
    @classmethod
    def validate_diagnosis(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError(
                "Diagnosis cannot be empty."
            )

        return value


class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    diagnosis: str
    notes: str | None
    record_date: datetime

    model_config = ConfigDict(
        from_attributes=True
    )