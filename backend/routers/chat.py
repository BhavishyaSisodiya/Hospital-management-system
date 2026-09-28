import json
import os
import re
from datetime import date, time, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models.admission import AdmissionDB
from models.appointments import AppointmentDB
from models.bed import BedDB
from models.department import DepartmentDB
from models.doctor import DoctorDB
from models.doctorScedule import DoctorScheduleDB
from models.employee import EmployeeDB
from models.lab import LabTestDB
from models.lab_result import LabResultDB
from models.medical_batch import MedicineBatchDB
from models.medical_record import MedicalRecordDB
from models.medicine import MedicineDB
from models.nurse_assignment import NurseAssignmentDB
from models.patient import PatientDB
from models.pharmacy_Stock import PharmacyStockDB
from models.prescription import PrescriptionDB
from models.room import RoomDB
from models.users import UserDB
from models.vitals import VitalDB
from utils.dependencies import get_current_user, require_admin

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

AI_BASE_URL = os.getenv("AI_BASE_URL", "http://localhost:11434/v1")
AI_API_KEY = os.getenv("AI_API_KEY", "ollama")
AI_MODEL = os.getenv("AI_MODEL", "qwen2.5:3b")
AI_TIMEOUT = float(os.getenv("AI_TIMEOUT", "60"))

WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

# ============================================================
# AI PROVIDER CONFIG
# ============================================================
# Providers are OpenAI-compatible except Gemini. A key saved at runtime
# (POST /chat/config) is stored here and overrides the .env values, so the
# online AI can be switched on without editing any file.

AI_CONFIG_FILE = os.getenv("AI_CONFIG_FILE", "ai_config.json")

# provider -> (base_url, default_model, needs_key)
AI_PROVIDERS = {
    "ollama": ("http://localhost:11434/v1", "qwen2.5:3b", False),
    "groq": ("https://api.groq.com/openai/v1", "llama-3.1-8b-instant", True),
    "openrouter": ("https://openrouter.ai/api/v1", "meta-llama/llama-3.3-70b-instruct:free", True),
    "together": ("https://api.together.xyz/v1", "meta-llama/Llama-3.3-70B-Instruct-Turbo", True),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "gemini-2.0-flash", True),
    "custom": (None, None, True),
}

_ai_state: dict = {}


def _load_saved_config() -> dict:
    """Read the runtime AI config saved by POST /chat/config."""
    try:
        with open(AI_CONFIG_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh) or {}
    except (OSError, json.JSONDecodeError):
        return {}


def _init_ai_config() -> dict:
    provider = os.getenv("AI_PROVIDER", "").strip().lower()
    saved = _load_saved_config()

    # Runtime config wins over .env
    if saved.get("api_key"):
        provider = saved.get("provider") or provider
    else:
        provider = provider or "ollama"

    if provider not in AI_PROVIDERS:
        provider = "ollama"

    preset_url, preset_model, needs_key = AI_PROVIDERS[provider]

    state = {
        "provider": provider,
        "base_url": saved.get("base_url") or os.getenv("AI_BASE_URL") or preset_url,
        "api_key": saved.get("api_key") or os.getenv("AI_API_KEY") or "ollama",
        "model": saved.get("model") or os.getenv("AI_MODEL") or preset_model,
    }

    if provider == "ollama" and not os.getenv("AI_BASE_URL") and not saved.get("base_url"):
        state["base_url"] = preset_url
    if provider != "ollama" and saved.get("api_key"):
        state["base_url"] = saved.get("base_url") or preset_url
        state["model"] = saved.get("model") or preset_model

    return state


def refresh_ai_config() -> dict:
    """Re-read the saved config (called at startup and after saving)."""
    global _ai_state
    _ai_state = _init_ai_config()
    return _ai_state


def ai_config() -> dict:
    if not _ai_state:
        refresh_ai_config()
    return _ai_state


def _mask(value: str) -> str:
    if not value or value == "ollama":
        return value or ""
    return f"{value[:6]}...{value[-4:]}" if len(value) > 12 else "***"


# Populated at import time; .env is loaded by config.py before routers import.
refresh_ai_config()


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    reply: str


class ChatConfigRequest(BaseModel):
    provider: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None


# ============================================================
# LLM CALL (OpenAI-compatible: Ollama / Groq / OpenRouter / Gemini)
# ============================================================

def llm_is_available() -> bool:
    """Cheap reachability probe for the configured provider."""
    cfg = ai_config()
    if not cfg["base_url"]:
        return False
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(
                f"{cfg['base_url'].rstrip('/')}/models",
                headers={"Authorization": f"Bearer {cfg['api_key']}"},
            )
            return resp.status_code < 500
    except Exception:
        return False


