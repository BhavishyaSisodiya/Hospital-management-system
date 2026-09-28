from datetime import date

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class PatientBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    date_of_birth: date | None = None
    gender: str = Field(min_length=1, max_length=20)
    phone: str = Field(min_length=1, max_length=20)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=255)


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, min_length=1, max_length=20)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=255)


class PatientResponse(PatientBase):
    id: int

    model_config = ConfigDict(from_attributes=True)