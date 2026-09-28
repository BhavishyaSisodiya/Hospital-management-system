import api from "./axios";

export const getMedicines = async () => {
    const response = await api.get("/medicines/");
    return response.data;
};

export const getMedicine = async (medicineId) => {
    const response = await api.get(`/medicines/${medicineId}`);
    return response.data;
};

export const createMedicine = async (medicineData) => {
    const response = await api.post("/medicines/", medicineData);
    return response.data;
};

export const updateMedicine = async (medicineId, medicineData) => {
    const response = await api.put(`/medicines/${medicineId}`, medicineData);
    return response.data;
};

export const deleteMedicine = async (medicineId) => {
    await api.delete(`/medicines/${medicineId}`);
};
