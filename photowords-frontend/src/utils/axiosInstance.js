// src/utils/axiosInstance.js
import axios from "axios";

const axiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
});

// Add a response interceptor
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token
      localStorage.removeItem("id_token");
      // Redirect to login page
      window.location.href = "/admin/signin"; // change if your login path is different
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
