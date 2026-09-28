import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getDoctors,
    createDoctor,
    updateDoctor,
    deleteDoctor,
} from "../../api/doctors";
import { getDepartments } from "../../api/departments";

function AdminDoctors() {

    const [doctors, setDoctors] = useState([]);
    const [filteredDoctors, setFilteredDoctors] = useState([]);
    const [departments, setDepartments] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [filterDepartment, setFilterDepartment] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editingDoctor, setEditingDoctor] = useState(null);
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        phone: "",
        specialization: "",
        experience: "",
        departmentId: "",
    });
    const [formError, setFormError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                setError("");

                const [docData, deptData] = await Promise.all([
                    getDoctors(),
                    getDepartments(),
                ]);

                setDoctors(docData);
                setFilteredDoctors(docData);
                setDepartments(deptData);
            } catch (err) {
                console.error(err);
                if (err.response) {
                    setError(
                        err.response.data?.detail ||
                        "Unable to load doctors."
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

    useEffect(() => {
        if (filterDepartment) {
            setFilteredDoctors(
                doctors.filter(
                    (doc) =>
                        String(doc.department_id) ===
                        String(filterDepartment)
                )
            );
        } else {
            setFilteredDoctors(doctors);
        }
    }, [filterDepartment, doctors]);

    const resetForm = () => {
        setFormData({
            name: "",
            email: "",
            phone: "",
            specialization: "",
            experience: "",
            departmentId: "",
        });
        setFormError("");
        setEditingDoctor(null);
    };

    const openAddModal = () => {
        resetForm();
        setShowModal(true);
    };

    const openEditModal = (doctor) => {
        setEditingDoctor(doctor);
        setFormData({
            name: doctor.name || "",
            email: doctor.email || "",
            phone: doctor.phone || "",
            specialization: doctor.specialization || "",
            experience:
                doctor.experience_years != null
                    ? doctor.experience_years
                    : "",
            departmentId: doctor.department_id || "",
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
                email: formData.email,
                phone: formData.phone,
                specialization: formData.specialization || null,
                experience_years: formData.experience
                    ? parseInt(formData.experience)
                    : null,
                department_id: formData.departmentId || null,
            };

            if (editingDoctor) {
                await updateDoctor(editingDoctor.id, payload);
            } else {
                await createDoctor(payload);
            }

            const data = await getDoctors();
            setDoctors(data);
            setShowModal(false);
            resetForm();
        } catch (err) {
            console.error(err);
            if (err.response) {
                setFormError(
                    err.response.data?.detail ||
                    "Failed to save doctor."
                );
            } else {
                setFormError("Unable to connect to the server.");
            }
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (doctorId) => {
        if (!window.confirm("Are you sure you want to delete this doctor?")) {
            return;
        }

        try {
            await deleteDoctor(doctorId);
            const data = await getDoctors();
            setDoctors(data);
        } catch (err) {
            console.error(err);
            if (err.response) {
                setError(
                    err.response.data?.detail ||
                    "Failed to delete doctor."
                );
            } else {
                setError("Unable to connect to the server.");
            }
        }
    };

    const getDepartmentName = (deptId) => {
        const dept = departments.find((d) => d.id === deptId);
        return dept ? dept.name : "N/A";
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <p className="loading-message">Loading doctors...</p>
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
                        <h1>Doctors</h1>
                        <p>Manage all doctors across departments.</p>
                    </div>
                </div>

                <div className="filter-row">
                    <div className="filter-group">
                        <label>Department</label>
                        <select
                            value={filterDepartment}
                            onChange={(e) =>
                                setFilterDepartment(e.target.value)
                            }
                        >
                            <option value="">All Departments</option>
                            {departments.map((dept) => (
                                <option key={dept.id} value={dept.id}>
                                    {dept.name}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="filter-actions">
                        <button className="btn-add" onClick={openAddModal}>
                            Add Doctor
                        </button>
                    </div>
                </div>

                {filteredDoctors.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Doctors</h2>
                        <p>No doctors found matching the current filters.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Phone</th>
                                        <th>Qualification</th>
                                        <th>Experience</th>
                                        <th>Department</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredDoctors.map((doctor) => (
                                        <tr key={doctor.id}>
                                            <td>
                                                {doctor.name || "-"}
                                            </td>
                                            <td>{doctor.email || "N/A"}</td>
                                            <td>{doctor.phone || "N/A"}</td>
                                            <td>
                                                {doctor.specialization || "N/A"}
                                            </td>
                                            <td>
                                                {doctor.experience_years != null
                                                    ? `${doctor.experience_years} yrs`
                                                    : "N/A"}
                                            </td>
                                            <td>
                                                {doctor.department_name ||
                                                    getDepartmentName(
                                                        doctor.department_id
                                                    )}
                                            </td>
                                            <td>
                                                <button
                                                    className="btn-edit"
                                                    onClick={() =>
                                                        openEditModal(doctor)
                                                    }
                                                >
                                                    Edit
                                                </button>
                                                <button
                                                    className="btn-delete"
                                                    onClick={() =>
                                                        handleDelete(doctor.id)
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
                                    {editingDoctor
                                        ? "Edit Doctor"
                                        : "Add Doctor"}
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
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Full Name</label>
                                        <input
                                            type="text"
                                            name="name"
                                            value={formData.name}
                                            onChange={handleFormChange}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Email</label>
                                        <input
                                            type="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleFormChange}
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Phone</label>
                                        <input
                                            type="text"
                                            name="phone"
                                            value={formData.phone}
                                            onChange={handleFormChange}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Qualification</label>
                                        <input
                                            type="text"
                                            name="specialization"
                                            value={formData.specialization}
                                            onChange={handleFormChange}
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Experience (years)</label>
                                        <input
                                            type="number"
                                            name="experience"
                                            value={formData.experience}
                                            onChange={handleFormChange}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Department</label>
                                        <select
                                            name="departmentId"
                                            value={formData.departmentId}
                                            onChange={handleFormChange}
                                        >
                                            <option value="">
                                                Select Department
                                            </option>
                                            {departments.map((dept) => (
                                                <option
                                                    key={dept.id}
                                                    value={dept.id}
                                                >
                                                    {dept.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
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

export default AdminDoctors;
