import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getEmployees,
} from "../../api/employees";
import {
    getAdmissions,
} from "../../api/admissions";
import {
    getNurseAssignments,
    getNurseAssignment,
    createNurseAssignment,
    updateNurseAssignment,
    deleteNurseAssignment,
} from "../../api/nurseAssignments";

function AdminNurseAssignments() {

    const [assignments, setAssignments] = useState([]);
    const [nurses, setNurses] = useState([]);
    const [admissions, setAdmissions] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        nurse_id: "",
        admission_id: "",
        start_date: "",
        end_date: "",
        status: "active",
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
                    assignmentData,
                    employeeData,
                    admissionData,
                ] = await Promise.all([
                    getNurseAssignments(),
                    getEmployees(),
                    getAdmissions(),
                ]);

                setAssignments(assignmentData);

                const nurseList = employeeData.filter(
                    (emp) =>
                        emp.role &&
                        emp.role.toLowerCase() === "nurse"
                );

                setNurses(nurseList);

                setAdmissions(admissionData);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Failed to load nurse assignments."
                );

            } finally {

                setLoading(false);

            }
        };

        loadAll();

    }, []);


    const filtered = filterStatus
        ? assignments.filter(
            (a) => a.status === filterStatus
        )
        : assignments;


    const openAdd = () => {

        setEditing(null);

        setForm({
            nurse_id: "",
            admission_id: "",
            start_date: "",
            end_date: "",
            status: "active",
            notes: "",
        });

        setShowModal(true);

    };


    const openEdit = (assignment) => {

        setEditing(assignment);

        setForm({
            nurse_id: assignment.nurse_id || "",
            admission_id: assignment.admission_id || "",
            start_date: assignment.start_date || "",
            end_date: assignment.end_date || "",
            status: assignment.status || "active",
            notes: assignment.notes || "",
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

                await updateNurseAssignment(
                    editing.id,
                    form
                );

            } else {

                await createNurseAssignment(form);

            }

            const data = await getNurseAssignments();

            setAssignments(data);

            setShowModal(false);

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to save assignment."
            );

        } finally {

            setSubmitting(false);

        }
    };


    const handleDelete = async (id) => {

        if (
            !window.confirm(
                "Are you sure you want to delete this assignment?"
            )
        ) {

            return;

        }

        try {

            await deleteNurseAssignment(id);

            setAssignments((prev) =>
                prev.filter((a) => a.id !== id)
            );

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to delete assignment."
            );

        }
    };


    const getNurseName = (id) => {

        const n = nurses.find((x) => x.id === id);

        return n
            ? `${n.first_name} ${n.last_name}`
            : id;

    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Nurse Assignments</h1>

                    <p className="loading-message">
                        Loading nurse assignments...
                    </p>

                </div>

            </MainLayout>
        );

    }


    // ============================================================
    // ERROR
    // ============================================================

    if (error && assignments.length === 0) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Nurse Assignments</h1>

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
                            Nurse Assignments
                        </h2>

                        <p>
                            Manage nurse-to-admission
                            assignments.
                        </p>

                    </div>

                    <button
                        className="btn-add"
                        onClick={openAdd}
                    >
                        + New Assignment
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
                            <option value="completed">
                                Completed
                            </option>
                            <option value="cancelled">
                                Cancelled
                            </option>
                        </select>

                    </div>

                </div>


                {filtered.length === 0 ? (

                    <div className="empty-state">
                        <h2>No Assignments</h2>
                        <p>
                            No nurse assignments found.
                        </p>
                    </div>

                ) : (

                    <div className="table-wrapper">

                        <div className="table-container">

                            <table className="appointments-table">

                                <thead>

                                    <tr>

                                        <th>Nurse Name</th>

                                        <th>Admission ID</th>

                                        <th>Start Date</th>

                                        <th>End Date</th>

                                        <th>Status</th>

                                        <th>Notes</th>

                                        <th>Actions</th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {filtered.map(
                                        (assignment) => (
                                            <tr
                                                key={
                                                    assignment.id
                                                }
                                            >

                                                <td>
                                                    {
                                                        getNurseName(
                                                            assignment.nurse_id
                                                        )
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        assignment.admission_id
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        assignment.start_date
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        assignment.end_date ||
                                                        "-"
                                                    }
                                                </td>

                                                <td>
                                                    <span
                                                        className={`status-badge status-${assignment.status}`}
                                                    >
                                                        {
                                                            assignment.status
                                                        }
                                                    </span>
                                                </td>

                                                <td>
                                                    {
                                                        assignment.notes ||
                                                        "-"
                                                    }
                                                </td>

                                                <td>

                                                    <button
                                                        className="btn-edit"
                                                        onClick={() =>
                                                            openEdit(
                                                                assignment
                                                            )
                                                        }
                                                    >
                                                        Edit
                                                    </button>

                                                    <button
                                                        className="btn-delete"
                                                        onClick={() =>
                                                            handleDelete(
                                                                assignment.id
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
                                        ? "Edit Assignment"
                                        : "New Assignment"
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
                                            Nurse
                                        </label>

                                        <select
                                            className="form-select"
                                            name="nurse_id"
                                            value={
                                                form.nurse_id
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        >
                                            <option value="">
                                                Select Nurse
                                            </option>

                                            {nurses.map(
                                                (n) => (
                                                    <option
                                                        key={
                                                            n.id
                                                        }
                                                        value={
                                                            n.id
                                                        }
                                                    >
                                                        {
                                                            n.first_name
                                                        }{" "}
                                                        {
                                                            n.last_name
                                                        }
                                                    </option>
                                                )
                                            )}

                                        </select>

                                    </div>

                                    <div className="form-group">

                                        <label className="form-label">
                                            Admission
                                        </label>

                                        <select
                                            className="form-select"
                                            name="admission_id"
                                            value={
                                                form.admission_id
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        >
                                            <option value="">
                                                Select Admission
                                            </option>

                                            {admissions.map(
                                                (a) => (
                                                    <option
                                                        key={
                                                            a.id
                                                        }
                                                        value={
                                                            a.id
                                                        }
                                                    >
                                                        Admission{" "}
                                                        #
                                                        {
                                                            a.id
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
                                            Start Date
                                        </label>

                                        <input
                                            type="date"
                                            className="form-input"
                                            name="start_date"
                                            value={
                                                form.start_date
                                            }
                                            onChange={
                                                handleChange
                                            }
                                            required
                                        />

                                    </div>

                                    <div className="form-group">

                                        <label className="form-label">
                                            End Date
                                        </label>

                                        <input
                                            type="date"
                                            className="form-input"
                                            name="end_date"
                                            value={
                                                form.end_date
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
                                        <option value="active">
                                            Active
                                        </option>
                                        <option value="completed">
                                            Completed
                                        </option>
                                        <option value="cancelled">
                                            Cancelled
                                        </option>
                                    </select>

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

export default AdminNurseAssignments;
