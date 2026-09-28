import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";

import {
    getPrescriptionMedicines,
    updatePrescriptionMedicine,
} from "../../api/prescriptions";

function DoctorEditPrescriptionMedicine() {
    const { id, medicineId } = useParams();
    const navigate = useNavigate();

    const [medicine, setMedicine] = useState(null);

    const [quantity, setQuantity] = useState("");
    const [dosage, setDosage] = useState("");
    const [duration, setDuration] = useState("");
    const [instructions, setInstructions] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    useEffect(() => {
        const loadMedicine = async () => {
            try {
                setLoading(true);
                setError("");

                const data =
                    await getPrescriptionMedicines();

                const foundMedicine = data.find(
                    (item) =>
                        String(item.prescription_id) ===
                            String(id) &&
                        String(item.medicine_id) ===
                            String(medicineId)
                );

                if (!foundMedicine) {
                    setError(
                        "Prescription medicine not found."
                    );
                    return;
                }

                setMedicine(foundMedicine);

                setQuantity(foundMedicine.quantity);
                setDosage(foundMedicine.dosage || "");
                setDuration(foundMedicine.duration || "");
                setInstructions(
                    foundMedicine.instructions || ""
                );
            } catch (error) {
                console.error(error);

                setError(
                    error.response?.data?.detail ||
                    "Unable to load prescription medicine."
                );
            } finally {
                setLoading(false);
            }
        };

        loadMedicine();
    }, [id, medicineId]);

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");
        setSuccess("");

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

            await updatePrescriptionMedicine(
                Number(id),
                Number(medicineId),
                {
                    quantity: Number(quantity),
                    dosage: dosage.trim(),
                    duration: duration.trim() || null,
                    instructions:
                        instructions.trim() || null,
                }
            );

            setSuccess(
                "Prescription medicine updated successfully."
            );

            setTimeout(() => {
                navigate(
                    `/doctor/prescriptions/${id}`
                );
            }, 800);
        } catch (error) {
            console.error(error);

            setError(
                error.response?.data?.detail ||
                "Unable to update prescription medicine."
            );
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="prescriptions-page">
                    <div className="empty-state">
                        <p>
                            Loading medicine...
                        </p>
                    </div>
                </div>
            </MainLayout>
        );
    }

    if (error && !medicine) {
        return (
            <MainLayout>
                <div className="prescriptions-page">
                    <div className="empty-state">
                        <h2>
                            Unable to Load Medicine
                        </h2>

                        <p>{error}</p>

                        <button
                            type="button"
                            onClick={() =>
                                navigate(
                                    `/doctor/prescriptions/${id}`
                                )
                            }
                        >
                            Back to Prescription
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
                            Edit Prescription Medicine
                        </h1>

                        <p>
                            Update medicine details for
                            prescription #{id}.
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

                <div className="prescription-details">
                    <p>
                        <strong>
                            Medicine ID:
                        </strong>{" "}
                        {medicine.medicine_id}
                    </p>
                </div>

                <form
                    onSubmit={handleSubmit}
                    className="prescription-form"
                >
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
                            : "Update Medicine"}
                    </button>
                </form>
            </div>
        </MainLayout>
    );
}

export default DoctorEditPrescriptionMedicine;