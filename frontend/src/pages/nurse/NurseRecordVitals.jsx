import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { useAuth } from "../../context/AuthContext";
import { createVitals, getPatientVitals } from "../../api/vitals";
import { getAdmissions } from "../../api/admissions";

function NurseRecordVitals() {

    const { userId } = useAuth();

    const [admissions, setAdmissions] = useState([]);
    const [vitals, setVitals] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const [saving, setSaving] = useState(false);

    const [selectedAdmissionId, setSelectedAdmissionId] =
        useState("");
    const [selectedPatientId, setSelectedPatientId] =
        useState(null);

    const [formData, setFormData] = useState({
        temperature: "",
        heart_rate: "",
        blood_pressure_systolic: "",
        blood_pressure_diastolic: "",
        respiratory_rate: "",
        oxygen_saturation: "",
        weight: "",
        notes: "",
    });


    /* ============================================================
       LOAD ADMISSIONS
       ============================================================ */

    useEffect(() => {

        const loadAdmissions = async () => {

            try {

                setLoading(true);
                setError("");

                const data = await getAdmissions();

                const activeAdmissions = data.filter(
                    (a) => a.status === "admitted"
                );

                setAdmissions(activeAdmissions);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Unable to load admissions."
                );

            } finally {

                setLoading(false);

            }
        };

        loadAdmissions();

    }, []);


    /* ============================================================
       LOAD VITALS WHEN ADMISSION IS SELECTED
       ============================================================ */

    useEffect(() => {

        const loadVitals = async () => {

            if (!selectedAdmissionId) {
                setVitals([]);
                setSelectedPatientId(null);
                return;
            }

            const admission = admissions.find(
                (a) =>
                    a.id ===
                    parseInt(selectedAdmissionId, 10)
            );

            if (!admission) {
                return;
            }

            setSelectedPatientId(admission.patient_id);

            try {

                const data = await getPatientVitals(
                    admission.patient_id
                );

                setVitals(data);

            } catch (err) {

                console.error(err);

                setVitals([]);

            }
        };

        loadVitals();

    }, [selectedAdmissionId, admissions]);


    /* ============================================================
       FORM HANDLERS
       ============================================================ */

    const handleChange = (event) => {

        const { name, value } = event.target;

        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));

    };

    const handleSubmit = async (event) => {

        event.preventDefault();

        setError("");
        setSuccess("");
        setSaving(true);

        try {

            const payload = {
                patient_id: selectedPatientId,
                recorded_by: parseInt(userId, 10),
                temperature: formData.temperature
                    ? parseFloat(formData.temperature)
                    : null,
                heart_rate: formData.heart_rate
                    ? parseInt(formData.heart_rate, 10)
                    : null,
                blood_pressure_systolic:
                    formData.blood_pressure_systolic
                        ? parseInt(
                            formData.blood_pressure_systolic,
                            10
                        )
                        : null,
                blood_pressure_diastolic:
                    formData.blood_pressure_diastolic
                        ? parseInt(
                            formData.blood_pressure_diastolic,
                            10
                        )
                        : null,
                respiratory_rate: formData.respiratory_rate
                    ? parseInt(formData.respiratory_rate, 10)
                    : null,
                oxygen_saturation:
                    formData.oxygen_saturation
                        ? parseFloat(
                            formData.oxygen_saturation
                        )
                        : null,
                weight: formData.weight
                    ? parseFloat(formData.weight)
                    : null,
            };

            await createVitals(payload);

            setSuccess("Vitals recorded successfully.");

            setFormData({
                temperature: "",
                heart_rate: "",
                blood_pressure_systolic: "",
                blood_pressure_diastolic: "",
                respiratory_rate: "",
                oxygen_saturation: "",
                weight: "",
                notes: "",
            });

            const vitalsData = await getPatientVitals(
                selectedPatientId
            );

            setVitals(vitalsData);

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Unable to record vitals."
            );

        } finally {

            setSaving(false);

        }

    };


    /* ============================================================
       FORMAT HELPERS
       ============================================================ */

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


    /* ============================================================
       RENDER
       ============================================================ */

    return (
        <MainLayout>
            <div className="appointments-page">

                <div className="appointments-header">
                    <div>
                        <h1>Record Vitals</h1>
                        <p>
                            Select an admission and record vital
                            signs for the patient.
                        </p>
                    </div>
                </div>


                {success && (
                    <p className="success-message">{success}</p>
                )}

                {error && (
                    <p className="error-message">{error}</p>
                )}


                {/* ==================================================
                   LOADING
                   ================================================== */}

                {loading && (
                    <p className="loading-message">
                        Loading admissions...
                    </p>
                )}


                {/* ==================================================
                   ADMISSION SELECTOR + FORM
                   ================================================== */}

                {!loading && (

                    <div className="table-wrapper">

                        <div className="form-group">
                            <label className="form-label">
                                Select Admission
                            </label>
                            <select
                                className="form-select"
                                value={selectedAdmissionId}
                                onChange={(e) =>
                                    setSelectedAdmissionId(
                                        e.target.value
                                    )
                                }
                            >
                                <option value="">
                                    Select an admission
                                </option>
                                {admissions.map((a) => (
                                    <option
                                        key={a.id}
                                        value={a.id}
                                    >
                                        Admission #{a.id} —
                                        Patient #
                                        {a.patient_id}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {selectedAdmissionId && (

                            <form
                                className="form-group"
                                onSubmit={handleSubmit}
                            >

                                <div className="form-row">
                                    <div className="form-group">
                                        <label className="form-label">
                                            Temperature (°C)
                                        </label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            className="form-input"
                                            name="temperature"
                                            value={
                                                formData.temperature
                                            }
                                            onChange={
                                                handleChange
                                            }
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">
                                            Heart Rate (bpm)
                                        </label>
                                        <input
                                            type="number"
                                            className="form-input"
                                            name="heart_rate"
                                            value={
                                                formData.heart_rate
                                            }
                                            onChange={
                                                handleChange
                                            }
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label className="form-label">
                                            BP Systolic (mmHg)
                                        </label>
                                        <input
                                            type="number"
                                            className="form-input"
                                            name="blood_pressure_systolic"
                                            value={
                                                formData.blood_pressure_systolic
                                            }
                                            onChange={
                                                handleChange
                                            }
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">
                                            BP Diastolic (mmHg)
                                        </label>
                                        <input
                                            type="number"
                                            className="form-input"
                                            name="blood_pressure_diastolic"
                                            value={
                                                formData.blood_pressure_diastolic
                                            }
                                            onChange={
                                                handleChange
                                            }
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label className="form-label">
                                            Respiratory Rate
                                        </label>
                                        <input
                                            type="number"
                                            className="form-input"
                                            name="respiratory_rate"
                                            value={
                                                formData.respiratory_rate
                                            }
                                            onChange={
                                                handleChange
                                            }
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">
                                            Oxygen Saturation (%)
                                        </label>
                                        <input
                                            type="number"
                                            step="0.1"
                                            className="form-input"
                                            name="oxygen_saturation"
                                            value={
                                                formData.oxygen_saturation
                                            }
                                            onChange={
                                                handleChange
                                            }
                                        />
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">
                                        Weight (kg)
                                    </label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        className="form-input"
                                        name="weight"
                                        value={formData.weight}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">
                                        Notes
                                    </label>
                                    <textarea
                                        className="form-textarea"
                                        name="notes"
                                        value={formData.notes}
                                        onChange={handleChange}
                                        rows="3"
                                    />
                                </div>

                                <div className="booking-actions">
                                    <button
                                        type="submit"
                                        disabled={saving}
                                    >
                                        {saving
                                            ? "Saving..."
                                            : "Record Vitals"}
                                    </button>
                                </div>

                            </form>

                        )}

                    </div>

                )}


                {/* ==================================================
                   EXISTING VITALS
                   ================================================== */}

                {!loading && selectedAdmissionId && (
                    <div className="dashboard-section">

                        <h2 className="section-title">
                            Existing Vitals
                        </h2>

                        {vitals.length === 0 ? (
                            <div className="empty-state">
                                <h2>No Vitals Recorded</h2>
                                <p>
                                    No vital records found for
                                    this patient.
                                </p>
                            </div>
                        ) : (
                            <div className="vitals-grid">
                                {vitals.map((vital) => (
                                    <div
                                        key={vital.id}
                                        className="vital-card"
                                    >
                                        <h3>
                                            Record #
                                            {vital.id}
                                        </h3>

                                        <p>
                                            <strong>
                                                Recorded At:
                                            </strong>{" "}
                                            {formatDate(
                                                vital.recorded_at
                                            )}
                                        </p>

                                        <p>
                                            <strong>
                                                Recorded By:
                                            </strong>{" "}
                                            Employee #
                                            {vital.recorded_by}
                                        </p>

                                        <p>
                                            <strong>
                                                Temperature:
                                            </strong>{" "}
                                            {formatValue(
                                                vital.temperature,
                                                " °C"
                                            )}
                                        </p>

                                        <p>
                                            <strong>
                                                Heart Rate:
                                            </strong>{" "}
                                            {formatValue(
                                                vital.heart_rate,
                                                " bpm"
                                            )}
                                        </p>

                                        <p>
                                            <strong>
                                                Blood Pressure:
                                            </strong>{" "}
                                            {vital.blood_pressure_systolic !=
                                                null &&
                                            vital.blood_pressure_diastolic !=
                                                null
                                                ? `${vital.blood_pressure_systolic}/${vital.blood_pressure_diastolic} mmHg`
                                                : "-"}
                                        </p>

                                        <p>
                                            <strong>
                                                Respiratory Rate:
                                            </strong>{" "}
                                            {formatValue(
                                                vital.respiratory_rate,
                                                " breaths/min"
                                            )}
                                        </p>

                                        <p>
                                            <strong>
                                                O2 Saturation:
                                            </strong>{" "}
                                            {formatValue(
                                                vital.oxygen_saturation,
                                                "%"
                                            )}
                                        </p>

                                        <p>
                                            <strong>
                                                Weight:
                                            </strong>{" "}
                                            {formatValue(
                                                vital.weight,
                                                " kg"
                                            )}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        )}

                    </div>
                )}

            </div>
        </MainLayout>
    );
}

export default NurseRecordVitals;
