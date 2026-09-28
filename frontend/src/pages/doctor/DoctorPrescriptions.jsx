import { useEffect, useState } from "react";

import { useNavigate } from "react-router-dom";

import MainLayout from "../../layouts/MainLayout";

import {
    getMyDoctorPrescriptions,
} from "../../api/prescriptions";


function DoctorPrescriptions() {

    const navigate = useNavigate();

    const [prescriptions, setPrescriptions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    useEffect(() => {

        const loadPrescriptions = async () => {

            try {

                setLoading(true);
                setError("");

                const data =
                    await getMyDoctorPrescriptions();

                setPrescriptions(data);

            } catch (error) {

                console.error(error);

                setError(
                    error.response?.data?.detail ||
                    "Unable to load prescriptions."
                );

            } finally {

                setLoading(false);

            }
        };

        loadPrescriptions();

    }, []);


    return (

        <MainLayout>

            <div className="prescriptions-page">

                <div className="prescriptions-header">

                    <div>

                        <h1>Prescriptions</h1>

                        <p>
                            View and manage prescriptions
                            created for your patients.
                        </p>

                    </div>


                    <button
                        type="button"
                        onClick={() =>
                            navigate(
                                "/doctor/prescriptions/create"
                            )
                        }
                    >
                        Create Prescription
                    </button>

                </div>


                {loading && (

                    <div className="empty-state">

                        <p>
                            Loading prescriptions...
                        </p>

                    </div>

                )}


                {!loading && error && (

                    <div className="empty-state">

                        <h2>
                            Unable to Load Prescriptions
                        </h2>

                        <p>{error}</p>

                    </div>

                )}


                {!loading &&
                    !error &&
                    prescriptions.length === 0 && (

                        <div className="empty-state">

                            <h2>
                                No Prescriptions
                            </h2>

                            <p>
                                You have not created any
                                prescriptions yet.
                            </p>

                        </div>

                    )}


                {!loading &&
                    !error &&
                    prescriptions.length > 0 && (

                        <div className="appointments-table-container">

                            <table className="appointments-table">

                                <thead>

                                    <tr>

                                        <th>ID</th>
                                        <th>Patient ID</th>
                                        <th>Doctor ID</th>
                                        <th>Pharmacy ID</th>
                                        <th>Date</th>
                                        <th>Action</th>

                                    </tr>

                                </thead>


                                <tbody>

                                    {prescriptions.map(
                                        (prescription) => (

                                            <tr
                                                key={
                                                    prescription.id
                                                }
                                            >

                                                <td>
                                                    {
                                                        prescription.id
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        prescription.patient_id
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        prescription.doctor_id
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        prescription.pharmacy_id ??
                                                        "-"
                                                    }
                                                </td>

                                                <td>
                                                    {
                                                        prescription.prescription_date
                                                    }
                                                </td>

                                                <td>

                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            navigate(
                                                                `/doctor/prescriptions/${prescription.id}`
                                                            )
                                                        }
                                                    >
                                                        View
                                                    </button>

                                                </td>

                                            </tr>

                                        )
                                    )}

                                </tbody>

                            </table>

                        </div>

                    )}

            </div>

        </MainLayout>

    );
}


export default DoctorPrescriptions;