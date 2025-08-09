// src/pages/AdminSignIn.js
import React from "react";
import authConfig from "../auth/authConfig";

const AdminSignIn = () => {
  const handleSignIn = () => {
    const { clientId, redirectUri, domain } = authConfig;
    const responseType = "code";
    const scope = "email openid";

    window.location.href = `${domain}/login?client_id=${clientId}&response_type=${responseType}&scope=${scope}&redirect_uri=${redirectUri}`;
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="bg-white shadow-lg rounded-2xl p-8 max-w-md w-full text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          Photowords Admin Sign In
        </h1>
        <p className="text-gray-600 mb-6">
          Sign in to access the admin dashboard.
        </p>
        <button
          onClick={handleSignIn}
          className="w-full bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg shadow hover:bg-blue-700 transition-colors"
        >
          Sign In with Cognito
        </button>
        <p className="mt-6 text-xs text-gray-500">
          By signing in, you agree to our{" "}
          <a href="/terms" className="text-blue-600 hover:underline">
            Terms of Service
          </a>{" "}
          and{" "}
          <a href="/privacy" className="text-blue-600 hover:underline">
            Privacy Policy
          </a>.
        </p>
      </div>
    </div>
  );
};

export default AdminSignIn;
