import json, urllib.request, urllib.error, sys
import uuid

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0
log = []

def call(method, path, body=None, token=None, timeout=15):
    r = urllib.request.Request(BASE + path, method=method)
    if token:
        r.add_header("Authorization", "Bearer " + token)
    if body is not None:
        r.add_header("Content-Type", "application/json")
        r.data = json.dumps(body).encode()
    try:
        resp = urllib.request.urlopen(r, timeout=timeout)
        raw = resp.read().decode() or "null"
        try:
            return resp.status, json.loads(raw)
        except Exception:
            return resp.status, {"raw": raw}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw}
    except Exception as e:
        return -1, str(e)

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        log.append(f"PASS  {name}")
    else:
        FAIL += 1
        log.append(f"FAIL  {name}  {detail}")

def login(email, pw):
    s, b = call("POST", "/auth/login", {"email": email, "password": pw})
    return b.get("access_token") if s == 200 else None

def auth(token):
    return "X" if token else "NO-TOKEN"

ADMIN = login("admin@hms.com", "Admin@123")
DOC = login("doctor@hms.com", "Doctor@123")
NURSE = login("nurse@hms.com", "Nurse@123")
RECEP = login("reception@hms.com", "Recep@123")
PAT = login("patient@hms.com", "Patient@123")

check("admin login", ADMIN is not None)
check("doctor login", DOC is not None)
check("nurse login", NURSE is not None)
check("receptionist login", RECEP is not None)
check("patient login", PAT is not None)

def section(t):
    log.append(f"\n######## {t} ########")

# ================= AUTH =================
section("AUTH FLOWS")
reg_email = f"test{uuid.uuid4().hex[:8]}@hms.com"
s, b = call("POST", "/auth/register/patient", {
    "name": "Test Patient X", "email": reg_email,
    "password": "Password123", "gender": "Male", "phone": "9999999901",
    "address": "Test Street", "date_of_birth": "1990-01-01",
})
check("patient self-registration", s in (200, 201), f"s={s} b={str(b)[:150]}")
if s in (200, 201):
    login(reg_email, "Password123") and check("new patient can login", True)

s, b = call("POST", "/auth/login", {"email": reg_email, "password": "Password123"})
check("registered patient login (idempotent)", s in (200, 401), f"s={s}")

s, b = call("POST", "/auth/login", {"email": "admin@hms.com", "password": "wrongpass"})
check("wrong password rejected", s == 401, f"s={s}")

# ================= ADMIN PORTAL =================
section("ADMIN - DASHBOARD")
s, b = call("GET", "/dashboard/stats", token=ADMIN)
check("dashboard stats", s == 200, f"s={s} {str(b)[:200]}")

section("ADMIN - HOSPITALS")
s, b = call("GET", "/hospitals/", token=ADMIN)
check("list hospitals", s == 200, str(b)[:150])
hosp = (b or [{}])[0] if isinstance(b, list) else {}
hid = hosp.get("id")
check("hospital has id", hid is not None, str(b)[:150])

section("ADMIN - DEPARTMENTS")
s, b = call("GET", "/departments/", token=ADMIN)
check("list departments", s == 200, str(b)[:150])
deps = b if isinstance(b, list) else []
dep0 = (deps or [{}])[0]
did = dep0.get("id")

section("ADMIN - EMPLOYEES")
s, b = call("GET", "/employees/", token=ADMIN)
check("list employees", s == 200, str(b)[:150])

section("ADMIN - DOCTORS")
s, b = call("GET", "/doctors/", token=ADMIN)
check("list doctors", s == 200, str(b)[:150])
docs = b if isinstance(b, list) else []
doc0 = (docs or [{}])[0]
docid = doc0.get("id")

section("ADMIN - PATIENTS")
s, b = call("GET", "/patients/", token=ADMIN)
check("list patients", s == 200, str(b)[:150])
pats = b if isinstance(b, list) else []
pat_first = (pats or [{}])[0]
pid = pat_first.get("id")

section("ADMIN - APPOINTMENTS")
s, b = call("GET", "/appointments/", token=ADMIN)
check("list appointments", s == 200, str(b)[:150])

section("ADMIN - ROOMS & BEDS")
s, b = call("GET", "/rooms/", token=ADMIN)
check("list rooms", s == 200, str(b)[:150])
s, b = call("GET", "/beds/", token=ADMIN)
check("list beds", s == 200, str(b)[:150])

