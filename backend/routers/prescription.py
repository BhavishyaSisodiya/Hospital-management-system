from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.users import UserDB
from models.employee import EmployeeDB
from models.doctor import DoctorDB
from models.patient import PatientDB
from models.appointments import AppointmentDB
from models.prescription import PrescriptionDB
from models.pharmacy import PharmacyDB
from models.test import TestTypeDB
from models.lab import LabTestDB

from schema.prescription import (
    PrescriptionCreate,
    PrescriptionUpdate,
    PrescriptionResponse,
)

from utils.dependencies import (
    get_current_user,
)


router = APIRouter(
    prefix="/prescriptions",
    tags=["Prescriptions"],
)


# ============================================================
# ROLE HELPERS
# ============================================================

def get_role_name(current_user: UserDB) -> str:
    role = getattr(current_user, "role", None)

    if role is None:
        return ""

    role_name = getattr(role, "name", "")

    return str(role_name).strip().lower()


def is_member(current_user: UserDB) -> bool:
    account_type = getattr(
        current_user,
        "account_type",
        None,
    )

    if account_type is None:
        return False

    return (
        str(account_type).strip().lower()
        == "member"
    )


def has_role(
    current_user: UserDB,
    *roles: str,
) -> bool:

    if not is_member(current_user):
        return False

    current_role = get_role_name(
        current_user
    )

    allowed_roles = {
        role.strip().lower()
        for role in roles
    }

    return current_role in allowed_roles


def is_prescription_manager(
    current_user: UserDB,
) -> bool:

    return has_role(
        current_user,
        "admin",
        "doctor",
    )


def can_view_prescriptions(
    current_user: UserDB,
) -> bool:

    return has_role(
        current_user,
        "admin",
        "doctor",
        "nurse",
        "pharmacist",
        "receptionist",
        "lab_technician",
    )


def is_patient_owner(
    current_user: UserDB,
    patient_id: int,
) -> bool:

    account_type = getattr(
        current_user,
        "account_type",
        None,
    )

    if account_type is None:
        return False

    if (
        str(account_type).strip().lower()
        != "patient"
    ):
        return False

    patient = getattr(
        current_user,
        "patient",
        None,
    )

    if patient is None:
        return False

    return patient.id == patient_id


def can_delete_prescription(
    current_user: UserDB,
) -> bool:

    return has_role(
        current_user,
        "admin",
    )


# ============================================================
# GET AUTHENTICATED DOCTOR
# ============================================================

def get_authenticated_doctor(
    current_user: UserDB,
    db: Session,
) -> DoctorDB:

    employee = db.scalar(
        select(EmployeeDB).where(
            EmployeeDB.email
            == current_user.email
        )
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Employee profile not found "
                "for this doctor."
            ),
        )

    doctor = db.scalar(
        select(DoctorDB).where(
            DoctorDB.employee_id
            == employee.id
        )
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found.",
        )

    return doctor


# ============================================================
# CREATE PRESCRIPTION
# ============================================================

@router.post(
    "/",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_prescription(
    prescription_data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        get_current_user
    ),
):

    # --------------------------------------------------------
    # Only admin and doctor can create
    # --------------------------------------------------------

    if not is_prescription_manager(
        current_user
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only admin or doctor can "
                "create prescriptions."
            ),
        )

    # --------------------------------------------------------
    # Validate prescription date
    # --------------------------------------------------------

    if (
        prescription_data.prescription_date
        > date.today()
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Prescription date cannot "
                "be in the future."
            ),
        )

    # --------------------------------------------------------
    # Validate patient
    # --------------------------------------------------------

    patient = db.get(
        PatientDB,
        prescription_data.patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # --------------------------------------------------------
    # Determine doctor
    # --------------------------------------------------------

    if get_role_name(current_user) == "doctor":

        # IMPORTANT:
        # Do not trust doctor_id from frontend.

        doctor = get_authenticated_doctor(
            current_user,
            db,
        )

        doctor_id = doctor.id

    else:

        # Admin can choose doctor.

        if prescription_data.doctor_id is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail="Doctor is required.",
            )

        doctor = db.get(
            DoctorDB,
            prescription_data.doctor_id,
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

        doctor_id = doctor.id

    # --------------------------------------------------------
    # Validate pharmacy
    # --------------------------------------------------------

    if (
        prescription_data.pharmacy_id
        is not None
    ):

        pharmacy = db.get(
            PharmacyDB,
            prescription_data.pharmacy_id,
        )

        if pharmacy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pharmacy not found.",
            )

    # --------------------------------------------------------
    # Resolve lab test
    # --------------------------------------------------------

    if (
        prescription_data.test_type_id is not None
        and prescription_data.lab_test_id is not None
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Provide either test_type_id "
                "or lab_test_id, not both."
            ),
        )

    lab_test_id = prescription_data.lab_test_id

    if (
        prescription_data.test_type_id
        is not None
    ):

        test_type = db.get(
            TestTypeDB,
            prescription_data.test_type_id,
        )

        if test_type is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail="Test type not found.",
            )

        new_lab_test = LabTestDB(
            test_type_id=test_type.id,
            patient_id=patient.id,
            doctor_id=doctor_id,
            technician_id=None,
            status="pending",
        )

        db.add(new_lab_test)
        db.flush()

        lab_test_id = new_lab_test.id

    if lab_test_id is not None:

        lab_test = db.get(
            LabTestDB,
            lab_test_id,
        )

        if lab_test is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail="Lab test not found.",
            )

        if lab_test.patient_id != patient.id:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "Lab test must belong "
                    "to the same patient."
                ),
            )

        if lab_test.doctor_id != doctor_id:
            raise HTTPException(
                status_code=(
                    status.HTTP_403_FORBIDDEN
                ),
                detail=(
                    "Lab test must belong "
                    "to the same doctor."
                ),
            )

        if lab_test.status != "pending":
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "Only pending lab tests "
                    "can be attached."
                ),
            )

        attached = db.scalar(
            select(PrescriptionDB.id).where(
                PrescriptionDB.lab_test_id
                == lab_test_id
            )
        )

        if attached is not None:
            raise HTTPException(
                status_code=(
                    status.HTTP_409_CONFLICT
                ),
                detail=(
                    "Lab test is already attached "
                    "to another prescription."
                ),
            )

    # --------------------------------------------------------
    # Create prescription
    # --------------------------------------------------------

    prescription = PrescriptionDB(
        patient_id=prescription_data.patient_id,
        doctor_id=doctor_id,
        pharmacy_id=(
            prescription_data.pharmacy_id
        ),
        lab_test_id=lab_test_id,
        prescription_date=(
            prescription_data.prescription_date
        ),
    )

    db.add(prescription)

    try:
        db.commit()
        db.refresh(prescription)

    except IntegrityError as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Prescription could not be "
                "created because of a database "
                "constraint."
            ),
        )

    return prescription


# ============================================================
# GET PRESCRIPTIONS
# ============================================================

@router.get(
    "/",
    response_model=list[PrescriptionResponse],
    status_code=status.HTTP_200_OK,
)
def get_prescriptions(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        get_current_user
    ),
):

    # ========================================================
    # PATIENT
    # ========================================================

    if (
        str(
            getattr(
                current_user,
                "account_type",
                "",
            )
        ).strip().lower()
        == "patient"
    ):

        patient = getattr(
            current_user,
            "patient",
            None,
        )

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient profile not found.",
            )

        return db.scalars(
            select(PrescriptionDB)
            .where(
                PrescriptionDB.patient_id
                == patient.id
            )
            .order_by(
                PrescriptionDB.prescription_date.desc(),
                PrescriptionDB.id.desc(),
            )
        ).all()

    # ========================================================
    # DOCTOR
    # ========================================================

    if has_role(
        current_user,
        "doctor",
    ):

        doctor = get_authenticated_doctor(
            current_user,
            db,
        )

        return db.scalars(
            select(PrescriptionDB)
            .where(
                PrescriptionDB.doctor_id
                == doctor.id
            )
            .order_by(
                PrescriptionDB.prescription_date.desc(),
                PrescriptionDB.id.desc(),
            )
        ).all()

    # ========================================================
    # OTHER STAFF
    # ========================================================

    if has_role(
        current_user,
        "admin",
        "nurse",
        "pharmacist",
        "receptionist",
        "lab_technician",
    ):

        return db.scalars(
            select(PrescriptionDB)
            .order_by(
                PrescriptionDB.prescription_date.desc(),
                PrescriptionDB.id.desc(),
            )
        ).all()

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "You are not authorized to "
            "view prescriptions."
        ),
    )


# ============================================================
# GET PRESCRIPTIONS BY PATIENT
# ============================================================

@router.get(
    "/patient/{patient_id}",
    response_model=list[PrescriptionResponse],
    status_code=status.HTTP_200_OK,
)
def get_patient_prescriptions(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        get_current_user
    ),
):

    # --------------------------------------------------------
    # Verify patient
    # --------------------------------------------------------

    patient = db.get(
        PatientDB,
        patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    # ========================================================
    # PATIENT
    # ========================================================

    if (
        str(
            getattr(
                current_user,
                "account_type",
                "",
            )
        ).strip().lower()
        == "patient"
    ):

        if not is_patient_owner(
            current_user,
            patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only view "
                    "your own prescriptions."
                ),
            )

        return db.scalars(
            select(PrescriptionDB)
            .where(
                PrescriptionDB.patient_id
                == patient_id
            )
            .order_by(
                PrescriptionDB.prescription_date.desc(),
                PrescriptionDB.id.desc(),
            )
        ).all()

    # ========================================================
    # DOCTOR
    # ========================================================

    if has_role(
        current_user,
        "doctor",
    ):

        doctor = get_authenticated_doctor(
            current_user,
            db,
        )

        # ----------------------------------------------------
        # Verify patient is under doctor's care
        # ----------------------------------------------------

        appointment = db.scalar(
            select(AppointmentDB.id).where(
                AppointmentDB.patient_id
                == patient_id,
                AppointmentDB.doctor_id
                == doctor.id,
            )
        )

        if appointment is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "This patient is not "
                    "under your care."
                ),
            )

        return db.scalars(
            select(PrescriptionDB)
            .where(
                PrescriptionDB.patient_id
                == patient_id,
                PrescriptionDB.doctor_id
                == doctor.id,
            )
            .order_by(
                PrescriptionDB.prescription_date.desc(),
                PrescriptionDB.id.desc(),
            )
        ).all()

    # ========================================================
    # OTHER STAFF
    # ========================================================

    if has_role(
        current_user,
        "admin",
        "nurse",
        "pharmacist",
        "receptionist",
        "lab_technician",
    ):

        return db.scalars(
            select(PrescriptionDB)
            .where(
                PrescriptionDB.patient_id
                == patient_id
            )
            .order_by(
                PrescriptionDB.prescription_date.desc(),
                PrescriptionDB.id.desc(),
            )
        ).all()

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "You do not have permission "
            "to view prescriptions."
        ),
    )


# ============================================================
# GET PRESCRIPTION BY ID
# ============================================================

@router.get(
    "/{prescription_id}",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_200_OK,
)
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        get_current_user
    ),
):

    prescription = db.get(
        PrescriptionDB,
        prescription_id,
    )

    if prescription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found.",
        )

    # ========================================================
    # PATIENT
    # ========================================================

    if (
        str(
            getattr(
                current_user,
                "account_type",
                "",
            )
        ).strip().lower()
        == "patient"
    ):

        if not is_patient_owner(
            current_user,
            prescription.patient_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only view "
                    "your own prescription."
                ),
            )

        return prescription

    # ========================================================
    # DOCTOR
    # ========================================================

    if has_role(
        current_user,
        "doctor",
    ):

        doctor = get_authenticated_doctor(
            current_user,
            db,
        )

        if (
            prescription.doctor_id
            != doctor.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only view "
                    "your own prescriptions."
                ),
            )

        return prescription

    # ========================================================
    # OTHER STAFF
    # ========================================================

    if has_role(
        current_user,
        "admin",
        "nurse",
        "pharmacist",
        "receptionist",
        "lab_technician",
    ):
        return prescription

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "You do not have permission "
            "to view this prescription."
        ),
    )


# ============================================================
# UPDATE PRESCRIPTION
# ============================================================

