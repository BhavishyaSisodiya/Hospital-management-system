"""Give the demo accounts consistent, real-looking data.

Demo login accounts are linked to seeded staff via EmployeeDB.email == UserDB.email
(doctor@hms.com -> Dr. Arya Mehta -> DoctorDB id 1, nurse@hms.com -> Lisa Nurse).
patient@hms.com (Demo Patient) previously had zero linked records.

Run:  python seed_demo_data.py   (idempotent - safe to re-run)
"""
import sys
from datetime import date, time, datetime, timedelta, timezone

sys.path.insert(0, ".")

from database import SessionLocal
from models.users import UserDB
from models.patient import PatientDB
from models.employee import EmployeeDB
from models.doctor import DoctorDB
from models.bed import BedDB
from models.admission import AdmissionDB
from models.nurse_assignment import NurseAssignmentDB
from models.appointments import AppointmentDB
from models.medical_record import MedicalRecordDB
from models.test import TestTypeDB
from models.lab import LabTestDB
from models.lab_result import LabResultDB
from models.pharmacy import PharmacyDB
from models.medicine import MedicineDB
from models.prescription import PrescriptionDB
from models.prescription_medicine import PrescriptionMedicineDB
from models.vitals import VitalDB
from models.invoice import InvoiceDB
from models.invoice_item import InvoiceItemDB
from models.payment import PaymentDB
from decimal import Decimal

db = SessionLocal()

