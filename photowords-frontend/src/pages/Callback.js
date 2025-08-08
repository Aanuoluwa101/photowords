// src/pages/Callback.js
import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import authConfig from "../auth/authConfig";

const Callback = () => {
  const [error, setError] = useState(null);
  const hasFetched = useRef(false);

  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;

    const fetchTokens = async () => {
      const params = new URLSearchParams(window.location.search);
      const code = params.get("code");

      if (!code) {
        setError("Authorization code not found.");
        return;
      }

      const basicAuth = btoa(`${authConfig.clientId}:${authConfig.clientSecret}`);

      try {
        const response = await axios.post(
          authConfig.tokenUrl,
          new URLSearchParams({
            grant_type: "authorization_code",
            client_id: authConfig.clientId,
            code: code,
            redirect_uri: authConfig.redirectUri,
          }),
          {
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
              Authorization: `Basic ${basicAuth}`,
            },
          }
        );

        // Store tokens in localStorage
        localStorage.setItem("id_token", response.data.id_token);
        localStorage.setItem("access_token", response.data.access_token);

        // Redirect to admin dashboard
        window.location.href = "/admin";
      } catch (err) {
        console.error(err);
        setError("Failed to fetch tokens");
      }
    };

    fetchTokens();
  }, []);

  if (error) return <div>Error: {error}</div>;
  return <div>Logging you in...</div>;
};

export default Callback;
