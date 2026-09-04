/**
 * tasks.js - Quản lý nhiệm vụ
 */
if (!requireAuth()) throw new Error('Not authenticated');
document.getElementById('sidebar').innerHTML = getSidebarHTML('tasks');

let allTasks = [];

async function loadData() {
    try {
        const members = await apiCall('/api/members') || [];
        const activities = await apiCall('/api/activities') || [];

        const assigneeSelect = document.getElementById('taskAssignee');
        members.forEach(m => {
            assigneeSelect.innerHTML += `<option value="${m.id}">${m.name}</option>`;
        });

        const activitySelect = document.getElementById('taskActivity');
        activities.forEach(a => {
            activitySelect.innerHTML += `<option value="${a.id}">${a.name}</option>`;
        });

        await loadTasks();
    } catch (err) {
        console.error(err);
    }
}

async function loadTasks() {
    try {
        const search = document.getElementById('searchTask') ? document.getElementById('searchTask').value.trim() : '';
        const status = document.getElementById('filterStatus').value;
        const priority = document.getElementById('filterPriority').value;
        const sortVal = document.getElementById('sortTask') ? document.getElementById('sortTask').value : 'deadline_asc';

        let sortBy = 'deadline';
        let order = 'asc';
        if (sortVal === 'deadline_desc') {
            sortBy = 'deadline';
            order = 'desc';
        } else if (sortVal === 'priority_desc') {
            sortBy = 'priority';
            order = 'desc';
        } else if (sortVal === 'progress_desc') {
            sortBy = 'progress';
            order = 'desc';
        }

        let url = '/api/tasks?';
        if (search) url += `search=${encodeURIComponent(search)}&`;
        if (status) url += `status=${status}&`;
        if (priority) url += `priority=${priority}&`;
        if (sortBy) url += `sort_by=${sortBy}&`;
        if (order) url += `order=${order}&`;

        allTasks = await apiCall(url) || [];

        // Stats
        const total = allTasks.length;
        const completed = allTasks.filter(t => t.status === 'completed').length;
        const inProgress = allTasks.filter(t => t.status === 'in_progress').length;
        const overdue = allTasks.filter(t => t.status === 'overdue').length;

        document.getElementById('taskStats').innerHTML = `
            <div class="stat-card">
                <div class="stat-icon blue">📋</div>
                <div class="stat-info"><h3>${total}</h3><p>Tổng nhiệm vụ</p></div>
            </div>
            <div class="stat-card">
                <div class="stat-icon orange">⏳</div>
                <div class="stat-info"><h3>${inProgress}</h3><p>Đang thực hiện</p></div>
            </div>
            <div class="stat-card">
                <div class="stat-icon green">✅</div>
                <div class="stat-info"><h3>${completed}</h3><p>Hoàn thành</p></div>
            </div>
            <div class="stat-card">
                <div class="stat-icon pink">⚠️</div>
                <div class="stat-info"><h3>${overdue}</h3><p>Quá hạn</p></div>
            </div>
        `;

        renderTable();
    } catch (err) {
        console.error(err);
    }
}

function renderTable() {
    const tbody = document.getElementById('taskTable');
    const user = getUser();

    if (allTasks.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="empty-state"><div class="empty-icon">📋</div><h4>Chưa có nhiệm vụ</h4></td></tr>';
        return;
    }

    tbody.innerHTML = allTasks.map(t => `
        <tr>
            <td>${t.id}</td>
            <td><strong>${t.name}</strong><br><small style="color: var(--text-muted);">${t.description ? t.description.substring(0, 40) + '...' : ''}</small></td>
            <td>${t.activity_name || '—'}</td>
            <td>${t.assignee_name || '—'}</td>
            <td>${getPriorityBadge(t.priority)}</td>
            <td style="min-width: 120px;">${getProgressBar(t.progress)}</td>
            <td>${formatDate(t.deadline)}</td>
            <td>${getStatusBadge(t.status)}</td>
            <td>
                <button class="btn btn-ghost btn-sm" onclick="editTask(${t.id})" title="Sửa">✏️</button>
                ${user.role !== 'thanh_vien' ? `<button class="btn btn-ghost btn-sm" onclick="deleteTask(${t.id})" title="Xóa">🗑️</button>` : ''}
            </td>
        </tr>
    `).join('');
}

function setTaskFormReadOnly(isReadOnly) {
    ['taskName', 'taskDesc', 'taskActivity', 'taskAssignee', 'taskDeadline', 'taskPriority'].forEach(fieldId => {
        const el = document.getElementById(fieldId);
        if (el) el.disabled = isReadOnly;
    });
}

