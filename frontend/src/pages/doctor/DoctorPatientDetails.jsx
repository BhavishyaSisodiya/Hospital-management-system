import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";

import { getPatient } from "../../api/patients";
import { getPatientAppointments } from "../../api/appointments";
import { getPatientMedicalRecords } from "../../api/medicalRecords";
import { getMyPrescriptionMedicines } from "../../api/prescriptions";
import { getPatientVitals } from "../../api/vitals";
import { getPatientLabResults } from "../../api/labResults";
import {
    getDoctorPatientPrescriptions,
} from "../../api/prescriptions";

function DoctorPatientDetails() {
    const { patientId } = useParams();
    const navigate = useNavigate();

    const [patient, setPatient] = useState(null);
    const [appointments, setAppointments] = useState([]);
    const [records, setRecords] = useState([]);
    const [prescriptions, setPrescriptions] = useState([]);
    const [vitals, setVitals] = useState([]);
    const [labResults, setLabResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadPatientDetails = async () => {
            try {
                setLoading(true);
                setError("");

                const [
                    patientData,
                    appointmentData,
                    recordData,
                    vitalData,
                    labResultData,
                ] = await Promise.all([
                    getPatient(patientId),
                    getPatientAppointments(patientId),
                    getPatientMedicalRecords(patientId),
                    getPatientVitals(patientId),
                    getPatientLabResults(patientId),
                ]);
                const prescriptionData =
                    await getDoctorPatientPrescriptions(patientId);

                setPrescriptions(prescriptionData);
                setPatient(patientData);
                setAppointments(appointmentData);
                setRecords(recordData);
                setVitals(vitalData);
                setLabResults(labResultData);
            } catch (error) {
                console.error(error);

                setError(
                    error.response?.data?.detail ||
                    "Unable to load patient details."
                );
            } finally {
                setLoading(false);
            }
        };

        loadPatientDetails();
    }, [patientId]);

    if (loading) {
        return (
            <MainLayout>
                <div className="empty-state">
                    <p>Loading patient details...</p>
                </div>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <div className="empty-state">
                    <h2>Unable to Load Patient</h2>
                    <p>{error}</p>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="patient-details-page">

                <div className="patient-details-header">
                    <button
                        type="button"
                        onClick={() =>
                            navigate("/doctor/patients")
                        }
                    >
                        ← Back to Patients
                    </button>

                    <h1>{patient.name}</h1>

                    <p>
                        Patient ID: {patient.id}
                    </p>
                </div>

                {/* Patient Information */}

                <div className="patient-details-card">
                    <h2>Patient Information</h2>

                    <p>
                        <strong>Name:</strong>{" "}
                        {patient.name}
                    </p>

                    <p>
                        <strong>Email:</strong>{" "}
                        {patient.email || "-"}
                    </p>

                    <p>
                        <strong>Phone:</strong>{" "}
                        {patient.phone || "-"}
                    </p>

                    <p>
                        <strong>Gender:</strong>{" "}
                        {patient.gender || "-"}
                    </p>

                    <p>
                        <strong>Date of Birth:</strong>{" "}
                        {patient.dob || "-"}
                    </p>

                    <p>
                        <strong>Address:</strong>{" "}
                        {patient.address || "-"}
                    </p>
                </div>

                {/* Appointments */}

                <div className="patient-details-section">
                    <h2>Appointments</h2>

                    {appointments.length === 0 ? (
                        <p>No appointments found.</p>
                    ) : (
                        <div className="appointments-table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Date</th>
                                        <th>Time</th>
                                        <th>Reason</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {appointments.map(
                                        (appointment) => (
                                            <tr
                                                key={
                                                    appointment.id
                                                }
                                            >
                                                <td>
                                                    {
                                                        appointment.id
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        appointment.appointment_date
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        appointment.appointment_time
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        appointment.reason ||
                                                        "-"
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        appointment.status
                                                    }
                                                </td>
                                            </tr>
                                        )
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Medical Records */}

                <div className="patient-details-section">
                    <h2>Medical Records</h2>

                    {records.length === 0 ? (
                        <p>No medical records found.</p>
                    ) : (
                        <div className="medical-records-table-container">
                            <table className="medical-records-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Date</th>
                                        <th>Diagnosis</th>
                                        <th>Notes</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {records.map((record) => (
                                        <tr
                                            key={record.id}
                                        >
                                            <td>
                                                {record.id}
                                            </td>

                                            <td>
                                                {record.record_date}
                                            </td>

                                            <td>
                                                {record.diagnosis ||
                                                    "-"}
                                            </td>

                                            <td>
                                                {record.notes ||
                                                    "-"}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
                <div className="patient-details-section">
                    <h2>Vitals</h2>

                    {vitals.length === 0 ? (
                        <p>No vital records found.</p>
                    ) : (
                        <div className="medical-records-table-container">
                            <table className="medical-records-table">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Temperature</th>
                                        <th>Heart Rate</th>
                                        <th>Blood Pressure</th>
                                        <th>Respiratory Rate</th>
                                        <th>Oxygen Saturation</th>
                                        <th>Weight</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {vitals.map((vital) => (
                                        <tr key={vital.id}>
                                            <td>
                                                {vital.recorded_at}
                                            </td>

                                            <td>
                                                {vital.temperature ?? "-"}
                                            </td>

                                            <td>
                                                {vital.heart_rate ?? "-"}
                                            </td>

                                            <td>
                                                {vital.blood_pressure_systolic &&
                                                    vital.blood_pressure_diastolic
                                                    ? `${vital.blood_pressure_systolic}/${vital.blood_pressure_diastolic}`
                                                    : "-"}
                                            </td>

                                            <td>
                                                {vital.respiratory_rate ?? "-"}
                                            </td>

                                            <td>
                                                {vital.oxygen_saturation ?? "-"}
                                            </td>

                                            <td>
                                                {vital.weight ?? "-"}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
                <div className="patient-details-section">
                    <h2>Lab Results</h2>

                    {labResults.length === 0 ? (
                        <p>No lab results found.</p>
                    ) : (
                        <div className="medical-records-table-container">
                            <table className="medical-records-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Lab Test ID</th>
                                        <th>Result</th>
                                        <th>Remarks</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {labResults.map((result) => (
                                        <tr key={result.id}>
                                            <td>{result.id}</td>

                                            <td>
                                                {result.lab_test_id ?? "-"}
                                            </td>

                                            <td>
                                                {result.result_value ?? "-"}
                                            </td>

                                            <td>
                                                {result.remarks ?? "-"}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </MainLayout>
    );
}

export default DoctorPatientDetails;