-- ============================================================
-- Enrich HMS database: fill sparse tables with realistic, FK-safe data
-- Idempotent: safe to re-run (uses NOT EXISTS guards)
-- ============================================================

-- 1) APPOINTMENTS: add upcoming + historical for all patients/doctors
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
SELECT p.id, d.id, (CURRENT_DATE + off)::date, slot, 'General consultation', 'scheduled'
FROM (VALUES
    (1, 6, 3,  '10:00'::time),
    (2, 7, 4,  '11:30'::time),
    (3, 8, 5,  '09:30'::time),
    (4, 9, 3,  '14:00'::time),
    (5, 10, 4, '15:30'::time),
    (6, 11, 5, '16:00'::time),
    (1, 8, 7,  '10:00'::time),
    (2, 9, 8,  '11:30'::time),
    (3, 10, 9, '09:30'::time),
    (4, 11, 10,'14:00'::time)
) AS v(patient_id, doctor_id, off, slot)
JOIN patients p ON p.id = v.patient_id
JOIN doctors  d ON d.id = v.doctor_id
WHERE NOT EXISTS (
    SELECT 1 FROM appointments a
    WHERE a.patient_id = v.patient_id
      AND a.doctor_id = v.doctor_id
      AND a.appointment_date = (CURRENT_DATE + v.off)::date
      AND a.appointment_time = v.slot
)
ON CONFLICT ON CONSTRAINT uq_appointments_doctor_datetime DO NOTHING;

-- 2) ADMISSIONS: add discharged history + new current admissions
-- Only use beds currently 'available' so occupied beds stay consistent
INSERT INTO admissions (patient_id, doctor_id, bed_id, admission_date, discharge_date, status)
SELECT v.patient_id, v.doctor_id, b.id,
       v.admit_days, v.admit_days + (v.days || ' days')::interval, v.status
FROM (VALUES
    (3, 3, 3, (CURRENT_DATE - 40)::timestamp, 6, 'discharged'::varchar),
    (4, 4, 5, (CURRENT_DATE - 30)::timestamp, 4, 'discharged'::varchar),
    (5, 2, 6, (CURRENT_DATE - 20)::timestamp, 3, 'discharged'::varchar),
    (6, 3, 7, (CURRENT_DATE - 12)::timestamp, 2, 'discharged'::varchar),
    (3, 8, 8, (CURRENT_DATE - 2)::timestamp, NULL, 'admitted'::varchar),
    (5, 9, 9, (CURRENT_DATE - 1)::timestamp, NULL, 'admitted'::varchar)
) AS v(patient_id, doctor_id, bed_id, admit_days, days, status)
JOIN beds b ON b.id = v.bed_id
WHERE NOT EXISTS (SELECT 1 FROM admissions a WHERE a.patient_id = v.patient_id AND a.bed_id = v.bed_id)
  AND NOT EXISTS (SELECT 1 FROM admissions a WHERE a.bed_id = v.bed_id AND a.status = 'admitted');

-- 3) NURSE ASSIGNMENTS: cover every admission with a nurse
INSERT INTO nurse_assignments (admission_id, nurse_id, assigned_at, unassigned_at)
SELECT a.id, n.nurse_id, a.admission_date, NULL
FROM admissions a
CROSS JOIN (VALUES (5), (6), (11)) AS n(nurse_id)
WHERE NOT EXISTS (
    SELECT 1 FROM nurse_assignments na
    WHERE na.admission_id = a.id AND na.nurse_id = n.nurse_id
)
ON CONFLICT DO NOTHING;

