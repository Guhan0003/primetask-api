/**
 * PrimeTask - Frontend Application
 * A Scalable Task Management System
 */

// ==========================================
// Configuration
// ==========================================
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// ==========================================
// State Management
// ==========================================
let currentUser = null;
let accessToken = null;
let refreshToken = null;

// ==========================================
// Initialization
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // Check for existing session
    const savedAccessToken = localStorage.getItem('accessToken');
    const savedRefreshToken = localStorage.getItem('refreshToken');
    const savedUser = localStorage.getItem('user');

    if (savedAccessToken && savedRefreshToken && savedUser) {
        accessToken = savedAccessToken;
        refreshToken = savedRefreshToken;
        currentUser = JSON.parse(savedUser);
        showDashboard();
    }
});

// ==========================================
// Auth Functions
// ==========================================
function showLogin() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
}

function showRegister() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            // Save tokens and user info
            accessToken = data.access;
            refreshToken = data.refresh;
            currentUser = data.user;

            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('refreshToken', refreshToken);
            localStorage.setItem('user', JSON.stringify(currentUser));

            showToast('Login successful!', 'success');
            showDashboard();
        } else {
            const errorMsg = data.detail || 'Invalid credentials';
            showToast(errorMsg, 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Connection error. Please check if the server is running.', 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const passwordConfirm = document.getElementById('regPasswordConfirm').value;

    if (password !== passwordConfirm) {
        showToast('Passwords do not match', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                email,
                password,
                password_confirm: passwordConfirm,
            }),
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Save tokens and user info
            accessToken = data.data.tokens.access;
            refreshToken = data.data.tokens.refresh;
            currentUser = data.data.user;

            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('refreshToken', refreshToken);
            localStorage.setItem('user', JSON.stringify(currentUser));

            showToast('Registration successful!', 'success');
            showDashboard();
        } else {
            // Handle validation errors
            let errorMsg = 'Registration failed';
            if (data.errors) {
                const firstError = Object.values(data.errors)[0];
                errorMsg = Array.isArray(firstError) ? firstError[0] : firstError;
            } else if (data.message) {
                errorMsg = data.message;
            }
            showToast(errorMsg, 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Connection error. Please check if the server is running.', 'error');
    }
}

async function logout() {
    try {
        await fetch(`${API_BASE_URL}/auth/logout/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`,
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });
    } catch (error) {
        console.error('Logout error:', error);
    }

    // Clear local storage
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');

    accessToken = null;
    refreshToken = null;
    currentUser = null;

    showToast('Logged out successfully', 'success');
    showAuth();
}

// ==========================================
// Token Refresh
// ==========================================
async function refreshAccessToken() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        if (response.ok) {
            const data = await response.json();
            accessToken = data.access;
            if (data.refresh) {
                refreshToken = data.refresh;
                localStorage.setItem('refreshToken', refreshToken);
            }
            localStorage.setItem('accessToken', accessToken);
            return true;
        } else {
            // Refresh token expired, logout
            logout();
            return false;
        }
    } catch (error) {
        console.error('Token refresh error:', error);
        return false;
    }
}

// ==========================================
// API Helper
// ==========================================
async function apiRequest(endpoint, method = 'GET', body = null, retry = true) {
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
    };

    const options = {
        method,
        headers,
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        // Handle 401 - try to refresh token
        if (response.status === 401 && retry) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                return apiRequest(endpoint, method, body, false);
            }
        }

        return response;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// ==========================================
// View Switching
// ==========================================
function showAuth() {
    document.getElementById('authSection').style.display = 'flex';
    document.getElementById('dashboardSection').style.display = 'none';
    document.getElementById('navbar').style.display = 'none';
    
    // Reset forms
    document.getElementById('loginEmail').value = '';
    document.getElementById('loginPassword').value = '';
    showLogin();
}

