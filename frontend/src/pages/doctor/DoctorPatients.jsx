import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { getMyDoctorPatients } from "../../api/patients";
import { useNavigate } from "react-router-dom";
function DoctorPatients() {
    const [patients, setPatients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const navigate = useNavigate();
    useEffect(() => {
        const loadPatients = async () => {
            try {
                setLoading(true);
                setError("");

                const data = await getMyDoctorPatients();

                setPatients(data);
            } catch (error) {
                console.error(error);

                setError(
                    error.response?.data?.detail ||
                    "Unable to load your patients."
                );
            } finally {
                setLoading(false);
            }
        };

        loadPatients();
    }, []);

    return (
        <MainLayout>
            <div className="patients-page">
                <div className="patients-header">
                    <h1>My Patients</h1>
                    <p>
                        View patients who have appointments with you.
                    </p>
                </div>

                {loading && (
                    <div className="empty-state">
                        <p>Loading patients...</p>
                    </div>
                )}

                {!loading && error && (
                    <div className="empty-state">
                        <h2>Unable to Load Patients</h2>
                        <p>{error}</p>
                    </div>
                )}

                {!loading && !error && patients.length === 0 && (
                    <div className="empty-state">
                        <h2>No Patients</h2>
                        <p>
                            You currently have no patients with appointments.
                        </p>
                    </div>
                )}

                {!loading && !error && patients.length > 0 && (
                    <div className="patients-table-container">
                        <table className="patients-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Phone</th>
                                </tr>
                            </thead>

                            <tbody>
                                {patients.map((patient) => (
                                    <tr
                                        key={patient.id}
                                        onClick={() =>
                                            navigate(`/doctor/patients/${patient.id}`)
                                        }
                                        style={{ cursor: "pointer" }}
                                    >
                                        <td>{patient.id}</td>
                                        <td>{patient.name}</td>
                                        <td>{patient.email || "-"}</td>
                                        <td>{patient.phone || "-"}</td>
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

export default DoctorPatients;