@router.patch(
    "/{prescription_id}",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_200_OK,
)
def update_prescription(
    prescription_id: int,
    prescription_data: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        get_current_user
    ),
):

    if not is_prescription_manager(
        current_user
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only admin or doctor can "
                "update prescriptions."
            ),
        )

    prescription = db.get(
        PrescriptionDB,
        prescription_id,
    )

    if prescription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found.",
        )

    # --------------------------------------------------------
    # Doctor ownership check
    # --------------------------------------------------------

    if has_role(
        current_user,
        "doctor",
    ):

        doctor = get_authenticated_doctor(
            current_user,
            db,
        )

        if (
            prescription.doctor_id
            != doctor.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only update "
                    "your own prescriptions."
                ),
            )

    # --------------------------------------------------------
    # Get supplied fields
    # --------------------------------------------------------

    update_data = (
        prescription_data.model_dump(
            exclude_unset=True
        )
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No fields provided "
                "for update."
            ),
        )

    # --------------------------------------------------------
    # Doctor cannot change doctor_id
    # --------------------------------------------------------

    if has_role(
        current_user,
        "doctor",
    ):
        update_data.pop(
            "doctor_id",
            None,
        )

    # --------------------------------------------------------
    # Validate prescription date
    # --------------------------------------------------------

    if "prescription_date" in update_data:

        if (
            update_data["prescription_date"]
            > date.today()
        ):
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "Prescription date cannot "
                    "be in the future."
                ),
            )

    # --------------------------------------------------------
    # Validate patient
    # --------------------------------------------------------

    if "patient_id" in update_data:

        patient = db.get(
            PatientDB,
            update_data["patient_id"],
        )

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found.",
            )

    # --------------------------------------------------------
    # Validate doctor
    # --------------------------------------------------------

    if "doctor_id" in update_data:

        doctor = db.get(
            DoctorDB,
            update_data["doctor_id"],
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

    # --------------------------------------------------------
    # Validate pharmacy
    # --------------------------------------------------------

    if "pharmacy_id" in update_data:

        pharmacy_id = update_data[
            "pharmacy_id"
        ]

        if pharmacy_id is not None:

            pharmacy = db.get(
                PharmacyDB,
                pharmacy_id,
            )

            if pharmacy is None:
                raise HTTPException(
                    status_code=(
                        status.HTTP_404_NOT_FOUND
                    ),
                    detail="Pharmacy not found.",
                )

    # --------------------------------------------------------
    # Validate lab test
    # --------------------------------------------------------

    if "lab_test_id" in update_data:

        lab_test_id = update_data[
            "lab_test_id"
        ]

        if lab_test_id is not None:

            lab_test = db.get(
                LabTestDB,
                lab_test_id,
            )

            if lab_test is None:
                raise HTTPException(
                    status_code=(
                        status.HTTP_404_NOT_FOUND
                    ),
                    detail="Lab test not found.",
                )

            if (
                lab_test.patient_id
                != prescription.patient_id
            ):
                raise HTTPException(
                    status_code=(
                        status.HTTP_422_UNPROCESSABLE_ENTITY
                    ),
                    detail=(
                        "Lab test must belong "
                        "to the same patient."
                    ),
                )

            if (
                lab_test.doctor_id
                != prescription.doctor_id
            ):
                raise HTTPException(
                    status_code=(
                        status.HTTP_403_FORBIDDEN
                    ),
                    detail=(
                        "Lab test must belong "
                        "to the same doctor."
                    ),
                )

            if lab_test.status != "pending":
                raise HTTPException(
                    status_code=(
                        status.HTTP_422_UNPROCESSABLE_ENTITY
                    ),
                    detail=(
                        "Only pending lab tests "
                        "can be attached."
                    ),
                )

            attached = db.scalar(
                select(PrescriptionDB.id).where(
                    PrescriptionDB.lab_test_id
                    == lab_test_id,
                    PrescriptionDB.id
                    != prescription.id,
                )
            )

            if attached is not None:
                raise HTTPException(
                    status_code=(
                        status.HTTP_409_CONFLICT
                    ),
                    detail=(
                        "Lab test is already attached "
                        "to another prescription."
                    ),
                )

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            prescription,
            field,
            value,
        )

    try:
        db.commit()
        db.refresh(prescription)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Prescription could not be "
                "updated because of a database "
                "constraint."
            ),
        )

    return prescription


# ============================================================
# DELETE PRESCRIPTION
# ============================================================

@router.delete(
    "/{prescription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(
        get_current_user
    ),
):

    if not can_delete_prescription(
        current_user
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete prescriptions.",
        )

    prescription = db.get(
        PrescriptionDB,
        prescription_id,
    )

    if prescription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found.",
        )

    db.delete(prescription)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Prescription cannot be "
                "deleted because it is referenced "
                "by existing records."
            ),
        )

    return None