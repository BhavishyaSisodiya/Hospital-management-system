import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getMyDoctorAppointments,
    updateAppointment,
} from "../../api/appointments";

function DoctorAppointments() {

    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {

        const loadAppointments = async () => {

            try {

                setLoading(true);
                setError("");

                const data = await getMyDoctorAppointments();

                setAppointments(data);

            } catch (error) {

                console.error(error);

                setError(
                    error.response?.data?.detail ||
                    "Unable to load your appointments."
                );

            } finally {

                setLoading(false);

            }
        };

        loadAppointments();

    }, []);
    const handleStatusUpdate = async (appointmentId, status) => {
    try {
        setError("");

        await updateAppointment(
            appointmentId,
            { status }
        );

        setAppointments((previous) =>
            previous.map((appointment) =>
                appointment.id === appointmentId
                    ? {
                          ...appointment,
                          status,
                      }
                    : appointment
            )
        );
    } catch (error) {
        console.error(error);

        setError(
            error.response?.data?.detail ||
            "Unable to update appointment."
        );
    }
};


    return (
        <MainLayout>

            <div className="appointments-page">

                <div className="appointments-header">

                    <h1>My Appointments</h1>

                    <p>
                        View and manage your appointments with patients.
                    </p>

                </div>


                {loading && (
                    <div className="empty-state">
                        <p>Loading appointments...</p>
                    </div>
                )}


                {!loading && error && (
                    <div className="empty-state">
                        <h2>Unable to Load Appointments</h2>
                        <p>{error}</p>
                    </div>
                )}


                {!loading && !error && appointments.length === 0 && (
                    <div className="empty-state">
                        <h2>No Appointments</h2>
                        <p>
                            There are currently no appointments.
                        </p>
                    </div>
                )}


                {!loading && !error && appointments.length > 0 && (

                    <div className="appointments-table-container">

                        <table className="appointments-table">

                            <thead>

                                <tr>
                                    <th>ID</th>
                                    <th>Patient ID</th>
                                    <th>Doctor ID</th>
                                    <th>Date</th>
                                    <th>Time</th>
                                    <th>Reason</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>

                            </thead>


                            <tbody>

                                {appointments.map((appointment) => (

                                    <tr key={appointment.id}>

                                        <td>
                                            {appointment.id}
                                        </td>

                                        <td>
                                            {appointment.patient_id}
                                        </td>

                                        <td>
                                            {appointment.doctor_id}
                                        </td>

                                        <td>
                                            {appointment.appointment_date}
                                        </td>

                                        <td>
                                            {appointment.appointment_time}
                                        </td>

                                        <td>
                                            {appointment.reason || "-"}
                                        </td>

                                        <td>
                                            <span
                                                className={`status-badge status-${appointment.status}`}
                                            >
                                                {appointment.status}
                                            </span>
                                        </td>
                                        <td>
                                            {appointment.status === "scheduled" && (
                                                <>
                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            handleStatusUpdate(
                                                                appointment.id,
                                                                "completed"
                                                            )
                                                        }
                                                    >
                                                        Complete
                                                    </button>

                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            handleStatusUpdate(
                                                                appointment.id,
                                                                "no_show"
                                                            )
                                                        }
                                                    >
                                                        No Show
                                                    </button>

                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            handleStatusUpdate(
                                                                appointment.id,
                                                                "cancelled"
                                                            )
                                                        }
                                                    >
                                                        Cancel
                                                    </button>
                                                </>
                                            )}
                                        </td>

                                    </tr>

                                ))}

                            </tbody>

                        </table>

                    </div>

                )}

            </div>

        </MainLayout>
    );
}

export default DoctorAppointments;