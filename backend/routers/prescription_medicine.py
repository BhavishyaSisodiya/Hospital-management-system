from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db

from models.prescription_medicine import PrescriptionMedicineDB
from models.prescription import PrescriptionDB
from models.medicine import MedicineDB
from models.employee import EmployeeDB
from models.doctor import DoctorDB
from models.patient import PatientDB

from schema.prescription_medicine import (
    PrescriptionMedicineCreate,
    PrescriptionMedicineUpdate,
    PrescriptionMedicineResponse,
)

from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/prescription-medicines",
    tags=["Prescription Medicines"],
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_role_name(current_user):
    return (
        current_user.role.name.lower()
        if current_user.role
        else ""
    )


def is_member(current_user):
    return (
        current_user.account_type
        and current_user.account_type.lower() == "member"
    )


def has_role(current_user, roles: set[str]):
    return (
        is_member(current_user)
        and get_role_name(current_user) in roles
    )


def is_prescription_manager(current_user):
    return has_role(
        current_user,
        {
            "admin",
            "doctor",
            "pharmacist",
        },
    )


def can_view_prescription_medicines(current_user):
    return has_role(
        current_user,
        {
            "admin",
            "doctor",
            "nurse",
            "pharmacist",
            "receptionist",
        },
    )


def is_doctor_owner(
    current_user,
    prescription,
    db: Session,
):
    if not has_role(current_user, {"doctor"}):
        return False

    doctor = get_current_doctor(
        current_user,
        db,
    )

    if doctor is None:
        return False

    return prescription.doctor_id == doctor.id


def is_patient_owner(
    current_user,
    prescription,
    db: Session,
):
    if not (
        current_user.account_type
        and current_user.account_type.lower() == "patient"
    ):
        return False

    patient = get_current_patient(
        current_user,
        db,
    )

    if patient is None:
        return False

    return prescription.patient_id == patient.id

def get_current_doctor(
    current_user,
    db: Session,
):
    employee = (
        db.query(EmployeeDB)
        .filter(
            EmployeeDB.email == current_user.email
        )
        .first()
    )

    if employee is None:
        return None

    return (
        db.query(DoctorDB)
        .filter(
            DoctorDB.employee_id == employee.id
        )
        .first()
    )


def get_current_patient(
    current_user,
    db: Session,
):
    return (
        db.query(PatientDB)
        .filter(
            PatientDB.email == current_user.email
        )
        .first()
    )


# ============================================================
# CREATE PRESCRIPTION MEDICINE
# ============================================================

@router.post(
    "/",
    response_model=PrescriptionMedicineResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_prescription_medicine(
    data: PrescriptionMedicineCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    if not is_prescription_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only admin, doctor, or pharmacist can "
                "manage prescription medicines."
            ),
        )

    # --------------------------------------------------------
    # Check prescription
    # --------------------------------------------------------

    prescription = db.get(
        PrescriptionDB,
        data.prescription_id,
    )

    if prescription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found.",
        )

    # --------------------------------------------------------
    # Doctor ownership check
    # --------------------------------------------------------

    if has_role(current_user, {"doctor"}):
        doctor = get_current_doctor(
            current_user,
            db,
        )
    
        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor profile not found.",
            )
    
        if prescription.doctor_id != doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only add medicines "
                    "to your own prescriptions."
                ),
            )

    # --------------------------------------------------------
    # Check medicine
    # --------------------------------------------------------

    medicine = db.get(
        MedicineDB,
        data.medicine_id,
    )

    if medicine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found.",
        )

    # --------------------------------------------------------
    # Check duplicate composite key
    # --------------------------------------------------------

    existing = (
        db.query(PrescriptionMedicineDB)
        .filter(
            PrescriptionMedicineDB.prescription_id
            == data.prescription_id,
            PrescriptionMedicineDB.medicine_id
            == data.medicine_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This medicine is already added "
                "to the prescription."
            ),
        )

    # --------------------------------------------------------
    # Clean string values
    # --------------------------------------------------------

    dosage = data.dosage.strip()

    if not dosage:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Dosage cannot be blank.",
        )

    duration = (
        data.duration.strip()
        if data.duration is not None
        else None
    )

    instructions = (
        data.instructions.strip()
        if data.instructions is not None
        else None
    )

    # --------------------------------------------------------
    # Create record explicitly
    # --------------------------------------------------------

    record = PrescriptionMedicineDB(
        prescription_id=data.prescription_id,
        medicine_id=data.medicine_id,
        quantity=data.quantity,
        dosage=dosage,
        duration=duration,
        instructions=instructions,
    )

    db.add(record)

    try:
        db.commit()
        db.refresh(record)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Prescription medicine could not be created.",
        )

    return record


# ============================================================
# GET ALL PRESCRIPTION MEDICINES
# ============================================================