try:
    demo_patient = db.query(PatientDB).filter(PatientDB.email == "patient@hms.com").first()
    demo_user = db.query(UserDB).filter(UserDB.email == "patient@hms.com").first()
    if demo_patient is None:
        print("Demo Patient not found; nothing to seed.")
        sys.exit(0)

    doc = db.query(DoctorDB).join(EmployeeDB).filter(EmployeeDB.email == "doctor@hms.com").first()
    nurse = db.query(EmployeeDB).filter(EmployeeDB.email == "nurse@hms.com").first()
    tech = db.query(EmployeeDB).filter(EmployeeDB.email == "rekha@hms.com").first()
    pharm = db.query(PharmacyDB).order_by(PharmacyDB.id).first()
    med = db.query(MedicineDB).filter(MedicineDB.name == "Paracetamol 500mg").first()
    cbc = db.query(TestTypeDB).filter(TestTypeDB.name == "Complete Blood Count").first()
    if not pharm: pharm = db.query(PharmacyDB).first()
    if not med: med = db.query(MedicineDB).first()
    if not cbc: cbc = db.query(TestTypeDB).first()
    if doc is None or nurse is None or tech is None:
        print("Demo doctor/nurse/tech employee link missing; check seed_all.py.")
        sys.exit(0)

    today = date.today()
    done = []
    skipped = []

    # --- Appointments (1 scheduled, 1 completed) with demo doctor ---
    if db.query(AppointmentDB).filter(AppointmentDB.patient_id == demo_patient.id).count() == 0:
        sched = AppointmentDB(patient_id=demo_patient.id, doctor_id=doc.id,
                              appointment_date=today + timedelta(days=7),
                              appointment_time=time(9, 30), reason="Follow-up", status="scheduled")
        db.add(sched); db.flush(); done.append(f"appointment scheduled id={sched.id}")

        past = datetime.now(timezone.utc) - timedelta(days=6)
        old = AppointmentDB(patient_id=demo_patient.id, doctor_id=doc.id,
                            appointment_date=past.date(), appointment_time=time(9, 0),
                            reason="Routine checkup", status="completed")
        db.add(old); db.flush(); done.append(f"appointment completed id={old.id}")
    else:
        skipped.append("appointments")

    # --- Medical record ---
    if db.query(MedicalRecordDB).filter(MedicalRecordDB.patient_id == demo_patient.id).count() == 0:
        mr = MedicalRecordDB(patient_id=demo_patient.id, doctor_id=doc.id,
                             diagnosis="Hypertension Stage 1",
                             notes="Elevated BP readings over two visits. Advised low-salt diet and daily monitoring.",
                             record_date=datetime.now(timezone.utc) - timedelta(days=4))
        db.add(mr); db.flush(); done.append(f"medical record id={mr.id}")
    else:
        skipped.append("medical record")

    # --- Lab test + result ---
    if db.query(LabTestDB).filter(LabTestDB.patient_id == demo_patient.id).count() == 0:
        lt = LabTestDB(test_type_id=cbc.id, patient_id=demo_patient.id, doctor_id=doc.id,
                       technician_id=tech.id, status="completed")
        db.add(lt); db.flush()
        lr = LabResultDB(lab_test_id=lt.id, result="13.8", unit="g/dL",
                         reference_range="12-16",
                         remarks="Within normal range. No further action needed.")
        db.add(lr); db.flush(); done.append(f"lab test id={lt.id} + result")
    else:
        skipped.append("lab test")

    # --- Prescription + medicine ---
    if db.query(PrescriptionDB).filter(PrescriptionDB.patient_id == demo_patient.id).count() == 0:
        pr = PrescriptionDB(patient_id=demo_patient.id, doctor_id=doc.id,
                            pharmacy_id=pharm.id,
                            prescription_date=today - timedelta(days=2))
        db.add(pr); db.flush()
        pm = PrescriptionMedicineDB(prescription_id=pr.id, medicine_id=med.id,
                                    quantity=3, dosage="500mg twice daily",
                                    duration="7 days", instructions="After meals")
        db.add(pm); db.flush(); done.append(f"prescription id={pr.id}")
    else:
        skipped.append("prescription")

    # --- Vitals recorded by demo nurse ---
    if db.query(VitalDB).filter(VitalDB.patient_id == demo_patient.id).count() == 0:
        v = VitalDB(patient_id=demo_patient.id, recorded_by=nurse.id,
                    temperature=Decimal("98.4"), heart_rate=78,
                    blood_pressure_systolic=128, blood_pressure_diastolic=84,
                    respiratory_rate=16, oxygen_saturation=Decimal("97.5"),
                    weight=Decimal("72.00"),
                    recorded_at=datetime.now(timezone.utc) - timedelta(days=3))
        db.add(v); db.flush(); done.append(f"vitals id={v.id}")
    else:
        skipped.append("vitals")

    # --- Admission + nurse assignment (bed must be free) ---
    if db.query(AdmissionDB).filter(
            AdmissionDB.patient_id == demo_patient.id,
            AdmissionDB.status == "admitted").count() == 0:
        used_bed_ids = {a.bed_id for a in db.query(AdmissionDB)
                        .filter(AdmissionDB.status == "admitted").all()}
        bed = db.query(BedDB).filter(BedDB.status == "available").first()
        if bed is None:
            bed = db.query(BedDB).filter(BedDB.id.notin_(used_bed_ids)).first()
        if bed is not None:
            adm = AdmissionDB(patient_id=demo_patient.id, doctor_id=doc.id,
                              bed_id=bed.id,
                              admission_date=datetime.now(timezone.utc) - timedelta(days=3),
                              status="admitted")
            db.add(adm); db.flush()
            bed.status = "occupied"
            na = NurseAssignmentDB(admission_id=adm.id, nurse_id=nurse.id)
            db.add(na); db.flush(); done.append(f"admission id={adm.id} (bed {bed.id}, nurse {nurse.name})")
        else:
            skipped.append("admission (no free bed)")
    else:
        skipped.append("admission")

    # --- Invoice + items + payment ---
    if db.query(InvoiceDB).filter(InvoiceDB.patient_id == demo_patient.id).count() == 0:
        inv = InvoiceDB(patient_id=demo_patient.id, status="paid",
                        invoice_date=datetime.now(timezone.utc) - timedelta(days=2))
        db.add(inv); db.flush()
        items = [
            ("Consultation Fee", 1, Decimal("500.00")),
            (f"Lab Test - {cbc.name}", 1, Decimal(str(cbc.price)) if cbc.price else Decimal("500.00")),
            (f"Medicine - {med.name}", 2, Decimal(str(med.unit_price)) if med.unit_price else Decimal("10.00")),
        ]
        total = Decimal("0.00")
        for desc, qty, uprice in items:
            amt = qty * uprice
            total += amt
            db.add(InvoiceItemDB(invoice_id=inv.id, description=desc, quantity=qty,
                                 unit_price=uprice, amount=amt))
        db.add(PaymentDB(invoice_id=inv.id, amount=total,
                         payment_method="upi", status="completed",
                         transaction_reference=f"TXNDEMO-{inv.id:05d}"))
        db.flush(); done.append(f"invoice id={inv.id} (total {total})")
    else:
        skipped.append("invoice")

    db.commit()
    print("Demo Patient data seeded:")
    if skipped:
        print("  (skipped, already present:", ", ".join(skipped), ")")
    for d in done:
        print("  +", d)

    # --- Credentials summary ---
    print()
    print("=== DEMO LOGIN CREDENTIALS ===")
    print(f"{'Account':<28} {'Email':<30} {'Password':<14} {'Dashboard'}")
    rows = [
        ("Admin", "admin@hms.com", "Admin@123"),
        ("Doctor (Dr. Arya Mehta)", "doctor@hms.com", "Doctor@123"),
        ("Nurse (Lisa)", "nurse@hms.com", "Nurse@123"),
        ("Receptionist", "reception@hms.com", "Recep@123"),
        ("Demo Patient", "patient@hms.com", "Patient@123"),
        ("Patient Rahul Sharma", "patient1@hms.com", "Patient@123"),
        ("Patient Priya Patel", "patient2@hms.com", "Patient@123"),
        ("Patient Amit Kumar", "patient3@hms.com", "Patient@123"),
        ("Patient Sneha Reddy", "patient4@hms.com", "Patient@123"),
        ("Patient Vikram Singh", "patient5@hms.com", "Patient@123"),
        ("Pharmacist", "pharmacist@hms.com", "Pharma@123"),
        ("Lab Technician", "labtech@hms.com", "Labtech@123"),
        ("Accountant", "accountant@hms.com", "Acc@123"),
    ]
    for label, email, pwd in rows:
        print(f"{label:<28} {email:<30} {pwd:<14}")

except Exception as e:
    db.rollback()
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()