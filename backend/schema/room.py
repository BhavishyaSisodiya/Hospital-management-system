from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


RoomStatus = Literal[
    "available",
    "occupied",
    "maintenance",
    "inactive",
]


class RoomBase(BaseModel):
    room_number: str = Field(
        min_length=1,
        max_length=20,
    )

    room_type: str = Field(
        min_length=1,
        max_length=50,
    )

    status: RoomStatus = "available"

    hospital_id: int

    department_id: int

    @field_validator("room_number", "room_type")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty.")

        return value


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    room_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    status: RoomStatus | None = None

    hospital_id: int | None = None

    department_id: int | None = None

    model_config = ConfigDict(
        extra="forbid"
    )

    @field_validator("room_number", "room_type")
    @classmethod
    def validate_text_fields(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty.")

        return value


class RoomResponse(BaseModel):
    id: int
    room_number: str
    room_type: str
    status: RoomStatus
    hospital_id: int
    department_id: int

    model_config = ConfigDict(
        from_attributes=True
    )