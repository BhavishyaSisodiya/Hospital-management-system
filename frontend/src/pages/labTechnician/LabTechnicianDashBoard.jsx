import { useNavigate } from "react-router-dom";
import MainLayout from "../../layouts/MainLayout";

function LabTechnicianDashBoard() {

    const navigate = useNavigate();

    const modules = [
        {
            title: "Lab Prescriptions & Billing",
            description: "Generate bills for prescribed lab tests.",
            path: "/lab-technician/billing",
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
            description: "Record and manage lab test results.",
            path: "/admin/lab-results",
        },
    ];

    return (
        <MainLayout>
            <div className="dashboard-page">

                <div className="dashboard-header">
                    <h1>Lab Technician Dashboard</h1>
                    <p>
                        Welcome to the Hospital Management System laboratory portal.
                    </p>
                </div>

                <div className="doctor-module-cards">

                    {modules.map((module) => (
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
                    <h2>Laboratory Operations</h2>
                    <p>
                        Manage test types, lab test orders, and results from this
                        dashboard.
                    </p>
                </div>

            </div>
        </MainLayout>
    );
}

export default LabTechnicianDashBoard;