/**
 * departments.js - Quản lý ban chuyên môn
 */
if (!requireRole(['chu_nhiem', 'truong_ban'])) throw new Error('Not authorized');
document.getElementById('sidebar').innerHTML = getSidebarHTML('departments');

let allDepts = [];
let allMembers = [];

async function loadData() {
    try {
        allMembers = await apiCall('/api/members') || [];
        await loadDepartments();
    } catch (err) {
        console.error(err);
    }
}

async function loadDepartments() {
    try {
        allDepts = await apiCall('/api/departments') || [];

        // Stats
        document.getElementById('deptStats').innerHTML = allDepts.map(d => `
            <div class="stat-card">
                <div class="stat-icon purple">🏢</div>
                <div class="stat-info">
                    <h3>${d.member_count}</h3>
                    <p>${d.name}</p>
                </div>
            </div>
        `).join('');

        // Leader dropdown
        const leaderSelect = document.getElementById('deptLeader');
        leaderSelect.innerHTML = '<option value="">-- Chọn trưởng ban --</option>';
        allMembers.forEach(m => {
            leaderSelect.innerHTML += `<option value="${m.id}">${m.name}</option>`;
        });

        renderTable();
    } catch (err) {
        console.error(err);
    }
}

function renderTable() {
    const tbody = document.getElementById('deptTable');
    const user = getUser();
    const isAdmin = user && user.role === 'chu_nhiem';

    if (allDepts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><div class="empty-icon">🏢</div><h4>Chưa có ban nào</h4></td></tr>';
        return;
    }

    tbody.innerHTML = allDepts.map(d => `
        <tr>
            <td>${d.id}</td>
            <td><strong>${d.name}</strong></td>
            <td><span style="font-size: 0.85rem; color: var(--text-secondary);">${d.description || '—'}</span></td>
            <td>${d.leader_name || '<span class="badge badge-gray">Chưa có</span>'}</td>
            <td><span class="badge badge-info">${d.member_count} người</span></td>
            <td>
                <button class="btn btn-ghost btn-sm" onclick="viewDept(${d.id})" title="Chi tiết">👁️</button>
                ${isAdmin ? `
                    <button class="btn btn-ghost btn-sm" onclick="editDept(${d.id})" title="Sửa">✏️</button>
                    <button class="btn btn-ghost btn-sm" onclick="deleteDept(${d.id})" title="Xóa">🗑️</button>
                ` : ''}
            </td>
        </tr>
    `).join('');
}

function openAddDept() {
    document.getElementById('deptModalTitle').textContent = 'Thêm ban mới';
    document.getElementById('deptEditId').value = '';
    document.getElementById('deptName').value = '';
    document.getElementById('deptDesc').value = '';
    document.getElementById('deptLeader').value = '';
    openModal('deptModal');
}

function editDept(id) {
    const d = allDepts.find(x => x.id === id);
    if (!d) return;
    document.getElementById('deptModalTitle').textContent = 'Sửa ban';
    document.getElementById('deptEditId').value = d.id;
    document.getElementById('deptName').value = d.name;
    document.getElementById('deptDesc').value = d.description || '';
    document.getElementById('deptLeader').value = d.leader_id || '';
    openModal('deptModal');
}

async function saveDept() {
    const id = document.getElementById('deptEditId').value;
    const data = {
        name: document.getElementById('deptName').value,
        description: document.getElementById('deptDesc').value || null,
        leader_id: document.getElementById('deptLeader').value ? parseInt(document.getElementById('deptLeader').value) : null
    };

    if (!data.name) {
        showToast('Vui lòng nhập tên ban', 'error');
        return;
    }

    try {
        if (id) {
            await apiCall(`/api/departments/${id}`, 'PUT', data);
            showToast('Cập nhật ban thành công!', 'success');
        } else {
            await apiCall('/api/departments', 'POST', data);
            showToast('Thêm ban thành công!', 'success');
        }
        closeModal('deptModal');
        await loadDepartments();
    } catch (err) {}
}

async function deleteDept(id) {
    if (!confirm('Bạn có chắc muốn xóa ban này? Các thành viên sẽ bị gỡ khỏi ban.')) return;
    try {
        await apiCall(`/api/departments/${id}`, 'DELETE');
        showToast('Xóa ban thành công!', 'success');
        await loadDepartments();
    } catch (err) {}
}

async function viewDept(id) {
    try {
        const d = await apiCall(`/api/departments/${id}`);
        if (!d) return;

        let membersHtml = '<p style="color: var(--text-muted);">Chưa có thành viên</p>';
        if (d.members && d.members.length > 0) {
            membersHtml = '<table style="width:100%;"><thead><tr><th>ID</th><th>Họ tên</th><th>Email</th></tr></thead><tbody>';
            membersHtml += d.members.map(m => `<tr><td>${m.id}</td><td>${m.name}</td><td>${m.email}</td></tr>`).join('');
            membersHtml += '</tbody></table>';
        }

        document.getElementById('deptDetailContent').innerHTML = `
            <div class="detail-grid">
                <div class="detail-item"><label>Tên ban</label><span>${d.name}</span></div>
                <div class="detail-item"><label>Trưởng ban</label><span>${d.leader_name || 'Chưa có'}</span></div>
                <div class="detail-item" style="grid-column: span 2;"><label>Mô tả</label><span>${d.description || '—'}</span></div>
            </div>
            <h4 style="margin: 20px 0 12px; color: var(--text-secondary);">👥 Thành viên (${d.member_count})</h4>
            ${membersHtml}
        `;
        openModal('deptDetailModal');
    } catch (err) {}
}

loadData();
