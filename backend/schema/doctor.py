from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# CREATE DOCTOR
# ============================================================

class DoctorCreate(BaseModel):
    # Attach to an existing doctor-role employee (alternative
    # to creating a brand-new employee below).
    employee_id: int | None = Field(
        default=None,
        gt=0,
    )

    # When employee_id is not supplied, the doctor is created
    # together with a new employee record using these fields.
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    department_id: int | None = Field(
        default=None,
        gt=0,
    )

    specialization: str = Field(
        default="General Medicine",
        min_length=1,
        max_length=100,
    )

    experience_years: int | None = Field(
        default=None,
        ge=0,
    )


# ============================================================
# UPDATE DOCTOR
# ============================================================

class DoctorUpdate(BaseModel):
    employee_id: int | None = Field(
        default=None,
        gt=0,
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    department_id: int | None = Field(
        default=None,
        gt=0,
    )

    specialization: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    experience_years: int | None = Field(
        default=None,
        ge=0,
    )


# ============================================================
# PUBLIC (used for patient self-booking)
# ============================================================

class DoctorPublicResponse(BaseModel):
    id: int
    name: str
    specialization: str
    experience_years: int | None


# ============================================================
# ADMIN / STAFF RESPONSE
# ============================================================

class DoctorResponse(BaseModel):
    id: int

    employee_id: int

    name: str

    email: str | None = None

    phone: str | None = None

    department_id: int | None = None

    department_name: str | None = None

    specialization: str

    experience_years: int | None = Field(
        default=None,
        ge=0,
    )

    model_config = ConfigDict(
        from_attributes=True,
    )