import api from "./axios";
export const getPharmacies = async () => {
    const response = await api.get("/pharmacies/");
    return response.data;
};
export const getPharmacy = async (pharmacyId) => {
    const response = await api.get(`/pharmacies/${pharmacyId}`);
    return response.data;
};
export const createPharmacy = async (pharmacyData) => {
    const response = await api.post("/pharmacies/", pharmacyData);
    return response.data;
};
export const updatePharmacy = async (pharmacyId, pharmacyData) => {
    const response = await api.patch(`/pharmacies/${pharmacyId}`, pharmacyData);
    return response.data;
};
export const deletePharmacy = async (pharmacyId) => {
    await api.delete(`/pharmacies/${pharmacyId}`);
};
