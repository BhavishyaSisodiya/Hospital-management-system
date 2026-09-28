import api from "./axios";

export const getMyPatientProfile = async () => {
    const response = await api.get("/patients/me");
    return response.data;
};

export const updateMyPatientProfile = async (patientId, patientData) => {
    const response = await api.put(
        `/patients/${patientId}`,
        patientData
    );

    return response.data;
};

export const getMyDoctorPatients = async () => {
    const response = await api.get("/patients/doctor/me");
    return response.data;
};

export const getPatient = async (patientId) => {
    const response = await api.get(`/patients/${patientId}`);
    return response.data;
};

export const getPatients = async () => {
    const response = await api.get("/patients/");
    return response.data;
};

export const createPatient = async (patientData) => {
    const response = await api.post("/patients/", patientData);
    return response.data;
};

export const updatePatient = async (patientId, patientData) => {
    const response = await api.put(`/patients/${patientId}`, patientData);
    return response.data;
};

export const deletePatient = async (patientId) => {
    await api.delete(`/patients/${patientId}`);
};