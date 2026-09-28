import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getDepartments,
    createDepartment,
    updateDepartment,
    deleteDepartment,
} from "../../api/departments";
import { getHospitals } from "../../api/hospitals";

function AdminDepartments() {

    const [departments, setDepartments] = useState([]);
    const [hospitals, setHospitals] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editingDepartment, setEditingDepartment] = useState(null);
    const [formData, setFormData] = useState({
        name: "",
        hospitalId: "",
        description: "",
    });
    const [formError, setFormError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                setError("");

                const [deptData, hospData] = await Promise.all([
                    getDepartments(),
                    getHospitals(),
                ]);

                setDepartments(deptData);
                setHospitals(hospData);
            } catch (err) {
                console.error(err);
                if (err.response) {
                    setError(
                        err.response.data?.detail ||
                        "Unable to load departments."
                    );
                } else {
                    setError("Unable to connect to the server.");
                }
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    const resetForm = () => {
        setFormData({
            name: "",
            hospitalId: "",
            description: "",
        });
        setFormError("");
        setEditingDepartment(null);
    };

    const openAddModal = () => {
        resetForm();
        setShowModal(true);
    };

    const openEditModal = (department) => {
        setEditingDepartment(department);
        setFormData({
            name: department.name || "",
            hospitalId: department.hospital_id || "",
            description: department.description || "",
        });
        setFormError("");
        setShowModal(true);
    };

    const handleFormChange = (event) => {
        const { name, value } = event.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setFormError("");
        setSubmitting(true);

        try {
            const payload = {
                name: formData.name,
                hospital_id: formData.hospitalId || null,
                description: formData.description || null,
            };

            if (editingDepartment) {
                await updateDepartment(editingDepartment.id, payload);
            } else {
                await createDepartment(payload);
            }

            const data = await getDepartments();
            setDepartments(data);
            setShowModal(false);
            resetForm();
        } catch (err) {
            console.error(err);
            if (err.response) {
                setFormError(
                    err.response.data?.detail ||
                    "Failed to save department."
                );
            } else {
                setFormError("Unable to connect to the server.");
            }
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (deptId) => {
        if (
            !window.confirm(
                "Are you sure you want to delete this department?"
            )
        ) {
            return;
        }

        try {
            await deleteDepartment(deptId);
            const data = await getDepartments();
            setDepartments(data);
        } catch (err) {
            console.error(err);
            if (err.response) {
                setError(
                    err.response.data?.detail ||
                    "Failed to delete department."
                );
            } else {
                setError("Unable to connect to the server.");
            }
        }
    };

    const getHospitalName = (hospId) => {
        const hosp = hospitals.find((h) => h.id === hospId);
        return hosp ? hosp.name : "N/A";
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <p className="loading-message">
                        Loading departments...
                    </p>
                </div>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <p className="error-message">{error}</p>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="dashboard-page">

                <div className="appointments-header">
                    <div>
                        <h1>Departments</h1>
                        <p>Manage hospital departments and assignments.</p>
                    </div>
                </div>

                <div className="filter-row">
                    <div className="filter-group">
                        <p style={{ margin: 0, color: "#6b7280" }}>
                            Total departments: {departments.length}
                        </p>
                    </div>
                    <div className="filter-actions">
                        <button className="btn-add" onClick={openAddModal}>
                            Add Department
                        </button>
                    </div>
                </div>

                {departments.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Departments</h2>
                        <p>No departments found.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Hospital</th>
                                        <th>Description</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {departments.map((dept) => (
                                        <tr key={dept.id}>
                                            <td>{dept.name}</td>
                                            <td>
                                                {getHospitalName(
                                                    dept.hospital_id
                                                )}
                                            </td>
                                            <td>
                                                {dept.description || "N/A"}
                                            </td>
                                            <td>
                                                <button
                                                    className="btn-edit"
                                                    onClick={() =>
                                                        openEditModal(dept)
                                                    }
                                                >
                                                    Edit
                                                </button>
                                                <button
                                                    className="btn-delete"
                                                    onClick={() =>
                                                        handleDelete(dept.id)
                                                    }
                                                >
                                                    Delete
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
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
                                    {editingDepartment
                                        ? "Edit Department"
                                        : "Add Department"}
                                </h2>
                                <button
                                    className="btn-cancel"
                                    onClick={() => {
                                        setShowModal(false);
                                        resetForm();
                                    }}
                                >
                                    Close
                                </button>
                            </div>

                            {formError && (
                                <p className="error-message">{formError}</p>
                            )}

                            <form
                                className="form-group"
                                onSubmit={handleSubmit}
                            >
                                <div className="form-group">
                                    <label>Name</label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleFormChange}
                                        required
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Hospital</label>
                                    <select
                                        name="hospitalId"
                                        value={formData.hospitalId}
                                        onChange={handleFormChange}
                                    >
                                        <option value="">
                                            Select Hospital
                                        </option>
                                        {hospitals.map((hosp) => (
                                            <option
                                                key={hosp.id}
                                                value={hosp.id}
                                            >
                                                {hosp.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>Description</label>
                                    <textarea
                                        name="description"
                                        value={formData.description}
                                        onChange={handleFormChange}
                                    />
                                </div>

                                <div className="booking-actions">
                                    <button
                                        type="submit"
                                        className="btn-save"
                                        disabled={submitting}
                                    >
                                        {submitting ? "Saving..." : "Save"}
                                    </button>
                                    <button
                                        type="button"
                                        className="btn-cancel"
                                        onClick={() => {
                                            setShowModal(false);
                                            resetForm();
                                        }}
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

export default AdminDepartments;
