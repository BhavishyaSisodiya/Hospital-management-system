import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Suspense, lazy } from "react";

import ProtectedRoute from "./ProtectedRoute";

const Home = lazy(() => import("../pages/home/Home"));
const Login = lazy(() => import("../pages/auth/Login"));
const Register = lazy(() => import("../pages/auth/Register"));
const Unauthorized = lazy(() => import("../pages/auth/unauthorized"));

const MemberDashboard = lazy(() => import("../pages/member/MemberDashBoard"));

const PatientDashboard = lazy(() => import("../pages/patient/PatientDashBoard"));
const PatientProfile = lazy(() => import("../pages/patient/PatientProfile"));
const PatientAppointments = lazy(() => import("../pages/patient/PatientAppointments"));
const PatientDoctors = lazy(() => import("../pages/patient/PatientDoctors"));
const BookAppointment = lazy(() => import("../pages/patient/BookAppointment"));
const PatientMedicalRecords = lazy(() => import("../pages/patient/PatientMedicalRecords"));
const PatientLabResults = lazy(() => import("../pages/patient/PatientLabResults"));
const PatientPrescriptions = lazy(() => import("../pages/patient/PatientPrescriptions"));
const PatientPayments = lazy(() => import("../pages/patient/PatientPayments"));
const PatientBilling = lazy(() => import("../pages/patient/PatientBilling"));
const PatientAdmissions = lazy(() => import("../pages/patient/PatientAdmissions"));
const PatientVitals = lazy(() => import("../pages/patient/PatientVitals"));
const PatientDoctorSchedule = lazy(() => import("../pages/patient/PatientDoctorSchedule"));

const DoctorDashBoard = lazy(() => import("../pages/doctor/DoctorDashBoard"));
const DoctorAppointments = lazy(() => import("../pages/doctor/DoctorAppointments"));
const DoctorPatients = lazy(() => import("../pages/doctor/DoctorPatients"));
const DoctorPrescriptions = lazy(() => import("../pages/doctor/DoctorPrescriptions"));
const DoctorCreatePrescription = lazy(() => import("../pages/doctor/DoctorCreatePrescription"));
const DoctorMedicalRecords = lazy(() => import("../pages/doctor/DoctorMedicalRecords"));
const CreateMedicalRecord = lazy(() => import("../pages/doctor/CreateMedicalRecord"));
const DoctorPatientDetails = lazy(() => import("../pages/doctor/DoctorPatientDetails"));
const DoctorPrescriptionDetails = lazy(() => import("../pages/doctor/DoctorPrescriptionDetails"));
const DoctorAddPrescriptionMedicine = lazy(() => import("../pages/doctor/DoctorAddPrescriptionMedicine"));
const DoctorEditPrescriptionMedicine = lazy(() => import("../pages/doctor/DoctorEditPrescriptionMedicine"));
const DoctorEditMedicalRecord = lazy(() => import("../pages/doctor/DoctorEditMedicalRecord"));
const DoctorSchedule = lazy(() => import("../pages/doctor/DoctorSchedule"));

const AdminDashBoard = lazy(() => import("../pages/admin/AdminDashBoard"));
const AdminHospitals = lazy(() => import("../pages/admin/AdminHospitals"));
const AdminEmployees = lazy(() => import("../pages/admin/AdminEmployees"));
const AdminEmployeeDetails = lazy(() => import("../pages/admin/AdminEmployeeDetails"));
const AdminDoctors = lazy(() => import("../pages/admin/AdminDoctors"));
const AdminPatients = lazy(() => import("../pages/admin/AdminPatients"));
const AdminDepartments = lazy(() => import("../pages/admin/AdminDepartments"));
const AdminAppointments = lazy(() => import("../pages/admin/AdminAppointments"));
const AdminAdmissions = lazy(() => import("../pages/admin/AdminAdmissions"));
const AdminRooms = lazy(() => import("../pages/admin/AdminRooms"));
const AdminBeds = lazy(() => import("../pages/admin/AdminBeds"));
const AdminNurseAssignments = lazy(() => import("../pages/admin/AdminNurseAssignments"));
const AdminTestTypes = lazy(() => import("../pages/admin/AdminTestTypes"));
const AdminLabTests = lazy(() => import("../pages/admin/AdminLabTests"));
const AdminLabResults = lazy(() => import("../pages/admin/AdminLabResults"));
const AdminMedicines = lazy(() => import("../pages/admin/AdminMedicines"));
const AdminMedicineBatches = lazy(() => import("../pages/admin/AdminMedicineBatches"));
const AdminPharmacies = lazy(() => import("../pages/admin/AdminPharmacies"));
const AdminPharmacyStock = lazy(() => import("../pages/admin/AdminPharmacyStock"));
const AdminInvoices = lazy(() => import("../pages/admin/AdminInvoices"));
const AdminInvoiceItems = lazy(() => import("../pages/admin/AdminInvoiceItems"));
const AdminPayments = lazy(() => import("../pages/admin/AdminPayments"));

const NurseDashBoard = lazy(() => import("../pages/nurse/NurseDashBoard"));
const NurseAssignedPatients = lazy(() => import("../pages/nurse/NurseAssignedPatients"));
const NurseRecordVitals = lazy(() => import("../pages/nurse/NurseRecordVitals"));

const ReceptionistDashBoard = lazy(() => import("../pages/receptionist/ReceptionistDashBoard"));
const ReceptionistPatients = lazy(() => import("../pages/receptionist/ReceptionistPatients"));
const ReceptionistAppointments = lazy(() => import("../pages/receptionist/ReceptionistAppointments"));
const ReceptionistAdmissions = lazy(() => import("../pages/receptionist/ReceptionistAdmissions"));
const ReceptionistBilling = lazy(() => import("../pages/receptionist/ReceptionistBilling"));

