import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import MainLayout from "../../layouts/MainLayout";
import { getRole } from "../../api/roles";
import { roleDashboardPath } from "../../utils/roleNav";

function MemberDashboard() {

    const navigate = useNavigate();
    const { accountType, roleId } = useAuth();

    const [resolving, setResolving] = useState(true);
    const [unknownRole, setUnknownRole] = useState(false);

    const roles = [
        {
            title: "Doctor",
            description: "Access doctor portal and manage your patients, appointments, medical records, and prescriptions.",
            path: "/doctor/dashboard",
        },
        {
            title: "Nurse",
            description: "Access nursing portal and manage assigned patient care activities.",
            path: "/nurse/dashboard",
        },
        {
            title: "Admin",
            description: "Access administrative portal and manage hospital operations.",
            path: "/admin/dashboard",
        },
        {
            title: "Receptionist",
            description: "Access reception portal and manage appointments and patient services.",
            path: "/receptionist/dashboard",
        },
    ];

    /* ============================================================
       AUTO-REDIRECT: members go straight to their role dashboard.
       Role cards are only a fallback for roles without a mapped
       dashboard (pharmacist, lab technician, accountant).
       ============================================================ */

    useEffect(() => {
        if (accountType !== "member") {
            navigate("/patient/dashboard", { replace: true });
            return;
        }

        const resolveRole = async () => {
            try {
                if (!roleId) {
                    setUnknownRole(true);
                    setResolving(false);
                    return;
                }

                const role = await getRole(roleId);

                const path = roleDashboardPath(role.name);

                if (path) {
                    navigate(path, { replace: true });
                    return;
                }

                setUnknownRole(true);
                setResolving(false);
            } catch (err) {
                console.error(err);
                setUnknownRole(true);
                setResolving(false);
            }
        };

        resolveRole();
    }, [accountType, roleId, navigate]);

    if (resolving) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <p className="loading-message">
                        Loading dashboard...
                    </p>
                </div>
            </MainLayout>
        );
    }

    if (!unknownRole) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <p className="loading-message">
                        Redirecting...
                    </p>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="dashboard-page">

                <div className="dashboard-header">
                    <h1>Member Dashboard</h1>

                    <p>
                        Welcome to the Hospital Management System.
                    </p>

                    <p>
                        Select a role portal to continue.
                    </p>
                </div>

                <div className="member-role-cards">

                    {roles.map((role) => (
                        <div
                            key={role.title}
                            className="member-role-card"
                            onClick={() => navigate(role.path)}
                        >
                            <div className="member-role-icon">
                                {role.title.charAt(0)}
                            </div>

                            <h3>{role.title}</h3>

                            <p>
                                {role.description}
                            </p>

                            <button
                                type="button"
                                onClick={(event) => {
                                    event.stopPropagation();
                                    navigate(role.path);
                                }}
                            >
                                Open Portal
                            </button>
                        </div>
                    ))}

                </div>

            </div>
        </MainLayout>
    );
}

export default MemberDashboard;