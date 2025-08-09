export function logout() {
  localStorage.removeItem("token"); // or whatever key you use
}
