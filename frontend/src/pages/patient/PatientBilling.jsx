import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getMyInvoices,
    getMyInvoiceItems,
    getMyPayments,
} from "../../api/billing";

function PatientBilling() {
    const [invoices, setInvoices] = useState([]);
    const [invoiceItems, setInvoiceItems] = useState({});
    const [payments, setPayments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");
    const [sortDir, setSortDir] = useState("desc");

    useEffect(() => {
        const fetchBilling = async () => {
            try {
                setLoading(true);
                setError("");

                const [invoiceData, paymentData] =
                    await Promise.all([
                        getMyInvoices(),
                        getMyPayments(),
                    ]);

                setInvoices(invoiceData);
                setPayments(paymentData);

                const itemsByInvoice = {};

                await Promise.all(
                    invoiceData.map(async (invoice) => {
                        const items = await getMyInvoiceItems(
                            invoice.id
                        );

                        itemsByInvoice[invoice.id] = items;
                    })
                );

                setInvoiceItems(itemsByInvoice);
            } catch (err) {
                console.error(
                    "Failed to fetch billing information:",
                    err
                );

                setError(
                    err.response?.data?.detail ||
                    "Failed to load billing information."
                );
            } finally {
                setLoading(false);
            }
        };

        fetchBilling();
    }, []);

    const calculateTotal = (invoiceId) => {
        const items = invoiceItems[invoiceId] || [];

        return items.reduce(
            (total, item) =>
                total + Number(item.amount || 0),
            0
        );
    };

    const calculatePaidAmount = (invoiceId) => {
        return payments
            .filter(
                (payment) =>
                    payment.invoice_id === invoiceId &&
                    payment.status === "completed"
            )
            .reduce(
                (total, payment) =>
                    total + Number(payment.amount || 0),
                0
            );
    };

    const calculateOutstanding = (invoiceId) => {
        const total = calculateTotal(invoiceId);
        const paid = calculatePaidAmount(invoiceId);

        return Math.max(total - paid, 0);
    };

    const visibleInvoices = invoices
        .filter(
            (invoice) =>
                statusFilter === "all" ||
                invoice.status === statusFilter
        )
        .sort((a, b) => {
            const da = new Date(a.invoice_date).getTime();
            const db = new Date(b.invoice_date).getTime();

            return sortDir === "desc" ? db - da : da - db;
        });

    const toggleSort = () =>
        setSortDir((dir) => (dir === "desc" ? "asc" : "desc"));

    if (loading) {
        return (
            <MainLayout>
                <h1>Billing</h1>
                <p>Loading billing information...</p>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <h1>Billing</h1>
                <p>{error}</p>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <h1>Billing</h1>

            <div className="filter-bar">
                <label>
                    Status:
                    <select
                        value={statusFilter}
                        onChange={(e) =>
                            setStatusFilter(e.target.value)
                        }
                    >
                        <option value="all">
                            All bills
                        </option>
                        <option value="paid">Paid</option>
                        <option value="unpaid">Unpaid</option>
                        <option value="partially_paid">
                            Partially Paid
                        </option>
                        <option value="cancelled">
                            Cancelled
                        </option>
                    </select>
                </label>

                <button
                    type="button"
                    onClick={toggleSort}
                    title="Toggle sort order"
                >
                    Sort by date:{" "}
                    {sortDir === "desc"
                        ? "Newest first"
                        : "Oldest first"}
                </button>

                <span className="count-note">
                    Showing {visibleInvoices.length} of{" "}
                    {invoices.length} bills
                </span>
            </div>

            {visibleInvoices.length === 0 ? (
                <p>
                    No{" "}
                    {statusFilter === "all"
                        ? ""
                        : statusFilter + " "}
                    invoices found.
                </p>
            ) : (
                visibleInvoices.map((invoice) => {
                    const items =
                        invoiceItems[invoice.id] || [];

                    const total = calculateTotal(invoice.id);
                    const paid = calculatePaidAmount(invoice.id);
                    const outstanding =
                        calculateOutstanding(invoice.id);

                    return (
                        <div
                            key={invoice.id}
                            className={`record-card ${
                                invoice.status === "paid"
                                    ? "record-card--success"
                                    : invoice.status === "unpaid"
                                    ? "record-card--danger"
                                    : "record-card--warn"
                            }`}
                        >
                            <div className="record-card-header">
                                <h2>Invoice #{invoice.id}</h2>
                                <span className={`status-badge status-${invoice.status}`}>
                                    {invoice.status.replace("_", " ")}
                                </span>
                            </div>

                            <div className="kv-grid">
                                <div className="kv-item">
                                    <strong>Invoice Date</strong>
                                    <span className="value">
                                        {new Date(
                                            invoice.invoice_date
                                        ).toLocaleDateString()}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Issued At</strong>
                                    <span className="value">
                                        {new Date(
                                            invoice.invoice_date
                                        ).toLocaleTimeString([], {
                                            hour: "2-digit",
                                            minute: "2-digit",
                                        })}
                                    </span>
                                </div>
                            </div>

                            <h3 className="kv-section-title">
                                Invoice Items
                            </h3>

                            {items.length === 0 ? (
                                <p className="muted">
                                    No items found for this
                                    invoice.
                                </p>
                            ) : (
                                <div className="table-wrapper table-wrapper--plain">
                                    <div className="table-container">
                                        <table className="appointments-table">
                                            <thead>
                                                <tr>
                                                    <th>
                                                        Description
                                                    </th>

                                                    <th className="num">
                                                        Qty
                                                    </th>

                                                    <th className="num">
                                                        Unit Price
                                                    </th>

                                                    <th className="num">
                                                        Amount
                                                    </th>
                                                </tr>
                                            </thead>

                                            <tbody>
                                                {items.map((item) => (
                                                    <tr key={item.id}>
                                                        <td>
                                                            {
                                                                item.description
                                                            }
                                                        </td>

                                                        <td className="num">
                                                            {
                                                                item.quantity
                                                            }
                                                        </td>

                                                        <td className="num">
                                                            ₹
                                                            {Number(
                                                                item.unit_price
                                                            ).toFixed(2)}
                                                        </td>

                                                        <td className="num">
                                                            ₹
                                                            {Number(
                                                                item.amount
                                                            ).toFixed(2)}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}

                            <div className="bill-totals">
                                <div className="bill-total">
                                    <span>Total Amount</span>
                                    <strong>₹{total.toFixed(2)}</strong>
                                </div>

                                <div className="bill-total bill-total--paid">
                                    <span>Paid Amount</span>
                                    <strong>₹{paid.toFixed(2)}</strong>
                                </div>

                                <div className={`bill-total ${
                                    outstanding > 0
                                        ? "bill-total--due"
                                        : "bill-total--paid"
                                }`}>
                                    <span>Outstanding</span>
                                    <strong>₹{outstanding.toFixed(2)}</strong>
                                </div>
                            </div>
                        </div>
                    );
                })
            )}
        </MainLayout>
    );
}

export default PatientBilling;