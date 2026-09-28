import api from "./axios";
export const getInvoiceItems = async () => {
    const response = await api.get("/invoice-items/");
    return response.data;
};
export const getInvoiceItem = async (itemId) => {
    const response = await api.get(`/invoice-items/${itemId}`);
    return response.data;
};
export const getMyInvoiceItems = async (invoiceId) => {
    const response = await api.get(`/invoice-items/my/${invoiceId}`);
    return response.data;
};
export const createInvoiceItem = async (itemData) => {
    const response = await api.post("/invoice-items/", itemData);
    return response.data;
};
export const updateInvoiceItem = async (itemId, itemData) => {
    const response = await api.patch(`/invoice-items/${itemId}`, itemData);
    return response.data;
};
export const deleteInvoiceItem = async (itemId) => {
    await api.delete(`/invoice-items/${itemId}`);
};
