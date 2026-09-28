import { useEffect, useState } from "react";

import MainLayout from "../../layouts/MainLayout";

import {
    getMyPrescriptions,
    getMyPrescriptionMedicines,
} from "../../api/prescriptions";

function PatientPrescriptions() {

    const [prescriptions, setPrescriptions] = useState([]);
    const [medicines, setMedicines] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchPrescriptions = async () => {
            try {
                setLoading(true);
                setError("");

                const [prescriptionData, medicineData] =
                    await Promise.all([
                        getMyPrescriptions(),
                        getMyPrescriptionMedicines(),
                    ]);

                setPrescriptions(prescriptionData);
                setMedicines(medicineData);

            } catch (err) {
                console.error("Failed to fetch prescriptions:", err);

                setError(
                    err.response?.data?.detail ||
                    "Failed to load prescriptions."
                );

            } finally {
                setLoading(false);
            }
        };

        fetchPrescriptions();
    }, []);

    if (loading) {
        return (
            <MainLayout>
                <h1>Prescriptions</h1>
                <p>Loading prescriptions...</p>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <h1>Prescriptions</h1>
                <p>{error}</p>
            </MainLayout>
        );
    }

    return (
        <MainLayout>

            <h1>Prescriptions</h1>

            {prescriptions.length === 0 ? (
                <p>No prescriptions found.</p>
            ) : (
                prescriptions.map((prescription) => {

                    const prescriptionMedicines =
                        medicines.filter(
                            (medicine) =>
                                medicine.prescription_id ===
                                prescription.id
                        );

                    return (
                        <div
                            key={prescription.id}
                            className="record-card"
                        >

                            <div className="record-card-header">
                                <h2>
                                    Prescription #{prescription.id}
                                </h2>
                                <span className="status-badge status-completed">
                                    {prescription.prescription_date}
                                </span>
                            </div>

                            <div className="kv-grid">
                                <div className="kv-item">
                                    <strong>Date</strong>
                                    <span className="value">
                                        {prescription.prescription_date}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Doctor</strong>
                                    <span className="value">
                                        {prescription.doctor_id}
                                    </span>
                                </div>

                                {prescription.pharmacy_id && (
                                    <div className="kv-item">
                                        <strong>Pharmacy</strong>
                                        <span className="value">
                                            {prescription.pharmacy_id}
                                        </span>
                                    </div>
                                )}
                            </div>

                            <h3 className="kv-section-title">Medicines</h3>

                            {prescriptionMedicines.length === 0 ? (
                                <p className="muted">
                                    No medicines added to this
                                    prescription.
                                </p>
                            ) : (
                                <div className="table-wrapper table-wrapper--plain">
                                    <div className="table-container">
                                        <table className="appointments-table">
                                            <thead>
                                                <tr>
                                                    <th>Medicine ID</th>
                                                    <th className="num">Quantity</th>
                                                    <th>Dosage</th>
                                                    <th>Duration</th>
                                                    <th>Instructions</th>
                                                </tr>
                                            </thead>

                                            <tbody>
                                                {prescriptionMedicines.map(
                                                    (medicine) => (
                                                        <tr
                                                            key={`${medicine.prescription_id}-${medicine.medicine_id}`}
                                                        >
                                                            <td>
                                                                {medicine.medicine_id}
                                                            </td>

                                                            <td className="num">
                                                                {medicine.quantity}
                                                            </td>

                                                            <td>
                                                                {medicine.dosage}
                                                            </td>

                                                            <td>
                                                                {medicine.duration ||
                                                                    "-"}
                                                            </td>

                                                            <td>
                                                                {medicine.instructions ||
                                                                    "-"}
                                                            </td>
                                                        </tr>
                                                    )
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}

                        </div>
                    );
                })
            )}

        </MainLayout>
    );
}

export default PatientPrescriptions;