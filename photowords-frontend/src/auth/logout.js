export function logout() {
  localStorage.removeItem("id_token"); // or whatever key you use
}
