// import React from "react";
// import { BrowserRouter, Routes, Route } from "react-router-dom";
// import Admin from "./pages/Admin";
// import Callback from "./pages/Callback";
// import PrivateRoute from "./auth/PrivateRoute";
// import UserGame from "./UserGame";

// function App() {
//   return (
//     <BrowserRouter>
//       <Routes>
//         <Route path="/" element={<UserGame />} />
//         <Route
//           path="/admin"
//           element={
//             <PrivateRoute>
//               <Admin />
//             </PrivateRoute>
//           }
//         />
//         <Route path="/callback" element={<Callback />} />
//       </Routes>
//     </BrowserRouter>
//   );
// }

// export default App;



// import React from "react";
// import { BrowserRouter, Routes, Route } from "react-router-dom";
// import Callback from "./pages/Callback";
// import UserGame from "./UserGame";
// import Admin from "./pages/Admin";
// import AdminHome from "./pages/AdminHome";
// import AdminImages from "./pages/AdminImages";
// import AdminGroups from "./pages/AdminGroups";

// function App() {
//   return (
//     <BrowserRouter>
//       <Routes>
//         <Route path="/" element={<UserGame />} />
//         <Route path="/callback" element={<Callback />} />
        
//         {/* Admin Section */}
//         <Route path="/admin" element={<Admin />}>
//           <Route index element={<AdminHome />} />
//           <Route path="images" element={<AdminImages />} />
//           <Route path="groups" element={<AdminGroups />} />
//         </Route>
//       </Routes>
//     </BrowserRouter>
//   );
// }

// export default App;



// src/App.js
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Callback from "./pages/Callback";
import UserGame from "./UserGame";
import Admin from "./pages/Admin";
import AdminHome from "./pages/AdminHome";
import AdminImages from "./pages/AdminImages";
import AdminGroups from "./pages/AdminGroups";
import AdminSignIn from "./pages/AdminSignIn";
import PrivateRoute from "./auth/PrivateRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UserGame />} />
        <Route path="/callback" element={<Callback />} />
        <Route path="/admin/signin" element={<AdminSignIn />} />

        {/* Protected Admin Section */}
        <Route path="/admin" element={<PrivateRoute />}>
          <Route element={<Admin />}>
            <Route index element={<AdminHome />} />
            <Route path="images" element={<AdminImages />} />
            <Route path="groups" element={<AdminGroups />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
