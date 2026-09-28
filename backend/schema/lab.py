from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


LabTestStatus = Literal[
    "pending",
    "in_progress",
    "completed",
    "cancelled",
]


class LabTestBase(BaseModel):
    test_type_id: int
    patient_id: int
    doctor_id: int | None = None
    technician_id: int | None = None

    test_date: datetime | None = None

    status: LabTestStatus = "pending"


class LabTestCreate(LabTestBase):
    pass


class LabTestUpdate(BaseModel):
    test_type_id: int | None = None
    patient_id: int | None = None
    doctor_id: int | None = None
    technician_id: int | None = None
    test_date: datetime | None = None
    status: LabTestStatus | None = None

    model_config = ConfigDict(
        extra="forbid"
    )


class LabTestResponse(BaseModel):
    id: int
    test_type_id: int
    patient_id: int
    doctor_id: int
    technician_id: int | None = None
    test_date: datetime
    status: LabTestStatus

    model_config = ConfigDict(
        from_attributes=True
    )