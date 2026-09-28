import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getDoctors,
} from "../../api/doctors";
import {
    getPatients,
} from "../../api/patients";
import {
    getDepartments,
} from "../../api/departments";
import {
    getAppointment,
    getAppointments,
    createAppointment,
    updateAppointment,
    deleteAppointment,
} from "../../api/appointments";

function AdminAppointments() {

    const [appointments, setAppointments] = useState([]);
    const [patients, setPatients] = useState([]);
    const [doctors, setDoctors] = useState([]);
    const [departments, setDepartments] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        patient_id: "",
        doctor_id: "",
        department_id: "",
        appointment_date: "",
        appointment_time: "",
        status: "scheduled",
        notes: "",
    });

    const [filterStatus, setFilterStatus] = useState("");
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {

        const loadAll = async () => {

            try {

                setLoading(true);
                setError("");

                const [
                    appointmentData,
                    patientData,
                    doctorData,
                    departmentData,
                ] = await Promise.all([
                    getAppointments(),
                    getPatients(),
                    getDoctors(),
                    getDepartments(),
                ]);

                setAppointments(appointmentData);
                setPatients(patientData);
                setDoctors(doctorData);
                setDepartments(departmentData);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Failed to load appointments."
                );

            } finally {

                setLoading(false);

            }
        };

        loadAll();

    }, []);


    const filtered = filterStatus
        ? appointments.filter(
            (a) => a.status === filterStatus
        )
        : appointments;


    const openAdd = () => {

        setEditing(null);

        setForm({
            patient_id: "",
            doctor_id: "",
            department_id: "",
            appointment_date: "",
            appointment_time: "",
            status: "scheduled",
            notes: "",
        });

        setShowModal(true);

    };


    const openEdit = (appointment) => {

        setEditing(appointment);

        setForm({
            patient_id: appointment.patient_id || "",
            doctor_id: appointment.doctor_id || "",
            department_id: appointment.department_id || "",
            appointment_date: appointment.appointment_date || "",
            appointment_time: appointment.appointment_time || "",
            status: appointment.status || "scheduled",
            notes: appointment.notes || "",
        });

        setShowModal(true);

    };


    const handleChange = (e) => {

        const { name, value } = e.target;

        setForm((prev) => ({ ...prev, [name]: value }));

    };


    const handleSubmit = async (e) => {

        e.preventDefault();

        setSubmitting(true);

        try {

            if (editing) {

                await updateAppointment(
                    editing.id,
                    form
                );

            } else {

                await createAppointment(form);

            }

            const data = await getAppointments();

            setAppointments(data);

            setShowModal(false);

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to save appointment."
            );

        } finally {

            setSubmitting(false);

        }
    };


    const handleDelete = async (id) => {

        if (
            !window.confirm(
                "Are you sure you want to delete this appointment?"
            )
        ) {

            return;

        }

        try {

            await deleteAppointment(id);

            setAppointments((prev) =>
                prev.filter((a) => a.id !== id)
            );

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to delete appointment."
            );

        }
    };


    const getPatientName = (id) => {

        const p = patients.find((x) => x.id === id);

        return p
            ? p.name
            : id;

    };


    const getDoctorName = (id) => {

        const d = doctors.find((x) => x.id === id);

        return d
            ? `Dr. ${d.name}`
            : id;

    };


    const getDepartmentName = (id) => {

        const dep = departments.find((x) => x.id === id);

        return dep ? dep.name : id;

    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Appointments</h1>

                    <p className="loading-message">
                        Loading appointments...
                    </p>

                </div>

            </MainLayout>
        );

    }


    // ============================================================
    // ERROR
    // ============================================================

    if (error && appointments.length === 0) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Appointments</h1>

                    <p className="error-message">
                        {error}
                    </p>

                </div>

            </MainLayout>
        );

    }


    // ============================================================
    // PAGE
    // ============================================================

    return (

        <MainLayout>

            <div className="dashboard-page">

                <div className="section-header">

                    <div>

                        <h2 className="section-title">
                            Appointments
                        </h2>

                        <p>
                            Manage all patient appointments.
                        </p>

                    </div>

                    <button
                        className="btn-add"
                        onClick={openAdd}
                    >
                        + New Appointment
                    </button>

                </div>


                {error && (
                    <p className="error-message">
                        {error}
                    </p>
                )}


                <div className="filter-row">

                    <div className="filter-group">

                        <label className="form-label">
                            Status
                        </label>

                        <select
                            className="form-select"
                            value={filterStatus}
                            onChange={(e) =>
                                setFilterStatus(
                                    e.target.value
                                )
                            }
                        >
                            <option value="">
                                All Statuses
                            </option>
                            <option value="scheduled">
                                Scheduled
                            </option>
                            <option value="completed">
                                Completed
                            </option>
                            <option value="cancelled">
                                Cancelled
                            </option>
                            <option value="no-show">
                                No Show
                            </option>
                        </select>

                    </div>

                </div>


                {filtered.length === 0 ? (

                    <div className="empty-state">
                        <h2>No Appointments</h2>
                        <p>
                            No appointments found.
                        </p>
                    </div>

                ) : (

                    <div className="table-wrapper">

                        <div className="table-container">

                            <table className="appointments-table">

                                <thead>

                                    <tr>

                                        <th>Patient</th>

                                        <th>Doctor</th>

                                        <th>Department</th>

                                        <th>Date</th>

                                        <th>Time</th>

                                        <th>Status</th>

                                        <th>Notes</th>

                                        <th>Actions</th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {filtered.map(
                                        (appointment) => (
                                            <tr
                                                key={
                                                    appointment.id
                                                }
                                            >

                                                <td>
                                                    {
                                                        getPatientName(
                                                            appointment.patient_id
                                                        )
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        getDoctorName(
                                                            appointment.doctor_id
                                                        )
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        getDepartmentName(
                                                            appointment.department_id
                                                        )
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
                                                    <span
                                                        className={`status-badge status-${appointment.status}`}
                                                    >
                                                        {
                                                            appointment.status
                                                        }
                                                    </span>
                                                </td>

                                                <td>
                                                    {
                                                        appointment.notes ||
                                                        "-"
                                                    }
                                                </td>

                                                <td>

                                                    <button
                                                        className="btn-edit"
                                                        onClick={() =>
                                                            openEdit(
                                                                appointment
                                                            )
                                                        }
                                                    >
                                                        Edit
                                                    </button>

                                                    <button
                                                        className="btn-delete"
                                                        onClick={() =>
                                                            handleDelete(
                                                                appointment.id
                                                            )
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


                {showModal && (

                    <div className="modal-overlay">

                        <div className="modal-content">

                            <div className="modal-header">

                                <h2>
                                    {editing
                                        ? "Edit Appointment"
                                        : "New Appointment"
                                    }
                                </h2>

                                <button
                                    className="btn-cancel"
                                    onClick={() =>
                                        setShowModal(false)
                                    }
                                >
                                    &times;
                                </button>

                            </div>

                            <form
                                className="form-group"
                                onSubmit={handleSubmit}
                            >

                                <div className="form-row">

                                    <div className="form-group">

                                        <label className="form-label">
                                            Patient
                                        </label>

                                        <select
                                            className="form-select"
                                            name="patient_id"
                                            value={
                                                form.patient_id
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        >
                                            <option value="">
                                                Select Patient
                                            </option>

                                            {patients.map(
                                                (p) => (
                                                    <option
                                                        key={
                                                            p.id
                                                        }
                                                        value={
                                                            p.id
                                                        }
                                                    >
                                                        {
                                                            p.name
                                                        }
                                                    </option>
                                                )
                                            )}

                                        </select>

                                    </div>

                                    <div className="form-group">

                                        <label className="form-label">
                                            Doctor
                                        </label>

                                        <select
                                            className="form-select"
                                            name="doctor_id"
                                            value={
                                                form.doctor_id
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        >
                                            <option value="">
                                                Select Doctor
                                            </option>

                                            {doctors.map(
                                                (d) => (
                                                    <option
                                                        key={
                                                            d.id
                                                        }
                                                        value={
                                                            d.id
                                                        }
                                                    >
                                                        Dr.{" "}
                                                        {
                                                            d.name
                                                        }
                                                    </option>
                                                )
                                            )}

                                        </select>

                                    </div>

                                </div>


                                <div className="form-row">

                                    <div className="form-group">

                                        <label className="form-label">
                                            Department
                                        </label>

                                        <select
                                            className="form-select"
                                            name="department_id"
                                            value={
                                                form.department_id
                                            }
                                            onChange={
                                                handleChange
                                            }
                                        >
                                            <option value="">
                                                Select Department
                                            </option>

                                            {departments.map(
                                                (dep) => (
                                                    <option
                                                        key={
                                                            dep.id
                                                        }
                                                        value={
                                                            dep.id
                                                        }
                                                    >
                                                        {
                                                            dep.name
                                                        }
                                                    </option>
                                                )
                                            )}

                                        </select>

                                    </div>

                                    <div className="form-group">

                                        <label className="form-label">
                                            Status
                                        </label>

                                        <select
                                            className="form-select"
                                            name="status"
                                            value={
                                                form.status
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        >
                                            <option value="scheduled">
                                                Scheduled
                                            </option>
                                            <option value="completed">
                                                Completed
                                            </option>
                                            <option value="cancelled">
                                                Cancelled
                                            </option>
                                            <option value="no-show">
                                                No Show
                                            </option>
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
                                            value={
                                                form.appointment_date
                                            }
                                            onChange={
                                                handleChange
                                            }
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
                                            value={
                                                form.appointment_time
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        />

                                    </div>

                                </div>


                                <div className="form-group">

                                    <label className="form-label">
                                        Notes
                                    </label>

                                    <textarea
                                        className="form-textarea"
                                        name="notes"
                                        value={
                                            form.notes
                                        }
                                        onChange={
                                            handleChange
                                        }
                                        rows="3"
                                    />

                                </div>


                                <div className="form-actions">

                                    <button
                                        type="button"
                                        className="btn-cancel"
                                        onClick={() =>
                                            setShowModal(
                                                false
                                            )
                                        }
                                    >
                                        Cancel
                                    </button>

                                    <button
                                        type="submit"
                                        className="btn-save"
                                        disabled={
                                            submitting
                                        }
                                    >
                                        {submitting
                                            ? "Saving..."
                                            : editing
                                                ? "Update"
                                                : "Create"
                                        }
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

export default AdminAppointments;
