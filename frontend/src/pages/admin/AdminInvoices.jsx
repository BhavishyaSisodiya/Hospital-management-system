import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getInvoices,
    getInvoice,
    createInvoice,
    updateInvoice,
    deleteInvoice,
} from "../../api/invoices";

function AdminInvoices() {

    const [invoices, setInvoices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        invoice_number: "",
        patient_id: "",
        admission_id: "",
        total_amount: "",
        issue_date: "",
        due_date: "",
        status: "pending",
    });
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const data = await getInvoices();
            setInvoices(data);
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Unable to load invoices."
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
            invoice_number: "",
            patient_id: "",
            admission_id: "",
            total_amount: "",
            issue_date: "",
            due_date: "",
            status: "pending",
        });
        setFormError("");
        setShowModal(true);
    };

    const openEdit = (item) => {
        setEditing(item);
        setForm({
            invoice_number: item.invoice_number || "",
            patient_id: item.patient_id || "",
            admission_id: item.admission_id || "",
            total_amount: item.total_amount || "",
            issue_date: item.issue_date || "",
            due_date: item.due_date || "",
            status: item.status || "pending",
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
            patient_id: form.patient_id ? Number(form.patient_id) : null,
            admission_id: form.admission_id ? Number(form.admission_id) : null,
            total_amount: form.total_amount ? Number(form.total_amount) : null,
        };

        try {
            if (editing) {
                await updateInvoice(editing.id, payload);
            } else {
                await createInvoice(payload);
            }
            closeModal();
            await loadData();
        } catch (err) {
            console.error(err);
            setFormError(
                err.response?.data?.detail ||
                "Failed to save invoice."
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this invoice?")) return;

        try {
            await deleteInvoice(id);
            await loadData();
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Failed to delete invoice."
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
                    <h2 className="section-title">Invoices</h2>
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
                    <h2 className="section-title">Invoices</h2>
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
                    <h1>Invoices</h1>
                    <p>Manage patient invoices</p>
                    <button type="button" className="btn-add" onClick={openAdd}>
                        Add Invoice
                    </button>
                </div>


                {invoices.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Invoices</h2>
                        <p>No invoices found.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Invoice Number</th>
                                        <th>Patient</th>
                                        <th>Admission</th>
                                        <th>Total Amount</th>
                                        <th>Issue Date</th>
                                        <th>Due Date</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {invoices.map((item) => (
                                        <tr key={item.id}>
                                            <td>{item.invoice_number}</td>
                                            <td>{item.patient_id}</td>
                                            <td>{item.admission_id || "-"}</td>
                                            <td>{item.total_amount}</td>
                                            <td>{item.issue_date || "-"}</td>
                                            <td>{item.due_date || "-"}</td>
                                            <td>
                                                <span className={`status-badge status-${item.status}`}>
                                                    {item.status}
                                                </span>
                                            </td>
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
                                    {editing ? "Edit Invoice" : "Add Invoice"}
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
                                    <label className="form-label">Invoice Number</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="invoice_number"
                                        value={form.invoice_number}
                                        onChange={handleChange}
                                        required
                                    />
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
                                    <label className="form-label">Admission ID (optional)</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        name="admission_id"
                                        value={form.admission_id}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Total Amount</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        name="total_amount"
                                        value={form.total_amount}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Issue Date</label>
                                    <input
                                        type="date"
                                        className="form-input"
                                        name="issue_date"
                                        value={form.issue_date}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Due Date</label>
                                    <input
                                        type="date"
                                        className="form-input"
                                        name="due_date"
                                        value={form.due_date}
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
                                        <option value="paid">Paid</option>
                                        <option value="overdue">Overdue</option>
                                        <option value="cancelled">Cancelled</option>
                                    </select>
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

export default AdminInvoices;
