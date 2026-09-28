import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getLabTests,
    getLabTest,
    createLabTest,
    updateLabTest,
    deleteLabTest,
} from "../../api/labTests";
import { getTestTypes } from "../../api/testTypes";
import { getPatient } from "../../api/patients";

function AdminLabTests() {

    const [labTests, setLabTests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [testTypes, setTestTypes] = useState([]);
    const [patients, setPatients] = useState([]);

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        test_type_id: "",
        patient_id: "",
        prescription_id: "",
        status: "pending",
        date: "",
    });
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [testsData, typesData] = await Promise.all([
                getLabTests(),
                getTestTypes(),
            ]);
            setLabTests(testsData);
            setTestTypes(typesData);

            const patientIds = [
                ...new Set(testsData.map((t) => t.patient_id).filter(Boolean)),
            ];
            const patientPromises = patientIds.map((id) =>
                getPatient(id).catch(() => ({ id, full_name: `Patient ${id}` }))
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
                "Unable to load lab tests."
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
            test_type_id: "",
            patient_id: "",
            prescription_id: "",
            status: "pending",
            date: "",
        });
        setFormError("");
        setShowModal(true);
    };

    const openEdit = (item) => {
        setEditing(item);
        setForm({
            test_type_id: item.test_type_id || "",
            patient_id: item.patient_id || "",
            prescription_id: item.prescription_id || "",
            status: item.status || "pending",
            date: item.date || "",
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
            test_type_id: form.test_type_id ? Number(form.test_type_id) : null,
            patient_id: form.patient_id ? Number(form.patient_id) : null,
            prescription_id: form.prescription_id ? Number(form.prescription_id) : null,
        };

        try {
            if (editing) {
                await updateLabTest(editing.id, payload);
            } else {
                await createLabTest(payload);
            }
            closeModal();
            await loadData();
        } catch (err) {
            console.error(err);
            setFormError(
                err.response?.data?.detail ||
                "Failed to save lab test."
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this lab test?")) return;

        try {
            await deleteLabTest(id);
            await loadData();
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Failed to delete lab test."
            );
        }
    };

    const getTestTypeName = (id) => {
        const t = testTypes.find((tt) => tt.id === id);
        return t ? t.name : id;
    };

    const getPatientName = (id) => {
        const p = patients[id];
        return p ? p.full_name || p.name || id : id;
    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <h2 className="section-title">Lab Tests</h2>
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
                    <h2 className="section-title">Lab Tests</h2>
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
                    <h1>Lab Tests</h1>
                    <p>Manage laboratory tests</p>
                    <button type="button" className="btn-add" onClick={openAdd}>
                        Add Lab Test
                    </button>
                </div>


                {labTests.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Lab Tests</h2>
                        <p>No lab tests found.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Test Type</th>
                                        <th>Patient</th>
                                        <th>Prescription</th>
                                        <th>Status</th>
                                        <th>Date</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {labTests.map((item) => (
                                        <tr key={item.id}>
                                            <td>{getTestTypeName(item.test_type_id)}</td>
                                            <td>{getPatientName(item.patient_id)}</td>
                                            <td>{item.prescription_id || "-"}</td>
                                            <td>
                                                <span className={`status-badge status-${item.status}`}>
                                                    {item.status}
                                                </span>
                                            </td>
                                            <td>{item.date || "-"}</td>
                                            <td>
                                                <button type="button" className="action-btn btn-edit" onClick={() => openEdit(item)}>
                                                    Edit
                                                </button>
                                                <button type="button" className="action-btn btn-delete" onClick={() => handleDelete(item.id)}>
                                                    Delete
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
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
                                    {editing ? "Edit Lab Test" : "Add Lab Test"}
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

                            <form className="form-group" onSubmit={handleSubmit}>

                                <div className="form-row">
                                    <label className="form-label">Test Type</label>
                                    <select
                                        className="form-select"
                                        name="test_type_id"
                                        value={form.test_type_id}
                                        onChange={handleChange}
                                        required
                                    >
                                        <option value="">Select Test Type</option>
                                        {testTypes.map((tt) => (
                                            <option key={tt.id} value={tt.id}>
                                                {tt.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Patient ID</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        name="patient_id"
                                        value={form.patient_id}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Prescription ID (optional)</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        name="prescription_id"
                                        value={form.prescription_id}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Status</label>
                                    <select
                                        className="form-select"
                                        name="status"
                                        value={form.status}
                                        onChange={handleChange}
                                        required
                                    >
                                        <option value="pending">Pending</option>
                                        <option value="completed">Completed</option>
                                        <option value="cancelled">Cancelled</option>
                                    </select>
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Date</label>
                                    <input
                                        type="date"
                                        className="form-input"
                                        name="date"
                                        value={form.date}
                                        onChange={handleChange}
                                        required
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

export default AdminLabTests;
