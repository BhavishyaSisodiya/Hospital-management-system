from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


AdmissionStatus = Literal[
    "admitted",
    "discharged",
    "cancelled",
]


class AdmissionBase(BaseModel):
    patient_id: int
    doctor_id: int
    bed_id: int

    admission_date: datetime

    discharge_date: datetime | None = None

    status: AdmissionStatus = "admitted"

    @model_validator(mode="after")
    def validate_dates_and_status(self):
        # ----------------------------------------------------
        # Discharge date cannot be before admission date.
        # ----------------------------------------------------

        if (
            self.discharge_date is not None
            and self.discharge_date < self.admission_date
        ):
            raise ValueError(
                "discharge_date must be greater than or equal to admission_date."
            )

        # ----------------------------------------------------
        # An admitted patient should not have a discharge date.
        # ----------------------------------------------------

        if (
            self.status == "admitted"
            and self.discharge_date is not None
        ):
            raise ValueError(
                "An admitted admission cannot have a discharge_date."
            )

        # ----------------------------------------------------
        # A discharged admission must have a discharge date.
        # ----------------------------------------------------

        if (
            self.status == "discharged"
            and self.discharge_date is None
        ):
            raise ValueError(
                "A discharged admission must have a discharge_date."
            )

        return self


class AdmissionCreate(AdmissionBase):
    pass


class AdmissionUpdate(BaseModel):
    patient_id: int | None = None
    doctor_id: int | None = None
    bed_id: int | None = None

    admission_date: datetime | None = None

    discharge_date: datetime | None = None

    status: AdmissionStatus | None = None

    model_config = ConfigDict(
        extra="forbid"
    )


class AdmissionResponse(AdmissionBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )