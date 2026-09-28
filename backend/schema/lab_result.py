from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class LabResultBase(BaseModel):
    lab_test_id: int

    result: str = Field(
        min_length=1,
    )

    unit: str | None = Field(
        default=None,
        max_length=50,
    )

    reference_range: str | None = Field(
        default=None,
        max_length=100,
    )

    remarks: str | None = None

    reported_at: datetime | None = None

    @field_validator("result")
    @classmethod
    def validate_result(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Result cannot be empty.")

        return value


class LabResultCreate(BaseModel):
    lab_test_id: int

    result: str = Field(
        min_length=1,
    )

    unit: str | None = Field(
        default=None,
        max_length=50,
    )

    reference_range: str | None = Field(
        default=None,
        max_length=100,
    )

    remarks: str | None = None

    reported_at: datetime | None = None

    @field_validator("result")
    @classmethod
    def validate_result(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Result cannot be empty.")

        return value


class LabResultUpdate(BaseModel):
    lab_test_id: int | None = None

    result: str | None = Field(
        default=None,
        min_length=1,
    )

    unit: str | None = Field(
        default=None,
        max_length=50,
    )

    reference_range: str | None = Field(
        default=None,
        max_length=100,
    )

    remarks: str | None = None

    reported_at: datetime | None = None

    model_config = ConfigDict(
        extra="forbid",
    )

    @field_validator("result")
    @classmethod
    def validate_result(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Result cannot be empty.")

        return value


class LabResultResponse(BaseModel):
    id: int
    lab_test_id: int
    result: str
    unit: str | None
    reference_range: str | None
    remarks: str | None
    reported_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )