import { login, register } from "../api/client.js";
import { go } from "../router.js";
import { createElement } from "../core/utils.js";

export function Login() {
  const wrap = createElement("div", "grid");
  wrap.innerHTML = `
    <div style="text-align: center; margin-bottom: 40px;">
      <div class="h1" style="background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 16px;">Sign in to eye.math</div>
      <p class="muted">Sign in to your account to access all features</p>
    </div>
    
    <div class="card" style="max-width: 400px; margin: 0 auto;">
      <form id="loginForm">
        <div style="margin-bottom: 20px;">
          <label style="display: block; margin-bottom: 8px; color: var(--text); font-weight: 500;">Login Method</label>
          <select class="select" name="loginMethod" id="loginMethod" style="width: 100%;" required>
            <option value="email">Email Address</option>
            <option value="phone">Phone Number</option>
            <option value="username">Username</option>
          </select>
        </div>
        
        <div style="margin-bottom: 20px;">
          <label style="display: block; margin-bottom: 8px; color: var(--text); font-weight: 500;" id="loginLabel">Email Address</label>
          <input 
            class="input" 
            name="loginValue" 
            id="loginValue"
            type="text" 
            placeholder="your@email.com" 
            required 
            style="width: 100%;"
          />
        </div>
        
        <div style="margin-bottom: 24px;">
          <label style="display: block; margin-bottom: 8px; color: var(--text); font-weight: 500;">Password</label>
          <input 
            class="input" 
            name="password" 
            type="password" 
            placeholder="Enter your password" 
            required 
            style="width: 100%;"
          />
        </div>
        
        <button class="btn" type="submit" id="loginBtn" style="width: 100%; margin-bottom: 20px;">
          <span id="loginText">🔑 Sign In</span>
        </button>
        
        <div style="text-align: center; padding: 20px; background: var(--surface); border-radius: 12px; border: 1px solid var(--border);">
          <p style="margin: 0 0 12px; color: var(--muted);">Don't have an account?</p>
          <a href="#/register" class="btn secondary" style="text-decoration: none; display: inline-block;">
            📝 Create Account
          </a>
        </div>
        
        <div class="notice error" id="err" style="display:none; margin-top: 20px;"></div>
      </form>
    </div>
  `;
  
  const form = wrap.querySelector("#loginForm");
  const loginBtn = wrap.querySelector("#loginBtn");
  const loginText = wrap.querySelector("#loginText");
  const err = wrap.querySelector("#err");
  const loginMethod = wrap.querySelector("#loginMethod");
  const loginValue = wrap.querySelector("#loginValue");
  const loginLabel = wrap.querySelector("#loginLabel");
  
  function updateLoginField() {
    const method = loginMethod.value;
    const labels = {
      email: "Email Address",
      phone: "Phone Number", 
      username: "Username"
    };
    const placeholders = {
      email: "your@email.com",
      phone: "+7 (999) 123-45-67",
      username: "your_username"
    };
    const types = {
      email: "email",
      phone: "tel",
      username: "text"
    };
    
    loginLabel.textContent = labels[method];
    loginValue.placeholder = placeholders[method];
    loginValue.type = types[method];
    loginValue.name = method === "username" ? "user_name" : method;
  }
  
  loginMethod.addEventListener("change", updateLoginField);
  
  form.onsubmit = async (e) => {
    e.preventDefault();
    err.style.display = "none";
    
    loginBtn.classList.add('loading');
    loginText.textContent = 'Signing in...';
    
    const formData = new FormData(form);
    const method = formData.get("loginMethod");
    const value = formData.get("loginValue");
    const password = formData.get("password");
    
    const loginData = {
      password: password,
      dsh: "default"
    };
    
    // Only set the field that was selected, leave others undefined
    if (method === "username" && value && value.trim()) {
      loginData.user_name = value.trim();
    } else if (method === "phone" && value && value.trim()) {
      loginData.phone = value.trim();
    } else if (method === "email" && value && value.trim()) {
      loginData.email = value.trim();
    }
    
    // Remove undefined fields to avoid sending them to the server
    Object.keys(loginData).forEach(key => {
      if (loginData[key] === undefined) {
        delete loginData[key];
      }
    });
    
    // Validate that at least one login field is provided
    if (!loginData.user_name && !loginData.phone && !loginData.email) {
      err.textContent = "Please enter your login information";
      err.style.display = "block";
      loginBtn.classList.remove('loading');
      loginText.textContent = '🔑 Sign In';
      return;
    }
    
    // Validate password
    if (!password || !password.trim()) {
      err.textContent = "Please enter your password";
      err.style.display = "block";
      loginBtn.classList.remove('loading');
      loginText.textContent = '🔑 Sign In';
      return;
    }
    
    try {
      console.log('Sending login data:', loginData);
      await login(loginData);
      go("/");
    } catch (ex) {
      console.error('Login error:', ex);
      err.textContent = ex.message || "Sign in failed";
      err.style.display = "block";
    } finally {
      loginBtn.classList.remove('loading');
      loginText.textContent = '🔑 Sign In';
    }
  };
  
  return wrap;
}

