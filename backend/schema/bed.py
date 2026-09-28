from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


BedStatus = Literal[
    "available",
    "occupied",
    "maintenance",
    "inactive",
]


class BedBase(BaseModel):
    bed_number: str = Field(
        min_length=1,
        max_length=20,
    )

    room_id: int

    status: BedStatus = "available"

    @field_validator("bed_number")
    @classmethod
    def validate_bed_number(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Bed number cannot be empty.")

        return value


class BedCreate(BedBase):
    pass


class BedUpdate(BaseModel):
    bed_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    room_id: int | None = None

    status: BedStatus | None = None

    model_config = ConfigDict(
        extra="forbid"
    )

    @field_validator("bed_number")
    @classmethod
    def validate_bed_number(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Bed number cannot be empty.")

        return value


class BedResponse(BaseModel):
    id: int
    bed_number: str
    room_id: int
    status: BedStatus

    model_config = ConfigDict(
        from_attributes=True
    )