-- 4) MEDICAL RECORDS: diagnosis history for all patients
INSERT INTO medical_records (patient_id, doctor_id, diagnosis, notes, record_date)
SELECT v.patient_id, v.doctor_id, v.diagnosis, v.notes, v.rdate
FROM (VALUES
    (1, 1, 'Seasonal Allergic Rhinitis', 'Patient advised to avoid dust and dust mites. Started on antihistamines. Symptoms to be reviewed in 2 weeks.', (CURRENT_DATE - 10)::timestamp),
    (2, 2, 'Migraine with Aura', 'Classic aura symptoms. Triggered by stress and bright light. Started on sumatriptan prophylaxis. Sleep hygiene counselling given.', (CURRENT_DATE - 8)::timestamp),
    (3, 3, 'Lower Back Pain (Lumbar Disc)', 'L4-L5 disc prolapse on MRI. Managed conservatively with physiotherapy. Avoid heavy lifting for 6 weeks.', (CURRENT_DATE - 7)::timestamp),
    (4, 9, 'Type 2 Diabetes - Controlled', 'HbA1c improved from 8.4% to 6.9%. Continue metformin 500mg BD. Diet counselling and home glucose monitoring advised.', (CURRENT_DATE - 6)::timestamp),
    (5, 2, 'Iron Deficiency Anaemia', 'Haemoglobin 8.9 g/dL. Started on oral iron with vitamin C. Repeat CBC in 4 weeks.', (CURRENT_DATE - 5)::timestamp),
    (6, 8, 'Acute Gastritis', 'Due to irregular meals and NSAID use. Started on PPIs. Advised dietary modification and to avoid self-medication.', (CURRENT_DATE - 4)::timestamp),
    (1, 6, 'Essential Hypertension - Stable', 'Blood pressure well controlled on amlodipine 5mg. Lifestyle counselling reinforced. Monitor home BP daily.', (CURRENT_DATE - 3)::timestamp),
    (2, 7, 'Chronic Kidney Disease Stage 2', 'eGFR 68 mL/min. Nephrology follow-up planned. Nephrotoxin avoidance advised. Monitor serum creatinine monthly.', (CURRENT_DATE - 2)::timestamp)
) AS v(patient_id, doctor_id, diagnosis, notes, rdate)
JOIN patients p ON p.id = v.patient_id
JOIN doctors  d ON d.id = v.doctor_id
WHERE NOT EXISTS (
    SELECT 1 FROM medical_records m
    WHERE m.patient_id = v.patient_id AND m.diagnosis = v.diagnosis
);

-- 5) VITALS: recent readings for all patients
INSERT INTO vitals (patient_id, recorded_by, recorded_at, temperature, heart_rate,
                   blood_pressure_systolic, blood_pressure_diastolic,
                   respiratory_rate, oxygen_saturation, weight)
SELECT v.patient_id, v.recorded_by, v.rdate, v.temp, v.hr, v.sys, v.dia, v.rr, v.spo2, v.wt
FROM (VALUES
    (1, 6,  (CURRENT_DATE - 1)::timestamptz, 98.4::numeric, 78, 128, 82, 16, 98.20, 74.50),
    (2, 6,  (CURRENT_DATE - 1)::timestamptz, 98.1, 72, 118, 76, 15, 98.80, 68.20),
    (3, 5,  (CURRENT_DATE - 1)::timestamptz, 99.0, 88, 130, 85, 18, 97.50, 78.90),
    (4, 11, (CURRENT_DATE - 1)::timestamptz, 98.6, 95, 135, 88, 17, 98.00, 82.30),
    (5, 11, (CURRENT_DATE - 1)::timestamptz, 97.8, 70, 112, 72, 14, 99.10, 55.40),
    (6, 5,  (CURRENT_DATE - 1)::timestamptz, 98.9, 82, 124, 79, 16, 98.40, 70.10),
    (3, 6,  CURRENT_TIMESTAMP,          98.2, 80, 126, 81, 16, 98.30, 78.50),
    (5, 11, CURRENT_TIMESTAMP,          97.6, 68, 118, 74, 15, 99.00, 55.20)
) AS v(patient_id, recorded_by, rdate, temp, hr, sys, dia, rr, spo2, wt)
JOIN patients p ON p.id = v.patient_id
WHERE NOT EXISTS (
    SELECT 1 FROM vitals vi
    WHERE vi.patient_id = v.patient_id AND vi.recorded_at = v.rdate
);

