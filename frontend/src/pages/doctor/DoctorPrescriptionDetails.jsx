import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";
import {
    getMedicines,
} from "../../api/medicines";
import {
    getMyDoctorPrescriptions,
    getPrescriptionMedicines,
} from "../../api/prescriptions";

function DoctorPrescriptionDetails() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [prescription, setPrescription] = useState(null);
    const [medicines, setMedicines] = useState([]);
    const [medicineList, setMedicineList] = useState([]);

    const [loading, setLoading] = useState(true);
    const [medicineLoading, setMedicineLoading] = useState(true);

    const [error, setError] = useState("");
    const [medicineError, setMedicineError] = useState("");

    useEffect(() => {
        const loadPrescription = async () => {
            try {
                setLoading(true);
                setError("");

                const data = await getMyDoctorPrescriptions();

                const foundPrescription = data.find(
                    (item) =>
                        String(item.id) === String(id)
                );

                if (!foundPrescription) {
                    setError("Prescription not found.");
                    return;
                }

                setPrescription(foundPrescription);
            } catch (error) {
                console.error(error);

                setError(
                    error.response?.data?.detail ||
                    "Unable to load prescription."
                );
            } finally {
                setLoading(false);
            }
        };

        loadPrescription();
    }, [id]);
    useEffect(() => {
        const loadMedicineList = async () => {
            try {
                const data = await getMedicines();
                setMedicineList(data);
            } catch (error) {
                console.error(
                    "Unable to load medicine names:",
                    error
                );
            }
        };

        loadMedicineList();
    }, []);

    useEffect(() => {
        const loadMedicines = async () => {
            try {
                setMedicineLoading(true);
                setMedicineError("");

                const data =
                    await getPrescriptionMedicines();

                const prescriptionMedicines = data.filter(
                    (medicine) =>
                        String(medicine.prescription_id) ===
                        String(id)
                );

                setMedicines(prescriptionMedicines);
            } catch (error) {
                console.error(error);

                setMedicineError(
                    error.response?.data?.detail ||
                    "Unable to load prescription medicines."
                );
            } finally {
                setMedicineLoading(false);
            }
        };

        loadMedicines();
    }, [id]);

    if (loading) {
        return (
            <MainLayout>
                <div className="prescriptions-page">
                    <div className="empty-state">
                        <p>
                            Loading prescription...
                        </p>
                    </div>
                </div>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <div className="prescriptions-page">
                    <div className="empty-state">
                        <h2>
                            Unable to Load Prescription
                        </h2>

                        <p>{error}</p>

                        <button
                            type="button"
                            onClick={() =>
                                navigate(
                                    "/doctor/prescriptions"
                                )
                            }
                        >
                            Back to Prescriptions
                        </button>
                    </div>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="prescriptions-page">

                <div className="prescriptions-header">
                    <div>
                        <h1>
                            Prescription Details
                        </h1>

                        <p>
                            View prescription information
                            and prescribed medicines.
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={() =>
                            navigate(
                                "/doctor/prescriptions"
                            )
                        }
                    >
                        Back
                    </button>
                </div>


                {/* Prescription Information */}

                <div className="prescription-details">
                    <h2>
                        Prescription Information
                    </h2>

                    <p>
                        <strong>
                            Prescription ID:
                        </strong>{" "}
                        {prescription.id}
                    </p>

                    <p>
                        <strong>
                            Patient ID:
                        </strong>{" "}
                        {prescription.patient_id}
                    </p>

                    <p>
                        <strong>
                            Doctor ID:
                        </strong>{" "}
                        {prescription.doctor_id}
                    </p>

                    <p>
                        <strong>
                            Pharmacy ID:
                        </strong>{" "}
                        {prescription.pharmacy_id ?? "-"}
                    </p>

                    <p>
                        <strong>
                            Prescription Date:
                        </strong>{" "}
                        {prescription.prescription_date}
                    </p>
                </div>


                {/* Medicines */}

                <div className="prescription-details">

                    <div className="prescriptions-header">
                        <div>
                            <h2>
                                Prescribed Medicines
                            </h2>

                            <p>
                                Medicines added to this
                                prescription.
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={() =>
                                navigate(
                                    `/doctor/prescriptions/${id}/add-medicine`
                                )
                            }
                        >
                            Add Medicine
                        </button>
                    </div>


                    {medicineLoading && (
                        <div className="empty-state">
                            <p>
                                Loading medicines...
                            </p>
                        </div>
                    )}


                    {!medicineLoading &&
                        medicineError && (
                            <div className="empty-state">
                                <h3>
                                    Unable to Load Medicines
                                </h3>

                                <p>
                                    {medicineError}
                                </p>
                            </div>
                        )}


                    {!medicineLoading &&
                        !medicineError &&
                        medicines.length === 0 && (
                            <div className="empty-state">
                                <h3>
                                    No Medicines
                                </h3>

                                <p>
                                    No medicines have been
                                    added to this prescription.
                                </p>
                            </div>
                        )}


                    {!medicineLoading &&
                        !medicineError &&
                        medicines.length > 0 && (
                            <div className="appointments-table-container">
                                <table className="appointments-table">
                                    <thead>
                                        <tr>
                                            <th>
                                                Medicine
                                            </th>

                                            <th>
                                                Quantity
                                            </th>

                                            <th>
                                                Dosage
                                            </th>

                                            <th>
                                                Duration
                                            </th>

                                            <th>Instructions</th>
                                            <th>Action</th>
                                        </tr>
                                    </thead>

                                    <tbody>
                                        {medicines.map(
                                            (medicine) => (
                                                <tr
                                                    key={`${medicine.prescription_id}-${medicine.medicine_id}`}
                                                >
                                                    <td>
                                                        {
                                                            medicineList.find(
                                                                (item) =>
                                                                    item.id === medicine.medicine_id
                                                            )?.name || `Medicine #${medicine.medicine_id}`
                                                        }
                                                    </td>

                                                    <td>
                                                        {
                                                            medicine.quantity
                                                        }
                                                    </td>

                                                    <td>
                                                        {
                                                            medicine.dosage
                                                        }
                                                    </td>

                                                    <td>
                                                        {
                                                            medicine.duration ??
                                                            "-"
                                                        }
                                                    </td>

                                                    <td>
                                                        {
                                                            medicine.instructions ??
                                                            "-"
                                                        }
                                                    </td>
                                                    <td>
                                                        <button
                                                            type="button"
                                                            onClick={() =>
                                                                navigate(
                                                                    `/doctor/prescriptions/${id}/edit-medicine/${medicine.medicine_id}`
                                                                )
                                                            }
                                                        >
                                                            Edit
                                                        </button>
                                                    </td>
                                                </tr>
                                            )
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        )}
                </div>

            </div>
        </MainLayout>
    );
}

export default DoctorPrescriptionDetails;