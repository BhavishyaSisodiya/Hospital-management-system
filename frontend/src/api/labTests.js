import api from "./axios";
export const getLabTests = async () => {
    const response = await api.get("/lab-tests/");
    return response.data;
};
export const getLabTest = async (labTestId) => {
    const response = await api.get(`/lab-tests/${labTestId}`);
    return response.data;
};
export const createLabTest = async (labTestData) => {
    const response = await api.post("/lab-tests/", labTestData);
    return response.data;
};
export const updateLabTest = async (labTestId, labTestData) => {
    const response = await api.patch(`/lab-tests/${labTestId}`, labTestData);
    return response.data;
};
export const deleteLabTest = async (labTestId) => {
    await api.delete(`/lab-tests/${labTestId}`);
};
