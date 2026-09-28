import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";

import {
    getMyDoctorMedicalRecords,
} from "../../api/medicalRecords";

function DoctorMedicalRecords() {
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const navigate = useNavigate();

    useEffect(() => {
        const loadRecords = async () => {
            try {
                setLoading(true);
                setError("");

                const data =
                    await getMyDoctorMedicalRecords();

                setRecords(data);
            } catch (error) {
                console.error(error);

                setError(
                    error.response?.data?.detail ||
                        "Unable to load medical records."
                );
            } finally {
                setLoading(false);
            }
        };

        loadRecords();
    }, []);

    const formatDate = (dateString) => {
        if (!dateString) {
            return "-";
        }

        const date = new Date(dateString);

        if (Number.isNaN(date.getTime())) {
            return "-";
        }

        return date.toLocaleString();
    };

    return (
        <MainLayout>
            <div className="medical-records-page">

                <div className="medical-records-header">
                    <h1>Medical Records</h1>

                    <p>
                        View medical records created by you
                        for your patients.
                    </p>

                    <button
                        type="button"
                        onClick={() =>
                            navigate(
                                "/doctor/medical-records/create"
                            )
                        }
                    >
                        Create Medical Record
                    </button>
                </div>

                {loading && (
                    <div className="empty-state">
                        <p>
                            Loading medical records...
                        </p>
                    </div>
                )}

                {!loading && error && (
                    <div className="empty-state">
                        <h2>
                            Unable to Load Records
                        </h2>

                        <p>{error}</p>
                    </div>
                )}

                {!loading &&
                    !error &&
                    records.length === 0 && (
                        <div className="empty-state">
                            <h2>No Medical Records</h2>

                            <p>
                                You have not created any
                                medical records yet.
                            </p>
                        </div>
                    )}

                {!loading &&
                    !error &&
                    records.length > 0 && (
                        <div className="appointments-table-container">

                            <table className="appointments-table">

                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Patient ID</th>
                                        <th>Doctor ID</th>
                                        <th>Diagnosis</th>
                                        <th>Notes</th>
                                        <th>Date</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {records.map((record) => (
                                        <tr key={record.id}>

                                            <td>
                                                {record.id}
                                            </td>

                                            <td>
                                                {record.patient_id}
                                            </td>

                                            <td>
                                                {record.doctor_id}
                                            </td>

                                            <td>
                                                {record.diagnosis ||
                                                    "-"}
                                            </td>

                                            <td>
                                                {record.notes ||
                                                    "-"}
                                            </td>

                                            <td>
                                                {formatDate(
                                                    record.record_date
                                                )}
                                            </td>

                                            <td>
                                                <button
                                                    type="button"
                                                    onClick={() =>
                                                        navigate(
                                                            `/doctor/medical-records/edit/${record.id}`
                                                        )
                                                    }
                                                >
                                                    Edit
                                                </button>
                                            </td>

                                        </tr>
                                    ))}
                                </tbody>

                            </table>

                        </div>
                    )}
            </div>
        </MainLayout>
    );
}

export default DoctorMedicalRecords;

