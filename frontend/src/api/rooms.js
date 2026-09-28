import api from "./axios";
export const getRooms = async () => {
    const response = await api.get("/rooms/");
    return response.data;
};
export const getRoom = async (roomId) => {
    const response = await api.get(`/rooms/${roomId}`);
    return response.data;
};
export const getRoomsByHospital = async (hospitalId) => {
    const response = await api.get(`/rooms/hospital/${hospitalId}`);
    return response.data;
};
export const getRoomsByDepartment = async (departmentId) => {
    const response = await api.get(`/rooms/department/${departmentId}`);
    return response.data;
};
export const createRoom = async (roomData) => {
    const response = await api.post("/rooms/", roomData);
    return response.data;
};
export const updateRoom = async (roomId, roomData) => {
    const response = await api.patch(`/rooms/${roomId}`, roomData);
    return response.data;
};
export const deleteRoom = async (roomId) => {
    await api.delete(`/rooms/${roomId}`);
};
