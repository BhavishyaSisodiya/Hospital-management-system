import api from "./axios";
export const getMedicineBatches = async () => {
    const response = await api.get("/medicine-batches/");
    return response.data;
};
export const getMedicineBatch = async (batchId) => {
    const response = await api.get(`/medicine-batches/${batchId}`);
    return response.data;
};
export const createMedicineBatch = async (batchData) => {
    const response = await api.post("/medicine-batches/", batchData);
    return response.data;
};
export const updateMedicineBatch = async (batchId, batchData) => {
    const response = await api.patch(`/medicine-batches/${batchId}`, batchData);
    return response.data;
};
export const deleteMedicineBatch = async (batchId) => {
    await api.delete(`/medicine-batches/${batchId}`);
};
