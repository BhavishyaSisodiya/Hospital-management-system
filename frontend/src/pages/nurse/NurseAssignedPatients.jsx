import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { useAuth } from "../../context/AuthContext";
import {
    getNurseAssignmentsByNurse,
} from "../../api/nurseAssignments";
import { getAdmission } from "../../api/admissions";

function NurseAssignedPatients() {

    const { userId } = useAuth();

    const [assignments, setAssignments] = useState([]);
    const [enriched, setEnriched] = useState([]);
    const [filtered, setFiltered] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [filterStatus, setFilterStatus] = useState("");


    /* ============================================================
       LOAD ASSIGNMENTS
       ============================================================ */

    useEffect(() => {

        const loadAssignments = async () => {

            try {

                setLoading(true);
                setError("");

                const assignmentsData =
                    await getNurseAssignmentsByNurse(userId);

                const enrichedData = await Promise.all(
                    assignmentsData.map(async (assignment) => {

                        try {

                            const admission =
                                await getAdmission(
                                    assignment.admission_id
                                );

                            return {
                                ...assignment,
                                patient_name:
                                    admission.patient_id
                                        ? `Patient #${admission.patient_id}`
                                        : "-",
                                admission_status:
                                    admission.status || "-",
                                admission_date:
                                    admission.admission_date || "-",
                                doctor_id:
                                    admission.doctor_id || "-",
                            };

                        } catch {

                            return {
                                ...assignment,
                                patient_name: "Unknown",
                                admission_status: "Unknown",
                                admission_date: "-",
                                doctor_id: "-",
                            };

                        }

                    })
                );

                setAssignments(assignmentsData);
                setEnriched(enrichedData);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Unable to load assignments."
                );

            } finally {

                setLoading(false);

            }
        };

        if (userId) {
            loadAssignments();
        }

    }, [userId]);


    /* ============================================================
       FILTER
       ============================================================ */

    useEffect(() => {

        let result = enriched;

        if (filterStatus) {

            if (filterStatus === "active") {

                result = result.filter(
                    (a) => a.unassigned_at === null
                );

            } else if (filterStatus === "inactive") {

                result = result.filter(
                    (a) => a.unassigned_at !== null
                );

            }

        }

        setFiltered(result);

    }, [filterStatus, enriched]);


    /* ============================================================
       RENDER
       ============================================================ */

    return (
        <MainLayout>
            <div className="appointments-page">

                <div className="appointments-header">
                    <div>
                        <h1>Assigned Patients</h1>
                        <p>
                            Patients currently under your care.
                        </p>
                    </div>
                </div>


                {error && (
                    <p className="error-message">{error}</p>
                )}


                {/* ==================================================
                   FILTER
                   ================================================== */}

                <div className="filter-row">
                    <label htmlFor="status-filter">
                        Status:
                    </label>
                    <select
                        id="status-filter"
                        className="form-select"
                        value={filterStatus}
                        onChange={(e) =>
                            setFilterStatus(e.target.value)
                        }
                    >
                        <option value="">All</option>
                        <option value="active">Active</option>
                        <option value="inactive">
                            Inactive
                        </option>
                    </select>
                </div>


                {/* ==================================================
                   LOADING
                   ================================================== */}

                {loading && (
                    <p className="loading-message">
                        Loading assignments...
                    </p>
                )}


                {/* ==================================================
                   EMPTY STATE
                   ================================================== */}

                {!loading && filtered.length === 0 && (
                    <div className="empty-state">
                        <h2>No Assignments</h2>
                        <p>
                            You have no patient assignments at
                            this time.
                        </p>
                    </div>
                )}


                {/* ==================================================
                   TABLE
                   ================================================== */}

                {!loading && filtered.length > 0 && (

                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Patient</th>
                                        <th>
                                            Admission ID
                                        </th>
                                        <th>
                                            Assigned Date
                                        </th>
                                        <th>
                                            Admission Status
                                        </th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filtered.map(
                                        (assignment) => (
                                            <tr
                                                key={assignment.id}
                                            >
                                                <td>
                                                    {
                                                        assignment.patient_name
                                                    }
                                                </td>
                                                <td>
                                                    {
                                                        assignment.admission_id
                                                    }
                                                </td>
                                                <td>
                                                    {new Date(
                                                        assignment.assigned_at
                                                    ).toLocaleDateString()}
                                                </td>
                                                <td>
                                                    <span
                                                        className={`status-badge status-${assignment.admission_status}`}
                                                    >
                                                        {
                                                            assignment.admission_status
                                                        }
                                                    </span>
                                                </td>
                                                <td>
                                                    <span
                                                        className={`status-badge ${
                                                            assignment.unassigned_at ===
                                                            null
                                                                ? "status-scheduled"
                                                                : "status-completed"
                                                        }`}
                                                    >
                                                        {assignment.unassigned_at ===
                                                        null
                                                            ? "Active"
                                                            : "Inactive"}
                                                    </span>
                                                </td>
                                            </tr>
                                        )
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                )}

            </div>
        </MainLayout>
    );
}

export default NurseAssignedPatients;
