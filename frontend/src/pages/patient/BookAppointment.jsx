import { useEffect, useState } from "react";

import { useNavigate, useParams } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";

import {
    createAppointment,
    getDoctorBookedSlots,
} from "../../api/appointments";

import { getMyPatientProfile } from "../../api/patients";

import { getAvailableDoctors } from "../../api/doctors";

import { getDoctorSchedulesByDoctor } from "../../api/doctorSchedules";


function BookAppointment() {

    const { doctorId } = useParams();

    const navigate = useNavigate();

    const [bookedSlots, setBookedSlots] = useState([]);
    const [loadingBookedSlots, setLoadingBookedSlots] = useState(false);
    const [doctor, setDoctor] = useState(null);

    const [schedules, setSchedules] = useState([]);

    const [formData, setFormData] = useState({
        appointment_date: "",
        appointment_time: "",
        reason: "",
    });


    const [loading, setLoading] = useState(true);

    const [saving, setSaving] = useState(false);

    const [error, setError] = useState("");

    const [success, setSuccess] = useState("");

    const [createdAppointment, setCreatedAppointment] =
        useState(null);


    useEffect(() => {
        const fetchBookedSlots = async () => {
            if (!doctorId || !formData.appointment_date) {
                setBookedSlots([]);
                return;
            }

            try {
                setLoadingBookedSlots(true);

                const data = await getDoctorBookedSlots(
                    doctorId,
                    formData.appointment_date
                );

                setBookedSlots(data);
            } catch (error) {
                console.error("Failed to load booked slots:", error);
                setBookedSlots([]);
            } finally {
                setLoadingBookedSlots(false);
            }
        };

        fetchBookedSlots();
    }, [doctorId, formData.appointment_date]);

    // ============================================================
    // TODAY'S DATE
    // ============================================================

    const getToday = () => {

        const date = new Date();

        const year = date.getFullYear();

        const month = String(
            date.getMonth() + 1
        ).padStart(2, "0");

        const day = String(
            date.getDate()
        ).padStart(2, "0");

        return `${year}-${month}-${day}`;
    };

    const today = getToday();


    // ============================================================
    // LOAD DOCTOR AND SCHEDULE
    // ============================================================

    useEffect(() => {

        const loadDoctorAndSchedule = async () => {

            try {

                setLoading(true);

                setError("");


                // ------------------------------------------------
                // Load doctors
                // ------------------------------------------------

                const doctors =
                    await getAvailableDoctors();


                const selectedDoctor =
                    doctors.find(
                        (doctor) =>
                            doctor.id === Number(doctorId)
                    );


                if (!selectedDoctor) {

                    setError("Doctor not found.");

                    return;
                }


                setDoctor(selectedDoctor);


                // ------------------------------------------------
                // Load doctor's weekly schedule
                // ------------------------------------------------

                const doctorSchedules =
                    await getDoctorSchedulesByDoctor(
                        doctorId
                    );


                setSchedules(doctorSchedules);

            } catch (error) {

                console.error(error);


                if (error.response) {

                    setError(
                        error.response.data?.detail ||
                        "Unable to load doctor information."
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


        loadDoctorAndSchedule();

    }, [doctorId]);


    // ============================================================
    // HANDLE INPUT CHANGE
    // ============================================================

    const handleChange = (event) => {

        const { name, value } = event.target;


        setFormData((previousData) => ({
            ...previousData,
            [name]: value,
        }));


        setError("");


        // --------------------------------------------------------
        // When date changes, clear previously selected time
        // --------------------------------------------------------

        if (name === "appointment_date") {

            setFormData((previousData) => ({
                ...previousData,
                appointment_date: value,
                appointment_time: "",
            }));
        }
    };


    // ============================================================
    // GET DAY OF WEEK
    // ============================================================

    const getDayOfWeek = (dateString) => {

        if (!dateString) {
            return null;
        }


        const date = new Date(
            `${dateString}T00:00:00`
        );


        const days = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ];


        return days[date.getDay()];
    };


    // ============================================================
    // GET SCHEDULES FOR SELECTED DATE
    // ============================================================

    const getSchedulesForDate = (dateString) => {

        const selectedDay =
            getDayOfWeek(dateString);


        if (!selectedDay) {
            return [];
        }


        return schedules.filter(
            (schedule) =>
                schedule.day_of_week.toLowerCase() ===
                selectedDay
        );
    };


    // ============================================================
    // CONVERT TIME TO MINUTES
    // ============================================================

    const timeToMinutes = (timeString) => {

        const [hours, minutes] =
            timeString
                .slice(0, 5)
                .split(":")
                .map(Number);


        return (
            hours * 60 +
            minutes
        );
    };


    // ============================================================
    // CONVERT MINUTES TO HH:MM
    // ============================================================

    const minutesToTime = (totalMinutes) => {

        const hours =
            Math.floor(totalMinutes / 60);

        const minutes =
            totalMinutes % 60;


        return (
            String(hours).padStart(2, "0") +
            ":" +
            String(minutes).padStart(2, "0")
        );
    };


    // ============================================================
    // FORMAT TIME FOR DISPLAY
    // ============================================================

    const formatTime = (timeString) => {

        const [hours, minutes] =
            timeString.split(":").map(Number);


        const date = new Date();

        date.setHours(
            hours,
            minutes,
            0,
            0
        );


        return date.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });
    };


    // ============================================================
    // GENERATE 30-MINUTE APPOINTMENT SLOTS
    // ============================================================

    const getAvailableTimeSlots = () => {
        const selectedSchedules =
            getSchedulesForDate(formData.appointment_date);

        if (selectedSchedules.length === 0) {
            return [];
        }

        const slots = [];

        selectedSchedules.forEach((schedule) => {
            const start = timeToMinutes(schedule.start_time);
            const end = timeToMinutes(schedule.end_time);

            for (let time = start; time < end; time += 30) {
                slots.push(minutesToTime(time));
            }
        });

        const uniqueSlots = [...new Set(slots)].sort();

        return uniqueSlots.filter(
            (slot) => !bookedSlots.includes(slot)
        );
    };


    // ============================================================
    // AVAILABLE TIME SLOTS
    // ============================================================

    const availableTimeSlots =
        getAvailableTimeSlots();


    // ============================================================
    // CHECK WHETHER SELECTED DATE/TIME IS AVAILABLE
    // ============================================================

    const isWithinDoctorSchedule = (
        appointmentDate,
        appointmentTime
    ) => {

        if (
            !appointmentDate ||
            !appointmentTime
        ) {
            return false;
        }


        const selectedSchedules =
            getSchedulesForDate(
                appointmentDate
            );


        return selectedSchedules.some(
            (schedule) => {

                const startTime =
                    schedule.start_time.slice(
                        0,
                        5
                    );

                const endTime =
                    schedule.end_time.slice(
                        0,
                        5
                    );


                return (
                    appointmentTime >= startTime &&
                    appointmentTime < endTime
                );
            }
        );
    };


    // ============================================================
    // HANDLE APPOINTMENT BOOKING
    // ============================================================

    const handleSubmit = async (event) => {

        event.preventDefault();

        setError("");

        setSuccess("");

        setSaving(true);


        try {

            // ----------------------------------------------------
            // Validate date
            // ----------------------------------------------------

            if (!formData.appointment_date) {

                throw new Error(
                    "Please select an appointment date."
                );
            }


            // ----------------------------------------------------
            // Validate time
            // ----------------------------------------------------

            if (!formData.appointment_time) {

                throw new Error(
                    "Please select an appointment time."
                );
            }


            // ----------------------------------------------------
            // Validate doctor schedule
            // ----------------------------------------------------

            if (
                !isWithinDoctorSchedule(
                    formData.appointment_date,
                    formData.appointment_time
                )
            ) {

                const selectedDay =
                    getDayOfWeek(
                        formData.appointment_date
                    );


                const matchingSchedules =
                    schedules.filter(
                        (schedule) =>
                            schedule.day_of_week.toLowerCase() ===
                            selectedDay
                    );


                if (
                    matchingSchedules.length ===
                    0
                ) {

                    throw new Error(
                        "The doctor is not available on the selected day."
                    );
                }


                throw new Error(
                    "The selected time is outside the doctor's working hours."
                );
            }


            // ----------------------------------------------------
            // Get logged-in patient's profile
            // ----------------------------------------------------

            const patient =
                await getMyPatientProfile();


            // ----------------------------------------------------
            // Prepare appointment data
            // ----------------------------------------------------

            const appointmentData = {

                patient_id:
                    patient.id,

                doctor_id:
                    Number(doctorId),

                appointment_date:
                    formData.appointment_date,

                appointment_time:
                    formData.appointment_time,

                reason:
                    formData.reason || null,

                status:
                    "scheduled",
            };


            // ----------------------------------------------------
            // Create appointment
            // ----------------------------------------------------

            const appointment =
                await createAppointment(
                    appointmentData
                );


            console.log(
                "Appointment created:",
                appointment
            );


            // ----------------------------------------------------
            // Store created appointment
            // ----------------------------------------------------

            setCreatedAppointment(
                appointment
            );


            setSuccess(
                "Appointment booked successfully."
            );


            // ----------------------------------------------------
            // Clear form
            // ----------------------------------------------------

            setFormData({
                appointment_date: "",
                appointment_time: "",
                reason: "",
            });

        } catch (error) {

            console.error(error);


            // ----------------------------------------------------
            // Frontend validation error
            // ----------------------------------------------------

            if (error.message) {

                const frontendMessages = [

                    "Please select an appointment date.",

                    "Please select an appointment time.",

                    "The doctor is not available on the selected day.",

                    "The selected time is outside the doctor's working hours.",
                ];


                if (
                    frontendMessages.includes(
                        error.message
                    )
                ) {

                    setError(
                        error.message
                    );

                    return;
                }
            }


            // ----------------------------------------------------
            // Backend error
            // ----------------------------------------------------

            if (error.response) {

                setError(
                    error.response.data?.detail ||
                    "Unable to book appointment."
                );

            } else {

                setError(
                    "Unable to connect to the server."
                );
            }

        } finally {

            setSaving(false);
        }
    };


    // ============================================================
    // LOADING STATE
    // ============================================================

    if (loading) {

        return (

            <MainLayout>

                <h1>
                    Book Appointment
                </h1>

                <p>
                    Loading doctor and schedule...
                </p>

            </MainLayout>
        );
    }


    // ============================================================
    // DOCTOR NOT FOUND / LOAD ERROR
    // ============================================================

    if (error && !doctor) {

        return (

            <MainLayout>

                <h1>
                    Book Appointment
                </h1>

                <p className="error-message">
                    {error}
                </p>

            </MainLayout>
        );
    }


    // ============================================================
    // MAIN PAGE
    // ============================================================

    return (

        <MainLayout>

            <div className="booking-page">


                {/* ==================================================
                    HEADER
                ================================================== */}

                <div className="booking-header">

                    <h1>
                        Book Appointment
                    </h1>

                    <p>
                        Schedule an appointment with
                        your selected doctor.
                    </p>

                </div>


                {/* ==================================================
                    SUCCESS CARD
                ================================================== */}

                {createdAppointment && (

                    <div className="booking-success-card">

                        <h2>
                            Appointment Confirmed
                        </h2>


                        <div className="appointment-summary">

                            <p>
                                <strong>
                                    Appointment ID:
                                </strong>{" "}
                                {createdAppointment.id}
                            </p>


                            <p>
                                <strong>
                                    Doctor:
                                </strong>{" "}
                                {doctor.name}
                            </p>


                            <p>
                                <strong>
                                    Specialization:
                                </strong>{" "}
                                {doctor.specialization}
                            </p>


                            <p>
                                <strong>
                                    Date:
                                </strong>{" "}
                                {createdAppointment.appointment_date}
                            </p>


                            <p>
                                <strong>
                                    Time:
                                </strong>{" "}
                                {formatTime(
                                    createdAppointment.appointment_time
                                )}
                            </p>


                            <p>
                                <strong>
                                    Status:
                                </strong>{" "}
                                {createdAppointment.status}
                            </p>


                            <p>
                                <strong>
                                    Reason:
                                </strong>{" "}
                                {createdAppointment.reason ||
                                    "Not provided"}
                            </p>

                        </div>


                        <button
                            className="view-appointments-btn"
                            onClick={() =>
                                navigate(
                                    "/patient/appointments"
                                )
                            }
                        >
                            View My Appointments
                        </button>

                    </div>
                )}


                {/* ==================================================
                    BOOKING FORM
                ================================================== */}

                {!createdAppointment && (

                    <div className="booking-card">


                        {/* ==================================================
                            SELECTED DOCTOR
                        ================================================== */}

                        {doctor && (

                            <div className="selected-doctor">

                                <h2>
                                    {doctor.name}
                                </h2>

                                <p>
                                    {doctor.specialization}
                                </p>

                                {doctor.experience_years !==
                                    null && (

                                        <span>

                                            {
                                                doctor.experience_years
                                            }{" "}

                                            years experience

                                        </span>
                                    )}

                            </div>
                        )}


                        {/* ==================================================
                            ERROR
                        ================================================== */}

                        {error && (

                            <p className="error-message">
                                {error}
                            </p>
                        )}


                        {/* ==================================================
                            DOCTOR AVAILABILITY
                        ================================================== */}

                        {schedules.length === 0 ? (

                            <p className="error-message">

                                This doctor does not have
                                an available schedule.

                            </p>

                        ) : (

                            <div className="doctor-availability">

                                <h3>
                                    Doctor Availability
                                </h3>


                                {schedules.map(
                                    (schedule) => (

                                        <p
                                            key={
                                                schedule.id
                                            }
                                        >

                                            <strong>

                                                {schedule.day_of_week
                                                    .charAt(0)
                                                    .toUpperCase() +
                                                    schedule.day_of_week.slice(
                                                        1
                                                    )}

                                            </strong>

                                            {" : "}

                                            {
                                                schedule.start_time.slice(
                                                    0,
                                                    5
                                                )
                                            }

                                            {" - "}

                                            {
                                                schedule.end_time.slice(
                                                    0,
                                                    5
                                                )
                                            }

                                        </p>
                                    )
                                )}

                            </div>
                        )}


                        {/* ==================================================
                            FORM
                        ================================================== */}

                        <form
                            onSubmit={
                                handleSubmit
                            }
                        >


                            {/* ==================================================
                                APPOINTMENT DATE
                            ================================================== */}

                            <div className="form-group">

                                <label
                                    htmlFor="appointment_date"
                                >
                                    Appointment Date
                                </label>


                                <input
                                    id="appointment_date"
                                    name="appointment_date"
                                    type="date"
                                    min={today}
                                    value={
                                        formData.appointment_date
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    required
                                />

                            </div>


                            {/* ==================================================
                                APPOINTMENT TIME
                            ================================================== */}

                            <div className="form-group">

                                <label>
                                    Appointment Time
                                </label>


                                {!formData.appointment_date ? (

                                    <p>
                                        Please select a date
                                        first.
                                    </p>

                                ) : availableTimeSlots.length === 0 ? (

                                    <p className="error-message">

                                        The doctor is not available
                                        on the selected day.

                                    </p>

                                ) : (

                                    <div className="appointment-slots">
                                        {loadingBookedSlots ? (
                                            <p>Loading available slots...</p>
                                        ) : availableTimeSlots.length === 0 ? (
                                            <p>No available time slots for this date.</p>
                                        ) : (
                                            <div className="time-slots">
                                                {availableTimeSlots.map((time) => (
                                                    <button
                                                        key={time}
                                                        type="button"
                                                        className={
                                                            formData.appointment_time === time
                                                                ? "time-slot selected"
                                                                : "time-slot"
                                                        }
                                                        onClick={() =>
                                                            setFormData((previousData) => ({
                                                                ...previousData,
                                                                appointment_time: time,
                                                            }))
                                                        }
                                                    >
                                                        {formatTime(time)}
                                                    </button>
                                                ))}
                                            </div>
                                        )}
                                        {availableTimeSlots.map(
                                            (time) => (

                                                <button
                                                    key={time}
                                                    type="button"
                                                    className={
                                                        formData.appointment_time ===
                                                            time
                                                            ? "time-slot selected"
                                                            : "time-slot"
                                                    }
                                                    onClick={() =>
                                                        setFormData(
                                                            (
                                                                previousData
                                                            ) => ({
                                                                ...previousData,
                                                                appointment_time:
                                                                    time,
                                                            })
                                                        )
                                                    }
                                                >
                                                    {formatTime(
                                                        time
                                                    )}
                                                </button>
                                            )
                                        )}

                                    </div>
                                )}

                            </div>


                            {/* ==================================================
                                SELECTED TIME
                            ================================================== */}

                            {formData.appointment_time && (

                                <p>

                                    Selected time:{" "}

                                    <strong>
                                        {formatTime(
                                            formData.appointment_time
                                        )}
                                    </strong>

                                </p>
                            )}


                            {/* ==================================================
                                REASON
                            ================================================== */}

                            <div className="form-group">

                                <label
                                    htmlFor="reason"
                                >
                                    Reason
                                </label>


                                <textarea
                                    id="reason"
                                    name="reason"
                                    value={
                                        formData.reason
                                    }
                                    onChange={
                                        handleChange
                                    }
                                    placeholder="Enter reason for appointment"
                                    rows="4"
                                    maxLength="500"
                                />

                            </div>


                            {/* ==================================================
                                BUTTONS
                            ================================================== */}

                            <div className="booking-actions">

                                <button
                                    type="submit"
                                    disabled={
                                        saving ||
                                        schedules.length === 0 ||
                                        !formData.appointment_date ||
                                        !formData.appointment_time
                                    }
                                >

                                    {saving
                                        ? "Booking..."
                                        : "Confirm Appointment"}

                                </button>


                                <button
                                    type="button"
                                    className="cancel-btn"
                                    onClick={() =>
                                        navigate(
                                            "/patient/doctors"
                                        )
                                    }
                                    disabled={saving}
                                >
                                    Cancel
                                </button>

                            </div>

                        </form>

                    </div>
                )}

            </div>

        </MainLayout>
    );
}


export default BookAppointment;