function openAddTask() {
    const user = getUser();
    if (user && user.role === 'thanh_vien') {
        showToast('Chỉ Chủ nhiệm hoặc Trưởng ban mới có quyền tạo nhiệm vụ!', 'error');
        return;
    }
    setTaskFormReadOnly(false);
    document.getElementById('taskModalTitle').textContent = 'Thêm nhiệm vụ';
    document.getElementById('taskEditId').value = '';
    document.getElementById('taskName').value = '';
    document.getElementById('taskDesc').value = '';
    document.getElementById('taskActivity').value = '';
    document.getElementById('taskAssignee').value = '';
    document.getElementById('taskDeadline').value = '';
    document.getElementById('taskPriority').value = 'medium';
    document.getElementById('taskStatus').value = 'not_started';
    document.getElementById('taskProgress').value = '0';
    openModal('taskModal');
}

function editTask(id) {
    const t = allTasks.find(x => x.id === id);
    if (!t) return;

    const user = getUser();
    const isMember = user && user.role === 'thanh_vien';

    // Thành viên chỉ được sửa tiến độ & trạng thái
    setTaskFormReadOnly(isMember);

    document.getElementById('taskModalTitle').textContent = isMember ? 'Cập nhật tiến độ nhiệm vụ' : 'Sửa nhiệm vụ';
    document.getElementById('taskEditId').value = t.id;
    document.getElementById('taskName').value = t.name;
    document.getElementById('taskDesc').value = t.description || '';
    document.getElementById('taskActivity').value = t.activity_id || '';
    document.getElementById('taskAssignee').value = t.assigned_to || '';
    document.getElementById('taskDeadline').value = t.deadline ? t.deadline.slice(0, 16) : '';
    document.getElementById('taskPriority').value = t.priority;
    document.getElementById('taskStatus').value = t.status;
    document.getElementById('taskProgress').value = t.progress;
    openModal('taskModal');
}

async function saveTask() {
    const id = document.getElementById('taskEditId').value;
    const deadlineVal = document.getElementById('taskDeadline').value;
    const user = getUser();
    const isMember = user && user.role === 'thanh_vien';

    let data;
    if (isMember) {
        // Thành viên chỉ gửi status và progress
        data = {
            status: document.getElementById('taskStatus').value,
            progress: parseInt(document.getElementById('taskProgress').value) || 0
        };
    } else {
        data = {
            name: document.getElementById('taskName').value,
            description: document.getElementById('taskDesc').value || null,
            activity_id: document.getElementById('taskActivity').value ? parseInt(document.getElementById('taskActivity').value) : null,
            assigned_to: document.getElementById('taskAssignee').value ? parseInt(document.getElementById('taskAssignee').value) : null,
            deadline: deadlineVal ? new Date(deadlineVal).toISOString() : null,
            priority: document.getElementById('taskPriority').value,
            status: document.getElementById('taskStatus').value,
            progress: parseInt(document.getElementById('taskProgress').value) || 0
        };

        if (!data.name) {
            showToast('Vui lòng nhập tên nhiệm vụ', 'error');
            return;
        }
    }

    try {
        if (id) {
            await apiCall(`/api/tasks/${id}`, 'PUT', data);
            showToast('Cập nhật nhiệm vụ thành công!', 'success');
        } else {
            await apiCall('/api/tasks', 'POST', data);
            showToast('Tạo nhiệm vụ thành công!', 'success');
        }
        closeModal('taskModal');
        await loadTasks();
    } catch (err) {}
}

async function deleteTask(id) {
    if (!confirm('Bạn có chắc muốn xóa nhiệm vụ này?')) return;
    try {
        await apiCall(`/api/tasks/${id}`, 'DELETE');
        showToast('Xóa nhiệm vụ thành công!', 'success');
        await loadTasks();
    } catch (err) {}
}

// Events
if (document.getElementById('searchTask')) {
    document.getElementById('searchTask').addEventListener('input', function() {
        clearTimeout(this._timer);
        this._timer = setTimeout(loadTasks, 300);
    });
}
document.getElementById('filterStatus').addEventListener('change', loadTasks);
document.getElementById('filterPriority').addEventListener('change', loadTasks);
if (document.getElementById('sortTask')) {
    document.getElementById('sortTask').addEventListener('change', loadTasks);
}

loadData();
