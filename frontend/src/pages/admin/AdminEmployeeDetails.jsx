import { useEffect, useState } from "react";
import MainLayout from "../../layouts/MainLayout";
import { useNavigate, useParams } from "react-router-dom";
import {
    getEmployee,
    updateEmployee,
    deleteEmployee,
} from "../../api/employees";
import { getRoles } from "../../api/roles";
import { getDepartments } from "../../api/departments";
import { getHospitals } from "../../api/hospitals";

function AdminEmployeeDetails() {

    const navigate = useNavigate();
    const { employeeId } = useParams();

    const [employee, setEmployee] = useState(null);
    const [roles, setRoles] = useState([]);
    const [departments, setDepartments] = useState([]);
    const [hospitals, setHospitals] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [editing, setEditing] = useState(false);
    const [formData, setFormData] = useState({});
    const [formError, setFormError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            try {
                setLoading(true);
                setError("");

                const [empData, roleData, deptData, hospData] =
                    await Promise.all([
                        getEmployee(employeeId),
                        getRoles(),
                        getDepartments(),
                        getHospitals(),
                    ]);

                setEmployee(empData);
                setRoles(roleData);
                setDepartments(deptData);
                setHospitals(hospData);
                setFormData({
                    first_name: empData.first_name || "",
                    last_name: empData.last_name || "",
                    email: empData.email || "",
                    phone: empData.phone || "",
                    role_id: empData.role_id || "",
                    department_id: empData.department_id || "",
                    hospital_id: empData.hospital_id || "",
                    date_of_birth: empData.date_of_birth || "",
                    gender: empData.gender || "",
                    address: empData.address || "",
                    salary: empData.salary || "",
                    qualification: empData.qualification || "",
                    experience: empData.experience || "",
                    is_available: empData.is_available ?? true,
                });
            } catch (err) {
                console.error(err);
                if (err.response) {
                    setError(
                        err.response.data?.detail ||
                        "Unable to load employee details."
                    );
                } else {
                    setError("Unable to connect to the server.");
                }
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [employeeId]);

    const getRoleName = (roleId) => {
        const role = roles.find((r) => r.id === roleId);
        return role ? role.name : "N/A";
    };

    const getDepartmentName = (deptId) => {
        const dept = departments.find((d) => d.id === deptId);
        return dept ? dept.name : "N/A";
    };

    const getHospitalName = (hospId) => {
        const hosp = hospitals.find((h) => h.id === hospId);
        return hosp ? hosp.name : "N/A";
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
                first_name: formData.first_name,
                last_name: formData.last_name,
                email: formData.email,
                phone: formData.phone,
                role_id: formData.role_id || null,
                department_id: formData.department_id || null,
                hospital_id: formData.hospital_id || null,
                date_of_birth: formData.date_of_birth || null,
                gender: formData.gender || null,
                address: formData.address || null,
                salary: formData.salary
                    ? parseFloat(formData.salary)
                    : null,
                qualification: formData.qualification || null,
                experience: formData.experience
                    ? parseInt(formData.experience)
                    : null,
                is_available: formData.is_available,
            };

            await updateEmployee(employeeId, payload);
            const updated = await getEmployee(employeeId);
            setEmployee(updated);
            setEditing(false);
        } catch (err) {
            console.error(err);
            if (err.response) {
                setFormError(
                    err.response.data?.detail ||
                    "Failed to update employee."
                );
            } else {
                setFormError("Unable to connect to the server.");
            }
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async () => {
        if (!window.confirm("Are you sure you want to delete this employee?")) {
            return;
        }

        try {
            await deleteEmployee(employeeId);
            navigate("/admin/employees");
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

    if (loading) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <p className="loading-message">
                        Loading employee details...
                    </p>
                </div>
            </MainLayout>
        );
    }

    if (error) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <p className="error-message">{error}</p>
                    <button
                        className="btn-edit"
                        onClick={() => navigate("/admin/employees")}
                    >
                        Back to Employees
                    </button>
                </div>
            </MainLayout>
        );
    }

    if (!employee) {
        return (
            <MainLayout>
                <div className="dashboard-page">
                    <div className="empty-state">
                        <h2>Employee Not Found</h2>
                        <p>The requested employee could not be found.</p>
                    </div>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="dashboard-page">

                <div className="appointments-header">
                    <div>
                        <h1>Employee Details</h1>
                        <p>
                            {employee.first_name} {employee.last_name}
                        </p>
                    </div>
                    <div className="filter-actions">
                        <button
                            className="btn-edit"
                            onClick={() => setEditing(!editing)}
                        >
                            {editing ? "Cancel Edit" : "Edit"}
                        </button>
                        <button className="btn-delete" onClick={handleDelete}>
                            Delete
                        </button>
                        <button
                            className="btn-cancel"
                            onClick={() => navigate("/admin/employees")}
                        >
                            Back to List
                        </button>
                    </div>
                </div>

                {editing ? (
                    <div className="profile-card">
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
                                        name="first_name"
                                        value={formData.first_name}
                                        onChange={handleFormChange}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Last Name</label>
                                    <input
                                        type="text"
                                        name="last_name"
                                        value={formData.last_name}
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
                                        name="role_id"
                                        value={formData.role_id}
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
                                        name="department_id"
                                        value={formData.department_id}
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
                                        name="hospital_id"
                                        value={formData.hospital_id}
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
                                        name="date_of_birth"
                                        value={formData.date_of_birth}
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
                                        name="is_available"
                                        checked={formData.is_available}
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
                                    {submitting ? "Saving..." : "Save Changes"}
                                </button>
                                <button
                                    type="button"
                                    className="btn-cancel"
                                    onClick={() => setEditing(false)}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                ) : (
                    <div className="profile-card">
                        <div className="profile-row">
                            <strong>First Name</strong>
                            <span>{employee.first_name}</span>
                        </div>
                        <div className="profile-row">
                            <strong>Last Name</strong>
                            <span>{employee.last_name}</span>
                        </div>
                        <div className="profile-row">
                            <strong>Email</strong>
                            <span>{employee.email}</span>
                        </div>
                        <div className="profile-row">
                            <strong>Phone</strong>
                            <span>{employee.phone || "N/A"}</span>
                        </div>
                        <div className="profile-row">
                            <strong>Role</strong>
                            <span>
                                {getRoleName(employee.role_id)}
                            </span>
                        </div>
                        <div className="profile-row">
                            <strong>Department</strong>
                            <span>
                                {getDepartmentName(employee.department_id)}
                            </span>
                        </div>
                        <div className="profile-row">
                            <strong>Hospital</strong>
                            <span>
                                {getHospitalName(employee.hospital_id)}
                            </span>
                        </div>
                        <div className="profile-row">
                            <strong>Date of Birth</strong>
                            <span>{employee.date_of_birth || "N/A"}</span>
                        </div>
                        <div className="profile-row">
                            <strong>Gender</strong>
                            <span>{employee.gender || "N/A"}</span>
                        </div>
                        <div className="profile-row">
                            <strong>Address</strong>
                            <span>{employee.address || "N/A"}</span>
                        </div>
                        <div className="profile-row">
                            <strong>Salary</strong>
                            <span>
                                {employee.salary != null
                                    ? `$${employee.salary}`
                                    : "N/A"}
                            </span>
                        </div>
                        <div className="profile-row">
                            <strong>Qualification</strong>
                            <span>{employee.qualification || "N/A"}</span>
                        </div>
                        <div className="profile-row">
                            <strong>Experience</strong>
                            <span>
                                {employee.experience != null
                                    ? `${employee.experience} years`
                                    : "N/A"}
                            </span>
                        </div>
                        <div className="profile-row">
                            <strong>Available</strong>
                            <span>
                                {employee.is_available ? "Yes" : "No"}
                            </span>
                        </div>
                    </div>
                )}

            </div>
        </MainLayout>
    );
}

export default AdminEmployeeDetails;
