const BASE = "https://to-do-list-30-production.up.railway.app";  // ← add Django's port explicitly


function getToken() {
  return localStorage.getItem("access_token");
}

function authHeaders(hasBody = true) {
    const headers = { "Authorization": `Bearer ${getToken()}` };
    if (hasBody) headers["Content-Type"] = "application/x-www-form-urlencoded";
    return headers;
}

// add this helper at the top of api.js
function toUTCString(localDatetime) {
    if (!localDatetime) return "";
    return new Date(localDatetime).toISOString();
}

export async function login(username, password) {
  const res = await fetch(`${BASE}/api/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password })
  });
  if (!res.ok) throw new Error("Invalid credentials");
  const data = await res.json();
  localStorage.setItem("access_token", data.access);
}



export async function register(username, password) {
    const res = await fetch(`${BASE}/api/auth/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password })
    });
    // if (!res.ok) throw new Error("Registration failed");
    if (!res.ok) {
        const err = await res.json();
        console.log("REGISTER ERROR:", err);  // ← add this
        throw new Error("Registration failed");
    }


    // ⚠️ Django register doesn't auto-login, so call login separately
    await login(username, password);

}


export function logout() {
  localStorage.removeItem("access_token");
  window.location.href = "/to-do-list-3.0/login";
}

// ── Tasks ──────────────────────────────────────────────
export async function getTasks() {
  const res = await fetch(`${BASE}/api/tasks/`, { headers: authHeaders(false) });
  if (res.status === 401) { logout(); return; }
  return res.json();
}

export async function addTask(title, description, deadline, category) {
    const res = await fetch(`${BASE}/api/tasks/add/`, {
        method: "POST",
        headers: authHeaders(),
        body: new URLSearchParams({ 
            title, 
            description, 
            deadline: toUTCString(deadline),  // ← convert
            category 
        })
    });
    if (!res.ok) throw new Error(`${res.status}: ${res.statusText}`);
    return res.json();
}


export async function updateTaskTitle(id, title) {
    const res = await fetch(`${BASE}/api/tasks/${id}/title/`, {
        method: "PATCH",
        headers: authHeaders(),
        body: new URLSearchParams({ title })
    });
    if (!res.ok) throw new Error("Failed to update task");
    return res.json();
}

export async function updateTaskDescription(id, description) {
    const res = await fetch(`${BASE}/api/tasks/${id}/description/`, {
        method: "PATCH",
        headers: authHeaders(),
        body: new URLSearchParams({ description })
    });
    if (!res.ok) throw new Error("Failed to update description");
    return res.json();
}

export async function updateTaskDeadline(id, deadline) {
    const res = await fetch(`${BASE}/api/tasks/${id}/deadline/`, {
        method: "PATCH",
        headers: authHeaders(),
        body: new URLSearchParams({ deadline: toUTCString(deadline) })  // ← convert
    });
    if (!res.ok) throw new Error("Failed to update deadline");
    return res.json();
}

export async function updateTaskCategory(id, category) {
    const res = await fetch(`${BASE}/api/tasks/${id}/category/`, {
        method: "PATCH",
        headers: authHeaders(),
        body: new URLSearchParams({ category })
    });
    if (!res.ok) throw new Error("Failed to update category");
    return res.json();
}
export async function toggleTask(id) {
    const res = await fetch(`${BASE}/api/tasks/${id}/toggle/`, {
        method: "PATCH",
        headers: authHeaders(false) 
    });
    if (!res.ok) throw new Error("Failed to toggle task");
    return res.json();
}

export async function deleteTask(id) {
    const res = await fetch(`${BASE}/api/tasks/${id}/delete/`, {
    method: "DELETE",
    headers: authHeaders(false)
  });
    if (!res.ok) throw new Error("Failed to delete task");
}


// ── Categories ─────────────────────────────────────────

export async function getCategories() {
    const res = await fetch(`${BASE}/api/categories/`, { headers: authHeaders(false) });
    if (res.status === 401) { logout(); return; }
    return res.json();
}

export async function addCategory(name, icon = "🏷️") {
    const res = await fetch(`${BASE}/api/categories/add/`, {
        method: "POST",
        headers: authHeaders(),
        body: new URLSearchParams({ name, icon })
    });
    if (!res.ok) throw new Error("Failed to add category");
    return res.json();
}

export async function updateCategory(id, name, icon) {
    const res = await fetch(`${BASE}/api/categories/${id}/update/`, {
        method: "PATCH",
        headers: authHeaders(),
        body: new URLSearchParams({ name, icon })
    });
    if (!res.ok) throw new Error("Failed to update category");
    return res.json();
}

export async function deleteCategory(id) {
    const res = await fetch(`${BASE}/api/categories/${id}/delete/`, {
        method: "DELETE",
        headers: authHeaders(false)
    });
    if (!res.ok) throw new Error("Failed to delete category");
}