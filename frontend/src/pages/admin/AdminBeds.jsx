import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getRooms,
} from "../../api/rooms";
import {
    getBeds,
    getBed,
    getBedsByRoom,
    createBed,
    updateBed,
    deleteBed,
} from "../../api/beds";

function AdminBeds() {

    const [beds, setBeds] = useState([]);
    const [rooms, setRooms] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        bed_number: "",
        room_id: "",
        bed_type: "",
        status: "available",
    });

    const [filterRoom, setFilterRoom] = useState("");
    const [filterStatus, setFilterStatus] = useState("");
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {

        const loadAll = async () => {

            try {

                setLoading(true);
                setError("");

                const [bedData, roomData] =
                    await Promise.all([
                        getBeds(),
                        getRooms(),
                    ]);

                setBeds(bedData);
                setRooms(roomData);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Failed to load beds."
                );

            } finally {

                setLoading(false);

            }
        };

        loadAll();

    }, []);


    const filtered = beds.filter((b) => {

        if (filterRoom && b.room_id !== Number(filterRoom)) {

            return false;

        }

        if (filterStatus && b.status !== filterStatus) {

            return false;

        }

        return true;

    });


    const openAdd = () => {

        setEditing(null);

        setForm({
            bed_number: "",
            room_id: "",
            bed_type: "",
            status: "available",
        });

        setShowModal(true);

    };


    const openEdit = (bed) => {

        setEditing(bed);

        setForm({
            bed_number: bed.bed_number || "",
            room_id: bed.room_id || "",
            bed_type: bed.bed_type || "",
            status: bed.status || "available",
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

                await updateBed(
                    editing.id,
                    form
                );

            } else {

                await createBed(form);

            }

            const data = await getBeds();

            setBeds(data);

            setShowModal(false);

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to save bed."
            );

        } finally {

            setSubmitting(false);

        }
    };


    const handleDelete = async (id) => {

        if (
            !window.confirm(
                "Are you sure you want to delete this bed?"
            )
        ) {

            return;

        }

        try {

            await deleteBed(id);

            setBeds((prev) =>
                prev.filter((b) => b.id !== id)
            );

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to delete bed."
            );

        }
    };


    const getRoomNumber = (id) => {

        const r = rooms.find((x) => x.id === id);

        return r ? r.room_number : id;

    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Beds</h1>

                    <p className="loading-message">
                        Loading beds...
                    </p>

                </div>

            </MainLayout>
        );

    }


    // ============================================================
    // ERROR
    // ============================================================

    if (error && beds.length === 0) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Beds</h1>

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
                            Beds
                        </h2>

                        <p>
                            Manage all hospital beds.
                        </p>

                    </div>

                    <button
                        className="btn-add"
                        onClick={openAdd}
                    >
                        + New Bed
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
                            Room
                        </label>

                        <select
                            className="form-select"
                            value={filterRoom}
                            onChange={(e) =>
                                setFilterRoom(
                                    e.target.value
                                )
                            }
                        >
                            <option value="">
                                All Rooms
                            </option>

                            {rooms.map((r) => (
                                <option
                                    key={r.id}
                                    value={r.id}
                                >
                                    {r.room_number}
                                </option>
                            ))}

                        </select>

                    </div>

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
                        <h2>No Beds</h2>
                        <p>
                            No beds found.
                        </p>
                    </div>

                ) : (

                    <div className="table-wrapper">

                        <div className="table-container">

                            <table className="appointments-table">

                                <thead>

                                    <tr>

                                        <th>Bed Number</th>

                                        <th>Room</th>

                                        <th>Type</th>

                                        <th>Status</th>

                                        <th>Actions</th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {filtered.map(
                                        (bed) => (
                                            <tr
                                                key={
                                                    bed.id
                                                }
                                            >

                                                <td>
                                                    {
                                                        bed.bed_number
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        getRoomNumber(
                                                            bed.room_id
                                                        )
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        bed.bed_type ||
                                                        "-"
                                                    }
                                                </td>

                                                <td>
                                                    <span
                                                        className={`status-badge status-${bed.status}`}
                                                    >
                                                        {
                                                            bed.status
                                                        }
                                                    </span>
                                                </td>

                                                <td>

                                                    <button
                                                        className="btn-edit"
                                                        onClick={() =>
                                                            openEdit(
                                                                bed
                                                            )
                                                        }
                                                    >
                                                        Edit
                                                    </button>

                                                    <button
                                                        className="btn-delete"
                                                        onClick={() =>
                                                            handleDelete(
                                                                bed.id
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
                                        ? "Edit Bed"
                                        : "New Bed"
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
                                            Bed Number
                                        </label>

                                        <input
                                            type="text"
                                            className="form-input"
                                            name="bed_number"
                                            value={
                                                form.bed_number
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        />

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
                                            Bed Type
                                        </label>

                                        <input
                                            type="text"
                                            className="form-input"
                                            name="bed_type"
                                            value={
                                                form.bed_type
                                            }
                                            onChange={
                                                handleChange
                                            }
                                        />

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

export default AdminBeds;
