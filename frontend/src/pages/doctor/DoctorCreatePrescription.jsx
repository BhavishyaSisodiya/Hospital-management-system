import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";

import {
    createPrescription,
} from "../../api/prescriptions";

import {
    getMyDoctorPatients,
} from "../../api/patients";

import {
    getPharmacies,
} from "../../api/pharmacies";

import {
    getTestTypes,
} from "../../api/testTypes";

function DoctorCreatePrescription() {
    const navigate = useNavigate();

    const [patients, setPatients] = useState([]);
    const [pharmacies, setPharmacies] = useState([]);
    const [testTypes, setTestTypes] = useState([]);

    const [patientId, setPatientId] = useState("");
    const [prescriptionDate, setPrescriptionDate] = useState(
        () => new Date().toISOString().slice(0, 10)
    );
    const [pharmacyId, setPharmacyId] = useState("");
    const [testTypeId, setTestTypeId] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [error, setError] = useState("");
    const [formError, setFormError] = useState("");

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                setError("");

                const [patientData, pharmacyData, testTypesData] =
                    await Promise.all([
                        getMyDoctorPatients(),
                        getPharmacies(),
                        getTestTypes(),
                    ]);

                setPatients(patientData);
                setPharmacies(pharmacyData);
                setTestTypes(testTypesData);
            } catch (error) {
                console.error(error);

                setError(
                    error.response?.data?.detail ||
                    "Unable to load patients or pharmacies."
                );
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    const handleSubmit = async (event) => {
        event.preventDefault();

        setFormError("");

        if (!patientId) {
            setFormError("Please select a patient.");
            return;
        }

        if (!prescriptionDate) {
            setFormError("Prescription date is required.");
            return;
        }

        try {
            setSaving(true);

            const prescription = await createPrescription({
                patient_id: Number(patientId),
                prescription_date: prescriptionDate,
                pharmacy_id: pharmacyId
                    ? Number(pharmacyId)
                    : null,
                test_type_id: testTypeId
                    ? Number(testTypeId)
                    : null,
            });

            navigate(
                `/doctor/prescriptions/${prescription.id}`
            );
        } catch (error) {
            console.error(error);

            setFormError(
                error.response?.data?.detail ||
                "Unable to create prescription."
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
                        <h1>Create Prescription</h1>

                        <p>
                            Create a new prescription
                            for one of your patients.
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


                {loading && (
                    <div className="empty-state">
                        <p>Loading patients and pharmacies...</p>
                    </div>
                )}


                {!loading && error && (
                    <div className="empty-state">
                        <h2>Unable to Load Data</h2>
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
                                Patient
                            </label>

                            <select
                                value={patientId}
                                onChange={(event) =>
                                    setPatientId(
                                        event.target.value
                                    )
                                }
                            >
                                <option value="">
                                    Select patient
                                </option>

                                {patients.map((patient) => (
                                    <option
                                        key={patient.id}
                                        value={patient.id}
                                    >
                                        {patient.name}
                                        {patient.email
                                            ? ` (${patient.email})`
                                            : ""}
                                    </option>
                                ))}
                            </select>
                        </div>


                        <div>
                            <label>
                                Prescription Date
                            </label>

                            <input
                                type="date"
                                value={prescriptionDate}
                                onChange={(event) =>
                                    setPrescriptionDate(
                                        event.target.value
                                    )
                                }
                                required
                            />
                        </div>


                        <div>
                            <label>
                                Pharmacy{" "}
                                <span className="form-note">
                                    (optional)
                                </span>
                            </label>

                            <select
                                value={pharmacyId}
                                onChange={(event) =>
                                    setPharmacyId(
                                        event.target.value
                                    )
                                }
                            >
                                <option value="">
                                    No pharmacy
                                </option>

                                {pharmacies.map((pharmacy) => (
                                    <option
                                        key={pharmacy.id}
                                        value={pharmacy.id}
                                    >
                                        {pharmacy.name} - {pharmacy.location}
                                    </option>
                                ))}
                            </select>
                        </div>


                        <div>
                            <label>
                                Lab Test{" "}
                                <span className="form-note">
                                    (optional)
                                </span>
                            </label>

                            <select
                                value={testTypeId}
                                onChange={(event) =>
                                    setTestTypeId(
                                        event.target.value
                                    )
                                }
                            >
                                <option value="">
                                    No lab test
                                </option>

                                {testTypes.map((testType) => (
                                    <option
                                        key={testType.id}
                                        value={testType.id}
                                    >
                                        {testType.name} - {"\u20B9"}
                                        {Number(
                                            testType.price
                                        ).toFixed(2)}
                                    </option>
                                ))}
                            </select>
                        </div>


                        {formError && (
                            <p className="error-message">{formError}</p>
                        )}


                        <button
                            type="submit"
                            disabled={saving}
                        >
                            {saving
                                ? "Creating..."
                                : "Create Prescription"}
                        </button>

                    </form>
                )}

            </div>
        </MainLayout>
    );
}

export default DoctorCreatePrescription;