-- 6) LAB TESTS + RESULTS: every completed test gets exactly one result (unique constraint on lab_test_id)
INSERT INTO lab_tests (test_type_id, patient_id, doctor_id, technician_id, test_date, status)
SELECT v.test_type_id, v.patient_id, v.doctor_id, 14, v.tdate, v.status
FROM (VALUES
    (1, 5, 2,  (CURRENT_DATE - 9)::timestamptz, 'completed'::varchar),
    (2, 6, 3,  (CURRENT_DATE - 8)::timestamptz, 'completed'::varchar),
    (3, 4, 9,  (CURRENT_DATE - 7)::timestamptz, 'completed'::varchar),
    (4, 5, 2,  (CURRENT_DATE - 6)::timestamptz, 'in_progress'::varchar),
    (5, 3, 3,  (CURRENT_DATE - 6)::timestamptz, 'completed'::varchar),
    (6, 2, 7,  (CURRENT_DATE - 5)::timestamptz, 'pending'::varchar),
    (7, 4, 9,  (CURRENT_DATE - 4)::timestamptz, 'completed'::varchar),
    (1, 6, 3,  (CURRENT_DATE - 3)::timestamptz, 'completed'::varchar),
    (3, 5, 2,  (CURRENT_DATE - 2)::timestamptz, 'completed'::varchar),
    (5, 1, 6,  (CURRENT_DATE - 1)::timestamptz, 'completed'::varchar),
    (2, 4, 9,  CURRENT_TIMESTAMP,          'pending'::varchar)
) AS v(test_type_id, patient_id, doctor_id, tdate, status)
JOIN patients p ON p.id = v.patient_id
JOIN test_types tt ON tt.id = v.test_type_id
WHERE NOT EXISTS (
    SELECT 1 FROM lab_tests lt
    WHERE lt.patient_id = v.patient_id AND lt.test_type_id = v.test_type_id AND lt.test_date = v.tdate
);

-- results for every completed test that lacks one
INSERT INTO lab_results (lab_test_id, result, unit, reference_range, remarks, reported_at)
SELECT lt.id, v.result, v.unit, v.ref, v.remarks, lt.test_date + interval '6 hours'
FROM lab_tests lt
JOIN test_types tt ON tt.id = lt.test_type_id
JOIN (VALUES
    ('Complete Blood Count', 'Haemoglobin 13.8, WBC 7200, Platelets 2.4L', 'g/dL & cells', 'Hb 13-17, WBC 4000-11000', 'All parameters within normal limits'),
    ('Blood Sugar Fasting', 'Fasting glucose 96', 'mg/dL', '70-100', 'Normal fasting glucose, diabetic range excluded'),
    ('Lipid Profile',      'Total cholesterol 182, HDL 48, Triglycerides 130', 'mg/dL', 'Total <200, HDL >40', 'Borderline cholesterol, lifestyle modification advised'),
    ('Thyroid Panel',      'TSH 2.4, Free T3 1.2, Free T4 1.05', 'mIU/L', 'TSH 0.4-4.0', 'Euthyroid state, no thyroid abnormality'),
    ('X-Ray Chest',        'Normal cardiomediastinal silhouette, clear lung fields', 'Report', 'No consolidation', 'No active cardiopulmonary disease'),
    ('MRI Brain',          'No intracranial haemorrhage or mass lesion', 'Report', 'Normal study', 'Normal study'),
    ('ECG',                'Sinus rhythm, 72 bpm, PR 160ms', 'Report', 'Normal ECG', 'Normal sinus rhythm')
) AS v(ttname, result, unit, ref, remarks) ON v.ttname = tt.name
WHERE lt.status = 'completed'
  AND NOT EXISTS (SELECT 1 FROM lab_results lr WHERE lr.lab_test_id = lt.id);

-- 7) MEDICINES: expand catalogue
INSERT INTO medicines (name, manufacturer, unit_price)
SELECT v.name, v.mfr, v.price FROM (VALUES
    ('Ibuprofen 400mg',      'Dr. Reddy''s', 14.00),
    ('Azithromycin 500mg',   'Alkem Labs',  68.00),
    ('Pantoprazole 40mg',    'Abbott',      32.00),
    ('Salbutamol Inhaler',   'Cipla',      210.00),
    ('Ondansetron 4mg',      'Sun Pharma',  22.00),
    ('Diclofenac Gel',       'Lupin',       95.00),
    ('Loratadine 10mg',      'Ranbaxy',     11.00),
    ('Montelukast 10mg',     'MSD',         85.00),
    ('Insulin Glargine',     'Sanofi',     950.00),
    ('Levothyroxine 50mcg',  'Abbott',      75.00),
    ('Rosuvastatin 10mg',    'Ranbaxy',     42.00),
    ('Clopidogrel 75mg',     'Sanofi',      55.00)
) AS v(name, mfr, price)
WHERE NOT EXISTS (SELECT 1 FROM medicines m WHERE m.name = v.name);

