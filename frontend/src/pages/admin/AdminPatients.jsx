import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getPatients,
    createPatient,
    updatePatient,
    deletePatient,
} from "../../api/patients";

function AdminPatients() {

    const [patients, setPatients] = useState([]);
    const [filteredPatients, setFilteredPatients] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [filterBloodGroup, setFilterBloodGroup] = useState("");
    const [showModal, setShowModal] = useState(false);
    const [editingPatient, setEditingPatient] = useState(null);
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        phone: "",
        dateOfBirth: "",
        gender: "",
        address: "",
    });
    const [formError, setFormError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                setError("");
                const data = await getPatients();
                setPatients(data);
                setFilteredPatients(data);
            } catch (err) {
                console.error(err);
                if (err.response) {
                    setError(
                        err.response.data?.detail ||
                        "Unable to load patients."
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
        const q = filterBloodGroup.trim().toLowerCase();
        if (q) {
            setFilteredPatients(
                patients.filter(
                    (pat) =>
                        (pat.name || "").toLowerCase().includes(q) ||
                        (pat.email || "").toLowerCase().includes(q) ||
                        (pat.phone || "").toLowerCase().includes(q)
                )
            );
        } else {
            setFilteredPatients(patients);
        }
    }, [filterBloodGroup, patients]);

    const resetForm = () => {
        setFormData({
            name: "",
            email: "",
            phone: "",
            dateOfBirth: "",
            gender: "",
            address: "",
        });
        setFormError("");
        setEditingPatient(null);
    };

    const openAddModal = () => {
        resetForm();
        setShowModal(true);
    };

    const openEditModal = (patient) => {
        setEditingPatient(patient);
        setFormData({
            name: patient.name || "",
            email: patient.email || "",
            phone: patient.phone || "",
            dateOfBirth: patient.date_of_birth || "",
            gender: patient.gender || "",
            address: patient.address || "",
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
                date_of_birth: formData.dateOfBirth || null,
                gender: formData.gender || null,
                address: formData.address || null,
            };

            if (editingPatient) {
                await updatePatient(editingPatient.id, payload);
            } else {
                await createPatient(payload);
            }

            const data = await getPatients();
            setPatients(data);
            setShowModal(false);
            resetForm();
        } catch (err) {
            console.error(err);
            if (err.response) {
                setFormError(
                    err.response.data?.detail ||
                    "Failed to save patient."
                );
            } else {
                setFormError("Unable to connect to the server.");
            }
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (patientId) => {
        if (!window.confirm("Are you sure you want to delete this patient?")) {
            return;
        }

        try {
            await deletePatient(patientId);
            const data = await getPatients();
            setPatients(data);
        } catch (err) {
            console.error(err);
            if (err.response) {
                setError(
                    err.response.data?.detail ||
                    "Failed to delete patient."
                );
            } else {
                setError("Unable to connect to the server.");
            }
        }
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <p className="loading-message">Loading patients...</p>
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
                        <h1>Patients</h1>
                        <p>View and manage all patient records.</p>
                    </div>
                </div>

                <div className="filter-row">
                    <div className="filter-group">
                        <label>Search</label>
                        <input
                            type="text"
                            placeholder="Search by name, email, or phone"
                            value={filterBloodGroup}
                            onChange={(e) =>
                                setFilterBloodGroup(e.target.value)
                            }
                        />
                    </div>
                    <div className="filter-actions">
                        <button className="btn-add" onClick={openAddModal}>
                            Add Patient
                        </button>
                    </div>
                </div>

                {filteredPatients.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Patients</h2>
                        <p>No patients found matching the current filters.</p>
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
                                        <th>Gender</th>
                                        <th>Date of Birth</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredPatients.map((patient) => (
                                        <tr key={patient.id}>
                                            <td>
                                                {patient.name}
                                            </td>
                                            <td>{patient.email}</td>
                                            <td>{patient.phone || "N/A"}</td>
                                            <td>
                                                {patient.gender || "N/A"}
                                            </td>
                                            <td>
                                                {patient.date_of_birth ||
                                                    "N/A"}
                                            </td>
                                            <td>
                                                <button
                                                    className="btn-edit"
                                                    onClick={() =>
                                                        openEditModal(patient)
                                                    }
                                                >
                                                    Edit
                                                </button>
                                                <button
                                                    className="btn-delete"
                                                    onClick={() =>
                                                        handleDelete(
                                                            patient.id
                                                        )
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
                                    {editingPatient
                                        ? "Edit Patient"
                                        : "Add Patient"}
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
                                    <label>Full Name</label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleFormChange}
                                        required
                                    />
                                </div>

                                <div className="form-row">
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
                                    <div className="form-group">
                                        <label>Phone</label>
                                        <input
                                            type="text"
                                            name="phone"
                                            value={formData.phone}
                                            onChange={handleFormChange}
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Date of Birth</label>
                                        <input
                                            type="date"
                                            name="dateOfBirth"
                                            value={formData.dateOfBirth}
                                            onChange={handleFormChange}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Gender</label>
                                        <select
                                            name="gender"
                                            value={formData.gender}
                                            onChange={handleFormChange}
                                        >
                                            <option value="">
                                                Select Gender
                                            </option>
                                            <option value="male">
                                                Male
                                            </option>
                                            <option value="female">
                                                Female
                                            </option>
                                            <option value="other">
                                                Other
                                            </option>
                                        </select>
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label>Address</label>
                                    <textarea
                                        name="address"
                                        value={formData.address}
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

export default AdminPatients;
