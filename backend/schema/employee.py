from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


EmploymentStatus = Literal[
    "active",
    "inactive",
    "on_leave",
    "terminated",
]


class EmployeeBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    role_id: int

    department_id: int

    dob: date | None = None

    gender: str | None = Field(
        default=None,
        max_length=20,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    email: EmailStr | None = None

    address: str | None = Field(
        default=None,
        max_length=255,
    )

    hire_date: date | None = None

    salary: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    employment_status: EmploymentStatus = "active"

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Employee name cannot be empty.")

        return value


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    role_id: int | None = None

    department_id: int | None = None

    dob: date | None = None

    gender: str | None = Field(
        default=None,
        max_length=20,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    email: EmailStr | None = None

    address: str | None = Field(
        default=None,
        max_length=255,
    )

    hire_date: date | None = None

    salary: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    employment_status: EmploymentStatus | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Employee name cannot be empty.")

        return value


class EmployeeResponse(BaseModel):
    id: int
    name: str
    role_id: int
    department_id: int
    dob: date | None
    gender: str | None
    phone: str | None
    email: EmailStr | None
    address: str | None
    hire_date: date | None
    salary: Decimal | None
    employment_status: EmploymentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )