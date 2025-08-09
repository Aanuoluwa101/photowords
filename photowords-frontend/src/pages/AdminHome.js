import React, { useEffect, useState } from "react";
import axiosInstance from "../utils/axiosInstance";

const AdminHome = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  const baseUrl = process.env.REACT_APP_API_BASE_URL;


  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      const token = localStorage.getItem("id_token");
      const response = await axiosInstance.get(`${baseUrl}/admin/summary`, {
        headers: {
          Authorization: token,
        },
      });

      setSummary(response.data);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error("Error fetching summary:", err);
      let message = "Failed to load dashboard data. Please try again.";
      if (err.response?.data?.error) {
        message = err.response.data.error;
      }
      setError(message);
      setTimeout(() => setError(null), 4000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1 style={{ marginBottom: "1rem" }}>Admin Dashboard</h1>

      {success && <div style={{ color: "green", marginBottom: "1rem" }}>{success}</div>}
      {error && <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>}

      {loading ? (
        <p>Loading dashboard...</p>
      ) : summary ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem" }}>
          <div style={cardStyle}>
            <h3>Images</h3>
            <p style={valueStyle}>{summary.num_images}</p>
          </div>
          <div style={cardStyle}>
            <h3>Groups</h3>
            <p style={valueStyle}>{summary.num_groups}</p>
          </div>
          <div style={cardStyle}>
            <h3>Active Game Attempts</h3>
            <p style={valueStyle}>{summary.num_active_game_attempts}</p>
          </div>
          <div style={cardStyle}>
            <h3>Completed Game Attempts</h3>
            <p style={valueStyle}>{summary.num_completed_game_attempts}</p>
          </div>
        </div>
      ) : (
        <p>No dashboard data available.</p>
      )}
    </div>
  );
};

const cardStyle = {
  background: "#fff",
  padding: "1.5rem",
  borderRadius: "8px",
  boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  textAlign: "center",
};

const valueStyle = {
  fontSize: "1.8rem",
  fontWeight: "bold",
  color: "#333",
  marginTop: "0.5rem",
};

export default AdminHome;
