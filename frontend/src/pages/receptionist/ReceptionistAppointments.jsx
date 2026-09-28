import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getAppointments,
    createAppointment,
    updateAppointment,
    deleteAppointment,
} from "../../api/appointments";
import { getDoctors } from "../../api/doctors";
import { getPatients } from "../../api/patients";

function ReceptionistAppointments() {

    const [appointments, setAppointments] = useState([]);
    const [filteredAppointments, setFilteredAppointments] = useState([]);
    const [doctors, setDoctors] = useState([]);
    const [patientsList, setPatientsList] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editingAppointment, setEditingAppointment] = useState(null);

    const [filterStatus, setFilterStatus] = useState("");

    const [formData, setFormData] = useState({
        patient_id: "",
        doctor_id: "",
        appointment_date: "",
        appointment_time: "",
        reason: "",
        status: "scheduled",
    });

    const [saving, setSaving] = useState(false);


    /* ============================================================
       LOAD DATA
       ============================================================ */

    useEffect(() => {

        const loadData = async () => {

            try {

                setLoading(true);
                setError("");

                const [
                    appointmentsData,
                    doctorsData,
                    patientsData,
                ] = await Promise.all([
                    getAppointments(),
                    getDoctors(),
                    getPatients(),
                ]);

                setAppointments(appointmentsData);
                setFilteredAppointments(appointmentsData);
                setDoctors(doctorsData);
                setPatientsList(patientsData);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Unable to load data."
                );

            } finally {

                setLoading(false);

            }
        };

        loadData();

    }, []);


    /* ============================================================
       FILTER
       ============================================================ */

    useEffect(() => {

        let result = appointments;

        if (filterStatus) {

            result = result.filter(
                (a) => a.status === filterStatus
            );

        }

        setFilteredAppointments(result);

    }, [filterStatus, appointments]);


    /* ============================================================
       LOOKUP HELPERS
       ============================================================ */

    const getPatientName = (patientId) => {

        const patient = patientsList.find(
            (p) => p.id === patientId
        );

        return patient ? patient.name : `Patient #${patientId}`;

    };

    const getDoctorName = (doctorId) => {

        const doctor = doctors.find(
            (d) => d.id === doctorId
        );

        return doctor
            ? `Dr. ${doctor.name}`
            : `Doctor #${doctorId}`;

    };


    /* ============================================================
       FORM HANDLERS
       ============================================================ */

    const handleChange = (event) => {

        const { name, value } = event.target;

        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));

    };

    const openAddModal = () => {

        setEditingAppointment(null);
        setFormData({
            patient_id: "",
            doctor_id: "",
            appointment_date: "",
            appointment_time: "",
            reason: "",
            status: "scheduled",
        });
        setError("");
        setSuccess("");
        setShowModal(true);

    };

    const openEditModal = (appointment) => {

        setEditingAppointment(appointment);
        setFormData({
            patient_id: appointment.patient_id || "",
            doctor_id: appointment.doctor_id || "",
            appointment_date: appointment.appointment_date || "",
            appointment_time: appointment.appointment_time || "",
            reason: appointment.reason || "",
            status: appointment.status || "scheduled",
        });
        setError("");
        setSuccess("");
        setShowModal(true);

    };

    const closeModal = () => {

        setShowModal(false);
        setEditingAppointment(null);
        setError("");

    };

    const handleSubmit = async (event) => {

        event.preventDefault();

        setError("");
        setSuccess("");
        setSaving(true);

        try {

            const payload = {
                ...formData,
                patient_id: parseInt(formData.patient_id, 10),
                doctor_id: parseInt(formData.doctor_id, 10),
            };

            if (editingAppointment) {

                await updateAppointment(
                    editingAppointment.id,
                    payload
                );

                setSuccess("Appointment updated successfully.");

            } else {

                await createAppointment(payload);

                setSuccess("Appointment created successfully.");

            }

            const data = await getAppointments();
            setAppointments(data);

            closeModal();

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Unable to save appointment."
            );

        } finally {

            setSaving(false);

        }

    };


    /* ============================================================
       DELETE
       ============================================================ */

    const handleDelete = async (appointmentId) => {

        const confirmed = window.confirm(
            "Are you sure you want to delete this appointment?"
        );

        if (!confirmed) {
            return;
        }

        try {

            setError("");
            setSuccess("");

            await deleteAppointment(appointmentId);

            setAppointments((prev) =>
                prev.filter((a) => a.id !== appointmentId)
            );

            setSuccess("Appointment deleted successfully.");

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Unable to delete appointment."
            );

        }

    };


    /* ============================================================
       STATUS OPTIONS
       ============================================================ */

    const statuses = [
        "scheduled", "completed", "cancelled", "no_show",
    ];


    /* ============================================================
       RENDER
       ============================================================ */

    return (
        <MainLayout>
            <div className="appointments-page">

                <div className="appointments-header">
                    <div>
                        <h1>Manage Appointments</h1>
                        <p>
                            View, add, edit, and delete patient
                            appointments.
                        </p>
                    </div>

                    <button
                        type="button"
                        className="action-btn-add"
                        onClick={openAddModal}
                    >
                        Add Appointment
                    </button>
                </div>


                {success && (
                    <p className="success-message">{success}</p>
                )}

                {error && !showModal && (
                    <p className="error-message">{error}</p>
                )}


                {/* ==================================================
                   FILTER
                   ================================================== */}

                <div className="filter-row">
                    <label htmlFor="status-filter">
                        Status:
                    </label>
                    <select
                        id="status-filter"
                        className="form-select"
                        value={filterStatus}
                        onChange={(e) =>
                            setFilterStatus(e.target.value)
                        }
                    >
                        <option value="">All</option>
                        {statuses.map((s) => (
                            <option key={s} value={s}>
                                {s.replace("_", " ")}
                            </option>
                        ))}
                    </select>
                </div>


                {/* ==================================================
                   LOADING
                   ================================================== */}

                {loading && (
                    <p className="loading-message">
                        Loading appointments...
                    </p>
                )}


                {/* ==================================================
                   EMPTY STATE
                   ================================================== */}

                {!loading && filteredAppointments.length === 0 && (
                    <div className="empty-state">
                        <h2>No Appointments Found</h2>
                        <p>
                            No appointments match your current
                            filter.
                        </p>
                    </div>
                )}


                {/* ==================================================
                   TABLE
                   ================================================== */}

                {!loading && filteredAppointments.length > 0 && (

                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Patient</th>
                                        <th>Doctor</th>
                                        <th>Date</th>
                                        <th>Time</th>
                                        <th>Status</th>
                                        <th>Reason</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredAppointments.map(
                                        (appointment) => (
                                            <tr key={appointment.id}>
                                                <td>
                                                    {getPatientName(
                                                        appointment.patient_id
                                                    )}
                                                </td>
                                                <td>
                                                    {getDoctorName(
                                                        appointment.doctor_id
                                                    )}
                                                </td>
                                                <td>
                                                    {appointment.appointment_date}
                                                </td>
                                                <td>
                                                    {appointment.appointment_time}
                                                </td>
                                                <td>
                                                    <span
                                                        className={`status-badge status-${appointment.status}`}
                                                    >
                                                        {appointment.status}
                                                    </span>
                                                </td>
                                                <td>
                                                    {appointment.reason || "-"}
                                                </td>
                                                <td>
                                                    <button
                                                        type="button"
                                                        className="action-btn action-btn-edit"
                                                        onClick={() =>
                                                            openEditModal(appointment)
                                                        }
                                                    >
                                                        Edit
                                                    </button>
                                                    <button
                                                        type="button"
                                                        className="action-btn action-btn-delete"
                                                        onClick={() =>
                                                            handleDelete(appointment.id)
                                                        }
                                                    >
                                                        Delete
                                                    </button>
                                                </td>
                                            </tr>
                                        )
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                )}


                {/* ==================================================
                   MODAL
                   ================================================== */}

                {showModal && (
                    <div className="modal-overlay">
                        <div className="modal-content">

                            <div className="modal-header">
                                <h2>
                                    {editingAppointment
                                        ? "Edit Appointment"
                                        : "Add Appointment"}
                                </h2>
                                <button
                                    type="button"
                                    className="modal-close-btn"
                                    onClick={closeModal}
                                >
                                    &times;
                                </button>
                            </div>

                            {error && (
                                <p className="error-message">
                                    {error}
                                </p>
                            )}

                            <form onSubmit={handleSubmit}>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label className="form-label">
                                            Patient
                                        </label>
                                        <select
                                            className="form-select"
                                            name="patient_id"
                                            value={formData.patient_id}
                                            onChange={handleChange}
                                            required
                                        >
                                            <option value="">
                                                Select Patient
                                            </option>
                                            {patientsList.map((p) => (
                                                <option key={p.id} value={p.id}>
                                                    {p.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">
                                            Doctor
                                        </label>
                                        <select
                                            className="form-select"
                                            name="doctor_id"
                                            value={formData.doctor_id}
                                            onChange={handleChange}
                                            required
                                        >
                                            <option value="">
                                                Select Doctor
                                            </option>
                                            {doctors.map((d) => (
                                                <option key={d.id} value={d.id}>
                                                    Dr. {d.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label className="form-label">
                                            Date
                                        </label>
                                        <input
                                            type="date"
                                            className="form-input"
                                            name="appointment_date"
                                            value={formData.appointment_date}
                                            onChange={handleChange}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">
                                            Time
                                        </label>
                                        <input
                                            type="time"
                                            className="form-input"
                                            name="appointment_time"
                                            value={formData.appointment_time}
                                            onChange={handleChange}
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">
                                        Status
                                    </label>
                                    <select
                                        className="form-select"
                                        name="status"
                                        value={formData.status}
                                        onChange={handleChange}
                                    >
                                        {statuses.map((s) => (
                                            <option key={s} value={s}>
                                                {s.replace("_", " ")}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">
                                        Reason
                                    </label>
                                    <textarea
                                        className="form-textarea"
                                        name="reason"
                                        value={formData.reason}
                                        onChange={handleChange}
                                        rows="3"
                                    />
                                </div>

                                <div className="booking-actions">
                                    <button
                                        type="submit"
                                        disabled={saving}
                                    >
                                        {saving
                                            ? "Saving..."
                                            : editingAppointment
                                                ? "Update Appointment"
                                                : "Create Appointment"}
                                    </button>
                                    <button
                                        type="button"
                                        className="cancel-btn"
                                        onClick={closeModal}
                                        disabled={saving}
                                    >
                                        Cancel
                                    </button>
                                </div>

                            </form>

                        </div>
                    </div>
                )}

            </div>
        </MainLayout>
    );
}

export default ReceptionistAppointments;
