/**
 * members.js - Quản lý thành viên
 */

if (!requireAuth()) throw new Error('Not authenticated');
document.getElementById('sidebar').innerHTML = getSidebarHTML('members');

let allMembers = [];
let departments = [];

// Load data
async function loadData() {
    try {
        // Load departments for filter
        departments = await apiCall('/api/departments') || [];
        const filterDept = document.getElementById('filterDept');
        const memberDept = document.getElementById('memberDept');

        departments.forEach(d => {
            filterDept.innerHTML += `<option value="${d.id}">${d.name}</option>`;
            memberDept.innerHTML += `<option value="${d.id}">${d.name}</option>`;
        });

        // Load members
        await loadMembers();
    } catch (err) {
        console.error('Load error:', err);
    }
}

async function loadMembers() {
    try {
        const search = document.getElementById('searchInput').value;
        const deptId = document.getElementById('filterDept').value;

        let url = '/api/members?';
        if (search) url += `search=${encodeURIComponent(search)}&`;
        if (deptId) url += `department_id=${deptId}&`;

        allMembers = await apiCall(url) || [];
        renderTable();
    } catch (err) {
        console.error('Load members error:', err);
    }
}

function renderTable() {
    const tbody = document.getElementById('membersTable');
    const user = getUser();

    if (allMembers.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-state">
            <div class="empty-icon">👥</div>
            <h4>Chưa có thành viên</h4>
            <p>Hãy thêm thành viên mới</p>
        </td></tr>`;
        return;
    }

    tbody.innerHTML = allMembers.map(m => `
        <tr>
            <td>${m.id}</td>
            <td><strong>${m.name}</strong></td>
            <td>${m.email}</td>
            <td>${m.phone || '—'}</td>
            <td>${m.department_name ? `<span class="badge badge-purple">${m.department_name}</span>` : '<span class="badge badge-gray">Chưa phân</span>'}</td>
            <td><span style="font-size: 0.8rem; color: var(--text-secondary);">${m.skills ? m.skills.substring(0, 30) + (m.skills.length > 30 ? '...' : '') : '—'}</span></td>
            <td>${getStatusBadge(m.status)}</td>
            <td>
                <button class="btn btn-ghost btn-sm" onclick="viewDetail(${m.id})" title="Chi tiết">👁️</button>
                ${user.role !== 'thanh_vien' || user.member_id === m.id ? `<button class="btn btn-ghost btn-sm" onclick="editMember(${m.id})" title="Sửa">✏️</button>` : ''}
                ${user.role === 'chu_nhiem' ? `<button class="btn btn-ghost btn-sm" onclick="deleteMember(${m.id})" title="Xóa">🗑️</button>` : ''}
            </td>
        </tr>
    `).join('');
}

// Add
function openAddModal() {
    document.getElementById('modalTitle').textContent = 'Thêm thành viên';
    document.getElementById('editId').value = '';
    document.getElementById('memberForm').reset();
    openModal('memberModal');
}

// Edit
function editMember(id) {
    const m = allMembers.find(x => x.id === id);
    if (!m) return;

    document.getElementById('modalTitle').textContent = 'Sửa thành viên';
    document.getElementById('editId').value = m.id;
    document.getElementById('memberName').value = m.name;
    document.getElementById('memberEmail').value = m.email;
    document.getElementById('memberPhone').value = m.phone || '';
    document.getElementById('memberDept').value = m.department_id || '';
    document.getElementById('memberSkills').value = m.skills || '';
    document.getElementById('memberAvailability').value = m.availability || '';
    document.getElementById('memberStatus').value = m.status;

    openModal('memberModal');
}

// Save
async function saveMember() {
    const id = document.getElementById('editId').value;
    const data = {
        name: document.getElementById('memberName').value,
        email: document.getElementById('memberEmail').value,
        phone: document.getElementById('memberPhone').value || null,
        department_id: document.getElementById('memberDept').value ? parseInt(document.getElementById('memberDept').value) : null,
        skills: document.getElementById('memberSkills').value || null,
        availability: document.getElementById('memberAvailability').value || null,
        status: document.getElementById('memberStatus').value
    };

    if (!data.name || !data.email) {
        showToast('Vui lòng nhập họ tên và email', 'error');
        return;
    }

    try {
        if (id) {
            await apiCall(`/api/members/${id}`, 'PUT', data);
            showToast('Cập nhật thành viên thành công!', 'success');
        } else {
            await apiCall('/api/members', 'POST', data);
            showToast('Thêm thành viên thành công!', 'success');
        }
        closeModal('memberModal');
        await loadMembers();
    } catch (err) {
        // Error handled by apiCall
    }
}

// Delete
async function deleteMember(id) {
    if (!confirm('Bạn có chắc chắn muốn xóa thành viên này?')) return;

    try {
        await apiCall(`/api/members/${id}`, 'DELETE');
        showToast('Xóa thành viên thành công!', 'success');
        await loadMembers();
    } catch (err) {
        // Error handled by apiCall
    }
}

// View detail
async function viewDetail(id) {
    try {
        const m = await apiCall(`/api/members/${id}`);
        if (!m) return;

        document.getElementById('detailContent').innerHTML = `
            <div class="detail-grid">
                <div class="detail-item"><label>ID</label><span>${m.id}</span></div>
                <div class="detail-item"><label>Họ tên</label><span>${m.name}</span></div>
                <div class="detail-item"><label>Email</label><span>${m.email}</span></div>
                <div class="detail-item"><label>Số điện thoại</label><span>${m.phone || '—'}</span></div>
                <div class="detail-item"><label>Ban</label><span>${m.department_name || 'Chưa phân ban'}</span></div>
                <div class="detail-item"><label>Trạng thái</label><span>${getStatusBadge(m.status)}</span></div>
                <div class="detail-item" style="grid-column: span 2;"><label>Kỹ năng</label><span>${m.skills || '—'}</span></div>
                <div class="detail-item" style="grid-column: span 2;"><label>Lịch rảnh</label><span>${m.availability || '—'}</span></div>
                <div class="detail-item"><label>Ngày tham gia</label><span>${formatDate(m.join_date)}</span></div>
            </div>
        `;
        openModal('detailModal');
    } catch (err) {
        // Error handled
    }
}

// Search & filter events
document.getElementById('searchInput').addEventListener('input', debounce(loadMembers, 300));
document.getElementById('filterDept').addEventListener('change', loadMembers);

function debounce(fn, delay) {
    let timer;
    return function () {
        clearTimeout(timer);
        timer = setTimeout(fn, delay);
    };
}

// Init
loadData();
