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



import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Admin from "./pages/Admin";
import Callback from "./pages/Callback";
import UserGame from "./UserGame";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UserGame />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/callback" element={<Callback />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

