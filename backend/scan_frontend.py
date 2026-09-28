"""Scan every route for console errors via Playwright."""
import sys, json
sys.path.insert(0, "C:\\Users\\ASHUTOSH\\AppData\\Local\\Temp\\opencode\\pwlib")
from playwright.sync_api import sync_playwright

BASE = "http://localhost:5173"
API = "http://127.0.0.1:8000"
RESULTS = []

ROUTES = [
    "/", "/login", "/register",
    "/admin/dashboard", "/admin/hospitals", "/admin/employees", "/admin/doctors",
    "/admin/patients", "/admin/departments", "/admin/appointments", "/admin/admissions",
    "/admin/rooms", "/admin/nurse-assignments", "/admin/test-types", "/admin/lab-tests",
    "/admin/lab-results", "/admin/medicines", "/admin/medicine-batches", "/admin/pharmacies",
    "/admin/pharmacy-stock", "/admin/invoices", "/admin/invoice-items", "/admin/payments",
    "/doctor/dashboard", "/doctor/appointments", "/doctor/patients",
    "/doctor/medical-records", "/doctor/prescriptions", "/doctor/schedule",
    "/nurse/dashboard", "/nurse/assigned-patients", "/nurse/record-vitals",
    "/receptionist/dashboard", "/receptionist/patients", "/receptionist/appointments",
    "/patient/dashboard",
]


def login(page, email, password):
    page.goto(f"{BASE}/login", wait_until="networkidle")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_timeout(1500)


def scan_routes(page, routes, label):
    errors = []
    for route in routes:
        page.goto(f"{BASE}{route}", wait_until="networkidle")
        page.wait_for_timeout(800)
        if errors_on_page:
            errors.append({"route": route, "errors": errors_on_page})
    return errors


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # ── Admin scan ──────────────────────────────────────────
    page = browser.new_page()
    console_errors = []
    page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ("error",) else None)
    page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {err}"))
    page.on("response", lambda resp: console_errors.append(f"[{resp.status}] {resp.url}") if resp.status >= 400 else None)

    login(page, "admin@hms.com", "Admin@123")
    page.wait_for_timeout(1000)

    admin_routes = [r for r in ROUTES if r.startswith("/admin")]
    print(f"\n=== SCANNING {len(admin_routes)} ADMIN ROUTES ===")
    for route in admin_routes:
        errs_before = len(console_errors)
        page.goto(f"{BASE}{route}", wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(1200)
        new_errs = console_errors[errs_before:]
        if new_errs:
            print(f"  FAIL {route}:")
            for e in new_errs:
                print(f"    {e}")
        else:
            print(f"  OK   {route}")

    # ── Doctor scan ─────────────────────────────────────────
    page2 = browser.new_page()
    console_errors2 = []
    page2.on("console", lambda msg: console_errors2.append(f"[{msg.type}] {msg.text}") if msg.type in ("error",) else None)
    page2.on("pageerror", lambda err: console_errors2.append(f"[pageerror] {err}"))
    page2.on("response", lambda resp: console_errors2.append(f"[{resp.status}] {resp.url}") if resp.status >= 400 else None)

    login(page2, "doctor@hms.com", "Doctor@123")
    page2.wait_for_timeout(1000)

    doctor_routes = [r for r in ROUTES if r.startswith("/doctor")]
    print(f"\n=== SCANNING {len(doctor_routes)} DOCTOR ROUTES ===")
    for route in doctor_routes:
        errs_before = len(console_errors2)
        page2.goto(f"{BASE}{route}", wait_until="networkidle", timeout=15000)
        page2.wait_for_timeout(1200)
        new_errs = console_errors2[errs_before:]
        if new_errs:
            print(f"  FAIL {route}:")
            for e in new_errs:
                print(f"    {e}")
        else:
            print(f"  OK   {route}")

    # ── Nurse scan ──────────────────────────────────────────
    page3 = browser.new_page()
    console_errors3 = []
    page3.on("console", lambda msg: console_errors3.append(f"[{msg.type}] {msg.text}") if msg.type in ("error",) else None)
    page3.on("pageerror", lambda err: console_errors3.append(f"[pageerror] {err}"))
    page3.on("response", lambda resp: console_errors3.append(f"[{resp.status}] {resp.url}") if resp.status >= 400 else None)

    login(page3, "nurse@hms.com", "Nurse@123")
    page3.wait_for_timeout(1000)

    nurse_routes = [r for r in ROUTES if r.startswith("/nurse")]
    print(f"\n=== SCANNING {len(nurse_routes)} NURSE ROUTES ===")
    for route in nurse_routes:
        errs_before = len(console_errors3)
        page3.goto(f"{BASE}{route}", wait_until="networkidle", timeout=15000)
        page3.wait_for_timeout(1200)
        new_errs = console_errors3[errs_before:]
        if new_errs:
            print(f"  FAIL {route}:")
            for e in new_errs:
                print(f"    {e}")
        else:
            print(f"  OK   {route}")

    # ── Receptionist scan ───────────────────────────────────
    page4 = browser.new_page()
    console_errors4 = []
    page4.on("console", lambda msg: console_errors4.append(f"[{msg.type}] {msg.text}") if msg.type in ("error",) else None)
    page4.on("pageerror", lambda err: console_errors4.append(f"[pageerror] {err}"))
    page4.on("response", lambda resp: console_errors4.append(f"[{resp.status}] {resp.url}") if resp.status >= 400 else None)

    login(page4, "reception@hms.com", "Recep@123")
    page4.wait_for_timeout(1000)

    receptionist_routes = [r for r in ROUTES if r.startswith("/receptionist")]
    print(f"\n=== SCANNING {len(receptionist_routes)} RECEPTIONIST ROUTES ===")
    for route in receptionist_routes:
        errs_before = len(console_errors4)
        page4.goto(f"{BASE}{route}", wait_until="networkidle", timeout=15000)
        page4.wait_for_timeout(1200)
        new_errs = console_errors4[errs_before:]
        if new_errs:
            print(f"  FAIL {route}:")
            for e in new_errs:
                print(f"    {e}")
        else:
            print(f"  OK   {route}")

    # ── Landing + login ─────────────────────────────────────
    page5 = browser.new_page()
    console_errors5 = []
    page5.on("console", lambda msg: console_errors5.append(f"[{msg.type}] {msg.text}") if msg.type in ("error",) else None)
    page5.on("pageerror", lambda err: console_errors5.append(f"[pageerror] {err}"))
    page5.on("response", lambda resp: console_errors5.append(f"[{resp.status}] {resp.url}") if resp.status >= 400 else None)

    print(f"\n=== SCANNING PUBLIC ROUTES ===")
    for route in ["/", "/login"]:
        errs_before = len(console_errors5)
        page5.goto(f"{BASE}{route}", wait_until="networkidle", timeout=15000)
        page5.wait_for_timeout(1200)
        new_errs = console_errors5[errs_before:]
        if new_errs:
            print(f"  FAIL {route}:")
            for e in new_errs:
                print(f"    {e}")
        else:
            print(f"  OK   {route}")

    browser.close()
    print("\n=== SCAN COMPLETE ===")
