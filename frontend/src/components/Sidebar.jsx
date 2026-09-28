import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getRoles } from "../api/roles";

function Sidebar() {

    const { accountType, roleId } = useAuth();

    const [roleName, setRoleName] = useState(null);

    useEffect(() => {
        if (accountType === "member" && roleId) {
            const fetchRole = async () => {
                try {
                    const roles = await getRoles();
                    const matched = roles.find(
                        (r) => r.id === Number(roleId)
                    );
                    if (matched) {
                        setRoleName(matched.name);
                    }
                } catch (err) {
                    console.error("Failed to fetch role:", err);
                }
            };
            fetchRole();
        }
    }, [accountType, roleId]);

    const menus = {

        patient: [
            { label: "Dashboard", path: "/patient/dashboard" },
            { label: "Profile", path: "/patient/profile" },
            { label: "Appointments", path: "/patient/appointments" },
            { label: "Doctors", path: "/patient/doctors" },
            { label: "Medical Records", path: "/patient/records" },
            { label: "Lab Results", path: "/patient/lab-results" },
            { label: "Prescriptions", path: "/patient/prescriptions" },
            { label: "Vitals", path: "/patient/vitals" },
            { label: "Admissions", path: "/patient/admissions" },
            { label: "Billing", path: "/patient/billing" },
            { label: "Payments", path: "/patient/payments" },
        ],

        member: [
            { label: "Dashboard", path: "/member/dashboard" },
            { label: "Doctor Schedule", path: "/doctor/schedule" },
        ],

        admin: [
            { label: "Dashboard", path: "/admin/dashboard" },
            { label: "Hospitals", path: "/admin/hospitals" },
            { label: "Employees", path: "/admin/employees" },
            { label: "Doctors", path: "/admin/doctors" },
            { label: "Patients", path: "/admin/patients" },
            { label: "Departments", path: "/admin/departments" },
            { label: "Appointments", path: "/admin/appointments" },
            { label: "Admissions", path: "/admin/admissions" },
            { label: "Rooms", path: "/admin/rooms" },
            { label: "Beds", path: "/admin/beds" },
            { label: "Nurse Assignments", path: "/admin/nurse-assignments" },
            { label: "Test Types", path: "/admin/test-types" },
            { label: "Lab Tests", path: "/admin/lab-tests" },
            { label: "Lab Results", path: "/admin/lab-results" },
            { label: "Medicines", path: "/admin/medicines" },
            { label: "Medicine Batches", path: "/admin/medicine-batches" },
            { label: "Pharmacies", path: "/admin/pharmacies" },
            { label: "Pharmacy Stock", path: "/admin/pharmacy-stock" },
            { label: "Invoices", path: "/admin/invoices" },
            { label: "Invoice Items", path: "/admin/invoice-items" },
            { label: "Payments", path: "/admin/payments" },
        ],

        doctor: [
            { label: "Dashboard", path: "/doctor/dashboard" },
            { label: "Appointments", path: "/doctor/appointments" },
            { label: "Patients", path: "/doctor/patients" },
            { label: "Medical Records", path: "/doctor/medical-records" },
            { label: "Prescriptions", path: "/doctor/prescriptions" },
            { label: "Schedule", path: "/doctor/schedule" },
        ],

        nurse: [
            { label: "Dashboard", path: "/nurse/dashboard" },
            { label: "Assigned Patients", path: "/nurse/assigned-patients" },
            { label: "Record Vitals", path: "/nurse/record-vitals" },
        ],

        receptionist: [
            { label: "Dashboard", path: "/receptionist/dashboard" },
            { label: "Patients", path: "/receptionist/patients" },
            { label: "Appointments", path: "/receptionist/appointments" },
            { label: "Admissions", path: "/receptionist/admissions" },
            { label: "Billing", path: "/receptionist/billing" },
        ],

        pharmacist: [
            { label: "Dashboard", path: "/pharmacist/dashboard" },
            { label: "Prescriptions & Billing", path: "/pharmacist/billing" },
            { label: "Medicines", path: "/admin/medicines" },
            { label: "Medicine Batches", path: "/admin/medicine-batches" },
            { label: "Pharmacies", path: "/admin/pharmacies" },
            { label: "Pharmacy Stock", path: "/admin/pharmacy-stock" },
        ],

        lab_technician: [
            { label: "Dashboard", path: "/lab-technician/dashboard" },
            { label: "Lab Prescriptions & Billing", path: "/lab-technician/billing" },
            { label: "Test Types", path: "/admin/test-types" },
            { label: "Lab Tests", path: "/admin/lab-tests" },
            { label: "Lab Results", path: "/admin/lab-results" },
        ],

        accountant: [
            { label: "Dashboard", path: "/accountant/dashboard" },
            { label: "Invoices", path: "/admin/invoices" },
            { label: "Invoice Items", path: "/admin/invoice-items" },
            { label: "Payments", path: "/admin/payments" },
        ],
    };

    let currentMenu;

    if (accountType === "patient") {
        currentMenu = menus.patient;
    } else if (accountType === "member" && roleName) {
        currentMenu = menus[roleName] || menus.member;
    } else {
        currentMenu = menus.member;
    }

    return (
        <aside className="sidebar">

            <h2 className="sidebar-title">
                Hospital Management
            </h2>

            <nav>
                {currentMenu.map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                    >
                        {item.label}
                    </Link>
                ))}
            </nav>

        </aside>
    );
}

export default Sidebar;
