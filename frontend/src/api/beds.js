import api from "./axios";
export const getBeds = async () => {
    const response = await api.get("/beds/");
    return response.data;
};
export const getBed = async (bedId) => {
    const response = await api.get(`/beds/${bedId}`);
    return response.data;
};
export const getBedsByRoom = async (roomId) => {
    const response = await api.get(`/beds/room/${roomId}`);
    return response.data;
};
export const getAvailableBeds = async (roomId) => {
    const response = await api.get(`/beds/room/${roomId}/available`);
    return response.data;
};
export const createBed = async (bedData) => {
    const response = await api.post("/beds/", bedData);
    return response.data;
};
export const updateBed = async (bedId, bedData) => {
    const response = await api.patch(`/beds/${bedId}`, bedData);
    return response.data;
};
export const deleteBed = async (bedId) => {
    await api.delete(`/beds/${bedId}`);
};