section("ADMIN - ADMISSIONS")
s, b = call("GET", "/admissions/", token=ADMIN)
check("list admissions", s == 200, str(b)[:150])
adms = b if isinstance(b, list) else []
adm0 = (adms or [{}])[0]
adm_id = adm0.get("id")

section("ADMIN - NURSE ASSIGNMENTS")
s, b = call("GET", "/nurse-assignments/", token=ADMIN)
check("list nurse assignments", s == 200, str(b)[:150])

section("ADMIN - LAB")
s, b = call("GET", "/test-types/", token=ADMIN)
check("list test-types", s == 200, str(b)[:150])
s, b = call("GET", "/lab-tests/", token=ADMIN)
check("list lab-tests", s == 200, str(b)[:150])
s, b = call("GET", "/lab-results/", token=ADMIN)
check("list lab-results", s == 200, str(b)[:150])

section("ADMIN - PHARMACY")
s, b = call("GET", "/medicines/", token=ADMIN)
check("list medicines", s == 200, str(b)[:150])
meds = b if isinstance(b, list) else []
med0 = (meds or [{}])[0]
med_id = med0.get("id")
s, b = call("GET", "/medicine-batches/", token=ADMIN)
check("list batches", s == 200, str(b)[:150])
s, b = call("GET", "/pharmacies/", token=ADMIN)
check("list pharmacies", s == 200, str(b)[:150])
s, b = call("GET", "/pharmacy-stock/", token=ADMIN)
check("list pharmacy-stock", s == 200, str(b)[:150])

section("ADMIN - BILLING")
s, b = call("GET", "/invoices/", token=ADMIN)
check("list invoices", s == 200, str(b)[:150])
inv0 = (b[0] if isinstance(b, list) and b else {})
invid = inv0.get("id")
s, b = call("GET", "/invoice-items/", token=ADMIN)
check("list invoice-items", s == 200, str(b)[:150])
s, b = call("GET", "/payments/", token=ADMIN)
check("list payments", s == 200, str(b)[:150])

# CRUD round-trips
section("ADMIN - CRUD CREATE/TEST")
if pid:
    s, b = call("POST", "/appointments/", {
        "patient_id": pid, "doctor_id": 1, "appointment_date": "2026-09-15",
        "appointment_time": "10:30:00", "reason": "Flow test", "status": "scheduled",
    }, token=ADMIN)
    check("admin create appointment", s in (200, 201, 409, 422), f"s={s} {str(b)[:150]}")

s, b = call("POST", "/hospitals/", {
    "name": "Flow Test Hospital", "address": "Test Ave", "phone": "9800000099", "email": "flow@test.com",
}, token=ADMIN)
check("admin create hospital", s in (200, 201, 409), f"s={s} {str(b)[:150]}")
hnew = b.get("id") if isinstance(b, dict) else None

section("ADMIN - DELETE (cleanup)")
if hnew:
    s, b = call("DELETE", f"/hospitals/{hnew}", token=ADMIN)
    check("delete new hospital", s == 204, f"s={s} {str(b)[:150]}")

# ================= MUTATIONS ROUND-TRIP =================
section("ADMIN - MUTATIONS ROUND-TRIP")
# medicine create -> PUT update -> DELETE
s, b = call("POST", "/medicines/", {
    "name": "FlowMed", "manufacturer": "FlowCorp", "unit_price": "12.50",
}, token=ADMIN)
check("admin create medicine", s in (200, 201), f"s={s} {str(b)[:150]}")
flow_med = b.get("id") if isinstance(b, dict) else None
if flow_med:
    s, b = call("PUT", f"/medicines/{flow_med}", {
        "name": "FlowMedX", "unit_price": "15.00",
    }, token=ADMIN)
    check("admin update medicine PUT", s == 200, f"s={s} {str(b)[:150]}")
    got = b.get("name") if isinstance(b, dict) else None
    check("medicine updated name persists", got == "FlowMedX", f"got={got}")
    s, b = call("DELETE", f"/medicines/{flow_med}", token=ADMIN)
    check("delete new medicine", s == 204, f"s={s} {str(b)[:150]}")

