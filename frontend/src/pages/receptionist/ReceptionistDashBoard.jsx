import MainLayout from "../../layouts/MainLayout";
import { useNavigate } from "react-router-dom";

function ReceptionistDashBoard() {

    const navigate = useNavigate();

    const modules = [
        {
            title: "Patients",
            description: "Manage patient records and information.",
            path: "/receptionist/patients",
        },
        {
            title: "Appointments",
            description: "Schedule and manage patient appointments.",
            path: "/receptionist/appointments",
        },
        {
            title: "Admissions",
            description: "Manage patient admissions and discharges.",
            path: "/admin/admissions",
        },
    ];

    return (
        <MainLayout>
            <div className="dashboard-page">

                <div className="dashboard-header">
                    <h1>Receptionist Dashboard</h1>
                    <p>
                        Manage patients, appointments, and admissions.
                    </p>
                </div>

                <div className="dashboard-cards">
                    {modules.map((module) => (
                        <div
                            key={module.title}
                            className="dashboard-card"
                            onClick={() => navigate(module.path)}
                            style={{ cursor: "pointer" }}
                        >
                            <h3>{module.title}</h3>
                            <p>{module.description}</p>
                        </div>
                    ))}
                </div>

                <div className="dashboard-section">
                    <h2>Quick Actions</h2>
                    <p>
                        Use the cards above to navigate to the
                        different modules you manage.
                    </p>
                </div>

            </div>
        </MainLayout>
    );
}

export default ReceptionistDashBoard;
