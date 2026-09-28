import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getHospitals,
    createHospital,
    updateHospital,
    deleteHospital,
} from "../../api/hospitals";

function AdminHospitals() {

    const [hospitals, setHospitals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState({
        name: "",
        address: "",
        phone: "",
        email: "",
    });

    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {

        const load = async () => {

            try {

                setLoading(true);
                setError("");

                const data = await getHospitals();

                setHospitals(data);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Failed to load hospitals."
                );

            } finally {

                setLoading(false);

            }
        };

        load();

    }, []);

    const openAdd = () => {

        setEditing(null);

        setForm({
            name: "",
            address: "",
            phone: "",
            email: "",
        });

        setShowModal(true);

    };

    const openEdit = (hospital) => {

        setEditing(hospital);

        setForm({
            name: hospital.name || "",
            address: hospital.address || "",
            phone: hospital.phone || "",
            email: hospital.email || "",
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
        setError("");

        try {

            if (editing) {

                await updateHospital(
                    editing.id,
                    form
                );

            } else {

                await createHospital(form);

            }

            const data = await getHospitals();

            setHospitals(data);

            setShowModal(false);

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to save hospital."
            );

        } finally {

            setSubmitting(false);

        }
    };

    const handleDelete = async (id) => {

        if (
            !window.confirm(
                "Are you sure you want to delete this hospital?"
            )
        ) {

            return;

        }

        try {

            await deleteHospital(id);

            setHospitals((prev) =>
                prev.filter((h) => h.id !== id)
            );

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to delete hospital."
            );

        }
    };

    if (loading) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Hospitals</h1>

                    <p className="loading-message">
                        Loading hospitals...
                    </p>

                </div>

            </MainLayout>
        );

    }

    if (error && hospitals.length === 0) {

        return (
            <MainLayout>

                <div className="dashboard-page">

                    <h1>Hospitals</h1>

                    <p className="error-message">
                        {error}
                    </p>

                </div>

            </MainLayout>
        );

    }

    return (

        <MainLayout>

            <div className="dashboard-page">

                <div className="section-header">

                    <div>

                        <h2 className="section-title">
                            Hospitals
                        </h2>

                        <p>
                            Manage hospital facilities.
                        </p>

                    </div>

                    <button
                        className="btn-add"
                        onClick={openAdd}
                    >
                        + New Hospital
                    </button>

                </div>

                {error && (
                    <p className="error-message">
                        {error}
                    </p>
                )}

                {hospitals.length === 0 ? (

                    <div className="empty-state">
                        <h2>No Hospitals</h2>
                        <p>
                            No hospital has been added yet.
                            Click "+ New Hospital" to add one.
                        </p>
                    </div>

                ) : (

                    <div className="table-wrapper">

                        <div className="table-container">

                            <table className="appointments-table">

                                <thead>

                                    <tr>

                                        <th>Name</th>

                                        <th>Address</th>

                                        <th>Phone</th>

                                        <th>Email</th>

                                        <th>Actions</th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {hospitals.map(
                                        (hospital) => (
                                            <tr
                                                key={
                                                    hospital.id
                                                }
                                            >

                                                <td>
                                                    {
                                                        hospital.name
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        hospital.address
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        hospital.phone
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        hospital.email
                                                    }
                                                </td>

                                                <td>

                                                    <button
                                                        className="btn-edit"
                                                        onClick={() =>
                                                            openEdit(
                                                                hospital
                                                            )
                                                        }
                                                    >
                                                        Edit
                                                    </button>

                                                    <button
                                                        className="btn-delete"
                                                        onClick={() =>
                                                            handleDelete(
                                                                hospital.id
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
                                        ? "Edit Hospital"
                                        : "New Hospital"
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

                                <div className="form-group">

                                    <label className="form-label">
                                        Hospital Name
                                    </label>

                                    <input
                                        type="text"
                                        className="form-input"
                                        name="name"
                                        value={form.name}
                                        onChange={handleChange}
                                        required
                                    />

                                </div>

                                <div className="form-group">

                                    <label className="form-label">
                                        Address
                                    </label>

                                    <input
                                        type="text"
                                        className="form-input"
                                        name="address"
                                        value={form.address}
                                        onChange={handleChange}
                                    />

                                </div>

                                <div className="form-row">

                                    <div className="form-group">

                                        <label className="form-label">
                                            Phone
                                        </label>

                                        <input
                                            type="text"
                                            className="form-input"
                                            name="phone"
                                            value={form.phone}
                                            onChange={handleChange}
                                            required
                                        />

                                    </div>

                                    <div className="form-group">

                                        <label className="form-label">
                                            Email
                                        </label>

                                        <input
                                            type="email"
                                            className="form-input"
                                            name="email"
                                            value={form.email}
                                            onChange={handleChange}
                                        />

                                    </div>

                                </div>

                                <div className="form-actions">

                                    <button
                                        type="button"
                                        className="btn-cancel"
                                        onClick={() =>
                                            setShowModal(false)
                                        }
                                    >
                                        Cancel
                                    </button>

                                    <button
                                        type="submit"
                                        className="btn-save"
                                        disabled={submitting}
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

export default AdminHospitals;