import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { getMyPrescriptions } from "../../api/prescriptions";
import { getLabTests } from "../../api/labTests";
import { getTestTypes } from "../../api/testTypes";
import { getPatients } from "../../api/patients";
import { getDoctors } from "../../api/doctors";
import { createBillingInvoice } from "../../api/billing";

function LabTechnicianLabBilling() {

    const [prescriptions, setPrescriptions] = useState([]);
    const [labTests, setLabTests] = useState([]);
    const [testTypes, setTestTypes] = useState([]);
    const [patients, setPatients] = useState([]);
    const [doctors, setDoctors] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [selectedPrescription, setSelectedPrescription] = useState(null);
    const [billItems, setBillItems] = useState([]);

    const [collectPayment, setCollectPayment] = useState(true);
    const [paymentMethod, setPaymentMethod] = useState("cash");
    const [paymentReference, setPaymentReference] = useState("");

    const [saving, setSaving] = useState(false);


    /* ============================================================
       LOAD DATA
       ============================================================ */

    useEffect(() => {

        const loadData = async () => {

            try {

                setLoading(true);
                setError("");

                const [
                    prescriptionsData,
                    labTestsData,
                    testTypesData,
                    patientsData,
                    doctorsData,
                ] = await Promise.all([
                    getMyPrescriptions(),
                    getLabTests(),
                    getTestTypes(),
                    getPatients(),
                    getDoctors(),
                ]);

                setPrescriptions(prescriptionsData);
                setLabTests(labTestsData);
                setTestTypes(testTypesData);
                setPatients(patientsData);
                setDoctors(doctorsData);

            } catch (err) {

                console.error(err);

                setError(
                    err.response?.data?.detail ||
                    "Unable to load data."
                );

            } finally {

                setLoading(false);

            }
        };

        loadData();

    }, []);


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

    const getLabTestForPrescription = (prescription) => {

        if (!prescription.lab_test_id) {
            return null;
        }

        return labTests.find(
            (lt) => lt.id === prescription.lab_test_id
        ) || null;

    };

    const getTestName = (prescription) => {

        const labTest = getLabTestForPrescription(
            prescription
        );

        if (!labTest) {
            return "";
        }

        const testType = testTypes.find(
            (t) => t.id === labTest.test_type_id
        );

        return testType
            ? testType.name
            : `Test #${labTest.test_type_id}`;

    };

    const getTestPrice = (prescription) => {

        const labTest = getLabTestForPrescription(
            prescription
        );

        if (!labTest) {
            return 0;
        }

        const testType = testTypes.find(
            (t) => t.id === labTest.test_type_id
        );

        return testType
            ? Number(testType.price)
            : 0;

    };


    /* ============================================================
       BILLING
       ============================================================ */

    const getBillTotal = (items) => {

        return items.reduce((sum, item) => {
            return (
                sum +
                Number(item.quantity) * Number(item.unit_price)
            );
        }, 0);

    };

    const openBillModal = (prescription) => {

        setSelectedPrescription(prescription);

        const labTest = getLabTestForPrescription(
            prescription
        );

        const testName = getTestName(prescription);

        setBillItems([
            {
                lab_test_id: labTest ? labTest.id : null,
                description: `Lab Test - ${testName}`,
                quantity: 1,
                unit_price: getTestPrice(prescription),
            },
        ]);

        setCollectPayment(true);
        setPaymentMethod("cash");
        setPaymentReference("");
        setError("");
        setSuccess("");
        setShowModal(true);

    };

    const updateBillItem = (index, field, value) => {

        setBillItems((prev) =>
            prev.map((item, i) =>
                i === index
                    ? { ...item, [field]: value }
                    : item
            )
        );

    };

    const handleGenerateBill = async (event) => {

        event.preventDefault();

        if (!selectedPrescription) {
            return;
        }

        const validItems = billItems.filter(
            (item) =>
                item.description && item.quantity > 0
        );

        if (!validItems.length) {
            setError("Add at least one bill item.");
            return;
        }

        setSaving(true);
        setError("");
        setSuccess("");

        try {

            const total = getBillTotal(validItems);

            const invoice = await createBillingInvoice({
                patient_id: selectedPrescription.patient_id,
                items: validItems,
                payment: collectPayment
                    ? {
                          amount: Math.round(total * 100) / 100,
                          method: paymentMethod,
                          reference: paymentReference,
                      }
                    : null,
            });

            setSuccess(
                `Invoice #${invoice.id} created for ` +
                `${getPatientName(selectedPrescription.patient_id)}. `
            );

            setShowModal(false);

        } catch (err) {

            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Unable to generate the bill."
            );

        } finally {

            setSaving(false);

        }

    };


    /* ============================================================
       RENDER
       ============================================================ */

    const total = getBillTotal(billItems);

    const labPrescriptions = prescriptions.filter(
        (prescription) => prescription.lab_test_id
    );

    return (
        <MainLayout>
            <div className="prescriptions-page">

                <div className="prescriptions-header">
                    <div>
                        <h1>Lab Test Prescriptions &amp; Billing</h1>
                        <p>
                            Review prescriptions that include lab
                            test orders and generate bills when
                            the tests are performed.
                        </p>
                    </div>
                </div>


                {success && (
                    <p className="success-message">{success}</p>
                )}

                {error && !showModal && (
                    <p className="error-message">{error}</p>
                )}


                {/* ==================================================
                   LOADING
                   ================================================== */}

                {loading && (
                    <p className="loading-message">
                        Loading lab prescriptions...
                    </p>
                )}


                {/* ==================================================
                   EMPTY STATE
                   ================================================== */}

                {!loading && labPrescriptions.length === 0 && (
                    <div className="empty-state">
                        <h2>No Lab Prescriptions Found</h2>
                        <p>
                            There are no prescriptions with
                            lab tests to bill.
                        </p>
                    </div>
                )}


                {/* ==================================================
                   PRESCRIPTIONS TABLE
                   ================================================== */}

                {!loading && labPrescriptions.length > 0 && (

                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="prescriptions-table">
                                <thead>
                                    <tr>
                                        <th>Patient</th>
                                        <th>Doctor</th>
                                        <th>Test</th>
                                        <th>Date</th>
                                        <th>Amount</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {labPrescriptions.map(
                                        (prescription) => {

                                            const labTest =
                                                getLabTestForPrescription(
                                                    prescription
                                                );

                                            return (
                                                <tr key={prescription.id}>
                                                    <td>
                                                        {getPatientName(
                                                            prescription.patient_id
                                                        )}
                                                    </td>
                                                    <td>
                                                        {getDoctorName(
                                                            prescription.doctor_id
                                                        )}
                                                    </td>
                                                    <td>
                                                        {getTestName(
                                                            prescription
                                                        )}
                                                        {labTest && (
                                                            <span
                                                                className={
                                                                    "status-badge"
                                                                }
                                                            >
                                                                {labTest.status}
                                                            </span>
                                                        )}
                                                    </td>
                                                    <td>
                                                        {prescription.prescription_date}
                                                    </td>
                                                    <td>
                                                        {"\u20B9"}{" "}
                                                        {getTestPrice(
                                                            prescription
                                                        ).toFixed(2)}
                                                    </td>
                                                    <td>
                                                        <button
                                                            type="button"
                                                            className="action-btn action-btn-edit"
                                                            onClick={() =>
                                                                openBillModal(
                                                                    prescription
                                                                )
                                                            }
                                                        >
                                                            Generate Bill
                                                        </button>
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


                {/* ==================================================
                   BILL MODAL
                   ================================================== */}

                {showModal && selectedPrescription && (

                    <div className="modal-overlay">
                        <div className="modal-content">

                            <div className="modal-header">
                                <h2>
                                    Generate Bill -{" "}
                                    {getPatientName(
                                        selectedPrescription.patient_id
                                    )}
                                </h2>
                                <button
                                    type="button"
                                    className="modal-close-btn"
                                    onClick={() =>
                                        setShowModal(false)
                                    }
                                >
                                    &times;
                                </button>
                            </div>

                            {error && (
                                <p className="error-message">
                                    {error}
                                </p>
                            )}

                            <form onSubmit={handleGenerateBill}>

                                <div className="form-group">
                                    <label className="form-label">
                                        Bill Items
                                    </label>
                                    <div className="table-wrapper">
                                        <div className="table-container">
                                            <table className="plain-table">
                                                <thead>
                                                    <tr>
                                                        <th>Description</th>
                                                        <th>Qty</th>
                                                        <th>Unit Price</th>
                                                        <th>Amount</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {billItems.map(
                                                        (item, index) => (
                                                            <tr key={index}>
                                                                <td>
                                                                    {item.description}
                                                                </td>
                                                                <td>
                                                                    <input
                                                                        type="number"
                                                                        min="1"
                                                                        className="form-input num-input"
                                                                        value={item.quantity}
                                                                        onChange={(e) =>
                                                                            updateBillItem(
                                                                                index,
                                                                                "quantity",
                                                                                Number(
                                                                                    e.target.value
                                                                                )
                                                                            )
                                                                        }
                                                                    />
                                                                </td>
                                                                <td>
                                                                    <input
                                                                        type="number"
                                                                        min="0"
                                                                        step="0.01"
                                                                        className="form-input num-input"
                                                                        value={item.unit_price}
                                                                        onChange={(e) =>
                                                                            updateBillItem(
                                                                                index,
                                                                                "unit_price",
                                                                                Number(
                                                                                    e.target.value
                                                                                )
                                                                            )
                                                                        }
                                                                    />
                                                                </td>
                                                                <td className="num">
                                                                    {"\u20B9"}
                                                                    {(
                                                                        Number(
                                                                            item.quantity
                                                                        ) *
                                                                        Number(
                                                                            item.unit_price
                                                                        )
                                                                    ).toFixed(2)}
                                                                </td>
                                                            </tr>
                                                        )
                                                    )}
                                                </tbody>
                                                <tfoot>
                                                    <tr>
                                                        <th colSpan={3}>
                                                            Total
                                                        </th>
                                                        <th className="num">
                                                            {"\u20B9"}
                                                            {total.toFixed(2)}
                                                        </th>
                                                    </tr>
                                                </tfoot>
                                            </table>
                                        </div>
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">
                                        <input
                                            type="checkbox"
                                            checked={collectPayment}
                                            onChange={(e) =>
                                                setCollectPayment(
                                                    e.target.checked
                                                )
                                            }
                                        />
                                        {" "}Collect payment now
                                    </label>
                                </div>

                                {collectPayment && (
                                    <div className="form-row">

                                        <div className="form-group">
                                            <label className="form-label">
                                                Payment Method
                                            </label>
                                            <select
                                                className="form-select"
                                                value={paymentMethod}
                                                onChange={(e) =>
                                                    setPaymentMethod(
                                                        e.target.value
                                                    )
                                                }
                                            >
                                                <option value="cash">
                                                    Cash
                                                </option>
                                                <option value="card">
                                                    Card
                                                </option>
                                                <option value="upi">
                                                    UPI
                                                </option>
                                                <option value="bank_transfer">
                                                    Bank Transfer
                                                </option>
                                            </select>
                                        </div>

                                        <div className="form-group">
                                            <label className="form-label">
                                                Transaction Reference
                                            </label>
                                            <input
                                                type="text"
                                                className="form-input"
                                                value={paymentReference}
                                                onChange={(e) =>
                                                    setPaymentReference(
                                                        e.target.value
                                                    )
                                                }
                                            />
                                        </div>

                                    </div>
                                )}

                                <div className="booking-actions">
                                    <button
                                        type="submit"
                                        disabled={saving}
                                    >
                                        {saving
                                            ? "Generating..."
                                            : "Generate Bill"}
                                    </button>
                                    <button
                                        type="button"
                                        className="cancel-btn"
                                        onClick={() =>
                                            setShowModal(false)
                                        }
                                        disabled={saving}
                                    >
                                        Cancel
                                    </button>
                                </div>

                            </form>

                        </div>
                    </div>

                )}

            </div>
        </MainLayout>
    );
}

export default LabTechnicianLabBilling;