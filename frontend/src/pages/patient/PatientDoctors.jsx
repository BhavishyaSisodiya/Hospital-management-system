
import { useEffect, useState } from "react";

import MainLayout from "../../layouts/MainLayout";

import { getAvailableDoctors } from "../../api/doctors";

import { useNavigate } from "react-router-dom";

function PatientDoctors() {
    const [doctors, setDoctors] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");

    const navigate = useNavigate();

    useEffect(() => {
        const loadDoctors = async () => {
            try {
                const data = await getAvailableDoctors();

                setDoctors(data);
            } catch (error) {
                console.error(error);

                if (error.response) {
                    setError(
                        error.response.data?.detail ||
                        "Unable to load doctors."
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

        loadDoctors();
    }, []);

    if (loading) {
        return (
            <MainLayout>
                <h1>Doctors</h1>
                <p>Loading doctors...</p>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <h1>Doctors</h1>
                <p className="error-message">
                    {error}
                </p>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="doctors-page">

                <div className="doctors-header">
                    <h1>Our Doctors</h1>

                    <p>
                        View our available doctors and
                        their specializations.
                    </p>
                </div>

                {doctors.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Doctors Available</h2>

                        <p>
                            There are currently no active
                            doctors available.
                        </p>
                    </div>
                ) : (
                    <div className="doctors-grid">

                        {doctors.map((doctor) => (
                            <div
                                className="doctor-card"
                                key={doctor.id}
                            >

                                <div className="doctor-icon">
                                    👨‍⚕️
                                </div>

                                <div className="doctor-info">

                                    <h2>
                                        {doctor.name}
                                    </h2>

                                    <p className="doctor-specialization">
                                        {doctor.specialization}
                                    </p>

                                    <p className="doctor-experience">
                                        {doctor.experience_years !== null
                                            ? `${doctor.experience_years} years of experience`
                                            : "Experience not provided"}
                                    </p>

                                </div>

                                <button
                                    className="view-schedule-btn"
                                    onClick={() =>
                                        navigate(
                                            `/patient/doctors/${doctor.id}/schedule`
                                        )
                                    }
                                >
                                    View Schedule
                                </button>

                                <button
                                    className="book-appointment-btn"
                                    onClick={() =>
                                        navigate(
                                            `/patient/book-appointment/${doctor.id}`
                                        )
                                    }
                                >
                                    Book Appointment
                                </button>

                            </div>
                        ))}

                    </div>
                )}

            </div>
        </MainLayout>
    );
}

export default PatientDoctors;


// ### What changed

// Your original:

//
// <div className="doctors-header">
//     ...
//     <button>
//         View Schedule
//     </button>
// </div>
// 

// was wrong because there is **no `doctor` variable** in `doctors-header`.

// Now it is inside:

// ```jsx
// {doctors.map((doctor) => (
//     <div className="doctor-card">
// ```

// so this works:

// ```jsx
// navigate(`/patient/doctors/${doctor.id}/schedule`)
// ```

// Each doctor will now have:

// **Dr. Name**
// Specialization
// Experience
// **View Schedule**
// **Book Appointment**

// ### Next step

// Now create the **`PatientDoctorSchedule.jsx`** page. It will:

// 1. Get `doctorId` from the URL.
// 2. Call `/doctor-schedules/doctor/{doctorId}`.
// 3. Display Monday–Sunday schedule.
// 4. Later connect the selected date/time to your existing `BookAppointment.jsx`.

// Also make sure this route exists in your main router:

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

// **Next: `PatientDoctorSchedule.jsx`.**
