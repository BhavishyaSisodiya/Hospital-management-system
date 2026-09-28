import api from "./axios";

export const getPatientMedicalRecords = async (patientId) => {
    const response = await api.get(
        `/medical-records/patient/${patientId}`
    );

    return response.data;
};

export const getMedicalRecord = async (recordId) => {
    const response = await api.get(
        `/medical-records/${recordId}`
    );

    return response.data;
};

export const getMyDoctorMedicalRecords = async () => {
    const response = await api.get("/medical-records/doctor/me");
    return response.data;
};

export const createMedicalRecord = async (recordData) => {
    const response = await api.post(
        "/medical-records/",
        recordData
    );

    return response.data;
};

export const updateMedicalRecord = async (recordId, recordData) => {
    const response = await api.patch(
        `/medical-records/${recordId}`,
        recordData
    );

    return response.data;
};