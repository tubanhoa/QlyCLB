/**
 * ai.js - Chức năng AI
 */
if (!requireRole(['chu_nhiem', 'truong_ban'])) throw new Error('Not authorized');
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

// ==================== PRESET FILLERS & COPY HELPERS ====================
function fillNotiPreset(type) {
    const presets = {
        workshop: {
            name: 'Workshop Nhập môn Python & Phân tích Dữ liệu',
            time: '14:00 - 17:00, Thứ Bảy ngày 20/10/2024',
            location: 'Hội trường B2 - Cơ sở chính & Online qua MS Teams',
            content: 'Workshop hướng dẫn lập trình Python từ con số 0, cài đặt môi trường Anaconda/VSCode, viết các script tự động hóa cơ bản và làm quen thư viện Pandas. Có mentor hỗ trợ cài đặt và cấp giấy chứng nhận tham gia.',
            target: 'Tân sinh viên K19, K20 & tất cả sinh viên đam mê công nghệ'
        },
        hackathon: {
            name: 'Hackathon CLB 2024: AI & Green Tech',
            time: '08:00 ngày 25/11 đến 18:00 ngày 26/11/2024 (36h liên tục)',
            location: 'Sảnh Đổi mới sáng tạo - Tòa nhà A',
            content: 'Cuộc thi sáng tạo sản phẩm công nghệ sinh viên. Đề bài xoay quanh ứng dụng Trí tuệ nhân tạo (AI/LLM) giải quyết các bài toán học đường và môi trường xanh. Tổng giải thưởng lên tới 15.000.000 VNĐ cùng cơ hội thực tập tại doanh nghiệp tài trợ.',
            target: 'Toàn bộ sinh viên toàn trường, đăng ký theo đội 3-5 người'
        },
        teambuilding: {
            name: 'Teambuilding Mùa Thu: Vững kết nối - Bứt phá tương lai',
            time: '07:00 - 18:00, Chủ Nhật ngày 10/11/2024',
            location: 'Khu sinh thái Ecopark',
            content: 'Chương trình dã ngoại kết nối gắn kết thành viên mới và cũ. Bao gồm chuỗi trò chơi vượt chướng ngại vật đồng đội, tiệc nướng BBQ ngoài trời, gala vinh danh các thành viên xuất sắc và bốc thăm may mắn trúng quà.',
            target: 'Tất cả ban chủ nhiệm, trưởng ban và thành viên chính thức CLB'
        },
        meeting: {
            name: 'Họp toàn thể CLB định kỳ tháng 10',
            time: '19:30 - 21:00, Thứ Ba ngày 08/10/2024',
            location: 'Phòng Hội thảo C102 & Google Meet',
            content: 'Đánh giá tiến độ hoạt động chiến dịch tuyển sinh viên đợt 1, phê duyệt ngân sách các sự kiện quý 4 và phân công nhân sự nòng cốt chuẩn bị cho Ngày hội câu lạc bộ Club Day.',
            target: 'Tất cả thành viên trực thuộc các ban trong CLB'
        }
    };

    const p = presets[type];
    if (!p) return;

    document.getElementById('ai-noti-name').value = p.name;
    document.getElementById('ai-noti-time').value = p.time;
    document.getElementById('ai-noti-location').value = p.location;
    document.getElementById('ai-noti-content').value = p.content;
    document.getElementById('ai-noti-target').value = p.target;
    showToast(`Đã điền mẫu: "${p.name}"`, 'info');
}

