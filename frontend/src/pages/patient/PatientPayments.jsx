import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { getMyPayments } from "../../api/billing";

function PatientPayments() {
    const [payments, setPayments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchPayments = async () => {
            try {
                setLoading(true);
                setError("");

                const data = await getMyPayments();

                setPayments(data);
            } catch (err) {
                console.error("Failed to fetch payments:", err);

                setError(
                    err.response?.data?.detail ||
                    "Failed to load payments."
                );
            } finally {
                setLoading(false);
            }
        };

        fetchPayments();
    }, []);

    if (loading) {
        return (
            <MainLayout>
                <h1>Payments</h1>
                <p>Loading payments...</p>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <h1>Payments</h1>
                <p>{error}</p>
            </MainLayout>
        );
    }

    const paidPayments = payments
        .filter((payment) => payment.status === "completed")
        .sort(
            (a, b) =>
                new Date(b.payment_date) - new Date(a.payment_date)
        );

    return (
        <MainLayout>
            <h1>Payments</h1>
            <p>
                <strong>Paid bills</strong> — payments received
                against your invoices ({paidPayments.length} of{" "}
                {payments.length}).
            </p>

            {paidPayments.length === 0 ? (
                <p>No paid bills found.</p>
            ) : (
                <div>
                    {paidPayments.map((payment) => (
                        <div
                            key={payment.id}
                            className="record-card record-card--success"
                        >
                            <div className="record-card-header">
                                <h2>
                                    Bill #{payment.invoice_id}
                                </h2>
                                <span className="status-badge status-completed">
                                    PAID
                                </span>
                            </div>

                            <div className="kv-grid">
                                <div className="kv-item">
                                    <strong>Paid Amount</strong>
                                    <span className="value">
                                        ₹
                                        {Number(
                                            payment.amount
                                        ).toFixed(2)}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Payment Date</strong>
                                    <span className="value">
                                        {new Date(
                                            payment.payment_date
                                        ).toLocaleDateString()}{" "}
                                        {new Date(
                                            payment.payment_date
                                        ).toLocaleTimeString([], {
                                            hour: "2-digit",
                                            minute: "2-digit",
                                        })}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Payment Method</strong>
                                    <span className="value">
                                        {payment.payment_method}
                                    </span>
                                </div>

                                <div className="kv-item">
                                    <strong>Transaction Ref</strong>
                                    <span className="value">
                                        {payment.transaction_reference ||
                                            "-"}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </MainLayout>
    );
}

export default PatientPayments;