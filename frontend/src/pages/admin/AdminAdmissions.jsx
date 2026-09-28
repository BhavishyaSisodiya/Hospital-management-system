import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getPatients,
} from "../../api/patients";
import {
    getRooms,
} from "../../api/rooms";
import {
    getBeds,
} from "../../api/beds";
import {
    getAdmissions,
    getAdmission,
    createAdmission,
    updateAdmission,
    deleteAdmission,
    dischargeAdmission,
} from "../../api/admissions";

function AdminAdmissions() {

    const [admissions, setAdmissions] = useState([]);
    const [patients, setPatients] = useState([]);
    const [rooms, setRooms] = useState([]);
    const [beds, setBeds] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        patient_id: "",
        room_id: "",
        bed_id: "",
        admission_date: "",
        discharge_date: "",
        status: "active",
        notes: "",
        diagnosis: "",
    });

    const [filterStatus, setFilterStatus] = useState("");
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {

        const loadAll = async () => {

            try {

                setLoading(true);
                setError("");

                const [
                    admissionData,
                    patientData,
                    roomData,
                    bedData,
                ] = await Promise.all([
                    getAdmissions(),
                    getPatients(),
                    getRooms(),
                    getBeds(),
                ]);

                setAdmissions(admissionData);
                setPatients(patientData);
                setRooms(roomData);
                setBeds(bedData);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Failed to load admissions."
                );

            } finally {

                setLoading(false);

            }
        };

        loadAll();

    }, []);


    const filtered = filterStatus
        ? admissions.filter(
            (a) => a.status === filterStatus
        )
        : admissions;


    const openAdd = () => {

        setEditing(null);

        setForm({
            patient_id: "",
            room_id: "",
            bed_id: "",
            admission_date: "",
            discharge_date: "",
            status: "active",
            notes: "",
            diagnosis: "",
        });

        setShowModal(true);

    };


    const openEdit = (admission) => {

        setEditing(admission);

        setForm({
            patient_id: admission.patient_id || "",
            room_id: admission.room_id || "",
            bed_id: admission.bed_id || "",
            admission_date: admission.admission_date || "",
            discharge_date: admission.discharge_date || "",
            status: admission.status || "active",
            notes: admission.notes || "",
            diagnosis: admission.diagnosis || "",
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

                await updateAdmission(
                    editing.id,
                    form
                );

            } else {

                await createAdmission(form);

            }

            const data = await getAdmissions();

            setAdmissions(data);

            setShowModal(false);

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to save admission."
            );

        } finally {

            setSubmitting(false);

        }
    };


    const handleDelete = async (id) => {

        if (
            !window.confirm(
                "Are you sure you want to delete this admission?"
            )
        ) {

            return;

        }

        try {

            await deleteAdmission(id);

            setAdmissions((prev) =>
                prev.filter((a) => a.id !== id)
            );

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to delete admission."
            );

        }
    };


    const handleDischarge = async (id) => {

        if (
            !window.confirm(
                "Are you sure you want to discharge this patient?"
            )
        ) {

            return;

        }

        try {

            await dischargeAdmission(id);

            const data = await getAdmissions();

            setAdmissions(data);

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to discharge patient."
            );

        }
    };


    const getPatientName = (id) => {

        const p = patients.find((x) => x.id === id);

        return p
            ? p.name
            : id;

    };


    const getRoomNumber = (id) => {

        const r = rooms.find((x) => x.id === id);

        return r ? r.room_number : id;

    };


    const getBedNumber = (id) => {

        const b = beds.find((x) => x.id === id);

        return b ? b.bed_number : id;

    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Admissions</h1>

                    <p className="loading-message">
                        Loading admissions...
                    </p>

                </div>

            </MainLayout>
        );

    }


    // ============================================================
    // ERROR
    // ============================================================

    if (error && admissions.length === 0) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Admissions</h1>

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
                            Admissions
                        </h2>

                        <p>
                            Manage all patient admissions.
                        </p>

                    </div>

                    <button
                        className="btn-add"
                        onClick={openAdd}
                    >
                        + New Admission
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
                            <option value="active">
                                Active
                            </option>
                            <option value="discharged">
                                Discharged
                            </option>
                            <option value="cancelled">
                                Cancelled
                            </option>
                        </select>

                    </div>

                </div>


                {filtered.length === 0 ? (

                    <div className="empty-state">
                        <h2>No Admissions</h2>
                        <p>
                            No admissions found.
                        </p>
                    </div>

                ) : (

                    <div className="table-wrapper">

                        <div className="table-container">

                            <table className="appointments-table">

                                <thead>

                                    <tr>

                                        <th>Patient</th>

                                        <th>Room</th>

                                        <th>Bed</th>

                                        <th>Admission Date</th>

                                        <th>Discharge Date</th>

                                        <th>Status</th>

                                        <th>Notes</th>

                                        <th>Actions</th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {filtered.map(
                                        (admission) => (
                                            <tr
                                                key={
                                                    admission.id
                                                }
                                            >

                                                <td>
                                                    {
                                                        getPatientName(
                                                            admission.patient_id
                                                        )
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        getRoomNumber(
                                                            admission.room_id
                                                        )
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        getBedNumber(
                                                            admission.bed_id
                                                        )
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        admission.admission_date
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        admission.discharge_date ||
                                                        "-"
                                                    }
                                                </td>

                                                <td>
                                                    <span
                                                        className={`status-badge status-${admission.status}`}
                                                    >
                                                        {
                                                            admission.status
                                                        }
                                                    </span>
                                                </td>

                                                <td>
                                                    {
                                                        admission.notes ||
                                                        "-"
                                                    }
                                                </td>

                                                <td>

                                                    {admission.status ===
                                                        "active" && (
                                                            <button
                                                                className="btn-edit"
                                                                onClick={() =>
                                                                    handleDischarge(
                                                                        admission.id
                                                                    )
                                                                }
                                                            >
                                                                Discharge
                                                            </button>
                                                        )}

                                                    <button
                                                        className="btn-edit"
                                                        onClick={() =>
                                                            openEdit(
                                                                admission
                                                            )
                                                        }
                                                    >
                                                        Edit
                                                    </button>

                                                    <button
                                                        className="btn-delete"
                                                        onClick={() =>
                                                            handleDelete(
                                                                admission.id
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
                                        ? "Edit Admission"
                                        : "New Admission"
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
                                            Room
                                        </label>

                                        <select
                                            className="form-select"
                                            name="room_id"
                                            value={
                                                form.room_id
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        >
                                            <option value="">
                                                Select Room
                                            </option>

                                            {rooms.map(
                                                (r) => (
                                                    <option
                                                        key={
                                                            r.id
                                                        }
                                                        value={
                                                            r.id
                                                        }
                                                    >
                                                        {
                                                            r.room_number
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
                                            Bed
                                        </label>

                                        <select
                                            className="form-select"
                                            name="bed_id"
                                            value={
                                                form.bed_id
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        >
                                            <option value="">
                                                Select Bed
                                            </option>

                                            {beds.map(
                                                (b) => (
                                                    <option
                                                        key={
                                                            b.id
                                                        }
                                                        value={
                                                            b.id
                                                        }
                                                    >
                                                        {
                                                            b.bed_number
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
                                            <option value="active">
                                                Active
                                            </option>
                                            <option value="discharged">
                                                Discharged
                                            </option>
                                            <option value="cancelled">
                                                Cancelled
                                            </option>
                                        </select>

                                    </div>

                                </div>


                                <div className="form-row">

                                    <div className="form-group">

                                        <label className="form-label">
                                            Admission Date
                                        </label>

                                        <input
                                            type="date"
                                            className="form-input"
                                            name="admission_date"
                                            value={
                                                form.admission_date
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        />

                                    </div>

                                    <div className="form-group">

                                        <label className="form-label">
                                            Discharge Date
                                        </label>

                                        <input
                                            type="date"
                                            className="form-input"
                                            name="discharge_date"
                                            value={
                                                form.discharge_date
                                            }
                                            onChange={
                                                handleChange
                                            }
                                        />

                                    </div>

                                </div>


                                <div className="form-group">

                                    <label className="form-label">
                                        Diagnosis
                                    </label>

                                    <input
                                        type="text"
                                        className="form-input"
                                        name="diagnosis"
                                        value={
                                            form.diagnosis
                                        }
                                        onChange={
                                            handleChange
                                        }
                                    />

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

export default AdminAdmissions;
