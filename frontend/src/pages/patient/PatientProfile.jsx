import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getMyPatientProfile,
    updateMyPatientProfile,
} from "../../api/patients";

function PatientProfile() {

    const [patient, setPatient] = useState(null);

    const [formData, setFormData] = useState({
        name: "",
        date_of_birth: "",
        gender: "",
        phone: "",
        email: "",
        address: "",
    });

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const [isEditing, setIsEditing] = useState(false);


    // ============================================================
    // LOAD PROFILE
    // ============================================================

    useEffect(() => {

        const loadProfile = async () => {

            try {

                const data = await getMyPatientProfile();

                setPatient(data);

                setFormData({
                    name: data.name || "",
                    date_of_birth: data.date_of_birth || "",
                    gender: data.gender || "",
                    phone: data.phone || "",
                    email: data.email || "",
                    address: data.address || "",
                });

            } catch (error) {

                console.error(error);

                if (error.response) {
                    setError(
                        error.response.data?.detail ||
                        "Unable to load patient profile."
                    );
                } else {
                    setError(
                        "Unable to connect to the server."
                    );
                }

            } finally {

                setLoading(false);

            }
        };

        loadProfile();

    }, []);


    // ============================================================
    // HANDLE INPUT CHANGE
    // ============================================================

    const handleChange = (event) => {

        const { name, value } = event.target;

        setFormData((previousData) => ({
            ...previousData,
            [name]: value,
        }));

    };


    // ============================================================
    // START EDITING
    // ============================================================

    const handleEdit = () => {

        setError("");
        setSuccess("");

        setIsEditing(true);

    };


    // ============================================================
    // CANCEL EDITING
    // ============================================================

    const handleCancel = () => {

        setError("");
        setSuccess("");

        setFormData({
            name: patient.name || "",
            date_of_birth: patient.date_of_birth || "",
            gender: patient.gender || "",
            phone: patient.phone || "",
            email: patient.email || "",
            address: patient.address || "",
        });

        setIsEditing(false);

    };


    // ============================================================
    // SAVE PROFILE
    // ============================================================

    const handleSubmit = async (event) => {

        event.preventDefault();

        setError("");
        setSuccess("");
        setSaving(true);

        try {

            const updatedPatient =
                await updateMyPatientProfile(
                    patient.id,
                    formData
                );

            setPatient(updatedPatient);

            setFormData({
                name: updatedPatient.name || "",
                date_of_birth:
                    updatedPatient.date_of_birth || "",
                gender: updatedPatient.gender || "",
                phone: updatedPatient.phone || "",
                email: updatedPatient.email || "",
                address: updatedPatient.address || "",
            });

            setIsEditing(false);

            setSuccess(
                "Profile updated successfully."
            );

        } catch (error) {

            console.error(error);

            if (error.response) {

                setError(
                    error.response.data?.detail ||
                    "Unable to update profile."
                );

            } else {

                setError(
                    "Unable to connect to the server."
                );

            }

        } finally {

            setSaving(false);

        }

    };


    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {

        return (
            <MainLayout>

                <h1>Patient Profile</h1>

                <p>Loading profile...</p>

            </MainLayout>
        );

    }


    // ============================================================
    // ERROR
    // ============================================================

    if (error && !patient) {

        return (
            <MainLayout>

                <h1>Patient Profile</h1>

                <p className="error-message">
                    {error}
                </p>

            </MainLayout>
        );

    }


    // ============================================================
    // PROFILE PAGE
    // ============================================================

    return (

        <MainLayout>

            <div className="profile-page">

                <div className="profile-header">

                    <div>

                        <h1>Patient Profile</h1>

                        <p>
                            View and manage your personal
                            information.
                        </p>

                    </div>

                    {!isEditing && (
                        <button
                            className="edit-profile-btn"
                            onClick={handleEdit}
                        >
                            Edit Profile
                        </button>
                    )}

                </div>


                {success && (
                    <p className="success-message">
                        {success}
                    </p>
                )}


                {error && (
                    <p className="error-message">
                        {error}
                    </p>
                )}


                {!isEditing ? (

                    // ==================================================
                    // VIEW MODE
                    // ==================================================

                    <div className="profile-card">

                        <div className="profile-row">
                            <strong>Patient ID</strong>
                            <span>{patient.id}</span>
                        </div>

                        <div className="profile-row">
                            <strong>Name</strong>
                            <span>{patient.name}</span>
                        </div>

                        <div className="profile-row">
                            <strong>Date of Birth</strong>
                            <span>
                                {patient.date_of_birth ||
                                    "Not provided"}
                            </span>
                        </div>

                        <div className="profile-row">
                            <strong>Gender</strong>
                            <span>{patient.gender}</span>
                        </div>

                        <div className="profile-row">
                            <strong>Phone</strong>
                            <span>{patient.phone}</span>
                        </div>

                        <div className="profile-row">
                            <strong>Email</strong>
                            <span>
                                {patient.email ||
                                    "Not provided"}
                            </span>
                        </div>

                        <div className="profile-row">
                            <strong>Address</strong>
                            <span>
                                {patient.address ||
                                    "Not provided"}
                            </span>
                        </div>

                    </div>

                ) : (

                    // ==================================================
                    // EDIT MODE
                    // ==================================================

                    <form
                        className="profile-card profile-form"
                        onSubmit={handleSubmit}
                    >

                        <div className="form-group">

                            <label htmlFor="name">
                                Name
                            </label>

                            <input
                                id="name"
                                name="name"
                                type="text"
                                value={formData.name}
                                onChange={handleChange}
                                required
                            />

                        </div>


                        <div className="form-group">

                            <label htmlFor="date_of_birth">
                                Date of Birth
                            </label>

                            <input
                                id="date_of_birth"
                                name="date_of_birth"
                                type="date"
                                value={formData.date_of_birth}
                                onChange={handleChange}
                            />

                        </div>


                        <div className="form-group">

                            <label htmlFor="gender">
                                Gender
                            </label>

                            <input
                                id="gender"
                                name="gender"
                                type="text"
                                value={formData.gender}
                                onChange={handleChange}
                                required
                            />

                        </div>


                        <div className="form-group">

                            <label htmlFor="phone">
                                Phone
                            </label>

                            <input
                                id="phone"
                                name="phone"
                                type="text"
                                value={formData.phone}
                                onChange={handleChange}
                                required
                            />

                        </div>


                        <div className="form-group">

                            <label htmlFor="email">
                                Email
                            </label>

                            <input
                                id="email"
                                name="email"
                                type="email"
                                value={formData.email}
                                onChange={handleChange}
                            />

                        </div>


                        <div className="form-group">

                            <label htmlFor="address">
                                Address
                            </label>

                            <textarea
                                id="address"
                                name="address"
                                value={formData.address}
                                onChange={handleChange}
                                rows="4"
                            />

                        </div>


                        <div className="profile-actions">

                            <button
                                type="submit"
                                disabled={saving}
                            >
                                {saving
                                    ? "Saving..."
                                    : "Save Changes"}
                            </button>

                            <button
                                type="button"
                                className="cancel-btn"
                                onClick={handleCancel}
                                disabled={saving}
                            >
                                Cancel
                            </button>

                        </div>

                    </form>

                )}

            </div>

        </MainLayout>
    );
}

export default PatientProfile;