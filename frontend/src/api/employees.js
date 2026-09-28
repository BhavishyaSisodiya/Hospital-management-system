import api from "./axios";
export const getEmployees = async () => {
    const response = await api.get("/employees/");
    return response.data;
};
export const getEmployee = async (employeeId) => {
    const response = await api.get(`/employees/${employeeId}`);
    return response.data;
};
export const getEmployeesByDepartment = async (departmentId) => {
    const response = await api.get(`/employees/department/${departmentId}`);
    return response.data;
};
export const createEmployee = async (employeeData) => {
    const response = await api.post("/employees/", employeeData);
    return response.data;
};
export const updateEmployee = async (employeeId, employeeData) => {
    const response = await api.patch(`/employees/${employeeId}`, employeeData);
    return response.data;
};
export const deleteEmployee = async (employeeId) => {
    await api.delete(`/employees/${employeeId}`);
};
