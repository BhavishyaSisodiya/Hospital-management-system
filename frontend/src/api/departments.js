import api from "./axios";
export const getDepartments = async () => {
    const response = await api.get("/departments/");
    return response.data;
};
export const getDepartment = async (departmentId) => {
    const response = await api.get(`/departments/${departmentId}`);
    return response.data;
};
export const getDepartmentsByHospital = async (hospitalId) => {
    const response = await api.get(`/departments/hospital/${hospitalId}`);
    return response.data;
};
export const createDepartment = async (departmentData) => {
    const response = await api.post("/departments/", departmentData);
    return response.data;
};
export const updateDepartment = async (departmentId, departmentData) => {
    const response = await api.patch(`/departments/${departmentId}`, departmentData);
    return response.data;
};
export const deleteDepartment = async (departmentId) => {
    await api.delete(`/departments/${departmentId}`);
};
