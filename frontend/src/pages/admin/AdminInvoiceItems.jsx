import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getInvoiceItems,
    getInvoiceItem,
    createInvoiceItem,
    updateInvoiceItem,
    deleteInvoiceItem,
} from "../../api/invoiceItems";
import { getInvoices } from "../../api/invoices";

function AdminInvoiceItems() {

    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [invoices, setInvoices] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        invoice_id: "",
        description: "",
        quantity: "",
        unit_price: "",
    });
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState("");

    const loadData = async () => {
        try {
            setLoading(true);
            setError("");
            const [itemsData, invoiceData] = await Promise.all([
                getInvoiceItems(),
                getInvoices(),
            ]);
            setItems(itemsData);
            setInvoices(invoiceData);
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Unable to load invoice items."
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
            description: "",
            quantity: "",
            unit_price: "",
        });
        setFormError("");
        setShowModal(true);
    };

    const openEdit = (item) => {
        setEditing(item);
        setForm({
            invoice_id: item.invoice_id || "",
            description: item.description || "",
            quantity: item.quantity || "",
            unit_price: item.unit_price || "",
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
            quantity: form.quantity ? Number(form.quantity) : null,
            unit_price: form.unit_price ? Number(form.unit_price) : null,
        };

        try {
            if (editing) {
                await updateInvoiceItem(editing.id, payload);
            } else {
                await createInvoiceItem(payload);
            }
            closeModal();
            await loadData();
        } catch (err) {
            console.error(err);
            setFormError(
                err.response?.data?.detail ||
                "Failed to save invoice item."
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Delete this invoice item?")) return;

        try {
            await deleteInvoiceItem(id);
            await loadData();
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                "Failed to delete invoice item."
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
                    <h2 className="section-title">Invoice Items</h2>
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
                    <h2 className="section-title">Invoice Items</h2>
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
                    <h1>Invoice Items</h1>
                    <p>Manage invoice line items</p>
                    <button type="button" className="btn-add" onClick={openAdd}>
                        Add Invoice Item
                    </button>
                </div>


                {items.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Invoice Items</h2>
                        <p>No invoice items found.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Invoice</th>
                                        <th>Description</th>
                                        <th>Quantity</th>
                                        <th>Unit Price</th>
                                        <th>Total</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items.map((item) => (
                                        <tr key={item.id}>
                                            <td>{getInvoiceNumber(item.invoice_id)}</td>
                                            <td>{item.description || "-"}</td>
                                            <td>{item.quantity}</td>
                                            <td>{item.unit_price}</td>
                                            <td>
                                                {item.total ||
                                                    (
                                                        Number(item.quantity) *
                                                        Number(item.unit_price)
                                                    ).toFixed(2)}
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
                                    {editing ? "Edit Invoice Item" : "Add Invoice Item"}
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
                                    <label className="form-label">Description</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="description"
                                        value={form.description}
                                        onChange={handleChange}
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

                                <div className="form-row">
                                    <label className="form-label">Unit Price</label>
                                    <input
                                        type="number"
                                        className="form-input"
                                        name="unit_price"
                                        value={form.unit_price}
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

export default AdminInvoiceItems;
