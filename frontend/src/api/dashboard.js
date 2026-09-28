import api from "./axios";
export const getDashboardStats = async () => {
    const response = await api.get("/dashboard/stats");
    return response.data;
};
export const getPatientDashboardStats = async () => {
    const response = await api.get("/dashboard/patient-stats");
    return response.data;
};
