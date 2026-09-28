import api from "./axios";

export const getPatientLabResults = async (patientId) => {
    const response = await api.get(
        `/lab-results/patient/${patientId}`
    );
    return response.data;
};

export const getLabResults = async () => {
    const response = await api.get("/lab-results/");
    return response.data;
};

export const getLabResult = async (labResultId) => {
    const response = await api.get(`/lab-results/${labResultId}`);
    return response.data;
};

export const createLabResult = async (labResultData) => {
    const response = await api.post("/lab-results/", labResultData);
    return response.data;
};

export const updateLabResult = async (labResultId, labResultData) => {
    const response = await api.patch(`/lab-results/${labResultId}`, labResultData);
    return response.data;
};

export const deleteLabResult = async (labResultId) => {
    await api.delete(`/lab-results/${labResultId}`);
};
