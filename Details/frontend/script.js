// app.js
const API_BASE = "http://localhost:3000/api";
let token = null;
let currentUser = null;

function showSection(id) {
  document.querySelectorAll("section").forEach(sec => sec.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}

function setOutput(msg) {
  document.getElementById("output").textContent = typeof msg === "string" ? msg : JSON.stringify(msg, null, 2);
}

// Register
document.getElementById("registerForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = {
    institution_id: 1,
    id_number: document.getElementById("reg_idnum").value,
    name: document.getElementById("reg_name").value,
    email: document.getElementById("reg_email").value,
    password: document.getElementById("reg_password").value,
    role: document.getElementById("reg_role").value
  };
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  setOutput(await res.json());
});

// Login
document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = {
    email: document.getElementById("login_email").value,
    password: document.getElementById("login_password").value
  };
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  const result = await res.json();
  if (result.token) {
    token = result.token;
    currentUser = result.user;
    setOutput("Login successful: " + currentUser.role);
    if (currentUser.role === "student") showSection("studentDashboard");
    if (currentUser.role === "lecturer") showSection("lecturerDashboard");
    if (currentUser.role === "admin") showSection("adminDashboard");
  } else {
    setOutput(result);
  }
});

// Student: Submit report
document.getElementById("submitReportForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = {
    template_id: document.getElementById("student_template").value,
    submission_values: { report: document.getElementById("student_report").value }
  };
  const res = await fetch(`${API_BASE}/submissions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify(data)
  });
  setOutput(await res.json());
});

async function loadMySubmissions() {
  const res = await fetch(`${API_BASE}/submissions/my`, {
    headers: { "Authorization": "Bearer " + token }
  });
  document.getElementById("student_submissions").textContent = JSON.stringify(await res.json(), null, 2);
}

// Lecturer: Create Template
document.getElementById("createTemplateForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = {
    title: document.getElementById("template_title").value,
    description: document.getElementById("template_desc").value,
    fields: JSON.parse(document.getElementById("template_fields").value)
  };
  const res = await fetch(`${API_BASE}/templates`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify(data)
  });
  setOutput(await res.json());
});

async function loadTemplates() {
  const res = await fetch(`${API_BASE}/templates`);
  const templates = await res.json();
  document.getElementById("lecturer_templates").textContent = JSON.stringify(templates, null, 2);

  // Populate student select
  const select = document.getElementById("student_template");
  select.innerHTML = "";
  templates.forEach(t => {
    const opt = document.createElement("option");
    opt.value = t.id;
    opt.textContent = t.title;
    select.appendChild(opt);
  });
}