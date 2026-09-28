import api from "./axios";
export const getTestTypes = async () => {
    const response = await api.get("/test-types/");
    return response.data;
};
export const getTestType = async (testTypeId) => {
    const response = await api.get(`/test-types/${testTypeId}`);
    return response.data;
};
export const createTestType = async (testTypeData) => {
    const response = await api.post("/test-types/", testTypeData);
    return response.data;
};
export const updateTestType = async (testTypeId, testTypeData) => {
    const response = await api.patch(`/test-types/${testTypeId}`, testTypeData);
    return response.data;
};
export const deleteTestType = async (testTypeId) => {
    await api.delete(`/test-types/${testTypeId}`);
};