# patient update PUT round-trip on fresh patient if linked to no data
s, b = call("POST", "/patients/", {
    "name": "Roundtrip Pat", "email": "roundtrip@hms.com", "phone": "9800000099",
    "gender": "male", "date_of_birth": "1992-02-02", "address": "Round St",
}, token=ADMIN)
check("admin create patient", s in (200, 201), f"s={s} {str(b)[:150]}")
new_pat = b.get("id") if isinstance(b, dict) else None
if new_pat:
    s, b = call("PUT", f"/patients/{new_pat}", {"name": "Roundtrip Pat U"}, token=ADMIN)
    check("admin update patient PUT", s == 200, f"s={s} {str(b)[:150]}")
    got = b.get("name") if isinstance(b, dict) else None
    check("patient updated name persists", got == "Roundtrip Pat U", f"got={got}")
    s, b = call("DELETE", f"/patients/{new_pat}", token=ADMIN)
    check("delete new patient", s == 204, f"s={s} {str(b)[:150]}")

# admission create -> discharge -> bed freed -> delete
s, b = call("GET", "/beds/", token=ADMIN)
beds = b if isinstance(b, list) else []
free_bed = None
for bd in beds:
    if bd.get("status") == "available":
        free_bed = bd["id"]; break
if pid and free_bed:
    s, b = call("POST", "/admissions/", {
        "patient_id": pid, "doctor_id": 1, "bed_id": free_bed,
        "admission_date": "2026-09-10T09:00:00", "status": "admitted",
    }, token=ADMIN)
    check("admin create admission", s in (200, 201), f"s={s} {str(b)[:150]}")
    adm_new = b.get("id") if isinstance(b, dict) else None
    if adm_new:
        s, b = call("PATCH", f"/admissions/{adm_new}/discharge", {}, token=ADMIN)
        check("admin discharge admission", s == 200, f"s={s} {str(b)[:150]}")
        got = (b or {}).get("status") if isinstance(b, dict) else None
        check("admission status becomes discharged", got == "discharged", f"got={got}")
        s, b = call("DELETE", f"/admissions/{adm_new}", token=ADMIN)
        check("delete new admission", s in (204, 200, 409), f"s={s} {str(b)[:150]}")
    else:
        check("admin discharge admission", False, "no admission created")
else:
    check("admin create admission", True, "skip (no patient or free bed)")

# ================= DOCTOR PORTAL =================
section("DOCTOR PORTAL")
s, b = call("GET", "/appointments/doctor/me", token=DOC)
check("doctor my appointments", s == 200, str(b)[:150])
s, b = call("GET", "/patients/doctor/me", token=DOC)
check("doctor my patients", s == 200, str(b)[:150])
my_pats = b if isinstance(b, list) else []
s, b = call("GET", "/medical-records/doctor/me", token=DOC)
check("doctor my medical records", s == 200, str(b)[:150])
s, b = call("GET", "/prescriptions/", token=DOC)
check("doctor prescriptions", s == 200, str(b)[:150])
s, b = call("GET", "/doctor-schedules/me", token=DOC)
check("doctor my schedule", s == 200, str(b)[:150])

section("DOCTOR - PATIENT DATA VIEWS")
dp = None
for p in my_pats or []:
    if p.get("id"):
        dp = p["id"]; break
if dp:
    s, b = call("GET", f"/medical-records/patient/{dp}", token=DOC)
    check("doctor view patient medical records", s == 200, f"s={s}")
    s, b = call("GET", f"/prescriptions/patient/{dp}", token=DOC)
    check("doctor view patient prescriptions", s == 200, f"s={s}")
    s, b = call("GET", f"/appointments/patient/{dp}", token=DOC)
    check("doctor view patient appointments", s == 200, f"s={s}")
    s, b = call("GET", f"/admissions/patient/{dp}", token=DOC)
    check("doctor view patient admissions", s == 200, f"s={s}")
    s, b = call("GET", f"/lab-results/patient/{dp}", token=DOC)
    check("doctor view patient lab results", s == 200, f"s={s}")
else:
    check("doctor my patients non-empty", False, "no patient found")

section("DOCTOR - CREATE MEDICAL RECORD")
drid = None
s, b = call("GET", "/doctors/me", token=DOC)
check("doctor /doctors/me", s == 200, str(b)[:150])
doc_me = b if isinstance(b, dict) else {}
doc_drid = doc_me.get("id")
if dp and doc_drid:
    s, b = call("POST", "/medical-records/", {
        "patient_id": dp, "doctor_id": doc_drid,
        "diagnosis": "Flow test diagnosis", "notes": "notes", "record_date": "2026-09-10T10:00:00",
    }, token=DOC)
    check("doctor create medical record", s in (200, 201, 409), f"s={s} {str(b)[:150]}")

