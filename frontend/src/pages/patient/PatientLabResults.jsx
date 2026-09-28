import { useEffect, useState } from "react";

import MainLayout from "../../layouts/MainLayout";

import { getMyPatientProfile } from "../../api/patients";
import { getPatientLabResults } from "../../api/labResults";

function PatientLabResults() {
    const [results, setResults] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadLabResults = async () => {
            try {
                // Get logged-in patient's profile
                const patient = await getMyPatientProfile();

                // Get patient's lab results
                const data =
                    await getPatientLabResults(patient.id);

                setResults(data);
            } catch (error) {
                console.error(error);

                if (error.response) {
                    setError(
                        error.response.data?.detail ||
                        "Unable to load lab results."
                    );
                } else {
                    setError(
                        "Unable to connect to the server."
                    );
                }
            } finally {
                setLoading(false);
            }
        };

        loadLabResults();
    }, []);

    // ============================================================
    // LOADING
    // ============================================================

    if (loading) {
        return (
            <MainLayout>
                <h1>Lab Results</h1>
                <p>Loading lab results...</p>
            </MainLayout>
        );
    }

    // ============================================================
    // ERROR
    // ============================================================

    if (error) {
        return (
            <MainLayout>
                <div className="lab-results-page">

                    <div className="lab-results-header">
                        <h1>Lab Results</h1>

                        <p>
                            View your laboratory test results.
                        </p>
                    </div>

                    <p className="error-message">
                        {error}
                    </p>

                </div>
            </MainLayout>
        );
    }

    // ============================================================
    // MAIN PAGE
    // ============================================================

    return (
        <MainLayout>
            <div className="lab-results-page">

                <div className="lab-results-header">
                    <h1>Lab Results</h1>

                    <p>
                        View your laboratory test results.
                    </p>
                </div>

                {results.length === 0 ? (
                    <div className="lab-results-empty">

                        <h2>
                            No Lab Results
                        </h2>

                        <p>
                            You currently have no laboratory
                            results available.
                        </p>

                    </div>
                ) : (
                    <div className="lab-results-list">

                        {results.map((result) => (
                            <div
                                className="lab-result-card"
                                key={result.id}
                            >

                                <div className="lab-result-header">

                                    <div>
                                        <h2>
                                            Lab Result
                                        </h2>

                                        <p>
                                            Result ID:{" "}
                                            {result.id}
                                        </p>
                                    </div>

                                    <span className="lab-result-date">
                                        {new Date(
                                            result.reported_at
                                        ).toLocaleDateString()}
                                    </span>

                                </div>

                                <div className="lab-result-details">

                                    <div className="lab-result-detail">
                                        <strong>
                                            Lab Test ID
                                        </strong>

                                        <span>
                                            {result.lab_test_id}
                                        </span>
                                    </div>

                                    <div className="lab-result-detail">
                                        <strong>
                                            Result
                                        </strong>

                                        <span>
                                            {result.result}
                                        </span>
                                    </div>

                                    <div className="lab-result-detail">
                                        <strong>
                                            Unit
                                        </strong>

                                        <span>
                                            {result.unit ||
                                                "Not provided"}
                                        </span>
                                    </div>

                                    <div className="lab-result-detail">
                                        <strong>
                                            Reference Range
                                        </strong>

                                        <span>
                                            {result.reference_range ||
                                                "Not provided"}
                                        </span>
                                    </div>

                                </div>

                                <div className="lab-result-remarks">

                                    <strong>
                                        Remarks
                                    </strong>

                                    <p>
                                        {result.remarks ||
                                            "No remarks provided."}
                                    </p>

                                </div>

                                <div className="lab-result-reported">

                                    <strong>
                                        Reported At:
                                    </strong>{" "}

                                    {new Date(
                                        result.reported_at
                                    ).toLocaleString()}

                                </div>

                            </div>
                        ))}

                    </div>
                )}

            </div>
        </MainLayout>
    );
}

export default PatientLabResults;