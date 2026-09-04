/**
 * auth.js - Module xác thực và tiện ích dùng chung
 */

const API_BASE = 'http://localhost:8000';

// ==================== AUTH ====================
function getToken() {
    return localStorage.getItem('token');
}

function getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

function isLoggedIn() {
    return !!getToken();
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
}

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

function requireRole(allowedRoles) {
    if (!requireAuth()) return false;
    const user = getUser();
    if (!user || !allowedRoles.includes(user.role)) {
        showToast('Bạn không có quyền truy cập vào trang này!', 'error');
        setTimeout(() => {
            window.location.href = '/dashboard.html';
        }, 1200);
        return false;
    }
    return true;
}

// ==================== API HELPER ====================
async function apiCall(endpoint, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json'
    };

    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = { method, headers };
    if (body && method !== 'GET') {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);

        if (response.status === 401) {
            logout();
            return null;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Lỗi không xác định');
        }

        return data;
    } catch (error) {
        if (error.message === 'Failed to fetch') {
            showToast('Không thể kết nối server. Hãy chắc chắn backend đang chạy.', 'error');
        } else {
            showToast(error.message, 'error');
        }
        throw error;
    }
}

// ==================== TOAST ====================
function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span> ${message}`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// ==================== MODAL ====================
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// ==================== SIDEBAR ====================
function initSidebar() {
    const user = getUser();
    if (!user) return;

    // User info
    const userNameEl = document.getElementById('user-name');
    const userRoleEl = document.getElementById('user-role');
    const userAvatarEl = document.getElementById('user-avatar');

    if (userNameEl) userNameEl.textContent = user.username;
    if (userRoleEl) {
        const roleMap = {
            'chu_nhiem': 'Chủ nhiệm',
            'truong_ban': 'Trưởng ban',
            'thanh_vien': 'Thành viên'
        };
        userRoleEl.textContent = roleMap[user.role] || user.role;
    }
    if (userAvatarEl) {
        userAvatarEl.textContent = user.username.charAt(0).toUpperCase();
    }

    // Active nav item
    const currentPage = window.location.pathname.split('/').pop().replace('.html', '');
    document.querySelectorAll('.nav-item').forEach(item => {
        const href = item.getAttribute('href') || '';
        if (href.includes(currentPage)) {
            item.classList.add('active');
        }
    });

    // Hide items based on role
    if (user.role === 'thanh_vien') {
        document.querySelectorAll('.admin-only, .manager-only').forEach(el => el.style.display = 'none');
    } else if (user.role === 'truong_ban') {
        document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'none');
    }
}

// ==================== HELPERS ====================
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('vi-VN', {
        day: '2-digit', month: '2-digit', year: 'numeric'
    });
}

function formatDateTime(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('vi-VN', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function getStatusBadge(status) {
    const map = {
        'active': '<span class="badge badge-success">Hoạt động</span>',
        'inactive': '<span class="badge badge-gray">Ngừng hoạt động</span>',
        'upcoming': '<span class="badge badge-info">Sắp diễn ra</span>',
        'ongoing': '<span class="badge badge-warning">Đang diễn ra</span>',
        'completed': '<span class="badge badge-success">Hoàn thành</span>',
        'cancelled': '<span class="badge badge-danger">Đã hủy</span>',
        'not_started': '<span class="badge badge-gray">Chưa bắt đầu</span>',
        'in_progress': '<span class="badge badge-warning">Đang thực hiện</span>',
        'overdue': '<span class="badge badge-danger">Quá hạn</span>',
        'present': '<span class="badge badge-success">Có mặt</span>',
        'absent': '<span class="badge badge-danger">Vắng</span>',
        'excused': '<span class="badge badge-warning">Có phép</span>',
    };
    return map[status] || `<span class="badge badge-gray">${status}</span>`;
}

function getPriorityBadge(priority) {
    const map = {
        'low': '<span class="badge badge-gray">Thấp</span>',
        'medium': '<span class="badge badge-info">Trung bình</span>',
        'high': '<span class="badge badge-warning">Cao</span>',
        'urgent': '<span class="badge badge-danger">Khẩn cấp</span>',
    };
    return map[priority] || `<span class="badge badge-gray">${priority}</span>`;
}

function getProgressBar(progress) {
    let cls = '';
    if (progress < 30) cls = 'low';
    else if (progress < 70) cls = 'medium';
    else cls = 'high';

    return `
        <div class="progress-bar">
            <div class="progress-fill ${cls}" style="width: ${progress}%"></div>
        </div>
        <span class="progress-text">${progress}%</span>
    `;
}

// Generate sidebar HTML
function getSidebarHTML(activePage) {
    const user = getUser();
    const role = user ? user.role : '';

    return `
    <div class="sidebar-header">
        <div class="brand">
            <div class="brand-icon">🎓</div>
            <div class="brand-text">
                <h2>CLB Manager</h2>
                <span>Quản lý CLB Sinh viên</span>
            </div>
        </div>
    </div>

    <nav class="sidebar-nav">
        <div class="nav-section">
            <div class="nav-section-title">Tổng quan</div>
            <a href="/dashboard.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
                <span class="nav-icon">📊</span> Dashboard
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-section-title">Quản lý</div>
            <a href="/members.html" class="nav-item ${activePage === 'members' ? 'active' : ''}">
                <span class="nav-icon">👥</span> Thành viên
            </a>
            ${role === 'chu_nhiem' ? `
            <a href="/departments.html" class="nav-item admin-only ${activePage === 'departments' ? 'active' : ''}">
                <span class="nav-icon">🏢</span> Ban chuyên môn
            </a>` : ''}
            <a href="/activities.html" class="nav-item ${activePage === 'activities' ? 'active' : ''}">
                <span class="nav-icon">📅</span> Hoạt động
            </a>
            ${role !== 'thanh_vien' ? `
            <a href="/attendance.html" class="nav-item manager-only ${activePage === 'attendance' ? 'active' : ''}">
                <span class="nav-icon">✅</span> Điểm danh
            </a>` : ''}
            <a href="/tasks.html" class="nav-item ${activePage === 'tasks' ? 'active' : ''}">
                <span class="nav-icon">📋</span> Nhiệm vụ
            </a>
            <a href="/notifications.html" class="nav-item ${activePage === 'notifications' ? 'active' : ''}">
                <span class="nav-icon">🔔</span> Thông báo
            </a>
        </div>

        ${role !== 'thanh_vien' ? `
        <div class="nav-section">
            <div class="nav-section-title">Trí tuệ nhân tạo</div>
            <a href="/ai.html" class="nav-item manager-only ${activePage === 'ai' ? 'active' : ''}">
                <span class="nav-icon">🤖</span> AI Assistant
            </a>
        </div>` : ''}

        <div class="nav-section">
            <div class="nav-section-title">Hỗ trợ</div>
            <a href="/chatbot.html" target="_blank" class="nav-item ${activePage === 'chatbot' ? 'active' : ''}">
                <span class="nav-icon">💬</span> UniClub Assistant
            </a>
        </div>
    </nav>

    <div class="sidebar-footer">
        <div class="user-card">
            <div class="user-avatar" id="user-avatar">${user ? user.username.charAt(0).toUpperCase() : '?'}</div>
            <div class="user-info">
                <div class="user-name" id="user-name">${user ? user.username : ''}</div>
                <div class="user-role" id="user-role">${user ? ({'chu_nhiem': 'Chủ nhiệm', 'truong_ban': 'Trưởng ban', 'thanh_vien': 'Thành viên'}[user.role] || user.role) : ''}</div>
            </div>
            <button class="btn-logout" onclick="logout()" title="Đăng xuất">🚪</button>
        </div>
    </div>
    `;
}

// ==================== FLOATING AI LAUNCHER ====================
function initFloatingAILauncher() {
    // Không hiện nếu đang ở trang chatbot
    if (window.location.pathname.includes('chatbot.html')) return;
    if (document.getElementById('floating-ai-launcher')) return;

    const launcher = document.createElement('a');
    launcher.id = 'floating-ai-launcher';
    launcher.className = 'floating-ai-launcher';
    launcher.href = '/chatbot.html';
    launcher.target = '_blank';
    launcher.title = 'Mở Trợ lý ảo UniClub Assistant';
    launcher.innerHTML = `
        <div class="floating-ai-avatar">🤖</div>
        <span class="floating-ai-label">Hỏi Trợ lý AI</span>
        <span class="floating-ai-ping"></span>
    `;

    document.body.appendChild(launcher);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFloatingAILauncher);
} else {
    initFloatingAILauncher();
}