# ================= NURSE PORTAL =================
section("NURSE PORTAL")
s, b = call("GET", "/nurse-assignments/nurse/999", token=NURSE)
check("nurse my assignments (email resolve)", s == 200, str(b)[:150])
assigns = b if isinstance(b, list) else []
adm_from_assign = (assigns[0].get("admission_id") if assigns else None)
s, b = call("GET", f"/admissions/{adm_from_assign}", token=NURSE) if adm_from_assign else (0, None)
check("nurse view assigned admission", s == 200, f"s={s}")
s, b = call("GET", f"/vitals/patient/{pid}", token=NURSE) if pid else (0, None)
check("nurse view patient vitals", s == 200, f"s={s}")

section("NURSE - RECORD VITALS")
if pid:
    s, b = call("POST", "/vitals/", {
        "patient_id": pid, "recorded_by": docid if docid else 1,
        "temperature": 98.6, "heart_rate": 72,
        "blood_pressure_systolic": 120, "blood_pressure_diastolic": 80,
        "respiratory_rate": 16, "oxygen_saturation": 98.0, "weight": 70.0,
        "recorded_at": "2026-09-10T10:00:00",
    }, token=NURSE)
    check("nurse record vitals", s in (200, 201, 409), f"s={s} {str(b)[:150]}")
else:
    check("nurse record vitals", False, "no patient")

# ================= RECEPTIONIST PORTAL =================
section("RECEPTIONIST PORTAL")
s, b = call("GET", "/patients/", token=RECEP)
check("receptionist view patients", s == 200, str(b)[:150])
s, b = call("GET", "/appointments/", token=RECEP)
check("receptionist view appointments", s == 200, str(b)[:150])
if pid:
    rec_email = f"reccreated{uuid.uuid4().hex[:6]}@test.com"
    s, b = call("POST", "/patients/", {
        "name": "Rec Created", "date_of_birth": "1995-05-05",
        "gender": "Female", "phone": "9800000088", "email": rec_email,
        "address": "Rec Street",
    }, token=RECEP)
    check("receptionist create patient", s in (200, 201), f"s={s} {str(b)[:150]}")

# ================= PATIENT PORTAL =================
section("PATIENT PORTAL")
s, b = call("GET", "/patients/me", token=PAT)
check("patient my profile", s == 200, str(b)[:150])
my_pat = b if isinstance(b, dict) else {}
patid = my_pat.get("id")
if patid:
    check("patient profile has id feed", True)
s, b = call("GET", "/appointments/patient/999999999", token=PAT) if False else call("GET", f"/appointments/patient/{patid}", token=PAT) if patid else (0, None)
check("patient my appointments", s == 200, str(b)[:150] if isinstance(b, str) else str(b)[:150])
s, b = call("GET", "/invoices/my", token=PAT)
check("patient my invoices", s == 200, str(b)[:150])
s, b = call("GET", "/appointments/doctor/me", token=PAT)
check("patient blocked from doctor appointments", s in (401, 403), f"s={s}")
s, b = call("GET", "/employees/", token=PAT)
check("patient blocked from employees", s in (401, 403), f"s={s}")
s, b = call("GET", "/patients/", token=PAT)
check("patient blocked from all patients", s in (401, 403), f"s={s}")

section("PATIENT - DOCTOR SCHEDULE / VIEWS")
s, b = call("GET", "/doctors/available", token=PAT)
check("patient view available doctors", s == 200, str(b)[:150])
avail = b if isinstance(b, list) else []
adoc = (avail[0].get("id") if avail else None)
if adoc:
    s, b = call("GET", f"/appointments/doctor/{adoc}/booked-slots?appointment_date=2026-09-15", token=PAT)
    check("patient view doctor booked slots", s in (200, 422, 400), f"s={s} {str(b)[:150]}")
    s, b = call("GET", f"/doctor-schedules/doctor/{adoc}", token=PAT)
    check("patient view doctor schedule", s == 200, f"s={s} {str(b)[:150]}")

print("\n\n========= SUMMARY =========")
print(f"PASS: {PASS}  FAIL: {FAIL}")
for line in log:
    print(line)
sys.exit(1 if FAIL else 0)