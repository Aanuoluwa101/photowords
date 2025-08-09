import React from "react";
import { Link, Routes, Route, Navigate, useNavigate } from "react-router-dom";

import AdminHome from "./AdminHome";
import AdminImages from "./AdminImages";
import AdminGroups from "./AdminGroups";

const Admin = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear any stored authentication (adjust as needed)
    localStorage.removeItem("id_token");  // or whatever key you use
    // Redirect to admin sign-in
    navigate("/admin/signin");
  };

  return (
    <div style={{ display: "flex" }}>
      {/* Sidebar */}
      <aside
    style={{
      width: "220px",
      background: "#1f2937",
      color: "white",
      padding: "20px 10px",
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      position: "fixed", // <-- Make it fixed
      top: 0,
      left: 0,
      height: "100vh", // full height
    }}
  >
        <div>
          <h2 style={{ marginBottom: "30px" }}>Admin</h2>
          <nav style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
            <Link to="" style={linkStyle}>Home</Link>
            <Link to="images" style={linkStyle}>Images</Link>
            <Link to="groups" style={linkStyle}>Groups</Link>
          </nav>
        </div>

        <button
          onClick={handleLogout}
          style={{
            marginTop: "20px",
            padding: "10px",
            backgroundColor: "#ef4444",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Logout
        </button>
      </aside>

      {/* Main Content */}
      <main
    style={{
      flex: 1,
      padding: "20px",
      marginLeft: "220px", // <-- offset for fixed sidebar width
      height: "100vh",
      overflowY: "auto", // scroll only content area
    }}
  >
        <Routes>
          <Route index element={<AdminHome />} />
          <Route path="images" element={<AdminImages />} />
          <Route path="groups" element={<AdminGroups />} />
          <Route path="*" element={<Navigate to="/admin" replace />} />
        </Routes>
      </main>
    </div>
  );
};

// Reusable link style
const linkStyle = {
  color: "white",
  textDecoration: "none",
  padding: "8px 12px",
  borderRadius: "4px",
  background: "#374151",
};

export default Admin;
