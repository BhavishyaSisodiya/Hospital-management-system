import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../../api/auth";
import { getRole } from "../../api/roles";
import { useAuth } from "../../context/AuthContext";
import { roleDashboardPath, MEMBER_FALLBACK } from "../../utils/roleNav";

function Login() {
    const navigate = useNavigate();

    const { login } = useAuth();

    const [formData, setFormData] = useState({
        email: "",
        password: "",
    });

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (event) => {
        const { name, value } = event.target;

        setFormData((previousData) => ({
            ...previousData,
            [name]: value,
        }));
    };

    const resolveMemberDashboard = async (roleId) => {
        try {
            if (!roleId) {
                return MEMBER_FALLBACK;
            }
            const role = await getRole(roleId);
            return roleDashboardPath(role.name) || MEMBER_FALLBACK;
        } catch (err) {
            console.error(err);
            return MEMBER_FALLBACK;
        }
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        setError("");
        setLoading(true);

        try {
            const data = await loginUser(formData);

            login(
                data.access_token,
                data.account_type,
                data.user_id,
                data.role_id,
                data.name,
                data.role
            );
            if (data.account_type === "patient") {
                navigate("/patient/dashboard");
            } else if (data.account_type === "member") {
                const redirectTo = await resolveMemberDashboard(
                    data.role_id
                );
                navigate(redirectTo);
            } else {
                setError("Unknown account type.");
            }

        } catch (error) {
            console.error(error);

            if (error.response) {
                setError(
                    error.response.data?.detail || "Login failed."
                );
            } else {
                setError("Unable to connect to the server.");
            }

        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-card">

                <h1>Hospital Management System</h1>

                <h2>Login</h2>

                {error && (
                    <p className="error-message">
                        {error}
                    </p>
                )}

                <form onSubmit={handleSubmit}>

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
                            placeholder="Enter your password"
                            required
                        />

                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                    >
                        {loading ? "Logging in..." : "Login"}
                    </button>

                </form>

                <p className="register-link">

                    Don't have an account?{" "}

                    <button
                        type="button"
                        onClick={() => navigate("/register")}
                    >
                        Register
                    </button>

                </p>

            </div>
        </div>
    );
}

export default Login;

