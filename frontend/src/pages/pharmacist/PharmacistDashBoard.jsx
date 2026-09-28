import { useNavigate } from "react-router-dom";
import MainLayout from "../../layouts/MainLayout";

function PharmacistDashBoard() {

    const navigate = useNavigate();

    const modules = [
        {
            title: "Medicines",
            description: "View and manage the medicine catalogue.",
            path: "/admin/medicines",
        },
        {
            title: "Medicine Batches",
            description: "Track medicine batches and expiry details.",
            path: "/admin/medicine-batches",
        },
        {
            title: "Pharmacies",
            description: "Manage pharmacy locations and details.",
            path: "/admin/pharmacies",
        },
        {
            title: "Pharmacy Stock",
            description: "Monitor and manage pharmacy stock levels.",
            path: "/admin/pharmacy-stock",
        },
    ];

    return (
        <MainLayout>
            <div className="dashboard-page">

                <div className="dashboard-header">
                    <h1>Pharmacist Dashboard</h1>
                    <p>
                        Welcome to the Hospital Management System pharmacy portal.
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
                    <h2>Pharmacy Operations</h2>
                    <p>
                        Manage medicines, batches, pharmacies, and stock levels
                        from this dashboard.
                    </p>
                </div>

            </div>
        </MainLayout>
    );
}

export default PharmacistDashBoard;