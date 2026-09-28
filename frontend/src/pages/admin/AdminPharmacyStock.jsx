import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getPharmacyStock,
    getPharmacyStockRecord,
    createPharmacyStock,
    updatePharmacyStock,
    deletePharmacyStock,
} from "../../api/pharmacyStock";
import { getPharmacies } from "../../api/pharmacies";
import { getMedicineBatches } from "../../api/medicineBatches";

function AdminPharmacyStock() {

    const [stock, setStock] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [pharmacies, setPharmacies] = useState([]);
    const [batches, setBatches] = useState([]);

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        pharmacy_id: "",
        batch_id: "",
        quantity: "",
    });
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [stockData, pharmData, batchData] = await Promise.all([
                getPharmacyStock(),
                getPharmacies(),
                getMedicineBatches(),
            ]);
            setStock(stockData);
            setPharmacies(pharmData);
            setBatches(batchData);
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Unable to load pharmacy stock."
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
        setForm({ pharmacy_id: "", batch_id: "", quantity: "" });
        setFormError("");
        setShowModal(true);
    };

    const openEdit = (item) => {
        setEditing(item);
        setForm({
            pharmacy_id: item.pharmacy_id || "",
            batch_id: item.batch_id || "",
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
            pharmacy_id: form.pharmacy_id ? Number(form.pharmacy_id) : null,
            batch_id: form.batch_id ? Number(form.batch_id) : null,
            quantity: form.quantity ? Number(form.quantity) : null,
        };

        try {
            if (editing) {
                await updatePharmacyStock(
                    editing.pharmacy_id,
                    editing.batch_id,
                    { quantity: payload.quantity }
                );
            } else {
                await createPharmacyStock(payload);
            }
            closeModal();
            await loadData();
        } catch (err) {
            console.error(err);
            setFormError(
                err.response?.data?.detail ||
                "Failed to save pharmacy stock."
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (pharmacyId, batchId) => {
        if (!window.confirm("Delete this stock record?")) return;

        try {
            await deletePharmacyStock(pharmacyId, batchId);
            await loadData();
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Failed to delete pharmacy stock."
            );
        }
    };

    const getPharmacyName = (id) => {
        const p = pharmacies.find((ph) => ph.id === id);
        return p ? p.name : id;
    };

    const getBatchNumber = (id) => {
        const b = batches.find((bat) => bat.id === id);
        return b ? b.batch_number || `Batch ${b.id}` : id;
    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <h2 className="section-title">Pharmacy Stock</h2>
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
                    <h2 className="section-title">Pharmacy Stock</h2>
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
                    <h1>Pharmacy Stock</h1>
                    <p>Manage pharmacy inventory</p>
                    <button type="button" className="btn-add" onClick={openAdd}>
                        Add Stock
                    </button>
                </div>


                {stock.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Stock Records</h2>
                        <p>No pharmacy stock records found.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Pharmacy</th>
                                        <th>Medicine Batch</th>
                                        <th>Quantity</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {stock.map((item, index) => (
                                        <tr key={`${item.pharmacy_id}-${item.batch_id}-${index}`}>
                                            <td>{getPharmacyName(item.pharmacy_id)}</td>
                                            <td>{getBatchNumber(item.batch_id)}</td>
                                            <td>{item.quantity}</td>
                                            <td>
                                                <button type="button" className="action-btn btn-edit" onClick={() => openEdit(item)}>
                                                    Edit
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() =>
                                                        handleDelete(
                                                            item.pharmacy_id,
                                                            item.batch_id
                                                        )
                                                    }
                                                >
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
                                    {editing ? "Edit Stock" : "Add Stock"}
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
                                    <label className="form-label">Pharmacy</label>
                                    <select
                                        className="form-select"
                                        name="pharmacy_id"
                                        value={form.pharmacy_id}
                                        onChange={handleChange}
                                        required
                                        disabled={!!editing}
                                    >
                                        <option value="">Select Pharmacy</option>
                                        {pharmacies.map((p) => (
                                            <option key={p.id} value={p.id}>
                                                {p.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Medicine Batch</label>
                                    <select
                                        className="form-select"
                                        name="batch_id"
                                        value={form.batch_id}
                                        onChange={handleChange}
                                        required
                                        disabled={!!editing}
                                    >
                                        <option value="">Select Batch</option>
                                        {batches.map((b) => (
                                            <option key={b.id} value={b.id}>
                                                {b.batch_number || `Batch ${b.id}`}
                                            </option>
                                        ))}
                                    </select>
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

export default AdminPharmacyStock;
