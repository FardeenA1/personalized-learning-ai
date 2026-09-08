const API_BASE = "http://127.0.0.1:8000";

function saveToken(token) {
  localStorage.setItem("styleNotesToken", token);
}

function getToken() {
  return localStorage.getItem("styleNotesToken");
}

function clearToken() {
  localStorage.removeItem("styleNotesToken");
}

function showError(message) {
  const box = document.getElementById("errorBox");
  box.textContent = message;
  box.classList.remove("hidden");
}

function hideError() {
  document.getElementById("errorBox").classList.add("hidden");
}

function setLoading(button, loading, label) {
  if (loading) {
    button.disabled = true;
    button.innerHTML = `<span class="spinner"></span> Please wait`;
  } else {
    button.disabled = false;
    button.innerHTML = label;
  }
}

// ---------------- REGISTER ----------------

async function handleRegister(event) {
  event.preventDefault();
  hideError();

  const fullName = document.getElementById("fullName").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const button = document.getElementById("submitBtn");

  setLoading(button, true);

  try {
    const response = await fetch(`${API_BASE}/users/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name: fullName, email: email, password: password })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Registration failed.");
    }

    window.location.href = "login.html?registered=true";

  } catch (err) {
    showError(err.message);
    setLoading(button, false, "Create account →");
  }
}

// ---------------- LOGIN ----------------

async function handleLogin(event) {
  event.preventDefault();
  hideError();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const button = document.getElementById("submitBtn");

  setLoading(button, true);

  try {
    const formBody = new URLSearchParams();
    formBody.append("username", email);
    formBody.append("password", password);

    const response = await fetch(`${API_BASE}/users/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formBody
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Login failed.");
    }

    saveToken(data.access_token);
    window.location.href = "dashboard.html";

  } catch (err) {
    showError(err.message);
    setLoading(button, false, "Log in →");
  }
}

// ---------------- ROUTE GUARD ----------------

function requireAuth() {
  if (!getToken()) {
    window.location.href = "login.html";
  }
}

function logout() {
  clearToken();
  window.location.href = "login.html";
}
