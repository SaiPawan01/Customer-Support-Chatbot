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
        withCredentials: true
    });
}