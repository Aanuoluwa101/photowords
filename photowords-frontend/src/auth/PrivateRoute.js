// src/auth/PrivateRoute.js
import React from "react";
import { Navigate } from "react-router-dom";
import authConfig from "./authConfig";

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("id_token");

  if (!token) {
    // Redirect to Cognito Hosted UI
    const loginUrl = `${authConfig.authUrl}?client_id=${authConfig.clientId}&response_type=code&scope=openid+profile+email&redirect_uri=${encodeURIComponent(authConfig.redirectUri)}`;
    window.location.href = loginUrl;
    return null;
  }

  return children;
};

export default PrivateRoute;
