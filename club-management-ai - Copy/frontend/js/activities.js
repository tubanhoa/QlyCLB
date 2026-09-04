/**
 * activities.js - Quản lý hoạt động
 */
if (!requireAuth()) throw new Error('Not authenticated');
document.getElementById('sidebar').innerHTML = getSidebarHTML('activities');

let allActivities = [];
let allMembers = [];

async function loadData() {
    try {
        allMembers = await apiCall('/api/members') || [];
        const managerSelect = document.getElementById('actManager');
        allMembers.forEach(m => {
            managerSelect.innerHTML += `<option value="${m.id}">${m.name}</option>`;
        });
        await loadActivities();
    } catch (err) {
        console.error(err);
    }
}

async function loadActivities() {
    try {
        const search = document.getElementById('searchInput').value;
        const status = document.getElementById('filterStatus').value;
        let url = '/api/activities?';
        if (search) url += `search=${encodeURIComponent(search)}&`;
        if (status) url += `status=${status}&`;

        allActivities = await apiCall(url) || [];
        renderTable();
    } catch (err) {
        console.error(err);
    }
}

function renderTable() {
    const tbody = document.getElementById('activityTable');
    const user = getUser();

    if (allActivities.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state"><div class="empty-icon">📅</div><h4>Chưa có hoạt động</h4></td></tr>';
        return;
    }

    tbody.innerHTML = allActivities.map(a => `
        <tr>
            <td>${a.id}</td>
            <td><strong>${a.name}</strong></td>
            <td>${formatDateTime(a.date)}</td>
            <td>${a.location || '—'}</td>
            <td>${a.manager_name || '—'}</td>
            <td>${getStatusBadge(a.status)}</td>
            <td>
                <button class="btn btn-ghost btn-sm" onclick="viewActivity(${a.id})" title="Chi tiết">👁️</button>
                ${user.role === 'chu_nhiem' ? `
                    <button class="btn btn-ghost btn-sm" onclick="editActivity(${a.id})" title="Sửa">✏️</button>
                    <button class="btn btn-ghost btn-sm" onclick="deleteActivity(${a.id})" title="Xóa">🗑️</button>
                ` : ''}
            </td>
        </tr>
    `).join('');
}

function openAddActivity() {
    document.getElementById('actModalTitle').textContent = 'Thêm hoạt động';
    document.getElementById('actEditId').value = '';
    document.getElementById('actName').value = '';
    document.getElementById('actDesc').value = '';
    document.getElementById('actDate').value = '';
    document.getElementById('actLocation').value = '';
    document.getElementById('actManager').value = '';
    document.getElementById('actStatus').value = 'upcoming';
    document.getElementById('actNotes').value = '';
    document.getElementById('actResult').value = '';
    openModal('activityModal');
}

function editActivity(id) {
    const a = allActivities.find(x => x.id === id);
    if (!a) return;
    document.getElementById('actModalTitle').textContent = 'Sửa hoạt động';
    document.getElementById('actEditId').value = a.id;
    document.getElementById('actName').value = a.name;
    document.getElementById('actDesc').value = a.description || '';
    document.getElementById('actDate').value = a.date ? a.date.slice(0, 16) : '';
    document.getElementById('actLocation').value = a.location || '';
    document.getElementById('actManager').value = a.manager_id || '';
    document.getElementById('actStatus').value = a.status;
    document.getElementById('actNotes').value = a.notes || '';
    document.getElementById('actResult').value = a.result || '';
    openModal('activityModal');
}

async function saveActivity() {
    const id = document.getElementById('actEditId').value;
    const dateVal = document.getElementById('actDate').value;
    const data = {
        name: document.getElementById('actName').value,
        description: document.getElementById('actDesc').value || null,
        date: dateVal ? new Date(dateVal).toISOString() : null,
        location: document.getElementById('actLocation').value || null,
        manager_id: document.getElementById('actManager').value ? parseInt(document.getElementById('actManager').value) : null,
        status: document.getElementById('actStatus').value,
        notes: document.getElementById('actNotes').value || null,
        result: document.getElementById('actResult').value || null
    };

    if (!data.name) { showToast('Vui lòng nhập tên hoạt động', 'error'); return; }

    try {
        if (id) {
            await apiCall(`/api/activities/${id}`, 'PUT', data);
            showToast('Cập nhật hoạt động thành công!', 'success');
        } else {
            await apiCall('/api/activities', 'POST', data);
            showToast('Thêm hoạt động thành công!', 'success');
        }
        closeModal('activityModal');
        await loadActivities();
    } catch (err) {}
}

async function deleteActivity(id) {
    if (!confirm('Bạn có chắc muốn xóa hoạt động này?')) return;
    try {
        await apiCall(`/api/activities/${id}`, 'DELETE');
        showToast('Xóa hoạt động thành công!', 'success');
        await loadActivities();
    } catch (err) {}
}

async function viewActivity(id) {
    try {
        const a = await apiCall(`/api/activities/${id}`);
        if (!a) return;

        document.getElementById('actDetailContent').innerHTML = `
            <div class="detail-grid">
                <div class="detail-item"><label>Tên hoạt động</label><span>${a.name}</span></div>
                <div class="detail-item"><label>Trạng thái</label><span>${getStatusBadge(a.status)}</span></div>
                <div class="detail-item"><label>Thời gian</label><span>${formatDateTime(a.date)}</span></div>
                <div class="detail-item"><label>Địa điểm</label><span>${a.location || '—'}</span></div>
                <div class="detail-item"><label>Phụ trách</label><span>${a.manager_name || '—'}</span></div>
                <div class="detail-item" style="grid-column: span 2;"><label>Mô tả</label><span>${a.description || '—'}</span></div>
                <div class="detail-item" style="grid-column: span 2;"><label>Ghi chú</label><span>${a.notes || '—'}</span></div>
                <div class="detail-item" style="grid-column: span 2;"><label>Kết quả</label><span>${a.result || '—'}</span></div>
            </div>
        `;
        openModal('actDetailModal');
    } catch (err) {}
}

// Events
document.getElementById('searchInput').addEventListener('input', function() {
    clearTimeout(this._timer);
    this._timer = setTimeout(loadActivities, 300);
});
document.getElementById('filterStatus').addEventListener('change', loadActivities);

loadData();
