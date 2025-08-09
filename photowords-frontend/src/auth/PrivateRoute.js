// src/auth/PrivateRoute.js
import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { jwtDecode } from 'jwt-decode';

// Check if token exists and is not expired
const isAuthenticated = () => {
  const token = localStorage.getItem("id_token");
  if (!token) return false;

  try {
    const { exp } = jwtDecode(token);
    return exp * 1000 > Date.now(); // expiration is in seconds, Date.now() is ms
  } catch (err) {
    return false;
  }
};

const PrivateRoute = () => {
  return isAuthenticated() ? <Outlet /> : <Navigate to="/admin/signin" />;
};

export default PrivateRoute;
