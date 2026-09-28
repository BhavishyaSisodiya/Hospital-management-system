import MainLayout from "../../layouts/MainLayout";
import { useNavigate } from "react-router-dom";

function NurseDashBoard() {

    const navigate = useNavigate();

    const modules = [
        {
            title: "Assigned Patients",
            description:
                "View patients currently assigned to you.",
            path: "/nurse/assigned-patients",
        },
        {
            title: "Record Vitals",
            description:
                "Record vital signs for admitted patients.",
            path: "/nurse/record-vitals",
        },
    ];

    return (
        <MainLayout>
            <div className="dashboard-page">

                <div className="dashboard-header">
                    <h1>Nurse Dashboard</h1>
                    <p>
                        View your assigned patients and record
                        vitals.
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
                        Use the cards above to access your
                        nursing modules.
                    </p>
                </div>

            </div>
        </MainLayout>
    );
}

export default NurseDashBoard;
