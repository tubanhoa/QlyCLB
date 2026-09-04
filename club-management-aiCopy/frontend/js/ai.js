/**
 * ai.js - Chức năng AI
 */
if (!requireAuth()) throw new Error('Not authenticated');
document.getElementById('sidebar').innerHTML = getSidebarHTML('ai');

let activitiesData = [];

// Init - Load activities for dropdowns
async function init() {
    try {
        activitiesData = await apiCall('/api/activities') || [];

        // Fill activity dropdowns
        const sumSelect = document.getElementById('ai-sum-activity');
        const assignSelect = document.getElementById('ai-assign-activity');

        activitiesData.forEach(a => {
            const opt = `<option value="${a.id}">${a.name}</option>`;
            sumSelect.innerHTML += opt;
            assignSelect.innerHTML += opt;
        });
    } catch (err) {
        console.error(err);
    }
}

// Switch tabs
function switchTab(tab) {
    document.querySelectorAll('.ai-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.ai-panel').forEach(p => p.classList.remove('active'));

    event.target.classList.add('active');
    document.getElementById(`panel-${tab}`).classList.add('active');
}

// Fill activity data for summarize tab
function fillActivityData() {
    const id = document.getElementById('ai-sum-activity').value;
    if (!id) return;

    const a = activitiesData.find(x => x.id === parseInt(id));
    if (a) {
        document.getElementById('ai-sum-name').value = a.name;
        document.getElementById('ai-sum-desc').value = a.description || '';
        document.getElementById('ai-sum-notes').value = a.notes || '';
        document.getElementById('ai-sum-result').value = a.result || '';
    }
}

// ==================== AI 1: SINH THÔNG BÁO ====================
async function generateNotification() {
    const name = document.getElementById('ai-noti-name').value;
    if (!name) {
        showToast('Vui lòng nhập tên hoạt động', 'error');
        return;
    }

    const btn = document.getElementById('btn-gen-noti');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Đang sinh thông báo...';

    try {
        const data = {
            activity_name: name,
            time: document.getElementById('ai-noti-time').value || null,
            location: document.getElementById('ai-noti-location').value || null,
            content: document.getElementById('ai-noti-content').value || null,
            target_audience: document.getElementById('ai-noti-target').value || null
        };

        const result = await apiCall('/api/ai/notification', 'POST', data);
        if (result) {
            document.getElementById('result-notification-content').innerHTML =
                result.result.replace(/\n/g, '<br>');
            document.getElementById('result-notification').style.display = 'block';
            showToast('Sinh thông báo thành công!', 'success');
        }
    } catch (err) {
        console.error(err);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '✨ Sinh thông báo';
    }
}

// Use notification - redirect to notifications page
async function useNotification() {
    const content = document.getElementById('result-notification-content').innerText;
    const name = document.getElementById('ai-noti-name').value;

    try {
        await apiCall('/api/notifications', 'POST', {
            title: `📢 Thông báo: ${name}`,
            content: content
        });
        showToast('Đã tạo thông báo thành công!', 'success');
        setTimeout(() => {
            window.location.href = '/notifications.html';
        }, 1000);
    } catch (err) {
        console.error(err);
    }
}

// ==================== AI 2: TÓM TẮT HOẠT ĐỘNG ====================
async function summarizeActivity() {
    const name = document.getElementById('ai-sum-name').value;
    if (!name) {
        showToast('Vui lòng nhập tên hoạt động', 'error');
        return;
    }

    const btn = document.getElementById('btn-summarize');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Đang tóm tắt...';

    try {
        const data = {
            activity_name: name,
            description: document.getElementById('ai-sum-desc').value || null,
            notes: document.getElementById('ai-sum-notes').value || null,
            result: document.getElementById('ai-sum-result').value || null,
            feedback: document.getElementById('ai-sum-feedback').value || null
        };

        const result = await apiCall('/api/ai/summarize', 'POST', data);
        if (result) {
            document.getElementById('result-summarize-content').innerHTML =
                result.result.replace(/\n/g, '<br>');
            document.getElementById('result-summarize').style.display = 'block';
            showToast('Tóm tắt thành công!', 'success');
        }
    } catch (err) {
        console.error(err);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '✨ Tóm tắt hoạt động';
    }
}

// ==================== AI 3: GỢI Ý PHÂN CÔNG ====================
async function suggestAssignment() {
    const activityId = document.getElementById('ai-assign-activity').value;
    const activityInfo = document.getElementById('ai-assign-info').value;
    const taskList = document.getElementById('ai-assign-tasks').value;

    if (!activityId && !activityInfo) {
        showToast('Vui lòng chọn hoạt động hoặc nhập thông tin', 'error');
        return;
    }

    const btn = document.getElementById('btn-assign');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Đang phân tích...';

    try {
        const data = {
            activity_id: activityId ? parseInt(activityId) : null,
            activity_info: activityInfo || null,
            task_list: taskList || null
        };

        const result = await apiCall('/api/ai/assign-task', 'POST', data);
        if (result) {
            document.getElementById('result-assign-content').innerHTML =
                result.result.replace(/\n/g, '<br>');
            document.getElementById('result-assign').style.display = 'block';
            showToast('Gợi ý phân công thành công!', 'success');
        }
    } catch (err) {
        console.error(err);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '✨ Gợi ý phân công';
    }
}

// Confirm assignment - redirect to tasks page
function confirmAssignment() {
    showToast('Đã xác nhận! Chuyển đến trang nhiệm vụ để tạo chi tiết.', 'info');
    setTimeout(() => {
        window.location.href = '/tasks.html';
    }, 1500);
}

init();
