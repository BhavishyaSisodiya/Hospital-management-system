import api from "./axios";

export const getMyInvoices = async () => {
    const response = await api.get("/invoices/my");
    return response.data;
};

export const getMyInvoiceItems = async (invoiceId) => {
    const response = await api.get(
        `/invoice-items/my/${invoiceId}`
    );
    return response.data;
};

export const getMyPayments = async () => {
    const response = await api.get("/payments/");
    return response.data;
};

export const createBillingInvoice = async ({
    patient_id,
    items,
    payment,
}) => {
    const nowIso = new Date().toISOString();

    const invoice = await api.post("/invoices/", {
        patient_id,
        invoice_date: nowIso,
        status: "unpaid",
    });

    for (const item of items) {
        await api.post("/invoice-items/", {
            invoice_id: invoice.data.id,
            description: item.description,
            quantity: item.quantity,
            unit_price: item.unit_price,
        });
    }

    if (payment && Number(payment.amount) > 0) {
        await api.post("/payments/", {
            invoice_id: invoice.data.id,
            amount: payment.amount,
            payment_date: nowIso,
            payment_method: payment.method,
            status: "completed",
            transaction_reference:
                payment.reference || null,
        });
    }

    return invoice.data;
};