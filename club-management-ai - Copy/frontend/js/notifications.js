/**
 * notifications.js - Quản lý thông báo
 */
if (!requireAuth()) throw new Error('Not authenticated');
document.getElementById('sidebar').innerHTML = getSidebarHTML('notifications');

let allNotifications = [];

async function loadNotifications() {
    try {
        allNotifications = await apiCall('/api/notifications') || [];
        renderNotifications();
    } catch (err) {
        console.error(err);
    }
}

function renderNotifications() {
    const container = document.getElementById('notificationsList');
    const user = getUser();

    if (allNotifications.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔔</div>
                <h4>Chưa có thông báo nào</h4>
                <p>Tạo thông báo mới hoặc sử dụng AI để sinh thông báo</p>
            </div>
        `;
        return;
    }

    container.innerHTML = allNotifications.map(n => `
        <div class="notification-card">
            <div class="noti-header">
                <span class="noti-title">${n.title}</span>
                <span class="noti-date">${formatDateTime(n.created_at)}</span>
            </div>
            <div class="noti-content">${n.content}</div>
            ${user.role === 'chu_nhiem' ? `
            <div class="noti-actions">
                <button class="btn btn-ghost btn-sm" onclick="editNotification(${n.id})">✏️ Sửa</button>
                <button class="btn btn-ghost btn-sm" onclick="deleteNotification(${n.id})">🗑️ Xóa</button>
            </div>
            ` : ''}
        </div>
    `).join('');
}

function openAddNotification() {
    document.getElementById('notiModalTitle').textContent = 'Tạo thông báo mới';
    document.getElementById('notiEditId').value = '';
    document.getElementById('notiTitle').value = '';
    document.getElementById('notiContent').value = '';
    openModal('notiModal');
}

function editNotification(id) {
    const n = allNotifications.find(x => x.id === id);
    if (!n) return;
    document.getElementById('notiModalTitle').textContent = 'Sửa thông báo';
    document.getElementById('notiEditId').value = n.id;
    document.getElementById('notiTitle').value = n.title;
    document.getElementById('notiContent').value = n.content;
    openModal('notiModal');
}

async function saveNotification() {
    const id = document.getElementById('notiEditId').value;
    const data = {
        title: document.getElementById('notiTitle').value,
        content: document.getElementById('notiContent').value
    };

    if (!data.title || !data.content) {
        showToast('Vui lòng nhập đầy đủ thông tin', 'error');
        return;
    }

    try {
        if (id) {
            await apiCall(`/api/notifications/${id}`, 'PUT', data);
            showToast('Cập nhật thông báo thành công!', 'success');
        } else {
            await apiCall('/api/notifications', 'POST', data);
            showToast('Tạo thông báo thành công!', 'success');
        }
        closeModal('notiModal');
        await loadNotifications();
    } catch (err) {}
}

async function deleteNotification(id) {
    if (!confirm('Bạn có chắc muốn xóa thông báo này?')) return;
    try {
        await apiCall(`/api/notifications/${id}`, 'DELETE');
        showToast('Xóa thông báo thành công!', 'success');
        await loadNotifications();
    } catch (err) {}
}

loadNotifications();
