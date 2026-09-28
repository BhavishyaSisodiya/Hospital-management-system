import api from "./axios";

// Get all doctor schedules
export const getDoctorSchedules = async () => {
    const response = await api.get("/doctor-schedules/");
    return response.data;
};

// Get a single schedule
export const getDoctorSchedule = async (scheduleId) => {
    const response = await api.get(`/doctor-schedules/${scheduleId}`);
    return response.data;
};

// Create a doctor schedule
export const createDoctorSchedule = async (scheduleData) => {
    const response = await api.post(
        "/doctor-schedules/",
        scheduleData
    );
    return response.data;
};

// Update a doctor schedule
export const updateDoctorSchedule = async (
    scheduleId,
    scheduleData
) => {
    const response = await api.patch(
        `/doctor-schedules/${scheduleId}`,
        scheduleData
    );
    return response.data;
};

// Delete a doctor schedule
export const deleteDoctorSchedule = async (scheduleId) => {
    await api.delete(`/doctor-schedules/${scheduleId}`);
};

// Get schedules for a specific doctor
export const getDoctorSchedulesByDoctor = async (doctorId) => {
    const response = await api.get(
        `/doctor-schedules/doctor/${doctorId}`
    );

    return response.data;
};
export const getMyDoctorSchedule = async () => {
    const response = await api.get("/doctor-schedules/me");
    return response.data;
};