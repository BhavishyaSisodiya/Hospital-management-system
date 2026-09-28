from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# PATIENT SELF REGISTRATION
# ============================================================

class PatientRegister(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    date_of_birth: date | None = None

    gender: str = Field(
        min_length=1,
        max_length=20,
    )

    phone: str = Field(
        min_length=1,
        max_length=20,
    )

    address: str | None = Field(
        default=None,
        max_length=255,
    )


# ============================================================
# PATIENT REGISTRATION RESPONSE
# ============================================================

class PatientRegisterResponse(BaseModel):

    message: str

    user_id: int

    patient_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )



class LoginRequest(BaseModel):
    email: EmailStr
    password: str    