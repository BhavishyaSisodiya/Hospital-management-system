import { useNavigate } from "react-router-dom";

function Home() {
    const navigate = useNavigate();

    return (
        <div className="home-page">
            <div className="home-hero">
                <h1 className="home-title">Hospital Management System</h1>
                <p className="home-subtitle">
                    Manage patients, doctors, appointments, and billing — all in one place.
                </p>
                <div className="home-actions">
                    <button
                        className="btn-primary"
                        onClick={() => navigate("/login")}
                    >
                        Login
                    </button>
                    <button
                        className="btn-secondary"
                        onClick={() => navigate("/register")}
                    >
                        Patient Registration
                    </button>
                </div>
            </div>

            <div className="home-features">
                <div className="home-feature-card">
                    <h3>Patients</h3>
                    <p>Register patients, view medical records, lab results and vitals.</p>
                </div>
                <div className="home-feature-card">
                    <h3>Doctors</h3>
                    <p>Manage doctor schedules, appointments, prescriptions and departments.</p>
                </div>
                <div className="home-feature-card">
                    <h3>Staff & Billing</h3>
                    <p>Admissions, nurse assignments, pharmacy stock, invoices and payments.</p>
                </div>
            </div>
        </div>
    );
}

export default Home;