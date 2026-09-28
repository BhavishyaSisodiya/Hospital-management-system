import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { getMyPatientProfile } from "../../api/patients";
import { getPatientAdmissions } from "../../api/admissions";

function PatientAdmissions() {
    const [admissions, setAdmissions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchAdmissions = async () => {
            try {
                setLoading(true);
                setError("");

                // Get logged-in patient's profile
                const patient = await getMyPatientProfile();

                // Get only this patient's admissions
                const data = await getPatientAdmissions(
                    patient.id
                );

                setAdmissions(data);
            } catch (err) {
                console.error(
                    "Failed to fetch admissions:",
                    err
                );

                setError(
                    err.response?.data?.detail ||
                    "Failed to load admissions."
                );
            } finally {
                setLoading(false);
            }
        };

        fetchAdmissions();
    }, []);

    const formatDate = (date) => {
        if (!date) {
            return "-";
        }

        return new Date(date).toLocaleString();
    };

    const getStatusLabel = (status) => {
        if (!status) {
            return "-";
        }

        return status.charAt(0).toUpperCase() +
            status.slice(1);
    };

    if (loading) {
        return (
            <MainLayout>
                <h1>Admissions</h1>
                <p>Loading admissions...</p>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <h1>Admissions</h1>
                <p>{error}</p>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <h1>Admissions</h1>

            {admissions.length === 0 ? (
                <p>
                    No admission records found.
                </p>
            ) : (
                <div>
                    {admissions.map((admission) => (
                        <div
                            key={admission.id}
                            className={`record-card ${
                                admission.status === "active" ||
                                admission.status === "admitted"
                                    ? "record-card--warn"
                                    : admission.status === "discharged"
                                    ? "record-card--success"
                                    : ""
                            }`}
                        >
                            <div className="record-card-header">
                                <h2>
                                    Admission #{admission.id}
                                </h2>
                                <span className={`status-badge status-${admission.status}`}>
                                    {getStatusLabel(
                                        admission.status
                                    )}
                                </span>
                            </div>

                            <div className="kv-grid">
                                <div className="kv-item">
                                    <strong>Admission Date</strong>
                                    <span className="value">
                                        {formatDate(
                                            admission.admission_date
                                        )}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Discharge Date</strong>
                                    <span className="value">
                                        {formatDate(
                                            admission.discharge_date
                                        )}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Doctor</strong>
                                    <span className="value">
                                        {admission.doctor_id}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Bed</strong>
                                    <span className="value">
                                        {admission.bed_id}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </MainLayout>
    );
}

export default PatientAdmissions;