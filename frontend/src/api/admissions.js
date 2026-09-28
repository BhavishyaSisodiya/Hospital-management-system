import api from "./axios";

export const getAdmissions = async () => {
    const response = await api.get("/admissions/");
    return response.data;
};

export const getPatientAdmissions = async (patientId) => {
    const response = await api.get(
        `/admissions/patient/${patientId}`
    );

    return response.data;
};

export const getAdmission = async (admissionId) => {
    const response = await api.get(
        `/admissions/${admissionId}`
    );

    return response.data;
};

export const createAdmission = async (admissionData) => {
    const response = await api.post(
        "/admissions/",
        admissionData
    );

    return response.data;
};

export const updateAdmission = async (
    admissionId,
    admissionData
) => {
    const response = await api.patch(
        `/admissions/${admissionId}`,
        admissionData
    );

    return response.data;
};

export const deleteAdmission = async (admissionId) => {
    await api.delete(`/admissions/${admissionId}`);
};

export const dischargeAdmission = async (admissionId) => {
    const response = await api.patch(
        `/admissions/${admissionId}/discharge`
    );

    return response.data;
};
