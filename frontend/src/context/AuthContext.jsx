import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {

    const [token, setToken] = useState(
        localStorage.getItem("access_token")
    );

    const [accountType, setAccountType] = useState(
        localStorage.getItem("account_type")
    );

    const [userId, setUserId] = useState(
        localStorage.getItem("user_id")
    );

    const [roleId, setRoleId] = useState(
        localStorage.getItem("role_id")
    );

    const [userName, setUserName] = useState(
        localStorage.getItem("user_name")
    );

    const [roleName, setRoleName] = useState(
        localStorage.getItem("role_name")
    );

    const login = (
        accessToken,
        type,
        id = null,
        role = null,
        name = null,
        roleName = null
    ) => {

        localStorage.setItem(
            "access_token",
            accessToken
        );

        localStorage.setItem(
            "account_type",
            type
        );

        if (id !== null && id !== undefined) {
            localStorage.setItem(
                "user_id",
                id
            );
        }

        if (role !== null && role !== undefined) {
            localStorage.setItem(
                "role_id",
                role
            );
        }

        if (name !== null && name !== undefined) {
            localStorage.setItem(
                "user_name",
                name
            );
        }

        if (roleName !== null && roleName !== undefined) {
            localStorage.setItem(
                "role_name",
                roleName
            );
        }

        setToken(accessToken);
        setAccountType(type);
        setUserId(id);
        setRoleId(role);
        setUserName(name);
        setRoleName(roleName);
    };

    const logout = () => {

        localStorage.removeItem("access_token");
        localStorage.removeItem("account_type");
        localStorage.removeItem("user_id");
        localStorage.removeItem("role_id");
        localStorage.removeItem("user_name");
        localStorage.removeItem("role_name");

        setToken(null);
        setAccountType(null);
        setUserId(null);
        setRoleId(null);
        setUserName(null);
        setRoleName(null);
    };

    const isAuthenticated = Boolean(token);

    return (
        <AuthContext.Provider
            value={{
                token,
                accountType,
                userId,
                roleId,
                userName,
                roleName,
                isAuthenticated,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}