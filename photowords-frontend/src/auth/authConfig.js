// src/auth/authConfig.js
const authConfig = {
  clientId: process.env.REACT_APP_CLIENT_ID,
  clientSecret: process.env.REACT_APP_CLIENT_SECRET,
  redirectUri: process.env.REACT_APP_REDIRECT_URI,
  tokenUrl: process.env.REACT_APP_TOKEN_URL,
  domain: process.env.REACT_APP_COGNITO_DOMAIN,
};

export default authConfig;
