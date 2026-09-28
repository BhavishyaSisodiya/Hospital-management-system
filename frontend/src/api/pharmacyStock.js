import api from "./axios";
export const getPharmacyStock = async () => {
    const response = await api.get("/pharmacy-stock/");
    return response.data;
};
export const getPharmacyStockRecord = async (pharmacyId, batchId) => {
    const response = await api.get(`/pharmacy-stock/${pharmacyId}/${batchId}`);
    return response.data;
};
export const createPharmacyStock = async (stockData) => {
    const response = await api.post("/pharmacy-stock/", stockData);
    return response.data;
};
export const updatePharmacyStock = async (pharmacyId, batchId, stockData) => {
    const response = await api.patch(`/pharmacy-stock/${pharmacyId}/${batchId}`, stockData);
    return response.data;
};
export const deletePharmacyStock = async (pharmacyId, batchId) => {
    await api.delete(`/pharmacy-stock/${pharmacyId}/${batchId}`);
};
