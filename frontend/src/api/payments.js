import api from "./axios";
export const getPayments = async () => {
    const response = await api.get("/payments/");
    return response.data;
};
export const getPayment = async (paymentId) => {
    const response = await api.get(`/payments/${paymentId}`);
    return response.data;
};
export const createPayment = async (paymentData) => {
    const response = await api.post("/payments/", paymentData);
    return response.data;
};
export const updatePayment = async (paymentId, paymentData) => {
    const response = await api.patch(`/payments/${paymentId}`, paymentData);
    return response.data;
};
export const deletePayment = async (paymentId) => {
    await api.delete(`/payments/${paymentId}`);
};
