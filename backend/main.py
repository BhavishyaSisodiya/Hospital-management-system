from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

import models

from config import settings

from utils.exception_handling import (
    http_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler,
)

from routers.auth import router as auth_router
from routers.dashboard import router as dashboard_router
from routers.chat import router as chat_router
from routers.users import router as users_router
from routers.hospital import router as hospital_router
from routers.departments import router as department_router
from routers.role import router as role_router
from routers.employee import router as employee_router
from routers.doctor import router as doctor_router
from routers.patient import router as patient_router
from routers.appointments import router as appointment_router
from routers.admission import router as admission_router
from routers.doctor_Schedule import router as doctor_schedule_router
from routers.medical_record import router as medical_record_router
from routers.vitals import router as vitals_router
from routers.bed import router as bed_router
from routers.room import router as room_router
from routers.nurse_assignment import router as nurse_assignment_router
from routers.test import router as test_router
from routers.lab import router as lab_router
from routers.lab_results import router as lab_result_router
from routers.medicine import router as medicine_router
from routers.medical_batch import router as medical_batch_router
from routers.pharmacy import router as pharmacy_router
from routers.pharmacyStock import router as pharmacy_stock_router
from routers.prescription import router as prescription_router
from routers.prescription_medicine import router as prescription_medicine_router
from routers.invoices import router as invoice_router
from routers.invoice_item import router as invoice_item_router
from routers.payment import router as payment_router


app = FastAPI(
    title="Hospital Management System API",
    description="Backend API for Hospital Management System",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# EXCEPTION HANDLERS
# ============================================================

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    SQLAlchemyError,
    sqlalchemy_exception_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "type": "validation_error",
                "message": "Request validation failed.",
                "details": exc.errors(),
            },
        },
    )


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(chat_router)

app.include_router(users_router)
app.include_router(hospital_router)
app.include_router(department_router)
app.include_router(role_router)
app.include_router(employee_router)
app.include_router(doctor_router)
app.include_router(patient_router)

app.include_router(appointment_router)
app.include_router(admission_router)
app.include_router(doctor_schedule_router)

app.include_router(medical_record_router)
app.include_router(vitals_router)

app.include_router(bed_router)
app.include_router(room_router)
app.include_router(nurse_assignment_router)

app.include_router(test_router)
app.include_router(lab_router)
app.include_router(lab_result_router)

app.include_router(medicine_router)
app.include_router(medical_batch_router)
app.include_router(pharmacy_router)
app.include_router(pharmacy_stock_router)

app.include_router(prescription_router)
app.include_router(prescription_medicine_router)

app.include_router(invoice_router)
app.include_router(invoice_item_router)
app.include_router(payment_router)


# ============================================================
# FRONTEND (SERVED FROM THE SAME PROCESS)
# ============================================================

from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@app.get("/", include_in_schema=False)
def root():
    if _FRONTEND_DIST.is_dir() and (_FRONTEND_DIST / "index.html").is_file():
        return FileResponse(_FRONTEND_DIST / "index.html")
    return {
        "message": "Hospital Management System API",
        "version": "1.0.0",
        "status": "running",
    }


if _FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=_FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str):
        candidate = (_FRONTEND_DIST / full_path).resolve()
        if (
            candidate.is_file()
            and candidate.is_relative_to(_FRONTEND_DIST.resolve())
        ):
            return FileResponse(candidate)
        return FileResponse(_FRONTEND_DIST / "index.html")