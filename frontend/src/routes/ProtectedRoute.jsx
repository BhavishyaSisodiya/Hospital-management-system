import { Navigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

function ProtectedRoute({
    children,
    allowedAccountTypes,
    allowedRoles,
}) {
    const {
        isAuthenticated,
        accountType,
        roleId,
    } = useAuth();

    // User is not logged in
    if (!isAuthenticated) {
        return (
            <Navigate
                to="/login"
                replace
            />
        );
    }

    // User's account type is not allowed
    if (
        allowedAccountTypes &&
        !allowedAccountTypes.includes(accountType)
    ) {
        return (
            <Navigate
                to="/unauthorized"
                replace
            />
        );
    }

    // Role authorization
    // Only checked when allowedRoles is provided
    if (
        allowedRoles &&
        !allowedRoles.includes(Number(roleId))
    ) {
        return (
            <Navigate
                to="/unauthorized"
                replace
            />
        );
    }

    // User is authenticated and authorized
    return children;
}

export default ProtectedRoute;