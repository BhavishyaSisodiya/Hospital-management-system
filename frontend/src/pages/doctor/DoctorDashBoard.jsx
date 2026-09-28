import MainLayout from "../../layouts/MainLayout";
import { useNavigate } from "react-router-dom";

function DoctorDashBoard() {

    const navigate = useNavigate();

    const doctorModules = [
        {
            title: "My Appointments",
            description: "View and manage appointments assigned to you.",
            path: "/doctor/appointments",
        },
        {
            title: "My Patients",
            description: "View patients who are under your care.",
            path: "/doctor/patients",
        },
        {
            title: "Medical Records",
            description: "View and manage medical records of your patients.",
            path: "/doctor/medical-records",
        },
        {
            title: "Prescriptions",
            description: "Create and manage prescriptions for your patients.",
            path: "/doctor/prescriptions",
        },
    ];

    return (
        <MainLayout>
            <div className="dashboard-page">

                <div className="dashboard-header">
                    <h1>Doctor Portal</h1>

                    <p>
                        Manage your patients and clinical activities.
                    </p>

                    <p>
                        All information shown here will belong to the
                        authenticated doctor.
                    </p>
                </div>

                <div className="doctor-module-cards">

                    {doctorModules.map((module) => (
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
                    <h2>Doctor Information</h2>

                    <p>
                        Your personal doctor information and statistics
                        will appear here.
                    </p>
                </div>

            </div>
        </MainLayout>
    );
}

export default DoctorDashBoard;