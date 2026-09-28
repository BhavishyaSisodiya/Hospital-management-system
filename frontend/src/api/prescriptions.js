import api from "./axios";

export const getMyPrescriptions = async () => {
    const response = await api.get("/prescriptions/");
    return response.data;
};

export const getMyDoctorPrescriptions = async () => {
    const response = await api.get("/prescriptions/");
    return response.data;
};

export const createPrescription = async (prescriptionData) => {
    const response = await api.post(
        "/prescriptions/",
        prescriptionData
    );
    return response.data;
};

export const getDoctorPatientPrescriptions = async (patientId) => {
    const response = await api.get(
        `/prescriptions/patient/${patientId}`
    );
    return response.data;
};

export const addPrescriptionMedicine = async (medicineData) => {
    const response = await api.post(
        "/prescription-medicines/",
        medicineData
    );
    return response.data;
};

export const getPrescriptionMedicines = async () => {
    const response = await api.get(
        "/prescription-medicines/"
    );
    return response.data;
};

export const getMyPrescriptionMedicines = async () => {
    const response = await api.get(
        "/prescription-medicines/"
    );
    return response.data;
};

export const updatePrescriptionMedicine = async (
    prescriptionId,
    medicineId,
    medicineData
) => {
    const response = await api.patch(
        `/prescription-medicines/${prescriptionId}/${medicineId}`,
        medicineData
    );

    return response.data;
};