import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getMedicines,
    getMedicine,
    createMedicine,
    updateMedicine,
    deleteMedicine,
} from "../../api/medicines";

function AdminMedicines() {

    const [medicines, setMedicines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        name: "",
        description: "",
        category: "",
        dosageForm: "",
        strength: "",
    });
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const data = await getMedicines();
            setMedicines(data);
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Unable to load medicines."
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
            name: "",
            description: "",
            category: "",
            dosageForm: "",
            strength: "",
        });
        setFormError("");
        setShowModal(true);
    };

    const openEdit = (item) => {
        setEditing(item);
        setForm({
            name: item.name || "",
            description: item.description || "",
            category: item.category || "",
            dosageForm: item.dosageForm || item.dosage_form || "",
            strength: item.strength || "",
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

        try {
            if (editing) {
                await updateMedicine(editing.id, form);
            } else {
                await createMedicine(form);
            }
            closeModal();
            await loadData();
        } catch (err) {
            console.error(err);
            setFormError(
                err.response?.data?.detail ||
                "Failed to save medicine."
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this medicine?")) return;

        try {
            await deleteMedicine(id);
            await loadData();
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Failed to delete medicine."
            );
        }
    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <h2 className="section-title">Medicines</h2>
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
                    <h2 className="section-title">Medicines</h2>
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
                    <h1>Medicines</h1>
                    <p>Manage medicine catalog</p>
                    <button type="button" className="btn-add" onClick={openAdd}>
                        Add Medicine
                    </button>
                </div>


                {medicines.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Medicines</h2>
                        <p>No medicines found.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Description</th>
                                        <th>Category</th>
                                        <th>Dosage Form</th>
                                        <th>Strength</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {medicines.map((item) => (
                                        <tr key={item.id}>
                                            <td>{item.name}</td>
                                            <td>{item.description || "-"}</td>
                                            <td>{item.category || "-"}</td>
                                            <td>{item.dosageForm || item.dosage_form || "-"}</td>
                                            <td>{item.strength || "-"}</td>
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
                                    {editing ? "Edit Medicine" : "Add Medicine"}
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
                                    <label className="form-label">Name</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="name"
                                        value={form.name}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Description</label>
                                    <textarea
                                        className="form-textarea"
                                        name="description"
                                        value={form.description}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Category</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="category"
                                        value={form.category}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Dosage Form</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="dosageForm"
                                        value={form.dosageForm}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Strength</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="strength"
                                        value={form.strength}
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

export default AdminMedicines;
