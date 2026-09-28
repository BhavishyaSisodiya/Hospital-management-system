import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getDepartments,
} from "../../api/departments";
import {
    getHospitals,
} from "../../api/hospitals";
import {
    getRooms,
    getRoom,
    createRoom,
    updateRoom,
    deleteRoom,
} from "../../api/rooms";

function AdminRooms() {

    const [rooms, setRooms] = useState([]);
    const [departments, setDepartments] = useState([]);
    const [hospitals, setHospitals] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        room_number: "",
        room_type: "",
        department_id: "",
        hospital_id: "",
        floor: "",
        capacity: "",
        status: "available",
    });

    const [filterStatus, setFilterStatus] = useState("");
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {

        const loadAll = async () => {

            try {

                setLoading(true);
                setError("");

                const [
                    roomData,
                    departmentData,
                    hospitalData,
                ] = await Promise.all([
                    getRooms(),
                    getDepartments(),
                    getHospitals(),
                ]);

                setRooms(roomData);
                setDepartments(departmentData);
                setHospitals(hospitalData);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Failed to load rooms."
                );

            } finally {

                setLoading(false);

            }
        };

        loadAll();

    }, []);


    const filtered = filterStatus
        ? rooms.filter(
            (r) => r.status === filterStatus
        )
        : rooms;


    const openAdd = () => {

        setEditing(null);

        setForm({
            room_number: "",
            room_type: "",
            department_id: "",
            hospital_id: "",
            floor: "",
            capacity: "",
            status: "available",
        });

        setShowModal(true);

    };


    const openEdit = (room) => {

        setEditing(room);

        setForm({
            room_number: room.room_number || "",
            room_type: room.room_type || "",
            department_id: room.department_id || "",
            hospital_id: room.hospital_id || "",
            floor: room.floor || "",
            capacity: room.capacity || "",
            status: room.status || "available",
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

                await updateRoom(
                    editing.id,
                    form
                );

            } else {

                await createRoom(form);

            }

            const data = await getRooms();

            setRooms(data);

            setShowModal(false);

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to save room."
            );

        } finally {

            setSubmitting(false);

        }
    };


    const handleDelete = async (id) => {

        if (
            !window.confirm(
                "Are you sure you want to delete this room?"
            )
        ) {

            return;

        }

        try {

            await deleteRoom(id);

            setRooms((prev) =>
                prev.filter((r) => r.id !== id)
            );

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to delete room."
            );

        }
    };


    const getDepartmentName = (id) => {

        const dep = departments.find((x) => x.id === id);

        return dep ? dep.name : id;

    };


    const getHospitalName = (id) => {

        const h = hospitals.find((x) => x.id === id);

        return h ? h.name : id;

    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Rooms</h1>

                    <p className="loading-message">
                        Loading rooms...
                    </p>

                </div>

            </MainLayout>
        );

    }


    // ============================================================
    // ERROR
    // ============================================================

    if (error && rooms.length === 0) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Rooms</h1>

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
                            Rooms
                        </h2>

                        <p>
                            Manage all hospital rooms.
                        </p>

                    </div>

                    <button
                        className="btn-add"
                        onClick={openAdd}
                    >
                        + New Room
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
                            <option value="available">
                                Available
                            </option>
                            <option value="occupied">
                                Occupied
                            </option>
                            <option value="maintenance">
                                Maintenance
                            </option>
                        </select>

                    </div>

                </div>


                {filtered.length === 0 ? (

                    <div className="empty-state">
                        <h2>No Rooms</h2>
                        <p>
                            No rooms found.
                        </p>
                    </div>

                ) : (

                    <div className="table-wrapper">

                        <div className="table-container">

                            <table className="appointments-table">

                                <thead>

                                    <tr>

                                        <th>Room Number</th>

                                        <th>Room Type</th>

                                        <th>Department</th>

                                        <th>Hospital</th>

                                        <th>Floor</th>

                                        <th>Capacity</th>

                                        <th>Status</th>

                                        <th>Actions</th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {filtered.map(
                                        (room) => (
                                            <tr
                                                key={
                                                    room.id
                                                }
                                            >

                                                <td>
                                                    {
                                                        room.room_number
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        room.room_type
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        getDepartmentName(
                                                            room.department_id
                                                        )
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        getHospitalName(
                                                            room.hospital_id
                                                        )
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        room.floor
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        room.capacity
                                                    }
                                                </td>

                                                <td>
                                                    <span
                                                        className={`status-badge status-${room.status}`}
                                                    >
                                                        {
                                                            room.status
                                                        }
                                                    </span>
                                                </td>

                                                <td>

                                                    <button
                                                        className="btn-edit"
                                                        onClick={() =>
                                                            openEdit(
                                                                room
                                                            )
                                                        }
                                                    >
                                                        Edit
                                                    </button>

                                                    <button
                                                        className="btn-delete"
                                                        onClick={() =>
                                                            handleDelete(
                                                                room.id
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
                                        ? "Edit Room"
                                        : "New Room"
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
                                            Room Number
                                        </label>

                                        <input
                                            type="text"
                                            className="form-input"
                                            name="room_number"
                                            value={
                                                form.room_number
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        />

                                    </div>

                                    <div className="form-group">

                                        <label className="form-label">
                                            Room Type
                                        </label>

                                        <input
                                            type="text"
                                            className="form-input"
                                            name="room_type"
                                            value={
                                                form.room_type
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        />

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
                                            required
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
                                            Hospital
                                        </label>

                                        <select
                                            className="form-select"
                                            name="hospital_id"
                                            value={
                                                form.hospital_id
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        >
                                            <option value="">
                                                Select Hospital
                                            </option>

                                            {hospitals.map(
                                                (h) => (
                                                    <option
                                                        key={
                                                            h.id
                                                        }
                                                        value={
                                                            h.id
                                                        }
                                                    >
                                                        {
                                                            h.name
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
                                            Floor
                                        </label>

                                        <input
                                            type="text"
                                            className="form-input"
                                            name="floor"
                                            value={
                                                form.floor
                                            }
                                            onChange={
                                                handleChange
                                            }
                                        />

                                    </div>

                                    <div className="form-group">

                                        <label className="form-label">
                                            Capacity
                                        </label>

                                        <input
                                            type="number"
                                            className="form-input"
                                            name="capacity"
                                            value={
                                                form.capacity
                                            }
                                            onChange={
                                                handleChange
                                            }
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
                                        value={
                                            form.status
                                        }
                                        onChange={
                                            handleChange
                                        }
                                        required
                                    >
                                        <option value="available">
                                            Available
                                        </option>
                                        <option value="occupied">
                                            Occupied
                                        </option>
                                        <option value="maintenance">
                                            Maintenance
                                        </option>
                                    </select>

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

export default AdminRooms;
