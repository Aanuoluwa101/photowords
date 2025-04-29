import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Callback from "./Callback";

const App = () => {
  // const navigate = useNavigate();

  const handleSignIn = () => {
    const domain = "https://eu-west-2imng8pdh4.auth.eu-west-2.amazoncognito.com";
    const clientId = "r5n1u8dodck65qnftsc26bb4u";
    const redirectUri = "http://localhost:3000/callback";
    const responseType = "code";

    window.location.href = `${domain}/login?client_id=${clientId}&response_type=${responseType}&scope=email+openid&redirect_uri=${redirectUri}`;
    // window.location.href = "https://eu-west-2imng8pdh4.auth.eu-west-2.amazoncognito.com/login/continue?client_id=r5n1u8dodck65qnftsc26bb4u&redirect_uri=https%3A%2F%2Fd84l1y8p4kdic.cloudfront.net&response_type=token&scope=email+openid"
  
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Cognito Auth Demo</h1>
      <button onClick={handleSignIn}>Sign In with Cognito</button>
    </div>
  );
};

export default function RootApp() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/callback" element={<Callback />} />
      </Routes>
    </Router>
  );
}
