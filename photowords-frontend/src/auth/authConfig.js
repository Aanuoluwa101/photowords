// src/auth/authConfig.js
const authConfig = {
  clientId: process.env.REACT_APP_CLIENT_ID,
  clientSecret: process.env.REACT_APP_CLIENT_SECRET,
  redirectUri: "http://localhost:3000/callback",
  tokenUrl: process.env.REACT_APP_TOKEN_URL,
  authUrl: process.env.REACT_APP_AUTH_URL, // Cognito hosted UI
};

export default authConfig;
