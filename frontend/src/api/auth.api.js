import api from "./axios.js";

export const registerUser = (data) => {
    return api.post("/api/register/", data);
}

export const loginUser = (data) => {
    return api.post("api/login/", data, { withCredentials: true });
}

export const verifyToken = (access_token) => {
    const token = access_token;
    return api.get("api/verify-token/", {
        headers: {
            Authorization: `Bearer ${token}`
        },
        withCredentials: true
    });
}

export const refreshToken = () => {
    return api.post("api/refresh/", {}, {
        withCredentials: true
    });
};

export const logoutUser = () => {
    return api.post("api/logout/", {}, {
        headers:{
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            
        },withCredentials: true
    });
}


export const sendOtp = (email) => {
    console.log(email, typeof email)
    return api.post("api/send-otp/", { email });
}


export const verifyOtp = (email, otp) => {
    return api.post("api/verify-otp/", { email, otp });
}


export const sendResetPasswordOtp = (email) => {
    return api.post("api/reset-password-otp/",{ email});
}

export const verifyResetPasswordOtp = (email, otp) => {
    return api.post("api/reset-password-verify-otp/", { email, otp });
}

export const resetPassword = (email, new_password) => {
    return api.post("api/reset-password/", { email, new_password });
}