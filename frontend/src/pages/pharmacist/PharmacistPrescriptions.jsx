import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { getMyPrescriptions } from "../../api/prescriptions";
import { getMyPrescriptionMedicines } from "../../api/prescriptions";
import { getPatients } from "../../api/patients";
import { getDoctors } from "../../api/doctors";
import { getMedicines } from "../../api/medicines";
import { createBillingInvoice } from "../../api/billing";

function PharmacistPrescriptions() {

    const [prescriptions, setPrescriptions] = useState([]);
    const [prescriptionMedicines, setPrescriptionMedicines] = useState([]);
    const [patients, setPatients] = useState([]);
    const [doctors, setDoctors] = useState([]);
    const [medicines, setMedicines] = useState([]);

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
                    medsData,
                    patientsData,
                    doctorsData,
                    medicineData,
                ] = await Promise.all([
                    getMyPrescriptions(),
                    getMyPrescriptionMedicines(),
                    getPatients(),
                    getDoctors(),
                    getMedicines(),
                ]);

                setPrescriptions(prescriptionsData);
                setPrescriptionMedicines(medsData);
                setPatients(patientsData);
                setDoctors(doctorsData);
                setMedicines(medicineData);

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

    const getMedicine = (medicineId) => {

        const medicine = medicines.find(
            (m) => m.id === medicineId
        );

        return medicine;

    };


    /* ============================================================
       BILLING
       ============================================================ */

    const medicinesForPrescription = (prescriptionId) => {

        if (!prescriptionMedicines.length) {
            return [];
        }

        return prescriptionMedicines.filter(
            (pm) => pm.prescription_id === prescriptionId
        );

    };

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

        const items = medicinesForPrescription(
            prescription.id
        ).map((pm) => {

            const medicine = getMedicine(pm.medicine_id);

            return {
                medicine_id: pm.medicine_id,
                description: medicine
                    ? `${medicine.name} (${pm.dosage})`
                    : `Medicine #${pm.medicine_id} (${pm.dosage})`,
                quantity: pm.quantity,
                unit_price: medicine
                    ? Number(medicine.unit_price)
                    : 0,
            };

        });

        setBillItems(items);
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

    return (
        <MainLayout>
            <div className="prescriptions-page">

                <div className="prescriptions-header">
                    <div>
                        <h1>Prescriptions &amp; Billing</h1>
                        <p>
                            Review patient prescriptions and
                            generate bills when medicines are
                            purchased from the hospital pharmacy.
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
                        Loading prescriptions...
                    </p>
                )}


                {/* ==================================================
                   EMPTY STATE
                   ================================================== */}

                {!loading && prescriptions.length === 0 && (
                    <div className="empty-state">
                        <h2>No Prescriptions Found</h2>
                        <p>
                            There are no prescriptions to bill.
                        </p>
                    </div>
                )}


                {/* ==================================================
                   PRESCRIPTIONS TABLE
                   ================================================== */}

                {!loading && prescriptions.length > 0 && (

                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="prescriptions-table">
                                <thead>
                                    <tr>
                                        <th>Patient</th>
                                        <th>Doctor</th>
                                        <th>Date</th>
                                        <th>Medicines</th>
                                        <th>Total</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {prescriptions.map(
                                        (prescription) => {

                                            const meds =
                                                medicinesForPrescription(
                                                    prescription.id
                                                );

                                            const billTotal =
                                                getBillTotal(
                                                    meds.map((pm) => {
                                                        const medicine =
                                                            getMedicine(
                                                                pm.medicine_id
                                                            );
                                                        return {
                                                            quantity: pm.quantity,
                                                            unit_price: medicine
                                                                ? Number(
                                                                      medicine.unit_price
                                                                  )
                                                                : 0,
                                                        };
                                                    })
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
                                                        {prescription.prescription_date}
                                                    </td>
                                                    <td>
                                                        {meds.length
                                                            ? `${
                                                                  meds.length
                                                              } medicine${
                                                                  meds.length > 1
                                                                      ? "s"
                                                                      : ""
                                                              }`
                                                            : "-"}
                                                    </td>
                                                    <td>
                                                        {"\u20B9"}{" "}
                                                        {billTotal.toFixed(2)}
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
                                                        <th>Medicine</th>
                                                        <th>Qty</th>
                                                        <th>Unit Price</th>
                                                        <th>Amount</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {billItems.map(
                                                        (item, index) => (
                                                            <tr key={item.medicine_id}>
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

export default PharmacistPrescriptions;