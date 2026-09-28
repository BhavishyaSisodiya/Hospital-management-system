import api from "./axios";
export const getInvoices = async () => {
    const response = await api.get("/invoices/");
    return response.data;
};
export const getInvoice = async (invoiceId) => {
    const response = await api.get(`/invoices/${invoiceId}`);
    return response.data;
};
export const getMyInvoices = async () => {
    const response = await api.get("/invoices/my");
    return response.data;
};
export const createInvoice = async (invoiceData) => {
    const response = await api.post("/invoices/", invoiceData);
    return response.data;
};
export const updateInvoice = async (invoiceId, invoiceData) => {
    const response = await api.patch(`/invoices/${invoiceId}`, invoiceData);
    return response.data;
};
export const deleteInvoice = async (invoiceId) => {
    await api.delete(`/invoices/${invoiceId}`);
};