export function Register() {
  const wrap = createElement("div", "grid");
  wrap.innerHTML = `
    <div style="text-align: center; margin-bottom: 40px;">
      <div class="h1" style="background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 16px;">Create eye.math Account</div>
      <p class="muted">Create an account to start working with mathematical expressions</p>
    </div>
    
    <div class="card" style="max-width: 400px; margin: 0 auto;">
      <form id="registerForm">
        <div style="margin-bottom: 20px;">
          <label style="display: block; margin-bottom: 8px; color: var(--text); font-weight: 500;">Username</label>
          <input 
            class="input" 
            name="user_name" 
            placeholder="username" 
            required 
            style="width: 100%;"
          />
        </div>
        
        <div style="margin-bottom: 20px;">
          <label style="display: block; margin-bottom: 8px; color: var(--text); font-weight: 500;">Email</label>
          <input 
            class="input" 
            name="email" 
            type="email" 
            placeholder="your@email.com" 
            required 
            style="width: 100%;"
          />
        </div>
        
        <div style="margin-bottom: 20px;">
          <label style="display: block; margin-bottom: 8px; color: var(--text); font-weight: 500;">First Name</label>
          <input 
            class="input" 
            name="first_name" 
            placeholder="Your first name" 
            required 
            style="width: 100%;"
          />
        </div>
        
        <div style="margin-bottom: 20px;">
          <label style="display: block; margin-bottom: 8px; color: var(--text); font-weight: 500;">Last Name</label>
          <input 
            class="input" 
            name="last_name" 
            placeholder="Your last name" 
            required 
            style="width: 100%;"
          />
        </div>
        
        <div style="margin-bottom: 20px;">
          <label style="display: block; margin-bottom: 8px; color: var(--text); font-weight: 500;">Middle Name</label>
          <input 
            class="input" 
            name="middle_name" 
            placeholder="Your middle name" 
            required 
            style="width: 100%;"
          />
        </div>
        
        <div style="margin-bottom: 20px;">
          <label style="display: block; margin-bottom: 8px; color: var(--text); font-weight: 500;">Phone</label>
          <input 
            class="input" 
            name="phone" 
            type="tel"
            placeholder="+7 (999) 123-45-67" 
            required 
            style="width: 100%;"
          />
        </div>
        
        <div style="margin-bottom: 24px;">
          <label style="display: block; margin-bottom: 8px; color: var(--text); font-weight: 500;">Password</label>
          <input 
            class="input" 
            name="password" 
            type="password" 
            placeholder="Create a password" 
            required 
            style="width: 100%;"
          />
        </div>
        
        <button class="btn" type="submit" id="registerBtn" style="width: 100%; margin-bottom: 20px;">
          <span id="registerText">📝 Create Account</span>
        </button>
        
        <div style="text-align: center; padding: 20px; background: var(--surface); border-radius: 12px; border: 1px solid var(--border);">
          <p style="margin: 0 0 12px; color: var(--muted);">Already have an account?</p>
          <a href="#/login" class="btn secondary" style="text-decoration: none; display: inline-block;">
            🔑 Sign In
          </a>
        </div>
        
        <div class="notice error" id="err" style="display:none; margin-top: 20px;"></div>
      </form>
    </div>
  `;
  
  const form = wrap.querySelector("#registerForm");
  const registerBtn = wrap.querySelector("#registerBtn");
  const registerText = wrap.querySelector("#registerText");
  const err = wrap.querySelector("#err");
  
  form.onsubmit = async (e) => {
    e.preventDefault();
    err.style.display = "none";
    
    registerBtn.classList.add('loading');
    registerText.textContent = 'Creating...';
    
    const data = Object.fromEntries(new FormData(form).entries());
    
    try {
      console.log('Sending registration data:', data);
      await register(data);
      go("/");
    } catch (ex) {
      console.error('Registration error:', ex);
      err.textContent = ex.message || "Registration failed";
      err.style.display = "block";
    } finally {
      registerBtn.classList.remove('loading');
      registerText.textContent = '📝 Create Account';
    }
  };
  
  return wrap;
}
