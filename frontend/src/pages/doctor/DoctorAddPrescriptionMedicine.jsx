import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";

import {
    addPrescriptionMedicine,
} from "../../api/prescriptions";

import {
    getMedicines,
} from "../../api/medicines";

function DoctorAddPrescriptionMedicine() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [medicines, setMedicines] = useState([]);

    const [medicineId, setMedicineId] = useState("");
    const [quantity, setQuantity] = useState("");
    const [dosage, setDosage] = useState("");
    const [duration, setDuration] = useState("");
    const [instructions, setInstructions] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    useEffect(() => {
        const loadMedicines = async () => {
            try {
                setLoading(true);
                setError("");

                const data = await getMedicines();

                setMedicines(data);
            } catch (error) {
                console.error(error);

                setError(
                    error.response?.data?.detail ||
                    "Unable to load medicines."
                );
            } finally {
                setLoading(false);
            }
        };

        loadMedicines();
    }, []);

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");
        setSuccess("");

        if (!medicineId) {
            setError("Please select a medicine.");
            return;
        }

        if (!quantity || Number(quantity) <= 0) {
            setError("Quantity must be greater than 0.");
            return;
        }

        if (!dosage.trim()) {
            setError("Dosage is required.");
            return;
        }

        try {
            setSaving(true);

            await addPrescriptionMedicine({
                prescription_id: Number(id),
                medicine_id: Number(medicineId),
                quantity: Number(quantity),
                dosage: dosage.trim(),
                duration: duration.trim() || null,
                instructions: instructions.trim() || null,
            });

            setSuccess(
                "Medicine added to prescription successfully."
            );

            setMedicineId("");
            setQuantity("");
            setDosage("");
            setDuration("");
            setInstructions("");

            setTimeout(() => {
                navigate(
                    `/doctor/prescriptions/${id}`
                );
            }, 800);
        } catch (error) {
            console.error(error);

            setError(
                error.response?.data?.detail ||
                "Unable to add medicine."
            );
        } finally {
            setSaving(false);
        }
    };

    return (
        <MainLayout>
            <div className="prescriptions-page">

                <div className="prescriptions-header">
                    <div>
                        <h1>Add Medicine</h1>

                        <p>
                            Add a medicine to prescription #{id}.
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={() =>
                            navigate(
                                `/doctor/prescriptions/${id}`
                            )
                        }
                    >
                        Back
                    </button>
                </div>


                {loading && (
                    <div className="empty-state">
                        <p>Loading medicines...</p>
                    </div>
                )}


                {!loading && error && (
                    <div className="empty-state">
                        <p>{error}</p>
                    </div>
                )}


                {!loading && !error && (
                    <form
                        onSubmit={handleSubmit}
                        className="prescription-form"
                    >

                        <div>
                            <label>
                                Medicine
                            </label>

                            <select
                                value={medicineId}
                                onChange={(event) =>
                                    setMedicineId(
                                        event.target.value
                                    )
                                }
                            >
                                <option value="">
                                    Select medicine
                                </option>

                                {medicines.map(
                                    (medicine) => (
                                        <option
                                            key={medicine.id}
                                            value={medicine.id}
                                        >
                                            {medicine.name}
                                        </option>
                                    )
                                )}
                            </select>
                        </div>


                        <div>
                            <label>
                                Quantity
                            </label>

                            <input
                                type="number"
                                min="1"
                                value={quantity}
                                onChange={(event) =>
                                    setQuantity(
                                        event.target.value
                                    )
                                }
                                placeholder="Enter quantity"
                            />
                        </div>


                        <div>
                            <label>
                                Dosage
                            </label>

                            <input
                                type="text"
                                value={dosage}
                                onChange={(event) =>
                                    setDosage(
                                        event.target.value
                                    )
                                }
                                placeholder="Example: 1 tablet twice daily"
                            />
                        </div>


                        <div>
                            <label>
                                Duration
                            </label>

                            <input
                                type="text"
                                value={duration}
                                onChange={(event) =>
                                    setDuration(
                                        event.target.value
                                    )
                                }
                                placeholder="Example: 5 days"
                            />
                        </div>


                        <div>
                            <label>
                                Instructions
                            </label>

                            <textarea
                                value={instructions}
                                onChange={(event) =>
                                    setInstructions(
                                        event.target.value
                                    )
                                }
                                placeholder="Example: Take after food"
                                rows="4"
                            />
                        </div>


                        {error && (
                            <p>{error}</p>
                        )}

                        {success && (
                            <p>{success}</p>
                        )}


                        <button
                            type="submit"
                            disabled={saving}
                        >
                            {saving
                                ? "Saving..."
                                : "Save Medicine"}
                        </button>

                    </form>
                )}

            </div>
        </MainLayout>
    );
}

export default DoctorAddPrescriptionMedicine;