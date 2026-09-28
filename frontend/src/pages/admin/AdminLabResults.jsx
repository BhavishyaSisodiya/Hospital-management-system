import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getLabResults,
    createLabResult,
    updateLabResult,
    deleteLabResult,
} from "../../api/labResults";
import { getLabTests } from "../../api/labTests";
import { getTestTypes } from "../../api/testTypes";
import { getPatient } from "../../api/patients";

function AdminLabResults() {

    const [labResults, setLabResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [labTests, setLabTests] = useState([]);
    const [testTypes, setTestTypes] = useState([]);
    const [patients, setPatients] = useState({});

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        lab_test_id: "",
        result: "",
        unit: "",
        reference_range: "",
        remarks: "",
    });
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [resultsData, testsData, typesData] = await Promise.all([
                getLabResults(),
                getLabTests(),
                getTestTypes(),
            ]);
            setLabResults(resultsData);
            setLabTests(testsData);
            setTestTypes(typesData);

            const patientIds = [
                ...new Set(testsData.map((t) => t.patient_id).filter(Boolean)),
            ];
            const patientPromises = patientIds.map((id) =>
                getPatient(id).catch(() => ({ id, name: `Patient ${id}` }))
            );
            const patientResults = await Promise.all(patientPromises);
            const patientMap = {};
            patientResults.forEach((p) => {
                patientMap[p.id] = p;
            });
            setPatients(patientMap);
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Unable to load lab results."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const openAdd = () => {
        setEditing(null);
        setForm({
            lab_test_id: "",
            result: "",
            unit: "",
            reference_range: "",
            remarks: "",
        });
        setFormError("");
        setShowModal(true);
    };

    const openEdit = (item) => {
        setEditing(item);
        setForm({
            lab_test_id: item.lab_test_id || "",
            result: item.result || "",
            unit: item.unit || "",
            reference_range: item.reference_range || "",
            remarks: item.remarks || "",
        });
        setFormError("");
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
        setEditing(null);
        setFormError("");
    };

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setFormError("");

        const payload = {
            ...form,
            lab_test_id: form.lab_test_id
                ? Number(form.lab_test_id)
                : null,
        };

        try {
            if (editing) {
                await updateLabResult(editing.id, payload);
            } else {
                await createLabResult(payload);
            }
            closeModal();
            await loadData();
        } catch (err) {
            console.error(err);
            setFormError(
                err.response?.data?.detail ||
                "Failed to save lab result."
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this lab result?")) return;

        try {
            await deleteLabResult(id);
            await loadData();
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Failed to delete lab result."
            );
        }
    };

    const getTestTypeName = (id) => {
        const t = testTypes.find((tt) => tt.id === id);
        return t ? t.name : id;
    };

    const getLabTestInfo = (labTestId) => {
        const lt = labTests.find((t) => t.id === labTestId);
        if (!lt) return { label: `Lab Test #${labTestId}` };
        const patient = patients[lt.patient_id];
        const patientName = patient
            ? patient.full_name || patient.name
            : `Patient #${lt.patient_id}`;
        return {
            label: `${patientName} - ${getTestTypeName(lt.test_type_id)}`,
            patientName,
        };
    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <h2 className="section-title">Lab Results</h2>
                    <p className="loading-message">Loading...</p>
                </div>
            </MainLayout>
        );
    }


    // ============================================================
    // ERROR
    // ============================================================

    if (error) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <h2 className="section-title">Lab Results</h2>
                    <p className="error-message">{error}</p>
                </div>
            </MainLayout>
        );
    }


    // ============================================================
    // PAGE
    // ============================================================

    return (
        <MainLayout>
            <div className="dashboard-page">

                <div className="dashboard-header">
                    <h1>Lab Results</h1>
                    <p>View laboratory test results</p>
                    <button type="button" className="btn-add" onClick={openAdd}>
                        Add Lab Result
                    </button>
                </div>


                {labResults.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Lab Results</h2>
                        <p>No lab results found.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Lab Test</th>
                                        <th>Result</th>
                                        <th>Unit</th>
                                        <th>Reference Range</th>
                                        <th>Remarks</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {labResults.map((item) => {
                                        const info = getLabTestInfo(
                                            item.lab_test_id
                                        );
                                        return (
                                            <tr key={item.id}>
                                                <td>{info.label}</td>
                                                <td>{item.result || "-"}</td>
                                                <td>{item.unit || "-"}</td>
                                                <td>
                                                    {item.reference_range || "-"}
                                                </td>
                                                <td>{item.remarks || "-"}</td>
                                                <td>
                                                    <button
                                                        type="button"
                                                        className="action-btn btn-edit"
                                                        onClick={() =>
                                                            openEdit(item)
                                                        }
                                                    >
                                                        Edit
                                                    </button>
                                                    <button
                                                        type="button"
                                                        className="action-btn btn-delete"
                                                        onClick={() =>
                                                            handleDelete(item.id)
                                                        }
                                                    >
                                                        Delete
                                                    </button>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}


                {showModal && (
                    <div className="modal-overlay">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h2>
                                    {editing
                                        ? "Edit Lab Result"
                                        : "Add Lab Result"}
                                </h2>
                                <button
                                    type="button"
                                    className="cancel-btn"
                                    onClick={closeModal}
                                >
                                    &times;
                                </button>
                            </div>

                            {formError && (
                                <p className="error-message">{formError}</p>
                            )}

                            <form
                                className="form-group"
                                onSubmit={handleSubmit}
                            >
                                <div className="form-row">
                                    <label className="form-label">
                                        Lab Test
                                    </label>
                                    <select
                                        className="form-select"
                                        name="lab_test_id"
                                        value={form.lab_test_id}
                                        onChange={handleChange}
                                        required
                                    >
                                        <option value="">
                                            Select Lab Test
                                        </option>
                                        {labTests.map((t) => {
                                            const info = {
                                                testName: getTestTypeName(
                                                    t.test_type_id
                                                ),
                                                patientName: (
                                                    patients[t.patient_id] ||
                                                    {}
                                                ).name,
                                            };
                                            return (
                                                <option
                                                    key={t.id}
                                                    value={t.id}
                                                >
                                                    #{t.id} -{" "}
                                                    {info.testName}
                                                    {info.patientName
                                                        ? ` - ${info.patientName}`
                                                        : ""}
                                                </option>
                                            );
                                        })}
                                    </select>
                                </div>

                                <div className="form-row">
                                    <label className="form-label">
                                        Result
                                    </label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="result"
                                        value={form.result}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">
                                        Unit
                                    </label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="unit"
                                        value={form.unit}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">
                                        Reference Range
                                    </label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="reference_range"
                                        value={form.reference_range}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">
                                        Remarks
                                    </label>
                                    <textarea
                                        className="form-textarea"
                                        name="remarks"
                                        value={form.remarks}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="booking-actions">
                                    <button
                                        type="submit"
                                        disabled={submitting}
                                    >
                                        {submitting
                                            ? "Saving..."
                                            : editing
                                                ? "Update"
                                                : "Create"}
                                    </button>
                                    <button
                                        type="button"
                                        className="cancel-btn"
                                        onClick={closeModal}
                                    >
                                        Cancel
                                    </button>
                                </div>

                            </form>
                        </div>
                    </div>
                )}

            </div>
        </MainLayout>
    );
}

export default AdminLabResults;