
import { initTheme } from "./theme.js";
import { startRouter, route } from "./router.js";
import Home from "./pages/Home.js";
import Recognize from "./pages/Recognize.js";
import Render from "./pages/Render.js";
import Solve from "./pages/Solve.js";
import { Login, Register } from "./pages/Auth.js";
import { logout } from "./api/client.js";
import { initAuth, setAuthState, isAuthenticated } from "./auth.js";
import "./animations.js";

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initAuth();
});

// Make setAuthState available globally for API client
window.setAuthState = setAuthState;

const app = document.getElementById("app");

route("/", () => {
  const homeElement = Home();
  return homeElement;
});
route("/recognize", () => {
  if (!isAuthenticated()) {
    location.hash = "#/login";
    return;
  }
  return Recognize();
});
route("/render", () => {
  if (!isAuthenticated()) {
    location.hash = "#/login";
    return;
  }
  return Render();
});
route("/solve", () => {
  if (!isAuthenticated()) {
    location.hash = "#/login";
    return;
  }
  return Solve();
});
route("/login", () => Login());
route("/register", () => Register());

startRouter(app);

// Handle logout button
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", ()=>{
    logout();
    setAuthState(false);
    location.hash = "#/login";
  });
}