-- 8) BATCHES for all medicines (unique per medicine+batch_number)
INSERT INTO medicine_batches (medicine_id, batch_number, expiry_date, unit_cost)
SELECT m.id, 'BATCH-' || LPAD(m.id::text, 3, '0') || '-B',
       (CURRENT_DATE + (180 + (m.id * 37) % 500))::date,
       m.unit_price * 0.85
FROM medicines m
WHERE NOT EXISTS (SELECT 1 FROM medicine_batches b WHERE b.medicine_id = m.id);

-- 9) PHARMACY STOCK for every batch
INSERT INTO pharmacy_stock (pharmacy_id, batch_id, quantity)
SELECT 1, b.id, 50 + (b.id * 23) % 250
FROM medicine_batches b
WHERE NOT EXISTS (SELECT 1 FROM pharmacy_stock ps WHERE ps.batch_id = b.id);

-- 10) PRESCRIPTIONS + MEDICINES: for all patients
INSERT INTO prescriptions (patient_id, doctor_id, prescription_date, pharmacy_id, lab_test_id)
SELECT v.patient_id, v.doctor_id, v.pdate, 1, NULL
FROM (VALUES
    (1, 6, (CURRENT_DATE - 1)::date),
    (2, 7, (CURRENT_DATE - 1)::date),
    (3, 8, (CURRENT_DATE - 2)::date),
    (4, 9, (CURRENT_DATE - 2)::date),
    (5, 2, (CURRENT_DATE - 3)::date),
    (6, 3, (CURRENT_DATE - 3)::date),
    (1, 1, (CURRENT_DATE - 9)::date),
    (2, 2, (CURRENT_DATE - 8)::date),
    (4, 9, (CURRENT_DATE - 6)::date),
    (6, 8, (CURRENT_DATE - 4)::date)
) AS v(patient_id, doctor_id, pdate)
JOIN patients p ON p.id = v.patient_id
JOIN doctors  d ON d.id = v.doctor_id
WHERE NOT EXISTS (
    SELECT 1 FROM prescriptions pr
    WHERE pr.patient_id = v.patient_id AND pr.doctor_id = v.doctor_id AND pr.prescription_date = v.pdate
);

-- link medicines to prescriptions (PK = prescription_id + medicine_id)
INSERT INTO prescription_medicines (prescription_id, medicine_id, quantity, dosage, duration, instructions)
SELECT pr.id, m.id, v.qty, v.dosage, v.duration, v.instr
FROM prescriptions pr
JOIN (VALUES
    (1, 1, 30, '10 units daily',    '30 days', 'Take after food with warm water'),
    (1, 2,  1, '500mg three times a day', '5 days',  'Complete the full antibiotic course'),
    (1, 4,  1, '10mg once at night', '30 days',  'Take in the evening after dinner')
) AS v(idx, medicine_id, qty, dosage, duration, instr) ON v.idx = pr.id
JOIN medicines m ON m.id = v.medicine_id
WHERE NOT EXISTS (
    SELECT 1 FROM prescription_medicines pm
    WHERE pm.prescription_id = pr.id AND pm.medicine_id = v.medicine_id
);

-- give every prescription at least one medicine line
INSERT INTO prescription_medicines (prescription_id, medicine_id, quantity, dosage, duration, instructions)
SELECT pr.id, m.id, 1, 'As directed by physician', '7 days', 'Follow the prescription strictly'
FROM prescriptions pr
JOIN LATERAL (
    SELECT id FROM medicines ORDER BY id LIMIT 1
) m ON TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM prescription_medicines pm WHERE pm.prescription_id = pr.id
);

