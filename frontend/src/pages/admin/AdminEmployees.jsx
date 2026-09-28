import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { useNavigate } from "react-router-dom";
import {
    getEmployees,
    createEmployee,
    updateEmployee,
    deleteEmployee,
} from "../../api/employees";
import { getRoles } from "../../api/roles";
import { getDepartments } from "../../api/departments";
import { getHospitals } from "../../api/hospitals";

function AdminEmployees() {

    const navigate = useNavigate();

    const [employees, setEmployees] = useState([]);
    const [filteredEmployees, setFilteredEmployees] = useState([]);
    const [roles, setRoles] = useState([]);
    const [departments, setDepartments] = useState([]);
    const [hospitals, setHospitals] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [filterDepartment, setFilterDepartment] = useState("");

    const [showModal, setShowModal] = useState(false);
    const [editingEmployee, setEditingEmployee] = useState(null);
    const [formData, setFormData] = useState({
        firstName: "",
        lastName: "",
        email: "",
        phone: "",
        roleId: "",
        departmentId: "",
        hospitalId: "",
        dateOfBirth: "",
        gender: "",
        address: "",
        salary: "",
        qualification: "",
        experience: "",
        isAvailable: true,
    });
    const [formError, setFormError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                setError("");

                const [empData, roleData, deptData, hospData] =
                    await Promise.all([
                        getEmployees(),
                        getRoles(),
                        getDepartments(),
                        getHospitals(),
                    ]);

                setEmployees(empData);
                setFilteredEmployees(empData);
                setRoles(roleData);
                setDepartments(deptData);
                setHospitals(hospData);
            } catch (err) {
                console.error(err);
                if (err.response) {
                    setError(
                        err.response.data?.detail ||
                        "Unable to load employees."
                    );
                } else {
                    setError("Unable to connect to the server.");
                }
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    useEffect(() => {
        if (filterDepartment) {
            setFilteredEmployees(
                employees.filter(
                    (emp) =>
                        String(emp.department_id) === String(filterDepartment)
                )
            );
        } else {
            setFilteredEmployees(employees);
        }
    }, [filterDepartment, employees]);

    const resetForm = () => {
        setFormData({
            firstName: "",
            lastName: "",
            email: "",
            phone: "",
            roleId: "",
            departmentId: "",
            hospitalId: "",
            dateOfBirth: "",
            gender: "",
            address: "",
            salary: "",
            qualification: "",
            experience: "",
            isAvailable: true,
        });
        setFormError("");
        setEditingEmployee(null);
    };

    const openAddModal = () => {
        resetForm();
        setShowModal(true);
    };

    const openEditModal = (employee) => {
        setEditingEmployee(employee);
        setFormData({
            firstName: employee.first_name || "",
            lastName: employee.last_name || "",
            email: employee.email || "",
            phone: employee.phone || "",
            roleId: employee.role_id || "",
            departmentId: employee.department_id || "",
            hospitalId: employee.hospital_id || "",
            dateOfBirth: employee.date_of_birth || "",
            gender: employee.gender || "",
            address: employee.address || "",
            salary: employee.salary || "",
            qualification: employee.qualification || "",
            experience: employee.experience || "",
            isAvailable: employee.is_available ?? true,
        });
        setFormError("");
        setShowModal(true);
    };

    const handleFormChange = (event) => {
        const { name, value, type, checked } = event.target;
        setFormData((prev) => ({
            ...prev,
            [name]: type === "checkbox" ? checked : value,
        }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setFormError("");
        setSubmitting(true);

        try {
            const payload = {
                first_name: formData.firstName,
                last_name: formData.lastName,
                email: formData.email,
                phone: formData.phone,
                role_id: formData.roleId || null,
                department_id: formData.departmentId || null,
                hospital_id: formData.hospitalId || null,
                date_of_birth: formData.dateOfBirth || null,
                gender: formData.gender || null,
                address: formData.address || null,
                salary: formData.salary ? parseFloat(formData.salary) : null,
                qualification: formData.qualification || null,
                experience: formData.experience
                    ? parseInt(formData.experience)
                    : null,
                is_available: formData.isAvailable,
            };

            if (editingEmployee) {
                await updateEmployee(editingEmployee.id, payload);
            } else {
                await createEmployee(payload);
            }

            const data = await getEmployees();
            setEmployees(data);
            setShowModal(false);
            resetForm();
        } catch (err) {
            console.error(err);
            if (err.response) {
                setFormError(
                    err.response.data?.detail ||
                    "Failed to save employee."
                );
            } else {
                setFormError("Unable to connect to the server.");
            }
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (employeeId) => {
        if (!window.confirm("Are you sure you want to delete this employee?")) {
            return;
        }

        try {
            await deleteEmployee(employeeId);
            const data = await getEmployees();
            setEmployees(data);
        } catch (err) {
            console.error(err);
            if (err.response) {
                setError(
                    err.response.data?.detail ||
                    "Failed to delete employee."
                );
            } else {
                setError("Unable to connect to the server.");
            }
        }
    };

    const getRoleName = (roleId) => {
        const role = roles.find((r) => r.id === roleId);
        return role ? role.name : "N/A";
    };

    const getDepartmentName = (deptId) => {
        const dept = departments.find((d) => d.id === deptId);
        return dept ? dept.name : "N/A";
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <p className="loading-message">Loading employees...</p>
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
            <div className="dashboard-page">

                <div className="appointments-header">
                    <div>
                        <h1>Employees</h1>
                        <p>Manage hospital staff and employee records.</p>
                    </div>
                </div>

                <div className="filter-row">
                    <div className="filter-group">
                        <label>Department</label>
                        <select
                            value={filterDepartment}
                            onChange={(e) =>
                                setFilterDepartment(e.target.value)
                            }
                        >
                            <option value="">All Departments</option>
                            {departments.map((dept) => (
                                <option key={dept.id} value={dept.id}>
                                    {dept.name}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="filter-actions">
                        <button className="btn-add" onClick={openAddModal}>
                            Add Employee
                        </button>
                    </div>
                </div>

                {filteredEmployees.length === 0 ? (
                    <div className="empty-state">
                        <h2>No Employees</h2>
                        <p>No employees found matching the current filters.</p>
                    </div>
                ) : (
                    <div className="table-wrapper">
                        <div className="table-container">
                            <table className="appointments-table">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Phone</th>
                                        <th>Role</th>
                                        <th>Department</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredEmployees.map((employee) => (
                                        <tr key={employee.id}>
                                            <td>
                                                {employee.first_name}{" "}
                                                {employee.last_name}
                                            </td>
                                            <td>{employee.email}</td>
                                            <td>{employee.phone}</td>
                                            <td>
                                                {getRoleName(employee.role_id)}
                                            </td>
                                            <td>
                                                {getDepartmentName(
                                                    employee.department_id
                                                )}
                                            </td>
                                            <td>
                                                <button
                                                    className="btn-edit"
                                                    onClick={() =>
                                                        openEditModal(employee)
                                                    }
                                                >
                                                    Edit
                                                </button>
                                                <button
                                                    className="btn-delete"
                                                    onClick={() =>
                                                        handleDelete(employee.id)
                                                    }
                                                >
                                                    Delete
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {showModal && (
                    <div className="modal-overlay">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h2>
                                    {editingEmployee
                                        ? "Edit Employee"
                                        : "Add Employee"}
                                </h2>
                                <button
                                    className="btn-cancel"
                                    onClick={() => {
                                        setShowModal(false);
                                        resetForm();
                                    }}
                                >
                                    Close
                                </button>
                            </div>

                            {formError && (
                                <p className="error-message">{formError}</p>
                            )}

                            <form
                                className="form-group"
                                onSubmit={handleSubmit}
                            >
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>First Name</label>
                                        <input
                                            type="text"
                                            name="firstName"
                                            value={formData.firstName}
                                            onChange={handleFormChange}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Last Name</label>
                                        <input
                                            type="text"
                                            name="lastName"
                                            value={formData.lastName}
                                            onChange={handleFormChange}
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Email</label>
                                        <input
                                            type="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleFormChange}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Phone</label>
                                        <input
                                            type="text"
                                            name="phone"
                                            value={formData.phone}
                                            onChange={handleFormChange}
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Role</label>
                                        <select
                                            name="roleId"
                                            value={formData.roleId}
                                            onChange={handleFormChange}
                                        >
                                            <option value="">Select Role</option>
                                            {roles.map((role) => (
                                                <option
                                                    key={role.id}
                                                    value={role.id}
                                                >
                                                    {role.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>Department</label>
                                        <select
                                            name="departmentId"
                                            value={formData.departmentId}
                                            onChange={handleFormChange}
                                        >
                                            <option value="">
                                                Select Department
                                            </option>
                                            {departments.map((dept) => (
                                                <option
                                                    key={dept.id}
                                                    value={dept.id}
                                                >
                                                    {dept.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Hospital</label>
                                        <select
                                            name="hospitalId"
                                            value={formData.hospitalId}
                                            onChange={handleFormChange}
                                        >
                                            <option value="">
                                                Select Hospital
                                            </option>
                                            {hospitals.map((hosp) => (
                                                <option
                                                    key={hosp.id}
                                                    value={hosp.id}
                                                >
                                                    {hosp.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>Date of Birth</label>
                                        <input
                                            type="date"
                                            name="dateOfBirth"
                                            value={formData.dateOfBirth}
                                            onChange={handleFormChange}
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Gender</label>
                                        <select
                                            name="gender"
                                            value={formData.gender}
                                            onChange={handleFormChange}
                                        >
                                            <option value="">Select Gender</option>
                                            <option value="male">Male</option>
                                            <option value="female">Female</option>
                                            <option value="other">Other</option>
                                        </select>
                                    </div>
                                    <div className="form-group">
                                        <label>Salary</label>
                                        <input
                                            type="number"
                                            name="salary"
                                            value={formData.salary}
                                            onChange={handleFormChange}
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Qualification</label>
                                        <input
                                            type="text"
                                            name="qualification"
                                            value={formData.qualification}
                                            onChange={handleFormChange}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Experience (years)</label>
                                        <input
                                            type="number"
                                            name="experience"
                                            value={formData.experience}
                                            onChange={handleFormChange}
                                        />
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label>Address</label>
                                    <textarea
                                        name="address"
                                        value={formData.address}
                                        onChange={handleFormChange}
                                    />
                                </div>

                                <div className="form-group">
                                    <label>
                                        <input
                                            type="checkbox"
                                            name="isAvailable"
                                            checked={formData.isAvailable}
                                            onChange={handleFormChange}
                                        />
                                        Available
                                    </label>
                                </div>

                                <div className="booking-actions">
                                    <button
                                        type="submit"
                                        className="btn-save"
                                        disabled={submitting}
                                    >
                                        {submitting ? "Saving..." : "Save"}
                                    </button>
                                    <button
                                        type="button"
                                        className="btn-cancel"
                                        onClick={() => {
                                            setShowModal(false);
                                            resetForm();
                                        }}
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

export default AdminEmployees;
