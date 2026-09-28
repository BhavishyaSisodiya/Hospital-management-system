import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";

import {
    createMedicalRecord,
} from "../../api/medicalRecords";

import {
    getMyDoctorPatients,
} from "../../api/patients";


function CreateMedicalRecord() {
    const navigate = useNavigate();

    const [patients, setPatients] = useState([]);

    const [patientId, setPatientId] = useState("");
    const [diagnosis, setDiagnosis] = useState("");
    const [notes, setNotes] = useState("");
    const [recordDate, setRecordDate] = useState("");

    const [loadingPatients, setLoadingPatients] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    useEffect(() => {
        const loadPatients = async () => {
            try {
                setLoadingPatients(true);
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
                setLoadingPatients(false);
            }
        };

        loadPatients();
    }, []);

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");
        setSuccess("");

        if (!patientId) {
            setError("Please select a patient.");
            return;
        }

        if (!diagnosis.trim()) {
            setError("Diagnosis is required.");
            return;
        }

        try {
            setSubmitting(true);

            const recordData = {
                patient_id: Number(patientId),

                // Backend will replace this with the
                // authenticated doctor's ID.
                doctor_id: 0,

                diagnosis: diagnosis.trim(),

                notes: notes.trim() || null,

                record_date: recordDate
                    ? new Date(recordDate).toISOString()
                    : null,
            };

            await createMedicalRecord(recordData);

            setSuccess(
                "Medical record created successfully."
            );

            setPatientId("");
            setDiagnosis("");
            setNotes("");
            setRecordDate("");

        } catch (error) {
            console.error(error);

            setError(
                error.response?.data?.detail ||
                "Unable to create medical record."
            );
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <MainLayout>
            <div className="medical-record-form-page">

                <div className="medical-records-header">
                    <h1>Create Medical Record</h1>

                    <p>
                        Create a medical record for one of
                        your patients.
                    </p>
                </div>

                {loadingPatients && (
                    <div className="empty-state">
                        <p>Loading patients...</p>
                    </div>
                )}

                {!loadingPatients && error && (
                    <div className="empty-state">
                        <p>{error}</p>
                    </div>
                )}

                {!loadingPatients && (
                    <form
                        className="medical-record-form"
                        onSubmit={handleSubmit}
                    >

                        <div className="form-group">
                            <label htmlFor="patient">
                                Patient
                            </label>

                            <select
                                id="patient"
                                value={patientId}
                                onChange={(event) =>
                                    setPatientId(
                                        event.target.value
                                    )
                                }
                                disabled={submitting}
                                required
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
                                        {" "}— ID: {patient.id}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="diagnosis">
                                Diagnosis
                            </label>

                            <input
                                id="diagnosis"
                                type="text"
                                value={diagnosis}
                                onChange={(event) =>
                                    setDiagnosis(
                                        event.target.value
                                    )
                                }
                                placeholder="Enter diagnosis"
                                maxLength={255}
                                disabled={submitting}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="recordDate">
                                Record Date
                            </label>

                            <input
                                id="recordDate"
                                type="datetime-local"
                                value={recordDate}
                                onChange={(event) =>
                                    setRecordDate(
                                        event.target.value
                                    )
                                }
                                disabled={submitting}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="notes">
                                Notes
                            </label>

                            <textarea
                                id="notes"
                                value={notes}
                                onChange={(event) =>
                                    setNotes(
                                        event.target.value
                                    )
                                }
                                placeholder="Enter additional notes"
                                rows={5}
                                disabled={submitting}
                            />
                        </div>

                        {error && (
                            <div className="form-error">
                                {error}
                            </div>
                        )}

                        {success && (
                            <div className="form-success">
                                {success}
                            </div>
                        )}

                        <div className="form-actions">

                            <button
                                type="button"
                                onClick={() =>
                                    navigate(
                                        "/doctor/medical-records"
                                    )
                                }
                                disabled={submitting}
                            >
                                Cancel
                            </button>

                            <button
                                type="submit"
                                disabled={submitting}
                            >
                                {submitting
                                    ? "Creating..."
                                    : "Create Record"}
                            </button>

                        </div>

                    </form>
                )}
            </div>
        </MainLayout>
    );
}

export default CreateMedicalRecord;