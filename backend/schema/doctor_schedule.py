from datetime import time

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


VALID_DAYS = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}


class DoctorScheduleBase(BaseModel):
    doctor_id: int

    day_of_week: str = Field(
        min_length=1,
        max_length=10,
    )

    start_time: time
    end_time: time

    @field_validator("day_of_week")
    @classmethod
    def validate_day_of_week(cls, value: str) -> str:
        value = value.strip().lower()

        if value not in VALID_DAYS:
            raise ValueError(
                "day_of_week must be a valid day from Monday to Sunday"
            )

        return value

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError(
                "end_time must be later than start_time"
            )

        return self


class DoctorScheduleCreate(DoctorScheduleBase):
    pass


class DoctorScheduleUpdate(BaseModel):
    doctor_id: int | None = None

    day_of_week: str | None = Field(
        default=None,
        min_length=1,
        max_length=10,
    )

    start_time: time | None = None
    end_time: time | None = None

    @field_validator("day_of_week")
    @classmethod
    def validate_day_of_week(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip().lower()

        if value not in VALID_DAYS:
            raise ValueError(
                "day_of_week must be a valid day from Monday to Sunday"
            )

        return value


class DoctorScheduleResponse(DoctorScheduleBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )