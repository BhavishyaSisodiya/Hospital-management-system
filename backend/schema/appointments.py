from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    reason: str | None = Field(default=None, max_length=500)
    status: str = Field(min_length=1, max_length=30)


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    patient_id: int | None = None
    doctor_id: int | None = None
    appointment_date: date | None = None
    appointment_time: time | None = None
    reason: str | None = Field(default=None, max_length=500)
    status: str | None = Field(default=None, max_length=30)


class AppointmentResponse(AppointmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)