-- 11) INVOICES + ITEMS for all patients
INSERT INTO invoices (patient_id, invoice_date, status)
SELECT v.patient_id, v.idate, v.status
FROM (VALUES
    (5, (CURRENT_DATE - 9)::timestamptz, 'unpaid'::varchar),
    (6, (CURRENT_DATE - 8)::timestamptz, 'partially_paid'::varchar),
    (3, (CURRENT_DATE - 7)::timestamptz, 'paid'::varchar),
    (5, (CURRENT_DATE - 4)::timestamptz, 'paid'::varchar),
    (6, (CURRENT_DATE - 2)::timestamptz, 'unpaid'::varchar)
) AS v(patient_id, idate, status)
JOIN patients p ON p.id = v.patient_id
WHERE NOT EXISTS (
    SELECT 1 FROM invoices i WHERE i.patient_id = v.patient_id AND i.invoice_date = v.idate
);

-- items for every invoice (consultation + a lab test)
INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, amount)
SELECT i.id, 'Consultation Fee', 1, 500.00, 500.00
FROM invoices i
WHERE NOT EXISTS (
    SELECT 1 FROM invoice_items ii WHERE ii.invoice_id = i.id AND ii.description = 'Consultation Fee'
);

INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, amount)
SELECT i.id, 'Diagnostic Services', 1, tt.price, tt.price
FROM invoices i
JOIN LATERAL (SELECT id, price FROM test_types ORDER BY id LIMIT 1) tt ON TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM invoice_items ii
    WHERE ii.invoice_id = i.id AND ii.description = 'Diagnostic Services'
);

-- 12) PAYMENTS: for paid + partially_paid invoices
INSERT INTO payments (invoice_id, amount, payment_date, payment_method, status, transaction_reference)
SELECT i.id,
       CASE WHEN i.status = 'partially_paid' THEN ROUND(it.total * 0.5, 2) ELSE it.total END,
       i.invoice_date + interval '2 hours',
       v.method,
       'completed',
       'TXN-' || LPAD(i.id::text, 4, '0') || '-' || UPPER(SUBSTRING(v.method, 1, 3))
FROM invoices i
JOIN (SELECT invoice_id, SUM(amount) AS total FROM invoice_items GROUP BY invoice_id) it
     ON it.invoice_id = i.id
JOIN (VALUES
    ('cash'::varchar),
    ('card'),
    ('upi'),
    ('bank_transfer'),
    ('other')
) AS v(method) ON true
WHERE i.status IN ('paid', 'partially_paid')
  AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.invoice_id = i.id);

-- 13) DOCTOR SCHEDULES: every doctor has weekly slots
INSERT INTO doctor_schedules (doctor_id, day_of_week, start_time, end_time)
SELECT d.id, v.day, v.start_t::time, v.end_t::time
FROM doctors d
CROSS JOIN (VALUES
    ('monday',    '09:00', '13:00'),
    ('monday',    '15:00', '18:00'),
    ('tuesday',   '09:00', '13:00'),
    ('wednesday', '09:00', '13:00'),
    ('thursday',  '10:00', '14:00'),
    ('friday',    '09:00', '13:00'),
    ('saturday',  '10:00', '14:00')
) AS v(day, start_t, end_t)
WHERE NOT EXISTS (
    SELECT 1 FROM doctor_schedules ds
    WHERE ds.doctor_id = d.id AND ds.day_of_week = v.day AND ds.start_time = v.start_t::time
);

-- 14) BEDS for existing rooms + a couple of new rooms
INSERT INTO rooms (room_number, room_type, status, hospital_id, department_id)
SELECT v.rn, v.rt, 'available', 1, v.dept
FROM (VALUES
    ('PVT-303', 'Private',  1),
    ('PVT-304', 'Private',  1),
    ('GEN-203', 'General',  5),
    ('EMR-001', 'Emergency', 6),
    ('ICU-102', 'ICU',      6),
    ('ONC-401', 'Oncology', 8)
) AS v(rn, rt, dept)
WHERE NOT EXISTS (SELECT 1 FROM rooms r WHERE r.hospital_id = 1 AND r.room_number = v.rn);

INSERT INTO beds (room_id, bed_number, status)
SELECT r.id, v.bn, 'available'
FROM rooms r
CROSS JOIN (VALUES ('A'), ('B'), ('C')) AS v(bn)
WHERE NOT EXISTS (SELECT 1 FROM beds b WHERE b.room_id = r.id AND b.bed_number = v.bn);
