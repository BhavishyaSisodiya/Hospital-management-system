import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import {
    getAdmissions,
} from "../../api/admissions";
import { getPatients } from "../../api/patients";
import { getDoctors } from "../../api/doctors";
import { getBeds } from "../../api/beds";

function ReceptionistAdmissions() {

    const [admissions, setAdmissions] = useState([]);
    const [filteredAdmissions, setFilteredAdmissions] = useState([]);
    const [patients, setPatients] = useState([]);
    const [doctors, setDoctors] = useState([]);
    const [beds, setBeds] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [filterStatus, setFilterStatus] = useState("");


    /* ============================================================
       LOAD DATA
       ============================================================ */

    useEffect(() => {

        const loadData = async () => {

            try {

                setLoading(true);
                setError("");

                const [
                    admissionsData,
                    patientsData,
                    doctorsData,
                    bedsData,
                ] = await Promise.all([
                    getAdmissions(),
                    getPatients(),
                    getDoctors(),
                    getBeds(),
                ]);

                setAdmissions(admissionsData);
                setFilteredAdmissions(admissionsData);
                setPatients(patientsData);
                setDoctors(doctorsData);
                setBeds(bedsData);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Unable to load admissions."
                );

            } finally {

                setLoading(false);

            }
        };

        loadData();

    }, []);


    /* ============================================================
       FILTER
       ============================================================ */

    useEffect(() => {

        let result = admissions;

        if (filterStatus) {

            result = result.filter(
                (a) => a.status === filterStatus
            );

        }

        setFilteredAdmissions(result);

    }, [filterStatus, admissions]);


    /* ============================================================
       LOOKUP HELPERS
       ============================================================ */

    const getPatientName = (patientId) => {

        const patient = patients.find(
            (p) => p.id === patientId
        );

        return patient ? patient.name : `Patient #${patientId}`;

    };

    const getDoctorName = (doctorId) => {

        const doctor = doctors.find(
            (d) => d.id === doctorId
        );

        return doctor
            ? `Dr. ${doctor.name}`
            : `Doctor #${doctorId}`;

    };

    const getBed = (bedId) => {

        const bed = beds.find(
            (b) => b.id === bedId
        );

        return bed;

    };


    /* ============================================================
       RENDER
       ============================================================ */

    const statuses = ["admitted", "discharged", "cancelled"];

    return (
        <MainLayout>
            <div className="appointments-page">

                <div className="appointments-header">
                    <div>
                        <h1>Admissions</h1>
                        <p>
                            View patient admissions and their bed
                            assignments.
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
                        {statuses.map((s) => (
                            <option key={s} value={s}>
                                {s.replace("_", " ")}
                            </option>
                        ))}
                    </select>
                </div>


                {/* ==================================================
                   LOADING
                   ================================================== */}

                {loading && (
                    <p className="loading-message">
                        Loading admissions...
                    </p>
                )}


                {/* ==================================================
                   EMPTY STATE
                   ================================================== */}

                {!loading && filteredAdmissions.length === 0 && (
                    <div className="empty-state">
                        <h2>No Admissions Found</h2>
                        <p>
                            No admissions match your current
                            filter.
                        </p>
                    </div>
                )}


                {/* ==================================================
                   TABLE
                   ================================================== */}

                {!loading && filteredAdmissions.length > 0 && (

                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="admissions-table">
                                <thead>
                                    <tr>
                                        <th>Patient</th>
                                        <th>Doctor</th>
                                        <th>Room</th>
                                        <th>Bed</th>
                                        <th>Admission Date</th>
                                        <th>Discharge Date</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredAdmissions.map(
                                        (admission) => {

                                            const bed = getBed(
                                                admission.bed_id
                                            );

                                            return (
                                                <tr key={admission.id}>
                                                    <td>
                                                        {getPatientName(
                                                            admission.patient_id
                                                        )}
                                                    </td>
                                                    <td>
                                                        {getDoctorName(
                                                            admission.doctor_id
                                                        )}
                                                    </td>
                                                    <td>
                                                        {bed
                                                            ? `Room ${bed.room_id}`
                                                            : `Bed #${admission.bed_id}`}
                                                    </td>
                                                    <td>
                                                        {bed
                                                            ? bed.bed_number
                                                            : "-"}
                                                    </td>
                                                    <td>
                                                        {admission.admission_date}
                                                    </td>
                                                    <td>
                                                        {admission.discharge_date ||
                                                            "-"}
                                                    </td>
                                                    <td>
                                                        <span
                                                            className={`status-badge status-${admission.status}`}
                                                        >
                                                            {admission.status}
                                                        </span>
                                                    </td>
                                                </tr>
                                            );
                                        }
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

export default ReceptionistAdmissions;