def call_llm(conversation: list[dict]) -> str:
    cfg = ai_config()
    if not cfg["base_url"]:
        raise LLMUnavailableError("No AI base_url configured.")

    payload = {
        "model": cfg["model"],
        "messages": conversation,
        "temperature": 0.3,
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    # OpenRouter asks clients to identify themselves
    if cfg["provider"] == "openrouter":
        headers["HTTP-Referer"] = "http://localhost:5173"
        headers["X-Title"] = "Hospital Management System"

    try:
        with httpx.Client(timeout=float(os.getenv("AI_TIMEOUT", "60"))) as client:
            resp = client.post(
                f"{cfg['base_url'].rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            if resp.status_code >= 400:
                raise LLMUnavailableError(
                    f"Provider returned HTTP {resp.status_code}: {resp.text[:200]}"
                )
            return resp.json()["choices"][0]["message"]["content"]
    except LLMUnavailableError:
        raise
    except Exception as exc:
        raise LLMUnavailableError(
            f"LLM call failed ({type(exc).__name__})."
        ) from exc


class LLMUnavailableError(RuntimeError):
    """Raised when the upstream AI provider cannot be reached."""


def _extract_blocks(text: str) -> list[str]:
    blocks = []
    start = None
    depth = 0
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append(text[start : i + 1])
                start = None
    return blocks


def extract_actions(text: str) -> list[dict]:
    actions = []
    for chunk in _extract_blocks(text):
        chunk = chunk.strip().strip("`")
        try:
            parsed = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and "action" in parsed:
            actions.append(parsed)
    return actions


# ============================================================
# SHARED HELPERS
# ============================================================

def _doctor_name(db: Session, doctor_id: int) -> str:
    doctor = db.get(DoctorDB, doctor_id)
    if doctor is None:
        return "Unknown"
    emp = db.get(EmployeeDB, doctor.employee_id)
    if not emp:
        return "Unknown"
    name = emp.name.strip()
    # Employee names are already stored as "Dr. ..." — avoid "Dr. Dr. ..."
    return name if name.lower().startswith("dr.") else f"Dr. {name}"


def _get_patient(db: Session, user: UserDB) -> PatientDB | None:
    return db.scalar(select(PatientDB).where(PatientDB.user_id == user.id))


def _role_of(user: UserDB) -> str:
    """Resolve a user to a lowercase role key used for permission checks."""
    if user.account_type == "patient":
        return "patient"
    role = getattr(user.role, "name", None) or ""
    return role.strip().lower() or "member"


def list_doctors(db: Session) -> str:
    rows = db.execute(
        select(DoctorDB, EmployeeDB.name, DepartmentDB.name)
        .join(EmployeeDB, DoctorDB.employee_id == EmployeeDB.id)
        .join(DepartmentDB, EmployeeDB.department_id == DepartmentDB.id)
        .order_by(EmployeeDB.name)
    ).all()
    if not rows:
        return "No doctors found."
    return "\n".join(
        f"- {name} (id={d.id}, {d.specialization}, {d.experience_years or 0} yrs, dept: {dept})"
        for d, name, dept in rows
    )


def doctor_schedule(db: Session, doctor_id: int) -> str:
    doctor = db.get(DoctorDB, doctor_id)
    if doctor is None:
        return f"Doctor id={doctor_id} not found."
    schedules = db.scalars(
        select(DoctorScheduleDB).where(DoctorScheduleDB.doctor_id == doctor_id)
    ).all()
    if not schedules:
        return f"Doctor id={doctor_id} has no weekly schedule."
    order = {d: i for i, d in enumerate(WEEKDAYS)}
    schedules = sorted(schedules, key=lambda s: (order.get(s.day_of_week.lower(), 99), s.start_time))
    return "Weekly schedule:\n" + "\n".join(
        f"- {s.day_of_week.capitalize()} {s.start_time.strftime('%H:%M')} to {s.end_time.strftime('%H:%M')}"
        for s in schedules
    )


def _schedule_ok(db: Session, doctor_id: int, d: date, t: time) -> bool:
    days = WEEKDAYS
    day = days[d.weekday()]
    schedules = db.scalars(
        select(DoctorScheduleDB).where(
            DoctorScheduleDB.doctor_id == doctor_id,
            DoctorScheduleDB.day_of_week == day,
        )
    ).all()
    return any(s.start_time <= t < s.end_time for s in schedules)


# ============================================================
# PATIENT TOOLS
# ============================================================

def my_appointments(db: Session, user: UserDB) -> str:
    patient = _get_patient(db, user)
    if patient is None:
        return "No patient profile linked to this account."
    appointments = db.scalars(
        select(AppointmentDB)
        .where(AppointmentDB.patient_id == patient.id)
        .order_by(AppointmentDB.appointment_date, AppointmentDB.appointment_time)
    ).all()
    if not appointments:
        return "You have no appointments."
    return "\n".join(
        f"- id={a.id}: {_doctor_name(db, a.doctor_id)} on {a.appointment_date} "
        f"{a.appointment_time.strftime('%H:%M')} (status: {a.status})"
        f"{(' - ' + a.reason) if a.reason else ''}"
        for a in appointments
    )


def cancel_appointment(db: Session, user: UserDB, appointment_id: int) -> str:
    patient = _get_patient(db, user)
    if patient is None:
        return "No patient profile linked to this account."
    appointment = (
        db.query(AppointmentDB)
        .filter(AppointmentDB.id == appointment_id, AppointmentDB.patient_id == patient.id)
        .first()
    )
    if appointment is None:
        return f"Appointment id={appointment_id} not found for you."
    if appointment.status == "cancelled":
        return "This appointment is already cancelled."
    appointment.status = "cancelled"
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return "Could not cancel the appointment."
    return f"Appointment id={appointment_id} cancelled."


def book_appointment(db: Session, user: UserDB, args: dict) -> str:
    patient = _get_patient(db, user)
    if patient is None:
        return "ERROR: No patient profile linked to this account."
    try:
        doctor_id = int(args.get("doctor_id"))
        d = date.fromisoformat(str(args.get("appointment_date")))
        t = time.fromisoformat(str(args.get("appointment_time"))[:8])
    except (TypeError, ValueError):
        return "ERROR: Provide doctor_id, appointment_date (YYYY-MM-DD) and appointment_time (HH:MM)."

    if db.get(DoctorDB, doctor_id) is None:
        return "ERROR: Doctor not found."
    days = WEEKDAYS
    day = days[d.weekday()]
    schedules = db.scalars(
        select(DoctorScheduleDB).where(
            DoctorScheduleDB.doctor_id == doctor_id,
            DoctorScheduleDB.day_of_week == day,
        )
    ).all()
    if not schedules:
        return f"ERROR: The doctor is not available on {day.capitalize()}."
    if not any(s.start_time <= t < s.end_time for s in schedules):
        return "ERROR: The selected time is outside the doctor's working hours."

    conflict = (
        db.query(AppointmentDB)
        .filter(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.appointment_date == d,
            AppointmentDB.appointment_time == t,
            AppointmentDB.status != "cancelled",
        )
        .first()
    )
    if conflict:
        return "ERROR: The doctor already has an appointment at this date and time."

    reason = (args.get("reason") or "").strip()[:500] or None
    appointment = AppointmentDB(
        patient_id=patient.id,
        doctor_id=doctor_id,
        appointment_date=d,
        appointment_time=t,
        reason=reason,
        status="scheduled",
    )
    db.add(appointment)
    try:
        db.commit()
        db.refresh(appointment)
    except IntegrityError:
        db.rollback()
        return "ERROR: Appointment could not be created."

    return (
        f"Appointment booked! id={appointment.id}, with {_doctor_name(db, doctor_id)} "
        f"on {d} at {t.strftime('%H:%M')} (status: scheduled)."
    )


# ============================================================
# STAFF TOOLS (internal)
# ============================================================

def staff_get_doctor_info(db: Session, doctor_id: int) -> str:
    if doctor_id is None:
        return "ERROR: Provide doctor_id."
    doctor = db.get(DoctorDB, doctor_id)
    if doctor is None:
        return f"Doctor id={doctor_id} not found."
    emp = db.get(EmployeeDB, doctor.employee_id)
    dept = db.get(DepartmentDB, emp.department_id) if emp else None
    upcoming = db.scalars(
        select(AppointmentDB)
        .where(
            AppointmentDB.doctor_id == doctor_id,
            AppointmentDB.appointment_date >= date.today(),
            AppointmentDB.status != "cancelled",
        )
        .order_by(AppointmentDB.appointment_date, AppointmentDB.appointment_time)
    ).all()
    parts = [
        f"Doctor: {_doctor_name(db, doctor_id)}",
        f"Specialization: {doctor.specialization}",
        f"Experience: {doctor.experience_years or 0} years",
        f"Department: {dept.name if dept else 'N/A'}",
        f"Upcoming appointments ({len(upcoming)}):",
    ]
    for a in upcoming[:15]:
        parts.append(
            f"- id={a.id}: patient_id={a.patient_id} on {a.appointment_date} "
            f"{a.appointment_time.strftime('%H:%M')} ({a.status})"
        )
    return "\n".join(parts)


def staff_patient_lookup(db: Session, query: str) -> str:
    if not query:
        return "ERROR: Provide a name, email or phone to search."
    q = f"%{query.strip()}%"
    patients = (
        db.query(PatientDB)
        .filter(
            PatientDB.name.ilike(q)
            | PatientDB.email.ilike(q)
            | PatientDB.phone.ilike(q)
        )
        .limit(10)
        .all()
    )
    if not patients:
        return f"No patients match '{query}'."
    lines = []
    for p in patients:
        appts = db.scalars(
            select(AppointmentDB)
            .where(
                AppointmentDB.patient_id == p.id,
                AppointmentDB.appointment_date >= date.today(),
                AppointmentDB.status != "cancelled",
            )
            .order_by(AppointmentDB.appointment_date)
        ).all()
        extra = ""
        if appts:
            a = appts[0]
            extra = (
                f" | next appt: {_doctor_name(db, a.doctor_id)} "
                f"{a.appointment_date} {a.appointment_time.strftime('%H:%M')}"
            )
        lines.append(
            f"- id={p.id}: {p.name} ({p.gender}, {p.phone}, {p.email or 'no email'}){extra}"
        )
    return "\n".join(lines)


def staff_patient_medical_history(db: Session, patient_id: int) -> str:
    """DOCTOR/ADMIN ONLY — a patient's clinical history."""
    if patient_id is None:
        return "ERROR: Provide patient_id."
    patient = db.get(PatientDB, patient_id)
    if patient is None:
        return f"Patient id={patient_id} not found."

    lines = [f"Clinical history for {patient.name} (id={patient.id}):"]

    records = db.scalars(
        select(MedicalRecordDB)
        .where(MedicalRecordDB.patient_id == patient_id)
        .order_by(MedicalRecordDB.record_date.desc())
    ).all()
    lines.append(f"\nMedical records ({len(records)}):")
    if not records:
        lines.append("- none")
    for r in records[:10]:
        lines.append(f"- {r.record_date:%Y-%m-%d} {r.diagnosis}: {r.notes or ''}")

    labs = db.scalars(
        select(LabTestDB)
        .where(LabTestDB.patient_id == patient_id)
        .order_by(LabTestDB.test_date.desc())
    ).all()
    lines.append(f"\nLab results ({len(labs)}):")
    if not labs:
        lines.append("- none")
    for lt in labs[:10]:
        test_name = lt.test_type.name if lt.test_type else f"test_type={lt.test_type_id}"
        if lt.result is not None:
            res = f"{lt.result.result} {lt.result.unit or ''} (ref {lt.result.reference_range or 'N/A'})"
        else:
            res = f"status: {lt.status}"
        lines.append(f"- {test_name}: {res}")

    rx = db.scalars(
        select(PrescriptionDB)
        .where(PrescriptionDB.patient_id == patient_id)
        .order_by(PrescriptionDB.prescription_date.desc())
    ).all()
    lines.append(f"\nPrescriptions ({len(rx)}):")
    if not rx:
        lines.append("- none")
    for p in rx[:10]:
        details = ", ".join(
            f"{pm.medicine.name if pm.medicine else pm.medicine_id} ({pm.dosage})"
            for pm in p.medicines[:5]
        ) or "-"
        lines.append(f"- {p.prescription_date}: {details}")

    return "\n".join(lines)


def staff_patient_vitals(db: Session, patient_id: int) -> str:
    """DOCTOR/ADMIN ONLY — a patient's vitals history."""
    if patient_id is None:
        return "ERROR: Provide patient_id."
    patient = db.get(PatientDB, patient_id)
    if patient is None:
        return f"Patient id={patient_id} not found."
    vitals = db.scalars(
        select(VitalDB)
        .where(VitalDB.patient_id == patient_id)
        .order_by(VitalDB.recorded_at.desc())
    ).all()
    if not vitals:
        return f"No vitals recorded for patient id={patient_id}."
    lines = [f"Vitals for {patient.name} (id={patient.id}):"]
    for v in vitals[:5]:
        lines.append(
            f"- {v.recorded_at:%Y-%m-%d %H:%M}: T {v.temperature}F, HR {v.heart_rate}, "
            f"BP {v.blood_pressure_systolic}/{v.blood_pressure_diastolic}, RR {v.respiratory_rate}, "
            f"SpO2 {v.oxygen_saturation}%, Wt {v.weight}kg"
        )
    return "\n".join(lines)


def staff_my_assignments(db: Session, user: UserDB) -> str:
    """NURSE/ADMIN ONLY — the nurse's own active patient assignments."""
    employee = db.scalar(
        select(EmployeeDB).where(EmployeeDB.email == user.email)
    )
    if employee is None:
        return "No employee profile linked to this account."
    assignments = db.scalars(
        select(NurseAssignmentDB)
        .where(
            NurseAssignmentDB.nurse_id == employee.id,
            NurseAssignmentDB.unassigned_at.is_(None),
        )
        .order_by(NurseAssignmentDB.assigned_at.desc())
    ).all()
    if not assignments:
        return "No active patient assignments for you."
    lines = ["Your current patient assignments:"]
    for na in assignments[:20]:
        ad = na.admission
        if ad is None:
            continue
        bed = ad.bed
        lines.append(
            f"- Admission id={ad.id}: {ad.patient.name} ({ad.patient.gender}), "
            f"bed {bed.bed_number if bed else 'N/A'}, since {ad.admission_date:%Y-%m-%d}"
        )
    if len(lines) == 1:
        return "No active patient assignments for you."
    return "\n".join(lines)


def staff_today_summary(db: Session) -> str:
    today = date.today()
    total = db.scalar(
        select(func.count())
        .select_from(AppointmentDB)
        .where(AppointmentDB.appointment_date == today, AppointmentDB.status != "cancelled")
    ) or 0
    admitted = db.scalars(
        select(AdmissionDB).where(
            AdmissionDB.admission_date == today,
            AdmissionDB.discharge_date.is_(None),
        )
    ).all()
    beds_used = db.scalar(
        select(func.count())
        .select_from(BedDB)
        .where(BedDB.status == "occupied")
    ) or 0
    beds_total = db.scalar(select(func.count()).select_from(BedDB)) or 0
    lines = [
        f"Today's appointments: {total}",
        f"New admissions today: {len(admitted)}",
        f"Bed occupancy: {beds_used}/{beds_total}",
    ]
    appts = db.scalars(
        select(AppointmentDB)
        .where(AppointmentDB.appointment_date == today, AppointmentDB.status != "cancelled")
        .order_by(AppointmentDB.appointment_time)
    ).all()
    if appts:
        lines.append("Schedule:")
        for a in appts[:20]:
            lines.append(
                f"- {a.appointment_time.strftime('%H:%M')} {_doctor_name(db, a.doctor_id)} "
                f"-> patient_id={a.patient_id} ({a.status})"
            )
    return "\n".join(lines)


def staff_bed_occupancy(db: Session) -> str:
    rooms = db.scalars(select(RoomDB).order_by(RoomDB.room_number)).all()
    lines = []
    for r in rooms:
        beds = db.scalars(select(BedDB).where(BedDB.room_id == r.id)).all()
        occupied = sum(1 for b in beds if b.status == "occupied")
        lines.append(
            f"- Room {r.room_number} ({r.room_type}): {occupied}/{len(beds)} beds occupied"
        )
    return "\n".join(lines) or "No rooms found."


def staff_low_stock(db: Session, threshold: int = 20) -> str:
    rows = db.execute(
        select(
            MedicineDB.name,
            MedicineBatchDB.batch_number,
            MedicineBatchDB.expiry_date,
            PharmacyStockDB.quantity,
        )
        .join(MedicineBatchDB, MedicineBatchDB.id == PharmacyStockDB.batch_id)
        .join(MedicineDB, MedicineDB.id == MedicineBatchDB.medicine_id)
        .order_by(PharmacyStockDB.quantity)
    ).all()
    low = [r for r in rows if r.quantity <= threshold]
    if not low:
        return f"No medicines at or below stock level {threshold}."
    return "Low-stock items:\n" + "\n".join(
        f"- {name} (batch {batch}, expires {exp}), qty={qty}"
        for name, batch, exp, qty in low[:20]
    )


def staff_department_summary(db: Session) -> str:
    rows = db.execute(
        select(DepartmentDB.name, func.count(EmployeeDB.id))
        .outerjoin(EmployeeDB, EmployeeDB.department_id == DepartmentDB.id)
        .group_by(DepartmentDB.name)
        .order_by(DepartmentDB.name)
    ).all()
    if not rows:
        return "No departments found."
    return "\n".join(f"- {name}: {count} employees" for name, count in rows)


# ============================================================
# TOOL DISPATCH BY ROLE (ACCESS MODIFIERS)
# ============================================================

TOOL_DESCRIPTIONS = {
    "list_doctors": "List all doctors (id, specialization, department).",
    "doctor_schedule": "Get a doctor's weekly schedule. Args: doctor_id (int).",
    "book_appointment": "Book an appointment for the logged-in patient. Args: doctor_id (int), appointment_date (YYYY-MM-DD), appointment_time (HH:MM), reason (str, optional).",
    "my_appointments": "List the logged-in patient's appointments.",
    "cancel_appointment": "Cancel the logged-in patient's appointment. Args: appointment_id (int).",
    "doctor_info": "Get a doctor's profile and their upcoming appointments. Args: doctor_id (int).",
    "patient_lookup": "Find patients by name, email or phone (basic info only). Args: query (str).",
    "patient_medical_history": "A patient's medical records, lab results and prescriptions (confidential). Args: patient_id (int).",
    "patient_vitals": "A patient's vitals history (confidential). Args: patient_id (int).",
    "today_summary": "Overview of today's appointments, admissions and bed occupancy.",
    "bed_occupancy": "Bed occupancy for every room.",
    "low_stock": "List pharmacy stock items at or below a quantity. Args: threshold (int, default 20).",
    "department_summary": "List departments and employee counts.",
    "my_assignments": "List the logged-in nurse's own active patient assignments.",
}

PATIENT_PERMISSIONS = {
    "list_doctors",
    "doctor_schedule",
    "book_appointment",
    "my_appointments",
    "cancel_appointment",
}

# Tool -> roles allowed to call it.
# Confidential clinical data (medical records, lab results, prescriptions,
# vitals) is limited to DOCTOR (and ADMIN). Nurses get operational tools and
# their own assignments only — never another patient's clinical history.
STAFF_PERMISSIONS = {
    "doctor_info": {"admin", "doctor"},
    "patient_lookup": {"admin", "doctor", "nurse", "receptionist", "pharmacist", "lab_technician"},
    "patient_medical_history": {"admin", "doctor"},
    "patient_vitals": {"admin", "doctor"},
    "today_summary": {"admin", "doctor", "nurse", "receptionist", "pharmacist", "lab_technician"},
    "bed_occupancy": {"admin", "doctor", "nurse", "receptionist"},
    "low_stock": {"admin", "doctor", "nurse", "pharmacist"},
    "department_summary": {"admin", "doctor", "nurse", "receptionist", "pharmacist", "lab_technician"},
    "my_assignments": {"admin", "nurse"},
    "list_doctors": {"admin", "doctor", "nurse", "receptionist"},
    "doctor_schedule": {"admin", "doctor", "nurse", "receptionist"},
}


def run_action(db: Session, user: UserDB, action: dict) -> str:
    name = action.get("action")
    args = action.get("args") or {}
    role = _role_of(user)

    try:
        # ---------------- PATIENT ----------------
        if role == "patient":
            if name not in PATIENT_PERMISSIONS:
                return f"ERROR: action '{name}' is not available to patients."
            if name == "list_doctors":
                return list_doctors(db)
            if name == "doctor_schedule":
                return doctor_schedule(db, int(args.get("doctor_id")))
            if name == "book_appointment":
                return book_appointment(db, user, args)
            if name == "my_appointments":
                return my_appointments(db, user)
            if name == "cancel_appointment":
                return cancel_appointment(db, user, int(args.get("appointment_id")))

        # ---------------- STAFF ----------------
        allowed_roles = STAFF_PERMISSIONS.get(name, set())
        if role not in allowed_roles:
            return (
                f"ERROR: action '{name}' is not permitted for your role "
                f"({role})."
            )
        if name == "doctor_info":
            return staff_get_doctor_info(db, int(args.get("doctor_id")))
        if name == "patient_lookup":
            return staff_patient_lookup(db, str(args.get("query", "")))
        if name == "patient_medical_history":
            return staff_patient_medical_history(db, int(args.get("patient_id")))
        if name == "patient_vitals":
            return staff_patient_vitals(db, int(args.get("patient_id")))
        if name == "today_summary":
            return staff_today_summary(db)
        if name == "bed_occupancy":
            return staff_bed_occupancy(db)
        if name == "low_stock":
            return staff_low_stock(db, int(args.get("threshold", 20)))
        if name == "department_summary":
            return staff_department_summary(db)
        if name == "my_assignments":
            return staff_my_assignments(db, user)
        if name == "list_doctors":
            return list_doctors(db)
        if name == "doctor_schedule":
            return doctor_schedule(db, int(args.get("doctor_id")))
        return f"ERROR: unknown action '{name}'."
    except (TypeError, ValueError):
        return f"ERROR: invalid arguments for action '{name}'."


# ============================================================
# SYSTEM PROMPTS (role-specific — only list allowed tools)
# ============================================================

def build_system_prompt(user: UserDB) -> str:
    role = _role_of(user)

    if role == "patient":
        lines = [
            "You are the Hospital Management System assistant helping a PATIENT.",
            "",
            "You can help patients by:",
        ]
        for tool in sorted(PATIENT_PERMISSIONS):
            lines.append(f"- {TOOL_DESCRIPTIONS[tool]}")
    else:
        lines = [
            f"You are the Hospital Management System internal assistant for a {role.upper()}.",
            "",
            "You can run these internal operations:",
        ]
        allowed = sorted(
            tool
            for tool, roles in STAFF_PERMISSIONS.items()
            if role in roles
        )
        if allowed:
            for tool in allowed:
                lines.append(f"- ({tool}) {TOOL_DESCRIPTIONS[tool]}")
        else:
            lines.append("- (no tools available to your role)")

        if role == "nurse":
            lines += [
                "",
                "ACCESS RULES:",
                "- You must NOT attempt patient_medical_history or patient_vitals; "
                "those are doctor-only and will be rejected.",
                "- You may only access your own nurse assignments via my_assignments.",
            ]
        elif role == "doctor":
            lines += [
                "",
                "ACCESS RULES:",
                "- Clinical history (patient_medical_history, patient_vitals) is "
                "available to you, but always protect patient confidentiality.",
            ]

    lines += [
        "",
        "To use a tool, respond ONLY with JSON like:",
        '{"action": "tool_name", "args": {...}}',
        "No other text when calling a tool.",
        "",
        "For normal replies, respond concisely and professionally.",
        "Never invent data, ids, dates or times. Ask the user for anything you need.",
    ]
    return "\n".join(lines)


# ============================================================
# OFFLINE FALLBACK
# ============================================================
# When the LLM provider is unreachable the chatbot still answers by
# matching the question against the tools below and running them
# directly through run_action(), so permissions stay enforced.

def _find_doctor_id(db: Session, text: str) -> int | None:
    """Resolve a doctor by explicit id, doctor name or employee name."""
    if not text:
        return None

    match = re.search(r"\b(?:id\s*[=:]\s*|doctor\s+)(\d+)\b", text, re.I)
    if match:
        candidate = db.get(DoctorDB, int(match.group(1)))
        return candidate.id if candidate else None

    rows = db.execute(
        select(DoctorDB.id, EmployeeDB.name)
        .join(EmployeeDB, DoctorDB.employee_id == EmployeeDB.id)
    ).all()
    lowered = text.lower()
    for doctor_id, name in rows:
        if name and name.lower() in lowered:
            return doctor_id
        surname = name.split()[-1].lower() if name else ""
        if len(surname) > 3 and surname in lowered:
            return doctor_id
    return None


def _find_patient_id(db: Session, text: str) -> int | None:
    """Resolve a patient by explicit id or by name."""
    if not text:
        return None

    match = re.search(r"\b(?:id\s*[=:]\s*|patient\s+)(\d+)\b", text, re.I)
    if match:
        candidate = db.get(PatientDB, int(match.group(1)))
        return candidate.id if candidate else None

    lowered = text.lower()
    for patient in db.scalars(select(PatientDB)).all():
        if patient.name and patient.name.lower() in lowered:
            return patient.id
    return None


def _extract_date(text: str) -> str | None:
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    return match.group(1) if match else None


def _extract_time(text: str) -> str | None:
    match = re.search(r"\b(\d{1,2}:\d{2})\b", text)
    return match.group(1) if match else None


def _extract_int(text: str, label: str) -> int | None:
    match = re.search(rf"\b{label}\s*[#:=]?\s*(\d+)\b", text, re.I)
    return int(match.group(1)) if match else None


def _run(db: Session, user: UserDB, action: dict) -> str:
    """Run a tool through the permission layer and tidy the error prefix."""
    result = run_action(db, user, action)
    if result.startswith("ERROR: "):
        return result[7:].strip()
    return result


def offline_reply(db: Session, user: UserDB, question: str) -> str:
    """Answer a question using the tool layer only (no LLM required)."""
    text = question.strip()
    if not text:
        return "Please type a question."

    lowered = text.lower()
    role = _role_of(user)

    # ---- Greetings ------------------------------------------------
    if re.fullmatch(r"\s*(hi|hello|hey|good\s+morning|good\s+evening)\W*", lowered):
        return (
            "Hello! I can help with appointments, doctor schedules, bed "
            "occupancy, stock levels and patient records. What would you "
            "like to know?"
        )
    if re.search(r"\b(thanks|thank you)\b", lowered):
        return "You're welcome. Ask me anything else."

    # ---- Explicit API errors get a clearer message ----------------
    if lowered.startswith("error:"):
        return text[6:].strip()

    # ---- Booking --------------------------------------------------
    if re.search(r"\b(book|schedule|create)\b", lowered) and "appointment" in lowered:
        doctor_id = _find_doctor_id(db, text)
        date_str = _extract_date(text)
        time_str = _extract_time(text)
        if doctor_id and date_str and time_str:
            return _run(
                db,
                user,
                {
                    "action": "book_appointment",
                    "args": {
                        "doctor_id": doctor_id,
                        "appointment_date": date_str,
                        "appointment_time": time_str,
                        "reason": text[:200],
                    },
                },
            )
        return (
            "To book an appointment I need: doctor name, a date "
            "(YYYY-MM-DD) and a time (HH:MM). For example: "
            "\"book appointment with Dr. Arya Mehta on 2026-10-01 at 10:00\"."
        )

    # ---- Cancelling -----------------------------------------------
    if "cancel" in lowered and "appointment" in lowered:
        appointment_id = _extract_int(text, "appointment")
        if appointment_id:
            return _run(
                db, user, {"action": "cancel_appointment", "args": {"appointment_id": appointment_id}}
            )
        return "Which appointment should I cancel? Give me the appointment id."

    # ---- My appointments ------------------------------------------
    if re.search(r"\bmy\b.*\bappointment", lowered):
        return _run(db, user, {"action": "my_appointments", "args": {}})

    # ---- Doctor schedule ------------------------------------------
    # Matches "schedule of Dr. X", "Dr. X timetable", "when is Dr. X free"
    if re.search(r"\b(schedule|timetime|working\s*hours|availability|free)\b", lowered):
        doctor_id = _find_doctor_id(db, text)
        if doctor_id:
            return _run(db, user, {"action": "doctor_schedule", "args": {"doctor_id": doctor_id}})
        if "doctor" in lowered or _find_doctor_id(db, text) is None:
            return "Which doctor's schedule? Give me a name, e.g. \"Dr. Arya Mehta\"."

    # ---- List doctors ---------------------------------------------
    if re.search(r"\b(list|show|all|which|available)\b", lowered) and "doctor" in lowered:
        return _run(db, user, {"action": "list_doctors", "args": {}})

    # ---- Staff operational queries ---------------------------------
    if re.search(r"\b(bed|occupancy|occupant)\b", lowered):
        return _run(db, user, {"action": "bed_occupancy", "args": {}})

    if re.search(r"\b(stock|inventory|medicine|pharmacy)\b", lowered):
        threshold = _extract_int(text, "threshold") or 20
        return _run(db, user, {"action": "low_stock", "args": {"threshold": threshold}})

    if re.search(r"\b(department)\b", lowered):
        return _run(db, user, {"action": "department_summary", "args": {}})

    if re.search(r"\b(my|assigned)\b.*\b(assignment|patient|ward)\b", lowered) and role in {"admin", "nurse"}:
        return _run(db, user, {"action": "my_assignments", "args": {}})

    if re.search(r"\b(today|summary|overview|dashboard)\b", lowered):
        return _run(db, user, {"action": "today_summary", "args": {}})

    # ---- Clinical lookups (permission-checked inside run_action) ---
    if re.search(r"\b(vital|vitals)\b", lowered):
        patient_id = _find_patient_id(db, text)
        if patient_id:
            return _run(db, user, {"action": "patient_vitals", "args": {"patient_id": patient_id}})
        return "Which patient? Give me the patient id or name."

    if re.search(r"\b(history|record|medical|prescription|lab)\b", lowered):
        patient_id = _find_patient_id(db, text)
        if patient_id:
            return _run(
                db, user, {"action": "patient_medical_history", "args": {"patient_id": patient_id}}
            )
        return "Which patient? Give me the patient id or name."

    if re.search(r"\b(find|search|look\s*up|patient)\b", lowered):
        query = re.sub(r"\b(find|search|look\s*up|for|the|patient|a|an)\b", " ", text).strip()
        if query:
            return _run(db, user, {"action": "patient_lookup", "args": {"query": query}})
        return "Which patient should I look up? Give me a name, email or phone."

    return (
        "The AI assistant is offline, so I can only answer hospital data "
        "questions right now. Try: \"list doctors\", \"my appointments\", "
        "\"book appointment with Dr. Arya Mehta on 2026-10-01 at 10:00\", "
        "\"bed occupancy\", \"low stock\" or \"today summary\"."
    )


# ============================================================
# CHAT ENDPOINT
# ============================================================

@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    system = build_system_prompt(current_user)
    conversation = [{"role": "system", "content": system}]
    conversation.extend({"role": m.role, "content": m.content} for m in request.messages)

    last_user_message = next(
        (m.content for m in reversed(request.messages) if m.role == "user"),
        "",
    )

    for _ in range(3):
        try:
            content = call_llm(conversation)
        except LLMUnavailableError:
            # AI provider is unreachable — answer from the tool layer instead
            # of failing the whole request.
            return ChatResponse(reply=offline_reply(db, current_user, last_user_message))

        actions = extract_actions(content)

        if not actions:
            return ChatResponse(reply=content)

        results = []
        for action in actions:
            results.append(run_action(db, current_user, action))

        conversation.append({"role": "assistant", "content": content})
        conversation.append(
            {"role": "user", "content": "Tool result:\n" + "\n".join(results)}
        )

    return ChatResponse(reply="I'm having trouble completing that. Please try again.")


@router.get("/health")
def chat_health():
    """Report the active AI provider and whether it is reachable."""
    cfg = ai_config()
    return {
        "ai_available": llm_is_available(),
        "provider": cfg["provider"],
        "base_url": cfg["base_url"],
        "model": cfg["model"],
        "api_key_set": bool(cfg["api_key"]) and cfg["api_key"] != "ollama",
        "api_key_preview": _mask(cfg["api_key"]),
        "providers": sorted(AI_PROVIDERS.keys()),
    }


@router.get("/config")
def get_chat_config(current_user: UserDB = Depends(require_admin)):
    """Current AI configuration (key masked). Admin only."""
    cfg = ai_config()
    return {
        "provider": cfg["provider"],
        "base_url": cfg["base_url"],
        "model": cfg["model"],
        "api_key_set": bool(cfg["api_key"]) and cfg["api_key"] != "ollama",
        "api_key_preview": _mask(cfg["api_key"]),
        "providers": {
            name: {"base_url": url, "default_model": model, "needs_key": needs}
            for name, (url, model, needs) in AI_PROVIDERS.items()
        },
    }


@router.post("/config")
def set_chat_config(
    payload: ChatConfigRequest,
    current_user: UserDB = Depends(require_admin),
):
    """Switch the AI provider / store an API key at runtime. Admin only."""
    provider = (payload.provider or ai_config()["provider"]).strip().lower()
    if provider not in AI_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown provider '{provider}'. Choose one of: {', '.join(sorted(AI_PROVIDERS))}.",
        )

    preset_url, preset_model, _ = AI_PROVIDERS[provider]
    current = ai_config()

    api_key = (payload.api_key or "").strip() or current["api_key"]
    base_url = (payload.base_url or "").strip() or preset_url or current["base_url"]
    model = (payload.model or "").strip() or preset_model or current["model"]

    to_save = {
        "provider": provider,
        "api_key": "" if provider == "ollama" else api_key,
        "base_url": base_url,
        "model": model,
    }

    try:
        with open(AI_CONFIG_FILE, "w", encoding="utf-8") as fh:
            json.dump(to_save, fh, indent=2)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save the AI configuration: {exc}",
        ) from exc

    refresh_ai_config()
    cfg = ai_config()

    return {
        "saved": True,
        "provider": cfg["provider"],
        "base_url": cfg["base_url"],
        "model": cfg["model"],
        "api_key_preview": _mask(cfg["api_key"]),
        "ai_available": llm_is_available(),
    }