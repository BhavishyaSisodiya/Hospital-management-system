from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.users import UserDB
from models.patient import PatientDB

from schema.auth import (
    PatientRegister,
    PatientRegisterResponse,
    LoginRequest,
)

from utils.security import (
    hash_password,
    verify_password,
)

from utils.jwt import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# PATIENT SELF REGISTRATION
# ============================================================
#
# Only patients can register themselves.
#
# This creates:
#
#       UserDB
#          |
#          | 1 : 1
#          ↓
#       PatientDB
#
# Member/staff accounts must NOT be created through this
# endpoint. They should be created by an administrator.
# ============================================================

@router.post(
    "/register/patient",
    response_model=PatientRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_patient(
    patient_data: PatientRegister,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Check whether email already exists
    # --------------------------------------------------------

    existing_user = (
        db.query(UserDB)
        .filter(UserDB.email == patient_data.email)
        .first()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    # --------------------------------------------------------
    # Create authentication account
    # --------------------------------------------------------

    user = UserDB(
        name=patient_data.name,
        email=patient_data.email,
        password_hash=hash_password(patient_data.password),
        account_type="patient",
        role_id=None,
        is_active=True,
    )

    db.add(user)

    try:
        # ----------------------------------------------------
        # Flush to obtain UserDB.id
        # ----------------------------------------------------

        db.flush()

        # ----------------------------------------------------
        # Create PatientDB
        # ----------------------------------------------------

        patient = PatientDB(
            name=patient_data.name,
            date_of_birth=patient_data.date_of_birth,
            gender=patient_data.gender,
            phone=patient_data.phone,
            email=patient_data.email,
            address=patient_data.address,
            user_id=user.id,
        )

        db.add(patient)

        # ----------------------------------------------------
        # Commit UserDB + PatientDB together
        # ----------------------------------------------------

        db.commit()

        db.refresh(user)
        db.refresh(patient)

    except IntegrityError as e:
        db.rollback()
        print("INTEGRITY ERROR:", e)
        raise HTTPException(
            status_code=409,
            detail=str(e.orig),
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return PatientRegisterResponse(
        message="Patient registered successfully.",
        user_id=user.id,
        patient_id=patient.id,
    )


# ============================================================
# LOGIN
# ============================================================
#
# Both patients and members use the same login endpoint.
#
# Patient:
#     account_type = "patient"
#
# Member:
#     account_type = "member"
#
# Authentication is based only on UserDB.
#
# EmployeeDB is NOT connected to authentication.
# ============================================================

@router.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Find user by email
    # --------------------------------------------------------

    user = (
        db.query(UserDB)
        .filter(UserDB.email == login_data.email)
        .first()
    )

    # --------------------------------------------------------
    # Invalid credentials
    #
    # Do not reveal whether the email exists.
    # --------------------------------------------------------

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # --------------------------------------------------------
    # Verify password
    # --------------------------------------------------------

    if not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # --------------------------------------------------------
    # Check account status
    # --------------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    # --------------------------------------------------------
    # Create JWT
    #
    # sub contains UserDB.id.
    #
    # Authorization later uses:
    #     UserDB.account_type
    #     UserDB.role
    # --------------------------------------------------------

    access_token = create_access_token(
        data={
            "sub": str(user.id),
        },
        expires_delta=timedelta(minutes=60),
    )

    # --------------------------------------------------------
    # Return authentication information
    # --------------------------------------------------------

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "account_type": user.account_type,
        "role_id": user.role_id,
        "name": user.name,
        "role": user.role.name if user.role else None,
    }

