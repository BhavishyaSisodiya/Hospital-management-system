import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";

import { getDoctorSchedulesByDoctor } from "../../api/doctorSchedules";

function PatientDoctorSchedule() {
    const { doctorId } = useParams();
    const navigate = useNavigate();

    const [schedules, setSchedules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadSchedule = async () => {
            try {
                setLoading(true);
                setError("");

                const data = await getDoctorSchedulesByDoctor(doctorId);

                setSchedules(data);
            } catch (error) {
                console.error(error);

                if (error.response) {
                    setError(
                        error.response.data?.detail ||
                        "Unable to load doctor schedule."
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

        loadSchedule();
    }, [doctorId]);

    const formatDay = (day) => {
        return (
            day.charAt(0).toUpperCase() +
            day.slice(1)
        );
    };

    const formatTime = (time) => {
        if (!time) {
            return "";
        }

        const [hours, minutes] = time.split(":");

        const date = new Date();

        date.setHours(
            Number(hours),
            Number(minutes),
            0,
            0
        );

        return date.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="page-container">
                    <h1>Doctor Schedule</h1>
                    <p>Loading schedule...</p>
                </div>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <div className="page-container">
                    <h1>Doctor Schedule</h1>

                    <p className="error-message">
                        {error}
                    </p>

                    <button
                        onClick={() =>
                            navigate("/patient/doctors")
                        }
                    >
                        Back to Doctors
                    </button>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="page-container">

                <h1>Doctor Schedule</h1>

                <p>
                    View the doctor's weekly availability.
                </p>

                {schedules.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Schedule Available</h2>

                        <p>
                            This doctor does not have a
                            schedule assigned yet.
                        </p>
                    </div>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>Day</th>
                                <th>Start Time</th>
                                <th>End Time</th>
                            </tr>
                        </thead>

                        <tbody>
                            {schedules.map((schedule) => (
                                <tr key={schedule.id}>
                                    <td>
                                        {formatDay(
                                            schedule.day_of_week
                                        )}
                                    </td>

                                    <td>
                                        {formatTime(
                                            schedule.start_time
                                        )}
                                    </td>

                                    <td>
                                        {formatTime(
                                            schedule.end_time
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}

                <button
                    onClick={() =>
                        navigate("/patient/doctors")
                    }
                >
                    Back to Doctors
                </button>

            </div>
        </MainLayout>
    );
}

export default PatientDoctorSchedule;


// ### One API function is also required

// Open:

// `src/api/doctorSchedules.js`

// Add this at the bottom:

// ```javascript
// // Get schedule of a specific doctor
// export const getDoctorSchedulesByDoctor = async (doctorId) => {
//     const response = await api.get(
//         `/doctor-schedules/doctor/${doctorId}`
//     );

//     return response.data;
// };
// ```

// ### Then verify the route

// Your main router should have:

// ```jsx
// import PatientDoctorSchedule from "./pages/patient/PatientDoctorSchedule";
// ```

// and:

// ```jsx
// <Route
//     path="/patient/doctors/:doctorId/schedule"
//     element={
//         <ProtectedRoute
//             allowedAccountTypes={["patient"]}
//         >
//             <PatientDoctorSchedule />
//         </ProtectedRoute>
//     }
// />
// ```

// ### Test the complete flow

// Login as **patient** → **Doctors** → choose any doctor → **View Schedule**.

// You should see something like:

// | Day       | Start Time | End Time |
// | --------- | ---------- | -------- |
// | Monday    | 09:00 AM   | 01:00 PM |
// | Wednesday | 10:00 AM   | 02:00 PM |
// | Friday    | 09:00 AM   | 01:00 PM |

// **Don't modify `BookAppointment.jsx` yet.**

// Once this page displays correctly, the next step is to connect the schedule with **date/time selection in your existing booking page**.
