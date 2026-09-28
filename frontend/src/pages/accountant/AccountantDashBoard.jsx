import { useNavigate } from "react-router-dom";
import MainLayout from "../../layouts/MainLayout";

function AccountantDashBoard() {

    const navigate = useNavigate();

    const modules = [
        {
            title: "Invoices",
            description: "View and manage billing invoices.",
            path: "/admin/invoices",
        },
        {
            title: "Invoice Items",
            description: "Manage line items on patient invoices.",
            path: "/admin/invoice-items",
        },
        {
            title: "Payments",
            description: "Track and manage patient payments.",
            path: "/admin/payments",
        },
    ];

    return (
        <MainLayout>
            <div className="dashboard-page">

                <div className="dashboard-header">
                    <h1>Accountant Dashboard</h1>
                    <p>
                        Welcome to the Hospital Management System accounting portal.
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
                    <h2>Billing Operations</h2>
                    <p>
                        Manage invoices, invoice items, and payments from this
                        dashboard.
                    </p>
                </div>

            </div>
        </MainLayout>
    );
}

export default AccountantDashBoard;