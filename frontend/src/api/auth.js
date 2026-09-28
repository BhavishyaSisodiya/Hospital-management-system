import api from "./axios";

export const loginUser = async (loginData) => {
  const response = await api.post("/auth/login", loginData);

  return response.data;
};

export const registerPatient = async (registerData) => {
    const response = await api.post(
        "/auth/register/patient",
        registerData
    );

    return response.data;
};