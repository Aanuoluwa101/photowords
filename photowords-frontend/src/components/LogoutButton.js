// src/components/LogoutButton.js
import React from "react";
import { useNavigate } from "react-router-dom";
import { logout } from "../auth/logout";

function LogoutButton() {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/admin/signin");
  };

  return (
    <button onClick={handleLogout}>
      Logout
    </button>
  );
}

export default LogoutButton;
