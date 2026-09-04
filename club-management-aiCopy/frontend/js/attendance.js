/**
 * attendance.js - Quản lý điểm danh
 */
if (!requireRole(['chu_nhiem', 'truong_ban'])) throw new Error('Not authorized');
document.getElementById('sidebar').innerHTML = getSidebarHTML('attendance');

let currentActivityId = null;
let allMembers = [];
let attendanceRecords = [];

async function init() {
    try {
        const activities = await apiCall('/api/activities') || [];
        const select = document.getElementById('selectActivity');
        activities.forEach(a => {
            select.innerHTML += `<option value="${a.id}">${a.name} (${formatDate(a.date)})</option>`;
        });
    } catch (err) {
        console.error(err);
    }
}

async function loadAttendance() {
    currentActivityId = document.getElementById('selectActivity').value;
    if (!currentActivityId) {
        showToast('Vui lòng chọn hoạt động', 'error');
        return;
    }

    try {
        // Load members
        allMembers = await apiCall('/api/members') || [];

        // Load existing attendance
        attendanceRecords = await apiCall(`/api/attendance?activity_id=${currentActivityId}`) || [];

        // Show sections
        document.getElementById('attendanceStats').style.display = 'grid';
        document.getElementById('attendanceTable').style.display = 'block';

        const activity = (await apiCall(`/api/activities/${currentActivityId}`));
        document.getElementById('attendanceTitle').textContent = `Điểm danh: ${activity ? activity.name : ''}`;

        renderAttendance();
        updateStats();
    } catch (err) {
        console.error(err);
    }
}

function renderAttendance() {
    const tbody = document.getElementById('attendanceBody');

    tbody.innerHTML = allMembers.map((m, i) => {
        const record = attendanceRecords.find(r => r.member_id === m.id);
        const status = record ? record.status : 'absent';

        return `
            <tr>
                <td>${i + 1}</td>
                <td><strong>${m.name}</strong></td>
                <td>${m.department_name || '—'}</td>
                <td>
                    <select class="status-select" data-member-id="${m.id}" onchange="updateStats()">
                        <option value="present" ${status === 'present' ? 'selected' : ''}>✅ Có mặt</option>
                        <option value="absent" ${status === 'absent' ? 'selected' : ''}>❌ Vắng</option>
                        <option value="excused" ${status === 'excused' ? 'selected' : ''}>⚠️ Có phép</option>
                    </select>
                </td>
            </tr>
        `;
    }).join('');
}

function updateStats() {
    const selects = document.querySelectorAll('.status-select');
    let present = 0, absent = 0, excused = 0;

    selects.forEach(s => {
        if (s.value === 'present') present++;
        else if (s.value === 'absent') absent++;
        else excused++;
    });

    const total = selects.length;
    const rate = total > 0 ? Math.round(present / total * 100) : 0;

    document.getElementById('stat-present').textContent = present;
    document.getElementById('stat-absent').textContent = absent;
    document.getElementById('stat-excused').textContent = excused;
    document.getElementById('stat-rate').textContent = rate + '%';
}

async function saveAllAttendance() {
    const selects = document.querySelectorAll('.status-select');
    const records = [];

    selects.forEach(s => {
        records.push({
            activity_id: parseInt(currentActivityId),
            member_id: parseInt(s.dataset.memberId),
            status: s.value
        });
    });

    try {
        await apiCall('/api/attendance/bulk', 'POST', {
            activity_id: parseInt(currentActivityId),
            records: records
        });
        showToast('Lưu điểm danh thành công!', 'success');
    } catch (err) {
        console.error(err);
    }
}

init();
