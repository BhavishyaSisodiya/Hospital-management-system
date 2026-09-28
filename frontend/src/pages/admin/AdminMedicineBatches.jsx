import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getMedicineBatches,
    getMedicineBatch,
    createMedicineBatch,
    updateMedicineBatch,
    deleteMedicineBatch,
} from "../../api/medicineBatches";
import { getMedicines } from "../../api/medicines";

function AdminMedicineBatches() {

    const [batches, setBatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [medicines, setMedicines] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        medicine_id: "",
        batch_number: "",
        expiry_date: "",
        price: "",
        quantity: "",
    });
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [batchData, medData] = await Promise.all([
                getMedicineBatches(),
                getMedicines(),
            ]);
            setBatches(batchData);
            setMedicines(medData);
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Unable to load medicine batches."
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
            medicine_id: "",
            batch_number: "",
            expiry_date: "",
            price: "",
            quantity: "",
        });
        setFormError("");
        setShowModal(true);
    };

    const openEdit = (item) => {
        setEditing(item);
        setForm({
            medicine_id: item.medicine_id || "",
            batch_number: item.batch_number || "",
            expiry_date: item.expiry_date || "",
            price: item.price || "",
            quantity: item.quantity || "",
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
            medicine_id: form.medicine_id ? Number(form.medicine_id) : null,
            price: form.price ? Number(form.price) : null,
            quantity: form.quantity ? Number(form.quantity) : null,
        };

        try {
            if (editing) {
                await updateMedicineBatch(editing.id, payload);
            } else {
                await createMedicineBatch(payload);
            }
            closeModal();
            await loadData();
        } catch (err) {
            console.error(err);
            setFormError(
                err.response?.data?.detail ||
                "Failed to save medicine batch."
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this medicine batch?")) return;

        try {
            await deleteMedicineBatch(id);
            await loadData();
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Failed to delete medicine batch."
            );
        }
    };

    const getMedicineName = (id) => {
        const m = medicines.find((med) => med.id === id);
        return m ? m.name : id;
    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <h2 className="section-title">Medicine Batches</h2>
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
                    <h2 className="section-title">Medicine Batches</h2>
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
                    <h1>Medicine Batches</h1>
                    <p>Manage medicine batch inventory</p>
                    <button type="button" className="btn-add" onClick={openAdd}>
                        Add Batch
                    </button>
                </div>


                {batches.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Batches</h2>
                        <p>No medicine batches found.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Medicine</th>
                                        <th>Batch Number</th>
                                        <th>Expiry Date</th>
                                        <th>Price</th>
                                        <th>Quantity</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {batches.map((item) => (
                                        <tr key={item.id}>
                                            <td>{getMedicineName(item.medicine_id)}</td>
                                            <td>{item.batch_number}</td>
                                            <td>{item.expiry_date || "-"}</td>
                                            <td>{item.price}</td>
                                            <td>{item.quantity}</td>
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
                                    {editing ? "Edit Batch" : "Add Batch"}
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
                                    <label className="form-label">Medicine</label>
                                    <select
                                        className="form-select"
                                        name="medicine_id"
                                        value={form.medicine_id}
                                        onChange={handleChange}
                                        required
                                    >
                                        <option value="">Select Medicine</option>
                                        {medicines.map((m) => (
                                            <option key={m.id} value={m.id}>
                                                {m.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Batch Number</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="batch_number"
                                        value={form.batch_number}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Expiry Date</label>
                                    <input
                                        type="date"
                                        className="form-input"
                                        name="expiry_date"
                                        value={form.expiry_date}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Price</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        name="price"
                                        value={form.price}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Quantity</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        name="quantity"
                                        value={form.quantity}
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

export default AdminMedicineBatches;
