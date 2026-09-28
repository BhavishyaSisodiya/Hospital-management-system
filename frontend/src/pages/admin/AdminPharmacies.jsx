import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getPharmacies,
    getPharmacy,
    createPharmacy,
    updatePharmacy,
    deletePharmacy,
} from "../../api/pharmacies";

function AdminPharmacies() {

    const [pharmacies, setPharmacies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        name: "",
        address: "",
        phone: "",
        email: "",
    });
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const data = await getPharmacies();
            setPharmacies(data);
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Unable to load pharmacies."
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
        setForm({ name: "", address: "", phone: "", email: "" });
        setFormError("");
        setShowModal(true);
    };

    const openEdit = (item) => {
        setEditing(item);
        setForm({
            name: item.name || "",
            address: item.address || "",
            phone: item.phone || "",
            email: item.email || "",
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
                await updatePharmacy(editing.id, form);
            } else {
                await createPharmacy(form);
            }
            closeModal();
            await loadData();
        } catch (err) {
            console.error(err);
            setFormError(
                err.response?.data?.detail ||
                "Failed to save pharmacy."
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this pharmacy?")) return;

        try {
            await deletePharmacy(id);
            await loadData();
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Failed to delete pharmacy."
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
                    <h2 className="section-title">Pharmacies</h2>
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
                    <h2 className="section-title">Pharmacies</h2>
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
                    <h1>Pharmacies</h1>
                    <p>Manage pharmacies</p>
                    <button type="button" className="btn-add" onClick={openAdd}>
                        Add Pharmacy
                    </button>
                </div>


                {pharmacies.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Pharmacies</h2>
                        <p>No pharmacies found.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Address</th>
                                        <th>Phone</th>
                                        <th>Email</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {pharmacies.map((item) => (
                                        <tr key={item.id}>
                                            <td>{item.name}</td>
                                            <td>{item.address || "-"}</td>
                                            <td>{item.phone || "-"}</td>
                                            <td>{item.email || "-"}</td>
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
                                    {editing ? "Edit Pharmacy" : "Add Pharmacy"}
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
                                    <label className="form-label">Address</label>
                                    <textarea
                                        className="form-textarea"
                                        name="address"
                                        value={form.address}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Phone</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="phone"
                                        value={form.phone}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Email</label>
                                    <input
                                        type="email"
                                        className="form-input"
                                        name="email"
                                        value={form.email}
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

export default AdminPharmacies;
