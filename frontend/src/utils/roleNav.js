const ROLE_DASHBOARDS = {
    admin: "/admin/dashboard",
    doctor: "/doctor/dashboard",
    nurse: "/nurse/dashboard",
    receptionist: "/receptionist/dashboard",
    pharmacist: "/pharmacist/dashboard",
    lab_technician: "/lab-technician/dashboard",
    accountant: "/accountant/dashboard",
};

export function roleDashboardPath(roleName) {
    if (!roleName) {
        return null;
    }
    return ROLE_DASHBOARDS[roleName.toLowerCase()] || null;
}

export const MEMBER_FALLBACK = "/member/dashboard";