import api from "./axios";

export const getAppointments = async () => {
    const response = await api.get("/appointments/");
    return response.data;
};

export const getPatientAppointments = async (patientId) => {
    const response = await api.get(
        `/appointments/patient/${patientId}`
    );

    return response.data;
};

export const createAppointment = async (appointmentData) => {
    const response = await api.post(
        "/appointments/",
        appointmentData
    );

    return response.data;
};

export const getAppointment = async (appointmentId) => {
    const response = await api.get(
        `/appointments/${appointmentId}`
    );

    return response.data;
};

export const updateAppointment = async (
    appointmentId,
    appointmentData
) => {
    const response = await api.put(
        `/appointments/${appointmentId}`,
        appointmentData
    );

    return response.data;
};

/* ============================================================
   DOCTOR - MY APPOINTMENTS
============================================================ */

export const getMyDoctorAppointments = async () => {
    const response = await api.get(
        "/appointments/doctor/me"
    );

    return response.data;
};

export const getDoctorBookedSlots = async (
    doctorId,
    appointmentDate
) => {
    const response = await api.get(
        `/appointments/doctor/${doctorId}/booked-slots`,
        {
            params: {
                appointment_date: appointmentDate,
            },
        }
    );

    return response.data;
};

export const deleteAppointment = async (appointmentId) => {
    await api.delete(`/appointments/${appointmentId}`);
};