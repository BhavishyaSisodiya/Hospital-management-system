import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { useNavigate } from "react-router-dom";
import { getDashboardStats } from "../../api/dashboard";

function AdminDashBoard() {

    const navigate = useNavigate();

    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadStats = async () => {
            try {
                setLoading(true);
                setError("");
                const data = await getDashboardStats();
                setStats(data);
            } catch (err) {
                console.error(err);
                if (err.response) {
                    setError(
                        err.response.data?.detail ||
                        "Unable to load dashboard stats."
                    );
                } else {
                    setError("Unable to connect to the server.");
                }
            } finally {
                setLoading(false);
            }
        };

        loadStats();
    }, []);

    const adminModules = [
        {
            title: "Employees",
            description: "Manage hospital staff and employee records.",
            path: "/admin/employees",
        },
        {
            title: "Doctors",
            description: "View and manage all doctors across departments.",
            path: "/admin/doctors",
        },
        {
            title: "Patients",
            description: "View and manage all patient records.",
            path: "/admin/patients",
        },
        {
            title: "Departments",
            description: "Manage hospital departments and assignments.",
            path: "/admin/departments",
        },
        {
            title: "Appointments",
            description: "View and manage all scheduled appointments.",
            path: "/admin/appointments",
        },
        {
            title: "Admissions",
            description: "Manage patient admissions and discharges.",
            path: "/admin/admissions",
        },
        {
            title: "Rooms / Beds",
            description: "Manage hospital rooms and bed allocations.",
            path: "/admin/rooms",
        },
        {
            title: "Nurse Assignments",
            description: "View and manage nurse-to-patient assignments.",
            path: "/admin/nurse-assignments",
        },
        {
            title: "Test Types",
            description: "Manage available laboratory test types.",
            path: "/admin/test-types",
        },
        {
            title: "Lab Tests",
            description: "View and manage all lab test orders.",
            path: "/admin/lab-tests",
        },
        {
            title: "Lab Results",
            description: "Review and manage lab test results.",
            path: "/admin/lab-results",
        },
        {
            title: "Medicines",
            description: "Manage medicine inventory and stock.",
            path: "/admin/medicines",
        },
        {
            title: "Pharmacies",
            description: "Manage pharmacy locations and details.",
            path: "/admin/pharmacies",
        },
        {
            title: "Invoices",
            description: "View and manage billing invoices.",
            path: "/admin/invoices",
        },
        {
            title: "Payments",
            description: "Track and manage patient payments.",
            path: "/admin/payments",
        },
    ];

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <p className="loading-message">Loading dashboard...</p>
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

                <div className="dashboard-header">
                    <h1>Admin Dashboard</h1>
                    <p>
                        Welcome to the Hospital Management System admin panel.
                    </p>
                </div>

                <div className="dashboard-cards">

                    <div className="dashboard-card">
                        <h3>Patients</h3>
                        <p>{stats?.total_patients ?? 0}</p>
                        <span>Total registered patients</span>
                    </div>

                    <div className="dashboard-card">
                        <h3>Doctors</h3>
                        <p>{stats?.total_doctors ?? 0}</p>
                        <span>Active doctors</span>
                    </div>

                    <div className="dashboard-card">
                        <h3>Appointments</h3>
                        <p>{stats?.total_appointments ?? 0}</p>
                        <span>Total appointments</span>
                    </div>

                    <div className="dashboard-card">
                        <h3>Departments</h3>
                        <p>{stats?.total_departments ?? 0}</p>
                        <span>Hospital departments</span>
                    </div>

                </div>

                <div className="doctor-module-cards">

                    {adminModules.map((module) => (
                        <div
                            key={module.title}
                            className="doctor-module-card"
                            onClick={() => navigate(module.path)}
                        >
                            <div className="doctor-module-icon">
                                {module.title.charAt(0)}
                            </div>
                            <h3>{module.title}</h3>
                            <p>{module.description}</p>
                            <button
                                type="button"
                                onClick={(event) => {
                                    event.stopPropagation();
                                    navigate(module.path);
                                }}
                            >
                                Open
                            </button>
                        </div>
                    ))}

                </div>

                <div className="dashboard-section">
                    <h2>Admin Information</h2>
                    <p>
                        Manage all hospital operations from this dashboard.
                        Use the module cards above to navigate to specific sections.
                    </p>
                </div>

            </div>
        </MainLayout>
    );
}

export default AdminDashBoard;
