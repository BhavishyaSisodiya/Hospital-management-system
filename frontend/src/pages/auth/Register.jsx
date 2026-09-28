import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerPatient } from "../../api/auth";

function Register() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        name: "",
        email: "",
        password: "",
        date_of_birth: "",
        gender: "",
        phone: "",
        address: "",
    });

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (event) => {
        const { name, value } = event.target;

        setFormData((previousData) => ({
            ...previousData,
            [name]: value,
        }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");
        setSuccess("");
        setLoading(true);

        try {
            const payload = {
                ...formData,
                date_of_birth:
                    formData.date_of_birth || null,
                address: formData.address || null,
            };

            const data = await registerPatient(payload);

            setSuccess(
                data.message ||
                "Patient registered successfully."
            );

            setFormData({
                name: "",
                email: "",
                password: "",
                date_of_birth: "",
                gender: "",
                phone: "",
                address: "",
            });

        } catch (error) {
            console.error(error);

            setError(
                error.response?.data?.detail ||
                "Registration failed."
            );

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-card register-card">

                <h1>Hospital Management System</h1>

                <h2>Patient Registration</h2>

                <p className="register-intro">
                    Create a patient account to book appointments,
                    view medical records, and manage your billing.
                </p>

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

                {success ? (
                    <div className="register-success-actions">
                        <button
                            type="button"
                            onClick={() => navigate("/login")}
                        >
                            Go to Login
                        </button>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit}>

                        <div className="form-group">
                            <label htmlFor="name">
                                Full Name
                            </label>
                            <input
                                id="name"
                                name="name"
                                type="text"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="Enter your full name"
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
                                placeholder="Enter your email"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">
                                Password
                            </label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="At least 8 characters"
                                minLength={8}
                                required
                            />
                        </div>

                        <div className="form-row">

                            <div className="form-group">
                                <label htmlFor="gender">
                                    Gender
                                </label>
                                <select
                                    id="gender"
                                    name="gender"
                                    value={formData.gender}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="">
                                        Select gender
                                    </option>
                                    <option value="Male">
                                        Male
                                    </option>
                                    <option value="Female">
                                        Female
                                    </option>
                                    <option value="Other">
                                        Other
                                    </option>
                                </select>
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

                        </div>

                        <div className="form-group">
                            <label htmlFor="phone">
                                Phone
                            </label>
                            <input
                                id="phone"
                                name="phone"
                                type="tel"
                                value={formData.phone}
                                onChange={handleChange}
                                placeholder="Enter contact number"
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="address">
                                Address
                            </label>
                            <textarea
                                id="address"
                                name="address"
                                rows="2"
                                value={formData.address}
                                onChange={handleChange}
                                placeholder="Enter your address (optional)"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                        >
                            {loading
                                ? "Registering..."
                                : "Register"}
                        </button>

                    </form>
                )}

                <p className="register-link">

                    Already have an account?{" "}

                    <button
                        type="button"
                        onClick={() => navigate("/login")}
                    >
                        Login
                    </button>

                </p>

            </div>
        </div>
    );
}

export default Register;