@router.get(
    "/",
    response_model=list[PrescriptionMedicineResponse],
)
def get_prescription_medicines(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    # --------------------------------------------------------
    # Doctor view - only own prescription medicines
    # --------------------------------------------------------

    if has_role(current_user, {"doctor"}):
        doctor = get_current_doctor(
            current_user,
            db,
        )
    
        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor profile not found.",
            )
    
        return (
            db.query(PrescriptionMedicineDB)
            .join(
                PrescriptionDB,
                PrescriptionDB.id
                == PrescriptionMedicineDB.prescription_id,
            )
            .filter(
                PrescriptionDB.doctor_id
                == doctor.id
            )
            .order_by(
                PrescriptionMedicineDB.prescription_id,
                PrescriptionMedicineDB.medicine_id,
            )
            .all()
        )

    # --------------------------------------------------------
    # Staff view
    # --------------------------------------------------------

    if can_view_prescription_medicines(current_user):

        return (
            db.query(PrescriptionMedicineDB)
            .order_by(
                PrescriptionMedicineDB.prescription_id,
                PrescriptionMedicineDB.medicine_id,
            )
            .all()
        )

    # --------------------------------------------------------
    # Patient view - only own prescription medicines
    # --------------------------------------------------------

    if (
        current_user.account_type
        and current_user.account_type.lower() == "patient"
        and current_user.patient is not None
    ):

        return (
            db.query(PrescriptionMedicineDB)
            .join(
                PrescriptionDB,
                PrescriptionDB.id
                == PrescriptionMedicineDB.prescription_id,
            )
            .filter(
                PrescriptionDB.patient_id
                == current_user.patient.id
            )
            .order_by(
                PrescriptionMedicineDB.prescription_id,
                PrescriptionMedicineDB.medicine_id,
            )
            .all()
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to view prescription medicines.",
    )


# ============================================================
# GET ONE PRESCRIPTION MEDICINE
# ============================================================

@router.get(
    "/{prescription_id}/{medicine_id}",
    response_model=PrescriptionMedicineResponse,
)
def get_prescription_medicine(
    prescription_id: int,
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    record = (
        db.query(PrescriptionMedicineDB)
        .filter(
            PrescriptionMedicineDB.prescription_id
            == prescription_id,
            PrescriptionMedicineDB.medicine_id
            == medicine_id,
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription medicine record not found.",
        )

    # --------------------------------------------------------
    # Get prescription
    # --------------------------------------------------------

    prescription = db.get(
        PrescriptionDB,
        record.prescription_id,
    )

    if prescription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found.",
        )

    # --------------------------------------------------------
    # Doctor can view only own prescription
    # --------------------------------------------------------

    if has_role(current_user, {"doctor"}):
        doctor = get_current_doctor(
            current_user,
            db,
        )
    
        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor profile not found.",
            )
    
        if prescription.doctor_id != doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You are not authorized "
                    "to view this prescription medicine."
                ),
            )

        return record

    # --------------------------------------------------------
    # Staff can view
    # --------------------------------------------------------

    if can_view_prescription_medicines(current_user):
        return record

    # --------------------------------------------------------
    # Patient can view only their own prescription
    # --------------------------------------------------------

    if is_patient_owner(current_user, prescription,db,):
        return record

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "You are not authorized "
            "to view this prescription medicine."
        ),
    )


# ============================================================
# UPDATE PRESCRIPTION MEDICINE
# ============================================================

@router.patch(
    "/{prescription_id}/{medicine_id}",
    response_model=PrescriptionMedicineResponse,
)
def update_prescription_medicine(
    prescription_id: int,
    medicine_id: int,
    data: PrescriptionMedicineUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    if not is_prescription_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only admin, doctor, or pharmacist can "
                "manage prescription medicines."
            ),
        )

    # --------------------------------------------------------
    # Find record using composite primary key
    # --------------------------------------------------------

    record = (
        db.query(PrescriptionMedicineDB)
        .filter(
            PrescriptionMedicineDB.prescription_id
            == prescription_id,
            PrescriptionMedicineDB.medicine_id
            == medicine_id,
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription medicine record not found.",
        )

    # --------------------------------------------------------
    # Find prescription
    # --------------------------------------------------------

    prescription = db.get(
        PrescriptionDB,
        record.prescription_id,
    )

    if prescription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found.",
        )

    # --------------------------------------------------------
    # Doctor ownership check
    # --------------------------------------------------------

    if has_role(current_user, {"doctor"}):
        doctor = get_current_doctor(
            current_user,
            db,
        )
    
        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor profile not found.",
            )
    
        if prescription.doctor_id != doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You can only update medicines "
                    "in your own prescriptions."
                ),
            )

    # --------------------------------------------------------
    # Partial update
    # --------------------------------------------------------

    update_data = data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    # --------------------------------------------------------
    # Clean string values
    # --------------------------------------------------------

    if "dosage" in update_data:

        dosage = update_data["dosage"].strip()

        if not dosage:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Dosage cannot be blank.",
            )

        update_data["dosage"] = dosage

    if "duration" in update_data:

        if update_data["duration"] is not None:

            duration = update_data["duration"].strip()

            update_data["duration"] = (
                duration if duration else None
            )

    if "instructions" in update_data:

        if update_data["instructions"] is not None:

            instructions = update_data["instructions"].strip()

            update_data["instructions"] = (
                instructions if instructions else None
            )

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(record, field, value)

    try:
        db.commit()
        db.refresh(record)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Prescription medicine could not be updated.",
        )

    return record


# ============================================================
# DELETE PRESCRIPTION MEDICINE
# ============================================================

@router.delete(
    "/{prescription_id}/{medicine_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_prescription_medicine(
    prescription_id: int,
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    if not has_role(current_user, {"admin"}):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete prescription medicines.",
        )

    # --------------------------------------------------------
    # Find record using composite primary key
    # --------------------------------------------------------

    record = (
        db.query(PrescriptionMedicineDB)
        .filter(
            PrescriptionMedicineDB.prescription_id
            == prescription_id,
            PrescriptionMedicineDB.medicine_id
            == medicine_id,
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription medicine record not found.",
        )

    db.delete(record)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Prescription medicine could not be deleted.",
        )

    return None