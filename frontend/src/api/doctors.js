import api from "./axios";

export const getDoctors = async () => {
    const response = await api.get("/doctors/");
    return response.data;
};

export const getDoctor = async (doctorId) => {
    const response = await api.get(`/doctors/${doctorId}`);
    return response.data;
};

export const getAvailableDoctors = async () => {
    const response = await api.get("/doctors/available");
    return response.data;
};

export const getDoctorsByDepartment = async (departmentId) => {
    const response = await api.get(`/doctors/department/${departmentId}`);
    return response.data;
};

export const createDoctor = async (doctorData) => {
    const response = await api.post("/doctors/", doctorData);
    return response.data;
};

export const updateDoctor = async (doctorId, doctorData) => {
    const response = await api.patch(`/doctors/${doctorId}`, doctorData);
    return response.data;
};

export const deleteDoctor = async (doctorId) => {
    await api.delete(`/doctors/${doctorId}`);
};