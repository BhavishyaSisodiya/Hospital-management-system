from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# MEMBER REGISTER
# ============================================================

class MemberRegister(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

    role_id: int

    department_id: int

    dob: date | None = None

    gender: str | None = Field(
        default=None,
        max_length=20
    )

    phone: str | None = Field(
        default=None,
        max_length=20
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )

    hire_date: date | None = None

    salary: float | None = Field(
        default=None,
        ge=0
    )

    employment_status: str = Field(
        min_length=1,
        max_length=20
    )


# ============================================================
# MEMBER REGISTER RESPONSE
# ============================================================

class MemberRegisterResponse(BaseModel):

    user_id: int

    employee_id: int

    name: str

    email: EmailStr

    role_id: int

    department_id: int

    message: str

    model_config = ConfigDict(
        from_attributes=True
    )