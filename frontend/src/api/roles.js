import api from "./axios";
export const getRoles = async () => {
    const response = await api.get("/roles/");
    return response.data;
};
export const getRole = async (roleId) => {
    const response = await api.get(`/roles/${roleId}`);
    return response.data;
};
export const createRole = async (roleData) => {
    const response = await api.post("/roles/", roleData);
    return response.data;
};
export const updateRole = async (roleId, roleData) => {
    const response = await api.patch(`/roles/${roleId}`, roleData);
    return response.data;
};
export const deleteRole = async (roleId) => {
    await api.delete(`/roles/${roleId}`);
};
