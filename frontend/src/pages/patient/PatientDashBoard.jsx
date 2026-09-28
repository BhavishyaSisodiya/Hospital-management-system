import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { getPatientDashboardStats } from "../../api/dashboard";

function PatientDashboard() {

    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadStats = async () => {
            try {
                setLoading(true);
                setError("");
                const data = await getPatientDashboardStats();
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

            <div className="dashboard">

                <div className="dashboard-header">
                    <h1>Patient Dashboard</h1>

                    <p>
                        Welcome to the Hospital Management System.
                    </p>
                </div>


                <div className="dashboard-cards">

                    <div className="dashboard-card">
                        <h3>Appointments</h3>
                        <p>{stats?.appointments ?? 0}</p>
                        <span>Your appointments</span>
                    </div>


                    <div className="dashboard-card">
                        <h3>Medical Records</h3>
                        <p>{stats?.medical_records ?? 0}</p>
                        <span>Your medical records</span>
                    </div>


                    <div className="dashboard-card">
                        <h3>Lab Results</h3>
                        <p>{stats?.lab_results ?? 0}</p>
                        <span>Available lab results</span>
                    </div>


                    <div className="dashboard-card">
                        <h3>Prescriptions</h3>
                        <p>{stats?.prescriptions ?? 0}</p>
                        <span>Active prescriptions</span>
                    </div>

                </div>


                <div className="dashboard-section">

                    <h2>Quick Information</h2>

                    <p>
                        Your appointments, medical records,
                        laboratory results and prescriptions
                        appear here.
                    </p>

                </div>

            </div>

        </MainLayout>
    );
}

export default PatientDashboard;

// ### Step 2 — Why are we using `0`?

// Don't worry about the `0`.

// Currently this is **static UI**:

// ```text
// Appointments      0
// Medical Records   0
// Lab Results       0
// Prescriptions     0
// ````

// Later we'll replace those numbers with actual data from your FastAPI backend.

// For example:

// ```text
// FastAPI
//    ↓
// GET /appointments/patient/...
//    ↓
// React
//    ↓
// Appointments: 3
// ```

// So we're deliberately separating:

// **Phase 1**

// ```text
// Build UI
// ```

// from

// **Phase 2**

// ```text
// Connect UI → FastAPI → PostgreSQL
// ```

// ---

// ## Step 3 — Update `AppRoutes.jsx`

// Import the dashboard:

// ```jsx
// import PatientDashboard from "../pages/patient/PatientDashboard";
// ```

// Then replace your current patient dashboard route with:

// ```jsx
// <Route
//     path="/patient/dashboard"
//     element={
//         <ProtectedRoute
//             allowedAccountTypes={["patient"]}
//         >
//             <PatientDashboard />
//         </ProtectedRoute>
//     }
// />
// ```

// Now the flow is:

// ```text
// Login
//   ↓
// account_type = patient
//   ↓
// /patient/dashboard
//   ↓
// ProtectedRoute
//   ↓
// PatientDashboard
//   ↓
// MainLayout
//   ├── Navbar
//   ├── Sidebar
//   └── Dashboard
// ```

// ---

// ## Step 4 — Add dashboard CSS

// Open:

// ```text
// src/styles/global.css
// ```

// Add:

// ```css
// .dashboard {
//     width: 100%;
// }

// .dashboard-header {
//     margin-bottom: 30px;
// }

// .dashboard-header h1 {
//     margin-bottom: 8px;
// }

// .dashboard-header p {
//     color: #6b7280;
// }

// .dashboard-cards {
//     display: grid;
//     grid-template-columns: repeat(4, 1fr);
//     gap: 20px;
// }

// .dashboard-card {
//     background-color: white;
//     padding: 24px;
//     border-radius: 10px;
//     box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
// }

// .dashboard-card h3 {
//     margin-bottom: 15px;
// }

// .dashboard-card p {
//     font-size: 32px;
//     font-weight: bold;
//     margin-bottom: 8px;
// }

// .dashboard-card span {
//     color: #6b7280;
//     font-size: 14px;
// }

// .dashboard-section {
//     background-color: white;
//     margin-top: 25px;
//     padding: 24px;
//     border-radius: 10px;
// }

// .dashboard-section h2 {
//     margin-bottom: 12px;
// }

// .dashboard-section p {
//     color: #6b7280;
// }
// ```

// ### What you should see

// After logging in as a patient:

// ```text
// ┌──────────────────────────────────────────────────────┐
// │ 🏥 HMS                         Patient      Logout     │
// ├───────────────┬──────────────────────────────────────┤
// │ Hospital      │                                      │
// │ Management    │  Patient Dashboard                   │
// │               │  Welcome to the Hospital...          │
// │ Dashboard     │                                      │
// │ Appointments  │  ┌──────────┐ ┌──────────┐           │
// │ Doctors       │  │Appointments│ │ Records │           │
// │ Records       │  │     0     │ │    0    │           │
// │ Lab Results   │  └──────────┘ └──────────┘           │
// │ Prescriptions │                                      │
// │ Billing       │  ┌──────────┐ ┌──────────┐           │
// │ Payments      │  │Lab Results│ │Prescriptions│        │
// │               │  │     0     │ │    0     │           │
// └───────────────┴──────────────────────────────────────┘
// ```

// Don't connect the cards to the backend yet. **First make sure this UI renders correctly.**

// Once this works, the next step is to create the **Patient Profile page and connect it to your actual `PatientDB` API**.
