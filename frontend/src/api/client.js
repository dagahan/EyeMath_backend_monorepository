import { CONFIG, API_ENDPOINTS } from '../core/config.js';
import { STORAGE_KEYS } from '../core/constants.js';
import { showNotification } from '../core/utils.js';

const API_BASE = CONFIG.API_BASE.replace(/\/+$/, "");

let tokens = {
  access: localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) || "",
  refresh: localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN) || "",
};

export function setTokens(access, refresh) {
  tokens.access = access || "";
  tokens.refresh = refresh || "";
  
  if (access) {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access);
  } else {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
  }
  
  if (refresh) {
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refresh);
  } else {
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  }
  
  if (typeof window !== 'undefined' && window.setAuthState) {
    window.setAuthState(!!access);
  }
}

export function isAuthed() {
  return !!tokens.access || !!tokens.refresh;
}

async function validateAccess() {
  if (!tokens.access) return false;
  
  const url = new URL(API_BASE + API_ENDPOINTS.TOKENS.ACCESS);
  url.searchParams.set("access_token", tokens.access);
  
  try {
    const response = await fetch(url, { 
      method: "GET",
      headers: {
        "Content-Type": "application/json"
      }
    });
    
    if (!response.ok) {
      console.warn('Token validation failed with status:', response.status);
      return false;
    }
    
    const data = await response.json();
    return !!data.valid;
  } catch (error) {
    console.error('Token validation failed:', error);
    return false;
  }
}

async function refreshAccess() {
  if (!tokens.refresh) return false;
  
  try {
    const response = await fetch(API_BASE + API_ENDPOINTS.TOKENS.REFRESH, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: tokens.refresh }),
    });
    
    if (!response.ok) return false;
    
    const data = await response.json();
    if (data.access_token) {
      setTokens(data.access_token, data.refresh_token || tokens.refresh);
    }
    
    return !!data.access_token;
  } catch (error) {
    console.error('Token refresh failed:', error);
    return false;
  }
}

export async function ensureAccess() {
  if (await validateAccess()) return true;
  return await refreshAccess();
}

export async function json(method, path, body) {
  try {
    const response = await fetch(API_BASE + path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    
    const text = await response.text();
    let data = null;
    
    try {
      data = text ? JSON.parse(text) : null;
    } catch (parseError) {
      console.error('Failed to parse response:', parseError);
      data = { detail: 'Invalid response format' };
    }
    
    if (!response.ok) {
      // Better error handling for 422 errors
      if (response.status === 422 && data && Array.isArray(data)) {
        const errorMessages = data.map(err => err.msg || err.message || 'Validation error').join(', ');
        throw new Error(errorMessages);
      }
      throw new Error(data?.detail || data?.message || response.statusText);
    }
    
    return data;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

export async function authJson(method, path, body) {
  if (!(await ensureAccess())) {
    throw new Error("Unauthorized");
  }
  
  try {
    const response = await fetch(API_BASE + path, {
      method,
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${tokens.access}`,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
    
    if (response.status === 401 && await refreshAccess()) {
      return authJson(method, path, body);
    }
    
    const text = await response.text();
    const data = text ? JSON.parse(text) : null;
    
    if (!response.ok) {
      throw new Error(data?.detail || response.statusText);
    }
    
    return data;
  } catch (error) {
    console.error('Authenticated API request failed:', error);
    throw error;
  }
}

export async function authForm(path, formData, signal) {
  if (!(await ensureAccess())) {
    throw new Error("Unauthorized");
  }
  
  try {
    const response = await fetch(API_BASE + path, {
      method: "POST",
      headers: { "Authorization": `Bearer ${tokens.access}` },
      body: formData,
      signal: signal
    });
    
    if (response.status === 401 && await refreshAccess()) {
      return authForm(path, formData, signal);
    }
    
    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      throw new Error(data?.detail || response.statusText);
    }
    
    return data;
  } catch (error) {
    console.error('Form API request failed:', error);
    throw error;
  }
}

export async function register({ user_name, email, password, first_name, last_name, middle_name, phone }) {
  const data = await json("POST", API_ENDPOINTS.AUTH.REGISTER, { 
    user_name, 
    email, 
    password, 
    first_name, 
    last_name,
    middle_name: middle_name || "",
    phone: phone || null, // Send null if not provided, let backend handle default
    dsh: "default",
    role: "user"
  });
  
  if (data?.access_token) {
    setTokens(data.access_token, data.refresh_token);
    showNotification("Registration successful!", "success");
  }
  
  return data;
}

export async function login(loginData) {
  const data = await json("POST", API_ENDPOINTS.AUTH.LOGIN, loginData);
  
  if (data?.access_token) {
    setTokens(data.access_token, data.refresh_token);
    showNotification("Login successful!", "success");
  }
  
  return data;
}

export function logout() {
  setTokens("", "");
  showNotification("Logged out successfully", "info");
}
