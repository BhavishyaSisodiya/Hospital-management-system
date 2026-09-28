import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { getMyPatientProfile } from "../../api/patients";
import { getPatientAppointments } from "../../api/appointments";

function PatientAppointments() {

    const [appointments, setAppointments] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {

        const loadAppointments = async () => {

            try {

                // First get the logged-in patient's profile
                const patient =
                    await getMyPatientProfile();

                // Then get that patient's appointments
                const data =
                    await getPatientAppointments(
                        patient.id
                    );

                setAppointments(data);

            } catch (error) {

                console.error(error);

                if (error.response) {

                    setError(
                        error.response.data?.detail ||
                        "Unable to load appointments."
                    );

                } else {

                    setError(
                        "Unable to connect to the server."
                    );

                }

            } finally {

                setLoading(false);

            }
        };

        loadAppointments();

    }, []);


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {

        return (
            <MainLayout>

                <h1>My Appointments</h1>

                <p>Loading appointments...</p>

            </MainLayout>
        );

    }


    // ============================================================
    // ERROR
    // ============================================================

    if (error) {

        return (
            <MainLayout>

                <h1>My Appointments</h1>

                <p className="error-message">
                    {error}
                </p>

            </MainLayout>
        );

    }


    // ============================================================
    // PAGE
    // ============================================================

    return (

        <MainLayout>

            <div className="appointments-page">

                <div className="appointments-header">

                    <div>

                        <h1>My Appointments</h1>

                        <p>
                            View your upcoming and previous
                            appointments.
                        </p>

                    </div>

                </div>


                {appointments.length === 0 ? (

                    <div className="empty-state">

                        <h2>No Appointments</h2>

                        <p>
                            You currently don't have any
                            appointments.
                        </p>

                    </div>

                ) : (

                    <div className="appointments-table-container">

                        <table className="appointments-table">

                            <thead>

                                <tr>

                                    <th>ID</th>

                                    <th>Doctor ID</th>

                                    <th>Date</th>

                                    <th>Time</th>

                                    <th>Reason</th>

                                    <th>Status</th>

                                </tr>

                            </thead>

                            <tbody>

                                {appointments.map(
                                    (appointment) => (

                                        <tr
                                            key={
                                                appointment.id
                                            }
                                        >

                                            <td>
                                                {
                                                    appointment.id
                                                }
                                            </td>

                                            <td>
                                                {
                                                    appointment.doctor_id
                                                }
                                            </td>

                                            <td>
                                                {
                                                    appointment.appointment_date
                                                }
                                            </td>

                                            <td>
                                                {
                                                    appointment.appointment_time
                                                }
                                            </td>

                                            <td>
                                                {
                                                    appointment.reason ||
                                                    "Not provided"
                                                }
                                            </td>

                                            <td>

                                                <span
                                                    className={`status-badge status-${appointment.status}`}
                                                >
                                                    {
                                                        appointment.status
                                                    }
                                                </span>

                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    </div>

                )}

            </div>

        </MainLayout>
    );
}

export default PatientAppointments;