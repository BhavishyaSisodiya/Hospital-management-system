import api from "./axios";

export const getVitals = async () => {
    const response = await api.get("/vitals/");
    return response.data;
};

export const createVitals = async (vitalData) => {
    const response = await api.post("/vitals/", vitalData);
    return response.data;
};

export const getPatientVitals = async (patientId) => {
    const response = await api.get(
        `/vitals/patient/${patientId}`
    );

    return response.data;
};

export const getVital = async (vitalId) => {
    const response = await api.get(
        `/vitals/${vitalId}`
    );

    return response.data;
};