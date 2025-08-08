import React from "react";
import { Link, Routes, Route, Navigate } from "react-router-dom";

import AdminHome from "./AdminHome";
import AdminImages from "./AdminImages";
import AdminGroups from "./AdminGroups";

const Admin = () => {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Sidebar */}
      <aside
        style={{
          width: "220px",
          background: "#1f2937",
          color: "white",
          padding: "20px 10px",
        }}
      >
        <h2 style={{ marginBottom: "30px" }}>Admin</h2>
        <nav style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
          <Link to="" style={linkStyle}>Home</Link>
          <Link to="images" style={linkStyle}>Images</Link>
          <Link to="groups" style={linkStyle}>Groups</Link>
        </nav>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, padding: "20px" }}>
        <Routes>
          <Route index element={<AdminHome />} />
          <Route path="images" element={<AdminImages />} />
          <Route path="groups" element={<AdminGroups />} />
          {/* Fallback */}
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
