import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";

import {
    getMedicalRecord,
    updateMedicalRecord,
} from "../../api/medicalRecords";

function DoctorEditMedicalRecord() {
    const { recordId } = useParams();
    const navigate = useNavigate();

    const [record, setRecord] = useState(null);

    const [diagnosis, setDiagnosis] = useState("");
    const [notes, setNotes] = useState("");
    const [recordDate, setRecordDate] = useState("");

    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    useEffect(() => {
        const loadRecord = async () => {
            try {
                setLoading(true);
                setError("");

                const data = await getMedicalRecord(recordId);

                setRecord(data);
                setDiagnosis(data.diagnosis || "");
                setNotes(data.notes || "");

                if (data.record_date) {
                    const date = new Date(data.record_date);

                    const localDate = new Date(
                        date.getTime() -
                            date.getTimezoneOffset() * 60000
                    )
                        .toISOString()
                        .slice(0, 16);

                    setRecordDate(localDate);
                }
            } catch (error) {
                console.error(error);

                setError(
                    error.response?.data?.detail ||
                        "Unable to load medical record."
                );
            } finally {
                setLoading(false);
            }
        };

        loadRecord();
    }, [recordId]);

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");
        setSuccess("");

        if (!diagnosis.trim()) {
            setError("Diagnosis is required.");
            return;
        }

        try {
            setSubmitting(true);

            const recordData = {
                diagnosis: diagnosis.trim(),
                notes: notes.trim() || null,
                record_date: recordDate
                    ? new Date(recordDate).toISOString()
                    : null,
            };

            const updatedRecord = await updateMedicalRecord(
                recordId,
                recordData
            );

            setRecord(updatedRecord);
            setDiagnosis(updatedRecord.diagnosis || "");
            setNotes(updatedRecord.notes || "");

            if (updatedRecord.record_date) {
                const date = new Date(
                    updatedRecord.record_date
                );

                const localDate = new Date(
                    date.getTime() -
                        date.getTimezoneOffset() * 60000
                )
                    .toISOString()
                    .slice(0, 16);

                setRecordDate(localDate);
            }

            setSuccess(
                "Medical record updated successfully."
            );
        } catch (error) {
            console.error(error);

            setError(
                error.response?.data?.detail ||
                    "Unable to update medical record."
            );
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="medical-record-form-page">
                    <div className="empty-state">
                        <p>Loading medical record...</p>
                    </div>
                </div>
            </MainLayout>
        );
    }

    if (error && !record) {
        return (
            <MainLayout>
                <div className="medical-record-form-page">
                    <div className="empty-state">
                        <h2>Unable to Load Medical Record</h2>
                        <p>{error}</p>

                        <button
                            type="button"
                            onClick={() =>
                                navigate(
                                    "/doctor/medical-records"
                                )
                            }
                        >
                            Back to Medical Records
                        </button>
                    </div>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="medical-record-form-page">
                <div className="medical-records-header">
                    <h1>Edit Medical Record</h1>

                    <p>
                        Update the medical record for your
                        patient.
                    </p>
                </div>

                {record && (
                    <div className="record-info">
                        <p>
                            <strong>Record ID:</strong>{" "}
                            {record.id}
                        </p>

                        <p>
                            <strong>Patient ID:</strong>{" "}
                            {record.patient_id}
                        </p>

                        <p>
                            <strong>Doctor ID:</strong>{" "}
                            {record.doctor_id}
                        </p>
                    </div>
                )}

                <form
                    className="medical-record-form"
                    onSubmit={handleSubmit}
                >
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
                                setNotes(event.target.value)
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
                                ? "Updating..."
                                : "Update Record"}
                        </button>
                    </div>
                </form>
            </div>
        </MainLayout>
    );
}

export default DoctorEditMedicalRecord;

