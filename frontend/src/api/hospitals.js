import api from "./axios";
export const getHospitals = async () => {
    const response = await api.get("/hospitals/");
    return response.data;
};
export const getHospital = async (hospitalId) => {
    const response = await api.get(`/hospitals/${hospitalId}`);
    return response.data;
};
export const createHospital = async (hospitalData) => {
    const response = await api.post("/hospitals/", hospitalData);
    return response.data;
};
export const updateHospital = async (hospitalId, hospitalData) => {
    const response = await api.patch(`/hospitals/${hospitalId}`, hospitalData);
    return response.data;
};
export const deleteHospital = async (hospitalId) => {
    await api.delete(`/hospitals/${hospitalId}`);
};
