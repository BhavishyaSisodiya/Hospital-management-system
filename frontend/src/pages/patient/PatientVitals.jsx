import { useEffect, useState } from "react";

import MainLayout from "../../layouts/MainLayout";

import { getMyPatientProfile } from "../../api/patients";
import { getPatientVitals } from "../../api/vitals";

function PatientVitals() {
    const [vitals, setVitals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchVitals = async () => {
            try {
                setLoading(true);
                setError("");

                const patient = await getMyPatientProfile();

                const data = await getPatientVitals(
                    patient.id
                );

                setVitals(data);
            } catch (err) {
                console.error(
                    "Failed to fetch vitals:",
                    err
                );

                setError(
                    err.response?.data?.detail ||
                    "Failed to load vital records."
                );
            } finally {
                setLoading(false);
            }
        };

        fetchVitals();
    }, []);

    const formatDate = (date) => {
        if (!date) {
            return "-";
        }

        return new Date(date).toLocaleString();
    };

    const formatValue = (value, unit = "") => {
        if (value === null || value === undefined) {
            return "-";
        }

        return `${value}${unit}`;
    };

    if (loading) {
        return (
            <MainLayout>
                <h1>Vitals</h1>
                <p>Loading vital records...</p>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <h1>Vitals</h1>
                <p>{error}</p>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <h1>Vitals</h1>

            {vitals.length === 0 ? (
                <p>No vital records found.</p>
            ) : (
                <div>
                    {vitals.map((vital) => (
                        <div
                            key={vital.id}
                            className="record-card"
                        >
                            <div className="record-card-header">
                                <h2>
                                    Vital Record #{vital.id}
                                </h2>
                                <span className="status-badge status-completed">
                                    {formatDate(vital.recorded_at)}
                                </span>
                            </div>

                            <div className="kv-grid">
                                <div className="kv-item">
                                    <strong>Recorded At</strong>
                                    <span className="value">
                                        {formatDate(
                                            vital.recorded_at
                                        )}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Recorded By</strong>
                                    <span className="value">
                                        {vital.recorded_by || "-"}
                                    </span>
                                </div>
                            </div>

                            <h3 className="kv-section-title">
                                Measurements
                            </h3>

                            <div className="kv-grid">
                                <div className="kv-item">
                                    <strong>Temperature</strong>
                                    <span className="value">
                                        {formatValue(
                                            vital.temperature,
                                            " °C"
                                        )}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Heart Rate</strong>
                                    <span className="value">
                                        {formatValue(
                                            vital.heart_rate,
                                            " bpm"
                                        )}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Blood Pressure</strong>
                                    <span className="value">
                                        {vital.blood_pressure_systolic !==
                                            null &&
                                        vital.blood_pressure_systolic !==
                                            undefined &&
                                        vital.blood_pressure_diastolic !==
                                            null &&
                                        vital.blood_pressure_diastolic !==
                                            undefined
                                            ? `${vital.blood_pressure_systolic}/${vital.blood_pressure_diastolic} mmHg`
                                            : "-"}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Respiratory Rate</strong>
                                    <span className="value">
                                        {formatValue(
                                            vital.respiratory_rate,
                                            " breaths/min"
                                        )}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Oxygen Saturation</strong>
                                    <span className="value">
                                        {formatValue(
                                            vital.oxygen_saturation,
                                            "%"
                                        )}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Weight</strong>
                                    <span className="value">
                                        {formatValue(
                                            vital.weight,
                                            " kg"
                                        )}
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

export default PatientVitals;