const PharmacistDashBoard = lazy(() => import("../pages/pharmacist/PharmacistDashBoard"));
const PharmacistPrescriptions = lazy(() => import("../pages/pharmacist/PharmacistPrescriptions"));
const LabTechnicianDashBoard = lazy(() => import("../pages/labTechnician/LabTechnicianDashBoard"));
const LabTechnicianLabBilling = lazy(() => import("../pages/labTechnician/LabTechnicianLabBilling"));
const AccountantDashBoard = lazy(() => import("../pages/accountant/AccountantDashBoard"));


function AppRoutes() {
    return (
        <BrowserRouter>
            <Suspense fallback={<div className="dashboard-page"><p className="loading-message">Loading...</p></div>}>
            <Routes>

                {/* ==================== HOME ==================== */}
                <Route
                    path="/"
                    element={<Home />}
                />

                {/* ==================== LOGIN ==================== */}
                <Route
                    path="/login"
                    element={<Login />}
                />

                {/* ==================== REGISTER ==================== */}
                <Route
                    path="/register"
                    element={<Register />}
                />

                {/* ==================== UNAUTHORIZED ==================== */}
                <Route
                    path="/unauthorized"
                    element={<Unauthorized />}
                />

                {/* ==================== PATIENT ==================== */}
                <Route
                    path="/patient/dashboard"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/profile"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientProfile />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/appointments"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientAppointments />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/doctors"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientDoctors />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/book-appointment/:doctorId"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <BookAppointment />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/records"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientMedicalRecords />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/lab-results"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientLabResults />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/prescriptions"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientPrescriptions />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/billing"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientBilling />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/payments"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientPayments />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/admissions"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientAdmissions />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/vitals"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientVitals />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/patient/doctors/:doctorId/schedule"
                    element={
                        <ProtectedRoute allowedAccountTypes={["patient"]}>
                            <PatientDoctorSchedule />
                        </ProtectedRoute>
                    }
                />

                {/* ==================== MEMBER ==================== */}
                <Route
                    path="/member/dashboard"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <MemberDashboard />
                        </ProtectedRoute>
                    }
                />

                {/* ==================== DOCTOR ==================== */}
                <Route
                    path="/doctor/dashboard"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorDashBoard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/appointments"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorAppointments />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/patients"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorPatients />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/patients/:patientId"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorPatientDetails />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/medical-records"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorMedicalRecords />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/medical-records/create"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <CreateMedicalRecord />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/medical-records/edit/:recordId"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorEditMedicalRecord />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/prescriptions"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorPrescriptions />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/prescriptions/create"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorCreatePrescription />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/prescriptions/:id"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorPrescriptionDetails />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/prescriptions/:id/add-medicine"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorAddPrescriptionMedicine />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/prescriptions/:id/edit-medicine/:medicineId"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorEditPrescriptionMedicine />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/doctor/schedule"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <DoctorSchedule />
                        </ProtectedRoute>
                    }
                />

                {/* ==================== ADMIN ==================== */}
                <Route
                    path="/admin/dashboard"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminDashBoard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/hospitals"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminHospitals />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/employees"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminEmployees />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/employees/:employeeId"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminEmployeeDetails />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/doctors"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminDoctors />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/patients"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminPatients />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/departments"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminDepartments />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/appointments"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminAppointments />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/admissions"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminAdmissions />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/rooms"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminRooms />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/beds"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminBeds />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/nurse-assignments"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminNurseAssignments />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/test-types"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminTestTypes />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/lab-tests"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminLabTests />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/lab-results"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminLabResults />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/medicines"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminMedicines />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/medicine-batches"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminMedicineBatches />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/pharmacies"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminPharmacies />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/pharmacy-stock"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminPharmacyStock />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/invoices"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminInvoices />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/invoice-items"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminInvoiceItems />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/admin/payments"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AdminPayments />
                        </ProtectedRoute>
                    }
                />

                {/* ==================== NURSE ==================== */}
                <Route
                    path="/nurse/dashboard"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <NurseDashBoard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/nurse/assigned-patients"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <NurseAssignedPatients />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/nurse/record-vitals"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <NurseRecordVitals />
                        </ProtectedRoute>
                    }
                />

                {/* ==================== RECEPTIONIST ==================== */}
                <Route
                    path="/receptionist/dashboard"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <ReceptionistDashBoard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/receptionist/patients"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <ReceptionistPatients />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/receptionist/appointments"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <ReceptionistAppointments />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/receptionist/admissions"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <ReceptionistAdmissions />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/receptionist/billing"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <ReceptionistBilling />
                        </ProtectedRoute>
                    }
                />

                {/* ==================== PHARMACIST ==================== */}
                <Route
                    path="/pharmacist/dashboard"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <PharmacistDashBoard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/pharmacist/billing"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <PharmacistPrescriptions />
                        </ProtectedRoute>
                    }
                />

                {/* ==================== LAB TECHNICIAN ==================== */}
                <Route
                    path="/lab-technician/dashboard"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <LabTechnicianDashBoard />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/lab-technician/billing"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <LabTechnicianLabBilling />
                        </ProtectedRoute>
                    }
                />

                {/* ==================== ACCOUNTANT ==================== */}
                <Route
                    path="/accountant/dashboard"
                    element={
                        <ProtectedRoute allowedAccountTypes={["member"]}>
                            <AccountantDashBoard />
                        </ProtectedRoute>
                    }
                />

                </Routes>
            </Suspense>
        </BrowserRouter>
    );
}

export default AppRoutes;
