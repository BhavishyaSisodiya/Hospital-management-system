import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getPatients,
    createPatient,
    updatePatient,
    deletePatient,
} from "../../api/patients";

function ReceptionistPatients() {

    const [patients, setPatients] = useState([]);
    const [filteredPatients, setFilteredPatients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editingPatient, setEditingPatient] = useState(null);

    const [searchQuery, setSearchQuery] = useState("");

    const [formData, setFormData] = useState({
        name: "",
        email: "",
        phone: "",
        gender: "",
        date_of_birth: "",
        address: "",
    });

    const [saving, setSaving] = useState(false);


    /* ============================================================
       LOAD PATIENTS
       ============================================================ */

    useEffect(() => {

        const loadPatients = async () => {

            try {

                setLoading(true);
                setError("");

                const data = await getPatients();

                setPatients(data);
                setFilteredPatients(data);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Unable to load patients."
                );

            } finally {

                setLoading(false);

            }
        };

        loadPatients();

    }, []);


    /* ============================================================
       FILTER
       ============================================================ */

    useEffect(() => {

        let result = patients;

        const q = searchQuery.trim().toLowerCase();

        if (q) {

            result = result.filter(
                (p) =>
                    (p.name || "").toLowerCase().includes(q) ||
                    (p.email || "").toLowerCase().includes(q) ||
                    (p.phone || "").toLowerCase().includes(q)
            );

        }

        setFilteredPatients(result);

    }, [searchQuery, patients]);


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

        setEditingPatient(null);
        setFormData({
            name: "",
            email: "",
            phone: "",
            gender: "",
            date_of_birth: "",
            address: "",
        });
        setError("");
        setSuccess("");
        setShowModal(true);

    };

    const openEditModal = (patient) => {

        setEditingPatient(patient);
        setFormData({
            name: patient.name || "",
            email: patient.email || "",
            phone: patient.phone || "",
            gender: patient.gender || "",
            date_of_birth: patient.date_of_birth || "",
            address: patient.address || "",
        });
        setError("");
        setSuccess("");
        setShowModal(true);

    };

    const closeModal = () => {

        setShowModal(false);
        setEditingPatient(null);
        setError("");

    };

    const handleSubmit = async (event) => {

        event.preventDefault();

        setError("");
        setSuccess("");
        setSaving(true);

        try {

            if (editingPatient) {

                await updatePatient(editingPatient.id, formData);

                setSuccess("Patient updated successfully.");

            } else {

                await createPatient(formData);

                setSuccess("Patient created successfully.");

            }

            const data = await getPatients();
            setPatients(data);

            closeModal();

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Unable to save patient."
            );

        } finally {

            setSaving(false);

        }

    };


    /* ============================================================
       DELETE
       ============================================================ */

    const handleDelete = async (patientId) => {

        const confirmed = window.confirm(
            "Are you sure you want to delete this patient?"
        );

        if (!confirmed) {
            return;
        }

        try {

            setError("");
            setSuccess("");

            await deletePatient(patientId);

            setPatients((prev) =>
                prev.filter((p) => p.id !== patientId)
            );

            setSuccess("Patient deleted successfully.");

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Unable to delete patient."
            );

        }

    };


    /* ============================================================
       RENDER
       ============================================================ */

    return (
        <MainLayout>
            <div className="appointments-page">

                <div className="appointments-header">
                    <div>
                        <h1>Manage Patients</h1>
                        <p>
                            View, add, edit, and delete patient
                            records.
                        </p>
                    </div>

                    <button
                        type="button"
                        className="action-btn-add"
                        onClick={openAddModal}
                    >
                        Add Patient
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
                    <label htmlFor="patient-search">
                        Search:
                    </label>
                    <input
                        id="patient-search"
                        type="text"
                        className="form-input"
                        placeholder="Search by name, email, or phone"
                        value={searchQuery}
                        onChange={(e) =>
                            setSearchQuery(e.target.value)
                        }
                    />
                </div>


                {/* ==================================================
                   LOADING
                   ================================================== */}

                {loading && (
                    <p className="loading-message">
                        Loading patients...
                    </p>
                )}


                {/* ==================================================
                   EMPTY STATE
                   ================================================== */}

                {!loading && filteredPatients.length === 0 && (
                    <div className="empty-state">
                        <h2>No Patients Found</h2>
                        <p>
                            No patients match your current filter.
                        </p>
                    </div>
                )}


                {/* ==================================================
                   TABLE
                   ================================================== */}

                {!loading && filteredPatients.length > 0 && (

                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Phone</th>
                                        <th>Gender</th>
                                        <th>DOB</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredPatients.map(
                                        (patient) => (
                                            <tr key={patient.id}>
                                                <td>{patient.name}</td>
                                                <td>
                                                    {patient.email || "-"}
                                                </td>
                                                <td>
                                                    {patient.phone || "-"}
                                                </td>
                                                <td>
                                                    {patient.gender || "-"}
                                                </td>
                                                <td>
                                                    {patient.date_of_birth || "-"}
                                                </td>
                                                <td>
                                                    <button
                                                        type="button"
                                                        className="action-btn action-btn-edit"
                                                        onClick={() =>
                                                            openEditModal(patient)
                                                        }
                                                    >
                                                        Edit
                                                    </button>
                                                    <button
                                                        type="button"
                                                        className="action-btn action-btn-delete"
                                                        onClick={() =>
                                                            handleDelete(patient.id)
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
                                    {editingPatient
                                        ? "Edit Patient"
                                        : "Add Patient"}
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

                                <div className="form-group">
                                    <label className="form-label">
                                        Name
                                    </label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleChange}
                                        required
                                    />
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label className="form-label">
                                            Email
                                        </label>
                                        <input
                                            type="email"
                                            className="form-input"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleChange}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">
                                            Phone
                                        </label>
                                        <input
                                            type="text"
                                            className="form-input"
                                            name="phone"
                                            value={formData.phone}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label className="form-label">
                                            Gender
                                        </label>
                                        <select
                                            className="form-select"
                                            name="gender"
                                            value={formData.gender}
                                            onChange={handleChange}
                                        >
                                            <option value="">
                                                Select
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
                                    <label className="form-label">
                                        Date of Birth
                                    </label>
                                    <input
                                        type="date"
                                        className="form-input"
                                        name="date_of_birth"
                                        value={formData.date_of_birth}
                                        onChange={handleChange}
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">
                                        Address
                                    </label>
                                    <textarea
                                        className="form-textarea"
                                        name="address"
                                        value={formData.address}
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
                                            : editingPatient
                                                ? "Update Patient"
                                                : "Create Patient"}
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

export default ReceptionistPatients;
