import { useEffect, useState } from "react";

import MainLayout from "../../layouts/MainLayout";

import { getMyPatientProfile } from "../../api/patients";
import { getPatientMedicalRecords } from "../../api/medicalRecords";

function PatientMedicalRecords() {
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadMedicalRecords = async () => {
            try {
                setLoading(true);
                setError("");

                // Get the currently logged-in patient's profile
                const patient = await getMyPatientProfile();

                // Make sure the patient ID exists
                if (!patient?.id) {
                    throw new Error("Patient information not found.");
                }

                // Get medical records using the actual patient ID
                const data = await getPatientMedicalRecords(patient.id);

                // Support either:
                // 1. Direct array response
                // 2. Axios-style { data: [...] } response
                const medicalRecords = Array.isArray(data)
                    ? data
                    : Array.isArray(data?.data)
                    ? data.data
                    : [];

                setRecords(medicalRecords);
            } catch (error) {
                console.error("Failed to load medical records:", error);

                if (error.response) {
                    setError(
                        error.response.data?.detail ||
                            "Unable to load medical records."
                    );
                } else if (error.message) {
                    setError(error.message);
                } else {
                    setError("Unable to connect to the server.");
                }
            } finally {
                setLoading(false);
            }
        };

        loadMedicalRecords();
    }, []);

    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {
        return (
            <MainLayout>
                <div className="medical-records-page">
                    <div className="medical-records-header">
                        <h1>Medical Records</h1>
                        <p>
                            View your medical history and diagnosis records.
                        </p>
                    </div>

                    <p>Loading medical records...</p>
                </div>
            </MainLayout>
        );
    }

    // ============================================================
    // ERROR
    // ============================================================

    if (error) {
        return (
            <MainLayout>
                <div className="medical-records-page">
                    <div className="medical-records-header">
                        <h1>Medical Records</h1>
                        <p>
                            View your medical history and diagnosis records.
                        </p>
                    </div>

                    <p className="error-message">{error}</p>
                </div>
            </MainLayout>
        );
    }

    // ============================================================
    // MAIN PAGE
    // ============================================================

    return (
        <MainLayout>
            <div className="medical-records-page">
                <div className="medical-records-header">
                    <h1>Medical Records</h1>

                    <p>
                        View your medical history and diagnosis records.
                    </p>
                </div>

                {/* Empty State */}

                {records.length === 0 ? (
                    <div className="medical-records-empty">
                        <h2>No Medical Records</h2>

                        <p>
                            You currently have no medical records available.
                        </p>
                    </div>
                ) : (
                    <div className="medical-records-list">
                        {records.map((record) => (
                            <div
                                className="medical-record-card"
                                key={record.id}
                            >
                                <div className="medical-record-header">
                                    <div>
                                        <h2>
                                            {record.diagnosis ||
                                                "Medical Record"}
                                        </h2>

                                        <p>
                                            Record ID: {record.id}
                                        </p>
                                    </div>

                                    <span className="record-date">
                                        {record.record_date
                                            ? new Date(
                                                  record.record_date
                                              ).toLocaleDateString()
                                            : "Date unavailable"}
                                    </span>
                                </div>

                                <div className="medical-record-details">
                                    <div className="record-detail">
                                        <strong>Doctor ID</strong>

                                        <span>
                                            {record.doctor_id ?? "N/A"}
                                        </span>
                                    </div>

                                    <div className="record-detail">
                                        <strong>Record Date</strong>

                                        <span>
                                            {record.record_date
                                                ? new Date(
                                                      record.record_date
                                                  ).toLocaleString()
                                                : "Date unavailable"}
                                        </span>
                                    </div>
                                </div>

                                <div className="medical-record-notes">
                                    <strong>Notes</strong>

                                    <p>
                                        {record.notes ||
                                            "No notes provided."}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </MainLayout>
    );
}

export default PatientMedicalRecords;

