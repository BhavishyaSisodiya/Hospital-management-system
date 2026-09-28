import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getPayments,
    getPayment,
    createPayment,
    updatePayment,
    deletePayment,
} from "../../api/payments";
import { getInvoices } from "../../api/invoices";

function AdminPayments() {

    const [payments, setPayments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [invoices, setInvoices] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        invoice_id: "",
        amount: "",
        payment_method: "",
        payment_date: "",
        notes: "",
    });
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [paymentsData, invoiceData] = await Promise.all([
                getPayments(),
                getInvoices(),
            ]);
            setPayments(paymentsData);
            setInvoices(invoiceData);
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Unable to load payments."
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
            invoice_id: "",
            amount: "",
            payment_method: "",
            payment_date: "",
            notes: "",
        });
        setFormError("");
        setShowModal(true);
    };

    const openEdit = (item) => {
        setEditing(item);
        setForm({
            invoice_id: item.invoice_id || "",
            amount: item.amount || "",
            payment_method: item.payment_method || "",
            payment_date: item.payment_date || "",
            notes: item.notes || "",
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
            invoice_id: form.invoice_id ? Number(form.invoice_id) : null,
            amount: form.amount ? Number(form.amount) : null,
        };

        try {
            if (editing) {
                await updatePayment(editing.id, payload);
            } else {
                await createPayment(payload);
            }
            closeModal();
            await loadData();
        } catch (err) {
            console.error(err);
            setFormError(
                err.response?.data?.detail ||
                "Failed to save payment."
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this payment?")) return;

        try {
            await deletePayment(id);
            await loadData();
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Failed to delete payment."
            );
        }
    };

    const getInvoiceNumber = (id) => {
        const inv = invoices.find((i) => i.id === id);
        return inv ? inv.invoice_number || `Invoice ${inv.id}` : id;
    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <h2 className="section-title">Payments</h2>
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
                    <h2 className="section-title">Payments</h2>
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
                    <h1>Payments</h1>
                    <p>Manage invoice payments</p>
                    <button type="button" className="btn-add" onClick={openAdd}>
                        Add Payment
                    </button>
                </div>


                {payments.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Payments</h2>
                        <p>No payments found.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Invoice</th>
                                        <th>Amount</th>
                                        <th>Payment Method</th>
                                        <th>Payment Date</th>
                                        <th>Notes</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {payments.map((item) => (
                                        <tr key={item.id}>
                                            <td>{getInvoiceNumber(item.invoice_id)}</td>
                                            <td>{item.amount}</td>
                                            <td>{item.payment_method || "-"}</td>
                                            <td>{item.payment_date || "-"}</td>
                                            <td>{item.notes || "-"}</td>
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
                                    {editing ? "Edit Payment" : "Add Payment"}
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
                                    <label className="form-label">Invoice</label>
                                    <select
                                        className="form-select"
                                        name="invoice_id"
                                        value={form.invoice_id}
                                        onChange={handleChange}
                                        required
                                    >
                                        <option value="">Select Invoice</option>
                                        {invoices.map((inv) => (
                                            <option key={inv.id} value={inv.id}>
                                                {inv.invoice_number || `Invoice ${inv.id}`}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Amount</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        name="amount"
                                        value={form.amount}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Payment Method</label>
                                    <select
                                        className="form-select"
                                        name="payment_method"
                                        value={form.payment_method}
                                        onChange={handleChange}
                                        required
                                    >
                                        <option value="">Select Method</option>
                                        <option value="cash">Cash</option>
                                        <option value="card">Card</option>
                                        <option value="upi">UPI</option>
                                        <option value="net_banking">Net Banking</option>
                                        <option value="insurance">Insurance</option>
                                    </select>
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Payment Date</label>
                                    <input
                                        type="date"
                                        className="form-input"
                                        name="payment_date"
                                        value={form.payment_date}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-row">
                                    <label className="form-label">Notes</label>
                                    <textarea
                                        className="form-textarea"
                                        name="notes"
                                        value={form.notes}
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

export default AdminPayments;
