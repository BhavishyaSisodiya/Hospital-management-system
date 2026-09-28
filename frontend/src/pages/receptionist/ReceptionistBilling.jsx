import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { getPatients } from "../../api/patients";
import { getDoctors } from "../../api/doctors";
import { getAppointments } from "../../api/appointments";
import { getAdmissions } from "../../api/admissions";
import { createBillingInvoice } from "../../api/billing";

function ReceptionistBilling() {

    const [tab, setTab] = useState("consult");

    const [patients, setPatients] = useState([]);
    const [doctors, setDoctors] = useState([]);
    const [appointments, setAppointments] = useState([]);
    const [admissions, setAdmissions] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const [consultPatientId, setConsultPatientId] = useState("");
    const [consultDoctorId, setConsultDoctorId] = useState("");
    const [consultAppointmentId, setConsultAppointmentId] = useState("");
    const [consultDescription, setConsultDescription] = useState(
        "Doctor consultation fee"
    );
    const [consultAmount, setConsultAmount] = useState("200");

    const [dischargePatientId, setDischargePatientId] = useState("");
    const [dischargeAdmissionId, setDischargeAdmissionId] = useState("");
    const [dischargeDescription, setDischargeDescription] = useState(
        "Discharge charges"
    );
    const [dischargeAmount, setDischargeAmount] = useState("1000");

    const [paymentMethod, setPaymentMethod] = useState("cash");
    const [paymentReference, setPaymentReference] = useState("");
    const [collectPayment, setCollectPayment] = useState(true);
    const [saving, setSaving] = useState(false);


    /* ============================================================
       LOAD DATA
       ============================================================ */

    useEffect(() => {

        const loadData = async () => {

            try {

                setLoading(true);
                setError("");

                const [
                    patientsData,
                    doctorsData,
                    appointmentsData,
                    admissionsData,
                ] = await Promise.all([
                    getPatients(),
                    getDoctors(),
                    getAppointments(),
                    getAdmissions(),
                ]);

                setPatients(patientsData);
                setDoctors(doctorsData);
                setAppointments(appointmentsData);
                setAdmissions(admissionsData);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Unable to load data."
                );

            } finally {

                setLoading(false);

            }
        };

        loadData();

    }, []);


    /* ============================================================
       HELPERS
       ============================================================ */

    const getPatientName = (patientId) => {

        const patient = patients.find(
            (p) => p.id === patientId
        );

        return patient ? patient.name : `Patient #${patientId}`;

    };

    const relatedAppointments = (patientId) => {

        return appointments.filter(
            (a) => a.patient_id === patientId
        );

    };

    const relatedAdmissions = (patientId) => {

        return admissions.filter(
            (a) => a.patient_id === patientId
        );

    };


    /* ============================================================
       SUBMIT
       ============================================================ */

    const handleConsultSubmit = async (event) => {

        event.preventDefault();

        if (!consultPatientId) {
            setError("Select a patient.");
            return;
        }

        const description = String(
            consultDescription || "Doctor consultation fee"
        ).trim();

        const amount = Number(consultAmount);

        if (!amount || amount <= 0) {
            setError("Enter a valid amount.");
            return;
        }

        const selectedAppointment = appointments.find(
            (a) => a.id === Number(consultAppointmentId)
        );

        const doctorName = consultDoctorId
            ? getSelectedDoctorName(
                  Number(consultDoctorId)
              )
            : "";

        setSaving(true);
        setError("");
        setSuccess("");

        try {

            const invoice = await createBillingInvoice({
                patient_id: Number(consultPatientId),
                items: [
                    {
                        description: doctorName
                            ? `${description} - ${doctorName}`
                            : description,
                        quantity: 1,
                        unit_price: amount,
                    },
                ],
                payment: collectPayment
                    ? {
                          amount: Math.round(amount * 100) / 100,
                          method: paymentMethod,
                          reference: paymentReference,
                      }
                    : null,
            });

            setSuccess(
                `Invoice #${invoice.id} created for ` +
                `${getPatientName(Number(consultPatientId))}.`
            );

            setConsultPatientId("");
            setConsultDoctorId("");
            setConsultAppointmentId("");
            setPaymentReference("");

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Unable to create the invoice."
            );

        } finally {

            setSaving(false);

        }

    };

    const getSelectedDoctorName = (doctorId) => {

        const doctor = doctors.find(
            (d) => d.id === doctorId
        );

        return doctor ? `Dr. ${doctor.name}` : "";

    };

    const handleDischargeSubmit = async (event) => {

        event.preventDefault();

        if (!dischargePatientId) {
            setError("Select a patient.");
            return;
        }

        const description = String(
            dischargeDescription || "Discharge charges"
        ).trim();

        const amount = Number(dischargeAmount);

        if (!amount || amount <= 0) {
            setError("Enter a valid amount.");
            return;
        }

        const admission = admissions.find(
            (a) => a.id === Number(dischargeAdmissionId)
        );

        setSaving(true);
        setError("");
        setSuccess("");

        try {

            const invoice = await createBillingInvoice({
                patient_id: Number(dischargePatientId),
                items: [
                    {
                        description: admission
                            ? `${description} (Admission #${admission.id})`
                            : description,
                        quantity: 1,
                        unit_price: amount,
                    },
                ],
                payment: collectPayment
                    ? {
                          amount: Math.round(amount * 100) / 100,
                          method: paymentMethod,
                          reference: paymentReference,
                      }
                    : null,
            });

            setSuccess(
                `Invoice #${invoice.id} created for ` +
                `${getPatientName(Number(dischargePatientId))}.`
            );

            setDischargePatientId("");
            setDischargeAdmissionId("");
            setPaymentReference("");

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Unable to create the invoice."
            );

        } finally {

            setSaving(false);

        }

    };


    /* ============================================================
       RENDER
       ============================================================ */

    return (
        <MainLayout>
            <div className="prescriptions-page">

                <div className="prescriptions-header">
                    <div>
                        <h1>Billing</h1>
                        <p>
                            Generate bills for doctor
                            appointments and patient discharge.
                        </p>
                    </div>
                </div>


                {success && (
                    <p className="success-message">{success}</p>
                )}

                {error && (
                    <p className="error-message">{error}</p>
                )}


                {loading && (
                    <p className="loading-message">
                        Loading data...
                    </p>
                )}


                {!loading && (

                    <>
                        <div className="filter-row">
                            <button
                                type="button"
                                className={
                                    tab === "consult"
                                        ? "btn-add"
                                        : "action-btn"
                                }
                                onClick={() => {
                                    setTab("consult");
                                    setError("");
                                }}
                            >
                                Appointment
                            </button>
                            <button
                                type="button"
                                className={
                                    tab === "discharge"
                                        ? "btn-add"
                                        : "action-btn"
                                }
                                onClick={() => {
                                    setTab("discharge");
                                    setError("");
                                }}
                            >
                                Discharge
                            </button>
                        </div>


                        {tab === "consult" && (

                            <div className="prescription-form">

                                <div className="form-group">
                                    <label className="form-label">
                                        Patient
                                    </label>
                                    <select
                                        className="form-select"
                                        value={consultPatientId}
                                        onChange={(e) => {
                                            setConsultPatientId(
                                                e.target.value
                                            );
                                            setError("");
                                        }}
                                        required
                                    >
                                        <option value="">
                                            Select Patient
                                        </option>
                                        {patients.map((p) => (
                                            <option key={p.id} value={p.id}>
                                                {p.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {consultPatientId &&
                                    relatedAppointments(
                                        Number(consultPatientId)
                                    ).length > 0 && (
                                        <div className="form-group">
                                            <label className="form-label">
                                                Appointment
                                            </label>
                                            <select
                                                className="form-select"
                                                value={consultAppointmentId}
                                                onChange={(e) =>
                                                    setConsultAppointmentId(
                                                        e.target.value
                                                    )
                                                }
                                            >
                                                <option value="">
                                                    Select Appointment
                                                </option>
                                                {relatedAppointments(
                                                    Number(
                                                        consultPatientId
                                                    )
                                                ).map((a) => (
                                                    <option key={a.id} value={a.id}>
                                                        #{a.id} -{" "}
                                                        {a.appointment_date} (
                                                        {a.status})
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                    )}

                                <div className="form-group">
                                    <label className="form-label">
                                        Doctor
                                    </label>
                                    <select
                                        className="form-select"
                                        value={consultDoctorId}
                                        onChange={(e) =>
                                            setConsultDoctorId(
                                                e.target.value
                                            )
                                        }
                                    >
                                        <option value="">
                                            Select Doctor
                                        </option>
                                        {doctors.map((d) => (
                                            <option key={d.id} value={d.id}>
                                                Dr. {d.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">
                                        Description
                                    </label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={consultDescription}
                                        onChange={(e) =>
                                            setConsultDescription(
                                                e.target.value
                                            )
                                        }
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">
                                        Amount ({consultDoctorId ? getSelectedDoctorName(consultDoctorId) : "Rs"})
                                    </label>
                                    <input
                                        type="number"
                                        min="1"
                                        step="0.01"
                                        className="form-input"
                                        value={consultAmount}
                                        onChange={(e) =>
                                            setConsultAmount(
                                                e.target.value
                                            )
                                        }
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">
                                        <input
                                            type="checkbox"
                                            checked={collectPayment}
                                            onChange={(e) =>
                                                setCollectPayment(
                                                    e.target.checked
                                                )
                                            }
                                        />
                                        {" "}Collect payment now
                                    </label>
                                </div>

                                {collectPayment && (
                                    <div className="form-row">
                                        <div className="form-group">
                                            <label className="form-label">
                                                Method
                                            </label>
                                            <select
                                                className="form-select"
                                                value={paymentMethod}
                                                onChange={(e) =>
                                                    setPaymentMethod(
                                                        e.target.value
                                                    )
                                                }
                                            >
                                                <option value="cash">Cash</option>
                                                <option value="card">Card</option>
                                                <option value="upi">UPI</option>
                                                <option value="bank_transfer">
                                                    Bank Transfer
                                                </option>
                                            </select>
                                        </div>
                                        <div className="form-group">
                                            <label className="form-label">
                                                Reference
                                            </label>
                                            <input
                                                type="text"
                                                className="form-input"
                                                value={paymentReference}
                                                onChange={(e) =>
                                                    setPaymentReference(
                                                        e.target.value
                                                    )
                                                }
                                            />
                                        </div>
                                    </div>
                                )}

                                <button
                                    type="button"
                                    onClick={handleConsultSubmit}
                                    disabled={saving}
                                >
                                    {saving
                                        ? "Creating..."
                                        : "Generate Bill"}
                                </button>
                            </div>
                        )}


                        {tab === "discharge" && (

                            <div className="prescription-form">

                                <div className="form-group">
                                    <label className="form-label">
                                        Patient
                                    </label>
                                    <select
                                        className="form-select"
                                        value={dischargePatientId}
                                        onChange={(e) => {
                                            setDischargePatientId(
                                                e.target.value
                                            );
                                            setError("");
                                        }}
                                        required
                                    >
                                        <option value="">
                                            Select Patient
                                        </option>
                                        {patients.map((p) => (
                                            <option key={p.id} value={p.id}>
                                                {p.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {dischargePatientId &&
                                    relatedAdmissions(
                                        Number(dischargePatientId)
                                    ).length > 0 && (
                                        <div className="form-group">
                                            <label className="form-label">
                                                Admission
                                            </label>
                                            <select
                                                className="form-select"
                                                value={dischargeAdmissionId}
                                                onChange={(e) =>
                                                    setDischargeAdmissionId(
                                                        e.target.value
                                                    )
                                                }
                                            >
                                                <option value="">
                                                    Select Admission
                                                </option>
                                                {relatedAdmissions(
                                                    Number(
                                                        dischargePatientId
                                                    )
                                                ).map((a) => (
                                                    <option key={a.id} value={a.id}>
                                                        #{a.id} -{" "}
                                                        {a.admission_date} (
                                                        {a.status})
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                    )}

                                <div className="form-group">
                                    <label className="form-label">
                                        Description
                                    </label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={dischargeDescription}
                                        onChange={(e) =>
                                            setDischargeDescription(
                                                e.target.value
                                            )
                                        }
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">
                                        Amount
                                    </label>
                                    <input
                                        type="number"
                                        min="1"
                                        step="0.01"
                                        className="form-input"
                                        value={dischargeAmount}
                                        onChange={(e) =>
                                            setDischargeAmount(
                                                e.target.value
                                            )
                                        }
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">
                                        <input
                                            type="checkbox"
                                            checked={collectPayment}
                                            onChange={(e) =>
                                                setCollectPayment(
                                                    e.target.checked
                                                )
                                            }
                                        />
                                        {" "}Collect payment now
                                    </label>
                                </div>

                                {collectPayment && (
                                    <div className="form-row">
                                        <div className="form-group">
                                            <label className="form-label">
                                                Method
                                            </label>
                                            <select
                                                className="form-select"
                                                value={paymentMethod}
                                                onChange={(e) =>
                                                    setPaymentMethod(
                                                        e.target.value
                                                    )
                                                }
                                            >
                                                <option value="cash">Cash</option>
                                                <option value="card">Card</option>
                                                <option value="upi">UPI</option>
                                                <option value="bank_transfer">
                                                    Bank Transfer
                                                </option>
                                            </select>
                                        </div>
                                        <div className="form-group">
                                            <label className="form-label">
                                                Reference
                                            </label>
                                            <input
                                                type="text"
                                                className="form-input"
                                                value={paymentReference}
                                                onChange={(e) =>
                                                    setPaymentReference(
                                                        e.target.value
                                                    )
                                                }
                                            />
                                        </div>
                                    </div>
                                )}

                                <button
                                    type="button"
                                    onClick={handleDischargeSubmit}
                                    disabled={saving}
                                >
                                    {saving
                                        ? "Creating..."
                                        : "Generate Bill"}
                                </button>
                            </div>
                        )}

                    </>
                )}

            </div>
        </MainLayout>
    );
}

export default ReceptionistBilling;