function fillSumPreset(type) {
    const presets = {
        workshop: {
            name: 'Workshop Git/GitHub cơ bản cho lập trình viên',
            desc: 'Hướng dẫn thực hành Git flow, commit, branch, merge và xử lý xung đột trong dự án nhóm sinh viên.',
            notes: 'Có 95 sinh viên tham dự trực tiếp tại phòng máy. Tất cả người tham gia đều thực hành tạo thành công repo và pull request.',
            result: '100% sinh viên hoàn thành bài thực hành cuối buổi; 15 dự án mini được nộp lên GitHub Classroom; tạo ấn tượng rất tốt về chất lượng đào tạo.',
            feedback: 'Đa số sinh viên đánh giá bài giảng dễ hiểu, slide trực quan, mong muốn CLB tổ chức thêm buổi nâng cao về Docker và CI/CD.'
        },
        contest: {
            name: 'Cuộc thi Ý tưởng Trí tuệ nhân tạo AI Challenge',
            desc: 'Sân chơi sáng tạo ý tưởng giải pháp AI phục vụ đời sống học đường và cộng đồng sinh viên.',
            notes: 'Nhận được 28 đề tài dự thi từ 6 khoa viện; 8 đội xuất sắc nhất lọt vào vòng chung kết Pitching.',
            result: 'Đội TechVanguard giành giải Nhất với giải pháp Điểm danh nhận diện khuôn mặt; 2 đề tài được bảo trợ ươm mầm khởi nghiệp.',
            feedback: 'Ban giám khảo khen ngợi tính ứng dụng cao; các đội đề xuất kéo dài thêm thời gian hoàn thiện MVP.'
        },
        volunteer: {
            name: 'Chiến dịch Mùa hè xanh - Vì nụ cười trẻ thơ',
            desc: 'Hoạt động tình nguyện hè tại xã khó khăn, tổ chức lớp phổ cập tin học và xây dựng sân chơi thiếu nhi.',
            notes: '45 tình nguyện viên tham gia 10 ngày đêm; phối hợp chặt chẽ với đoàn thanh niên địa phương.',
            result: 'Hoàn thành 01 sân chơi bê tông cho điểm trường mầm non, trao 30 suất học bổng cho học sinh nghèo vượt khó, dạy tin học cho 80 em nhỏ.',
            feedback: 'Chính quyền địa phương gửi thư cảm ơn sâu sắc; các thành viên trưởng thành vượt bậc về kỹ năng sống và tinh thần đồng đội.'
        }
    };

    const p = presets[type];
    if (!p) return;

    document.getElementById('ai-sum-name').value = p.name;
    document.getElementById('ai-sum-desc').value = p.desc;
    document.getElementById('ai-sum-notes').value = p.notes;
    document.getElementById('ai-sum-result').value = p.result;
    document.getElementById('ai-sum-feedback').value = p.feedback;
    showToast(`Đã điền mẫu: "${p.name}"`, 'info');
}

function fillAssignPreset(type) {
    const presets = {
        welcome: {
            info: 'Sự kiện Chào tân sinh viên "UniClub Welcome Day 2024" quy mô 500 sinh viên tham dự tại hội trường lớn.',
            tasks: '- Thiết kế bộ nhận diện sự kiện, banner sân khấu, standee và thẻ ban tổ chức\n- Setup hệ thống âm thanh, ánh sáng, máy chiếu và test video trình chiếu trước 2 tiếng\n- Điều phối khu vực check-in tân sinh viên, phát quà tặng lưu niệm và hướng dẫn chỗ ngồi\n- Viết kịch bản dẫn chương trình chi tiết, duyệt MC và sắp xếp timeline các tiết mục văn nghệ\n- Hậu cần mua sắm teabreak, nước uống cho khách mời và dọn dẹp sau sự kiện'
        },
        training: {
            info: 'Khóa đào tạo nội bộ 3 buổi "Hands-on AI & Prompt Engineering" dành cho 60 thành viên mới gia nhập CLB.',
            tasks: '- Soạn giáo trình bài giảng và lab bài tập thực hành Google Colab\n- Cài đặt tài khoản API OpenAI/Gemini phục vụ demo thực tế trong buổi học\n- Phụ trách hỗ trợ kỹ thuật và giải đáp thắc mắc (Tutor/Mentor) cho từng nhóm 5 bạn\n- Điểm danh, ghi chép biên bản buổi học và đánh giá chuyên cần'
        },
        talkshow: {
            info: 'Talkshow "Hành trình từ giảng đường đến Big Tech" với 2 diễn giả là cựu thành viên CLB hiện đang làm Tech Lead.',
            tasks: '- Liên hệ gửi thư mời chính thức, đón tiếp và chuẩn bị quà tặng tri ân diễn giả\n- Viết bài truyền thông trên Fanpage trước 1 tuần và chạy minigame tặng vé tham dự\n- Thu thập và tổng hợp câu hỏi thắc mắc của sinh viên gửi về trước buổi talkshow\n- MC dẫn dắt phần Q&A giao lưu trực tiếp và điều phối mic cho khán giả\n- Chụp ảnh sự kiện, quay video recap và viết bài cảm ơn hậu sự kiện'
        }
    };

    const p = presets[type];
    if (!p) return;

    document.getElementById('ai-assign-info').value = p.info;
    document.getElementById('ai-assign-tasks').value = p.tasks;
    showToast(`Đã điền mẫu phân công!`, 'info');
}

function copyAIResult(elementId, btn) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const textToCopy = el.innerText || el.textContent;
    if (!textToCopy || !textToCopy.trim()) {
        showToast('Chưa có nội dung để sao chép', 'warning');
        return;
    }

    navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = btn.innerHTML;
        btn.innerHTML = 'Đã chép! ✓';
        btn.classList.add('copied');
        showToast('Đã sao chép nội dung vào Clipboard!', 'success');
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('copied');
        }, 2000);
    }).catch(err => {
        console.error('Không thể sao chép:', err);
        showToast('Không thể sao chép tự động', 'error');
    });
}

// Confirm assignment - redirect to tasks page
function confirmAssignment() {
    showToast('Đã xác nhận! Chuyển đến trang nhiệm vụ để tạo chi tiết.', 'info');
    setTimeout(() => {
        window.location.href = '/tasks.html';
    }, 1500);
}

init();
