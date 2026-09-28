import api from "./axios";
export const getNurseAssignments = async () => {
    const response = await api.get("/nurse-assignments/");
    return response.data;
};
export const getNurseAssignment = async (assignmentId) => {
    const response = await api.get(`/nurse-assignments/${assignmentId}`);
    return response.data;
};
export const getAdmissionAssignments = async (admissionId) => {
    const response = await api.get(`/nurse-assignments/admission/${admissionId}`);
    return response.data;
};
export const getNurseAssignmentsByNurse = async (nurseId) => {
    const response = await api.get(`/nurse-assignments/nurse/${nurseId}`);
    return response.data;
};
export const createNurseAssignment = async (assignmentData) => {
    const response = await api.post("/nurse-assignments/", assignmentData);
    return response.data;
};
export const updateNurseAssignment = async (assignmentId, assignmentData) => {
    const response = await api.patch(`/nurse-assignments/${assignmentId}`, assignmentData);
    return response.data;
};
export const deleteNurseAssignment = async (assignmentId) => {
    await api.delete(`/nurse-assignments/${assignmentId}`);
};
