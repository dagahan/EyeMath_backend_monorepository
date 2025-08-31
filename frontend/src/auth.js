import { isAuthed } from "./api/client.js";

// Auth state management
let authState = {
  isAuthenticated: false,
  listeners: []
};

// Initialize auth state
export function initAuth() {
  authState.isAuthenticated = isAuthed();
  updateAuthUI();
}

// Subscribe to auth state changes
export function onAuthChange(callback) {
  authState.listeners.push(callback);
  
  return () => {
    authState.listeners = authState.listeners.filter(cb => cb !== callback);
  };
}

// Update auth state
export function setAuthState(isAuthenticated) {
  authState.isAuthenticated = isAuthenticated;
  authState.listeners.forEach(callback => callback(isAuthenticated));
  updateAuthUI();
}

// Update UI based on auth state
function updateAuthUI() {
  const authOutElements = document.querySelectorAll('[data-auth="out"]');
  const authInElements = document.querySelectorAll('[data-auth="in"]');
  
  if (authState.isAuthenticated) {
    authOutElements.forEach(el => el.style.display = 'none');
    authInElements.forEach(el => el.style.display = 'inline-flex');
  } else {
    authOutElements.forEach(el => el.style.display = 'inline-flex');
    authInElements.forEach(el => el.style.display = 'none');
  }
}

// Check if user is authenticated
export function isAuthenticated() {
  return authState.isAuthenticated;
}