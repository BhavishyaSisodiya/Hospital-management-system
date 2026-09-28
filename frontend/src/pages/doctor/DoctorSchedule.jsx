import { useEffect, useState } from "react";

import MainLayout from "../../layouts/MainLayout";

import { getMyDoctorSchedule } from "../../api/doctorSchedules";

function DoctorSchedule() {
    const [schedules, setSchedules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchMySchedule = async () => {
            try {
                setLoading(true);
                setError("");

                const data = await getMyDoctorSchedule();

                setSchedules(data);
            } catch (error) {
                console.error(error);

                setError(
                    error.response?.data?.detail ||
                    "Unable to load your schedule."
                );
            } finally {
                setLoading(false);
            }
        };

        fetchMySchedule();
    }, []);

    return (
        <MainLayout>
            <div className="page-container">
                <h1>My Schedule</h1>

                <p>
                    View your weekly availability and working hours.
                </p>

                {loading && <p>Loading schedule...</p>}

                {error && (
                    <p className="error-message">
                        {error}
                    </p>
                )}

                {!loading && !error && schedules.length === 0 && (
                    <p>
                        No schedule has been assigned to you yet.
                    </p>
                )}

                {!loading && !error && schedules.length > 0 && (
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
                                        {schedule.day_of_week
                                            .charAt(0)
                                            .toUpperCase() +
                                            schedule.day_of_week.slice(1)}
                                    </td>

                                    <td>
                                        {schedule.start_time}
                                    </td>

                                    <td>
                                        {schedule.end_time}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </MainLayout>
    );
}

export default DoctorSchedule;