function showDashboard() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('dashboardSection').style.display = 'block';
    document.getElementById('navbar').style.display = 'flex';

    // Update navbar
    document.getElementById('navUsername').textContent = currentUser.username;
    const roleEl = document.getElementById('navRole');
    roleEl.textContent = currentUser.role;
    roleEl.className = `badge ${currentUser.role}`;

    // Show admin section if admin
    if (currentUser.role === 'admin') {
        document.getElementById('adminSection').style.display = 'block';
        loadUsers();
        loadAllTasks();
    } else {
        document.getElementById('adminSection').style.display = 'none';
    }

    // Load data
    loadStats();
    loadTasks();
}

// ==========================================
// Dashboard Functions
// ==========================================
async function loadStats() {
    try {
        const response = await apiRequest('/tasks/stats/');
        
        if (response.ok) {
            const result = await response.json();
            const data = result.data;

            document.getElementById('statTotal').textContent = data.total;
            document.getElementById('statPending').textContent = data.pending;
            document.getElementById('statInProgress').textContent = data.in_progress;
            document.getElementById('statCompleted').textContent = data.completed;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadTasks() {
    const taskList = document.getElementById('taskList');
    taskList.innerHTML = '<div class="loading">Loading tasks...</div>';

    try {
        const statusFilter = document.getElementById('filterStatus').value;
        const priorityFilter = document.getElementById('filterPriority').value;

        let endpoint = '/tasks/';
        const params = new URLSearchParams();
        if (statusFilter) params.append('status', statusFilter);
        if (priorityFilter) params.append('priority', priorityFilter);
        if (params.toString()) endpoint += `?${params.toString()}`;

        const response = await apiRequest(endpoint);

        if (response.ok) {
            const data = await response.json();
            const tasks = data.results || data;

            if (tasks.length === 0) {
                taskList.innerHTML = `
                    <div class="empty-state">
                        <div class="icon">📝</div>
                        <p>No tasks found. Create your first task!</p>
                    </div>
                `;
            } else {
                taskList.innerHTML = tasks.map(task => createTaskHTML(task)).join('');
            }
        } else {
            taskList.innerHTML = '<div class="empty-state"><p>Error loading tasks</p></div>';
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
        taskList.innerHTML = '<div class="empty-state"><p>Error loading tasks</p></div>';
    }
}

function createTaskHTML(task) {
    const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date';
    
    return `
        <div class="task-item" data-id="${task.id}">
            <div class="task-info">
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-meta">
                    <span class="status-badge status-${task.status}">${task.status.replace('_', ' ')}</span>
                    <span class="priority-badge priority-${task.priority}">${task.priority}</span>
                    <span>📅 ${dueDate}</span>
                    ${task.owner_username ? `<span>👤 ${escapeHtml(task.owner_username)}</span>` : ''}
                </div>
            </div>
            <div class="task-actions">
                <button class="btn btn-sm btn-primary" onclick="editTask(${task.id})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteTask(${task.id})">Delete</button>
            </div>
        </div>
    `;
}

// ==========================================
// Task CRUD Functions
// ==========================================
function openTaskModal(task = null) {
    const modal = document.getElementById('taskModal');
    const modalTitle = document.getElementById('taskModalTitle');
    const form = document.getElementById('taskForm');

    if (task) {
        modalTitle.textContent = 'Edit Task';
        document.getElementById('taskId').value = task.id;
        document.getElementById('taskTitle').value = task.title;
        document.getElementById('taskDescription').value = task.description || '';
        document.getElementById('taskPriority').value = task.priority;
        document.getElementById('taskStatus').value = task.status;
        document.getElementById('taskDueDate').value = task.due_date ? task.due_date.slice(0, 16) : '';
        document.getElementById('taskStatus').disabled = false;
    } else {
        modalTitle.textContent = 'New Task';
        form.reset();
        document.getElementById('taskId').value = '';
        document.getElementById('taskStatus').value = 'pending';
        document.getElementById('taskStatus').disabled = true;
    }

    modal.style.display = 'flex';
}

function closeTaskModal() {
    document.getElementById('taskModal').style.display = 'none';
}

async function handleTaskSubmit(event) {
    event.preventDefault();

    const taskId = document.getElementById('taskId').value;
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        priority: document.getElementById('taskPriority').value,
        due_date: document.getElementById('taskDueDate').value || null,
    };

    if (taskId) {
        taskData.status = document.getElementById('taskStatus').value;
    }

    try {
        let response;
        if (taskId) {
            // Update existing task
            response = await apiRequest(`/tasks/${taskId}/`, 'PATCH', taskData);
        } else {
            // Create new task
            response = await apiRequest('/tasks/', 'POST', taskData);
        }

        if (response.ok) {
            showToast(taskId ? 'Task updated!' : 'Task created!', 'success');
            closeTaskModal();
            loadTasks();
            loadStats();
        } else {
            const data = await response.json();
            const errorMsg = data.errors ? Object.values(data.errors)[0][0] : 'Operation failed';
            showToast(errorMsg, 'error');
        }
    } catch (error) {
        console.error('Task submit error:', error);
        showToast('An error occurred', 'error');
    }
}

async function editTask(taskId) {
    try {
        const response = await apiRequest(`/tasks/${taskId}/`);
        
        if (response.ok) {
            const task = await response.json();
            openTaskModal(task);
        } else {
            showToast('Failed to load task', 'error');
        }
    } catch (error) {
        console.error('Edit task error:', error);
        showToast('An error occurred', 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }

    try {
        const response = await apiRequest(`/tasks/${taskId}/`, 'DELETE');
        
        if (response.ok || response.status === 204) {
            showToast('Task deleted!', 'success');
            loadTasks();
            loadStats();
            
            // Reload admin tasks if admin
            if (currentUser.role === 'admin') {
                loadAllTasks();
            }
        } else {
            showToast('Failed to delete task', 'error');
        }
    } catch (error) {
        console.error('Delete task error:', error);
        showToast('An error occurred', 'error');
    }
}

// ==========================================
// Admin Functions
// ==========================================
function showAdminTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    // Show/hide content
    if (tab === 'users') {
        document.getElementById('adminUsers').style.display = 'block';
        document.getElementById('adminAllTasks').style.display = 'none';
    } else {
        document.getElementById('adminUsers').style.display = 'none';
        document.getElementById('adminAllTasks').style.display = 'block';
    }
}

async function loadUsers() {
    const userList = document.getElementById('userList');
    userList.innerHTML = '<div class="loading">Loading users...</div>';

    try {
        const response = await apiRequest('/auth/admin/users/');
        
        if (response.ok) {
            const data = await response.json();
            const users = data.results || data;

            if (users.length === 0) {
                userList.innerHTML = '<div class="empty-state"><p>No users found</p></div>';
            } else {
                userList.innerHTML = users.map(user => `
                    <div class="user-item" data-id="${user.id}">
                        <div class="user-info">
                            <div class="user-email">${escapeHtml(user.email)}</div>
                            <div class="user-meta">
                                <span>@${escapeHtml(user.username)}</span>
                                <span class="badge ${user.role}">${user.role}</span>
                                <span>📋 ${user.tasks_count || 0} tasks</span>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        } else {
            userList.innerHTML = '<div class="empty-state"><p>Error loading users</p></div>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        userList.innerHTML = '<div class="empty-state"><p>Error loading users</p></div>';
    }
}

async function loadAllTasks() {
    const allTasksList = document.getElementById('allTasksList');
    allTasksList.innerHTML = '<div class="loading">Loading all tasks...</div>';

    try {
        const response = await apiRequest('/tasks/admin/all/');
        
        if (response.ok) {
            const data = await response.json();
            const tasks = data.results || data;

            if (tasks.length === 0) {
                allTasksList.innerHTML = '<div class="empty-state"><p>No tasks in the system</p></div>';
            } else {
                allTasksList.innerHTML = tasks.map(task => createTaskHTML(task)).join('');
            }
        } else {
            allTasksList.innerHTML = '<div class="empty-state"><p>Error loading tasks</p></div>';
        }
    } catch (error) {
        console.error('Error loading all tasks:', error);
        allTasksList.innerHTML = '<div class="empty-state"><p>Error loading tasks</p></div>';
    }
}

// ==========================================
// Utility Functions
// ==========================================
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal on outside click
document.addEventListener('click', (event) => {
    const modal = document.getElementById('taskModal');
    if (event.target === modal) {
        closeTaskModal();
    }
});

// Handle keyboard events
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeTaskModal();
    }
});
