
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function formatRole(role) {
    if (!role) return "";

    return role
        .replace(/_/g, " ")
        .replace(/\b\w/g, (ch) => ch.toUpperCase());
}

function Navbar() {

    const navigate = useNavigate();

    const {
        accountType,
        userName,
        roleName,
        logout,
    } = useAuth();

    const handleLogout = () => {

        logout();

        navigate("/login", {
            replace: true,
        });
    };

    const displayName =
        userName ||
        (accountType === "patient" ? "Patient" : "Member");

    const displayRole =
        accountType === "patient"
            ? "Patient"
            : formatRole(roleName);

    return (
        <header className="navbar">

            <div className="navbar-brand">
                🏥 HMS
            </div>

            <div className="navbar-right">

                <span className="user-name">
                    {displayName}
                    {displayRole ? (
                        <span className="user-role">
                            {" · "}
                            {displayRole}
                        </span>
                    ) : null}
                </span>

                <button
                    className="logout-btn"
                    onClick={handleLogout}
                >
                    Logout
                </button>

            </div>

        </header>
    );
}

export default Navbar;