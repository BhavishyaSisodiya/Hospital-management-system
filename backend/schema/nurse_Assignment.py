from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
)


class NurseAssignmentBase(BaseModel):
    admission_id: int
    nurse_id: int
    assigned_at: datetime | None = None
    unassigned_at: datetime | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.assigned_at is not None
            and self.unassigned_at is not None
            and self.unassigned_at < self.assigned_at
        ):
            raise ValueError(
                "unassigned_at must be greater than or equal to assigned_at."
            )

        return self


class NurseAssignmentCreate(NurseAssignmentBase):
    pass


class NurseAssignmentUpdate(BaseModel):
    admission_id: int | None = None
    nurse_id: int | None = None
    assigned_at: datetime | None = None
    unassigned_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class NurseAssignmentResponse(BaseModel):
    id: int
    admission_id: int
    nurse_id: int
    assigned_at: datetime
    unassigned_at: datetime | None

    model_config = ConfigDict(from_attributes=True)