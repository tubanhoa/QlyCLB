/**
 * chatbot.js - UniClub Assistant Chatbot Logic
 * Standalone — không yêu cầu auth.js
 */

const CHAT_API = '/api/ai/chat';
const CHAT_TIMEOUT_MS = 30000;

// ==================== STATE ====================
let isLoading = false;
let activeRequest = null;

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    initChatbot();
});

function initChatbot() {
    // Auto-resize textarea
    const input = document.getElementById('chat-input');
    input.addEventListener('input', autoResizeTextarea);
    input.addEventListener('input', updateCharacterCount);
    input.addEventListener('keydown', handleKeyDown);
    updateCharacterCount();

    // Show welcome message
    showWelcomeMessage();
}

// ==================== WELCOME ====================
function showWelcomeMessage() {
    const welcomeData = {
        answer: (
            "Xin chào bạn! 👋 Mình là **UniClub Assistant** — Trợ lý ảo chính thức của CLB Sinh viên!\n\n" +
            "Bạn đang băn khoăn hay có thắc mắc khi muốn tham gia CLB? Đừng ngần ngại, mình ở đây để đồng hành và gỡ rối mọi nỗi lo cho bạn:\n\n" +
            "- ❓ **'Chưa có kinh nghiệm / Chưa biết gì':** Có tham gia được không? (Khẳng định: *100% được!*)\n" +
            "- 📚 **'Cân bằng học tập & CLB':** Có bị trùng lịch học hay ảnh hưởng GPA không?\n" +
            "- 💰 **'Chi phí & Quỹ':** Tham gia CLB có mất phí gì không?\n" +
            "- 🎁 **'Quyền lợi thực tế':** Điểm rèn luyện, giấy chứng nhận Đoàn trường, cơ hội thực tập sớm.\n" +
            "- 🎤 **'Phỏng vấn':** Vòng phỏng vấn thường hỏi gì và mẹo ghi điểm cao?\n" +
            "- 🎯 **'Định hướng ban':** Tư vấn ban chuyên môn phù hợp nhất với sở thích và đam mê của bạn.\n\n" +
            "💡 *Hãy bấm vào các nút chủ đề nhanh phía dưới hoặc hỏi mình bất cứ điều gì bạn đang băn khoăn nhé!* 😊"
        ),
        suggestedClubs: [
            {"maDinhDanh": "DEPT_1", "tenClb": "Ban Truyền thông", "lyDoGoiY": "Sáng tạo nội dung, thiết kế Figma, video TikTok"},
            {"maDinhDanh": "DEPT_2", "tenClb": "Ban Kỹ thuật", "lyDoGoiY": "Đào tạo lập trình Web, App, AI từ con số 0"},
            {"maDinhDanh": "DEPT_3", "tenClb": "Ban Sự kiện", "lyDoGoiY": "Tổ chức chương trình, dẫn MC, kết nối bạn bè"}
        ],
        followUpQuestions: [
            "Chưa có kinh nghiệm có tham gia CLB được không?",
            "Tham gia CLB có bị trùng lịch học không?",
            "Tham gia CLB có mất phí gì không?",
            "Quyền lợi thực tế khi tham gia CLB là gì?",
            "Phỏng vấn CLB thường hỏi những câu gì?",
            "Em học khoa Kinh tế/trái ngành có tham gia được không?"
        ]
    };
    renderBotMessage(welcomeData);
}

// ==================== SEND MESSAGE ====================
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message || isLoading) return;

    // Render user message
    renderUserMessage(message);

    // Clear input
    input.value = '';
    input.style.height = 'auto';

    // Show typing indicator
    isLoading = true;
    updateSendButton();
    const typingEl = showTypingIndicator();

    try {
        activeRequest = new AbortController();
        const timeoutId = setTimeout(() => activeRequest.abort(), CHAT_TIMEOUT_MS);
        const response = await fetch(CHAT_API, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
            signal: activeRequest.signal
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        // Remove typing indicator
        typingEl.remove();

        // Render bot response
        renderBotMessage(data);

    } catch (error) {
        console.error('Chat error:', error);
        if (typingEl.isConnected) typingEl.remove();

        const errorMessage = error.name === 'AbortError'
            ? 'Phản hồi đang mất nhiều thời gian hơn dự kiến. Bạn thử gửi lại câu hỏi nhé.'
            : 'Mình chưa kết nối được với hệ thống. Bạn thử lại sau hoặc liên hệ Ban chủ nhiệm CLB nhé.';

        renderBotMessage({
            answer: `**Chưa nhận được phản hồi**\n\n${errorMessage}`,
            suggestedClubs: [],
            followUpQuestions: [
                "Thử lại câu hỏi trước",
                "CLB có những ban chuyên môn nào?"
            ]
        });
    } finally {
        activeRequest = null;
        isLoading = false;
        updateSendButton();
        document.getElementById('chat-input').focus();
    }
}

// ==================== RENDER MESSAGES ====================
function renderUserMessage(text) {
    const container = document.getElementById('chat-messages');

    const msgEl = document.createElement('div');
    msgEl.className = 'chat-message chat-message-user';
    msgEl.innerHTML = `
        <div class="chat-bubble chat-bubble-user">
            <div class="chat-text">${escapeHtml(text)}</div>
        </div>
        <div class="chat-avatar chat-avatar-user">👤</div>
    `;

    container.appendChild(msgEl);
    scrollToBottom();
}

function renderBotMessage(data) {
    const container = document.getElementById('chat-messages');

    const msgEl = document.createElement('div');
    msgEl.className = 'chat-message chat-message-bot';

    let html = `
        <div class="chat-avatar chat-avatar-bot">🤖</div>
        <div class="chat-bubble chat-bubble-bot">
            <div class="chat-text">${renderMarkdown(data.answer)}</div>
    `;

    // Suggested clubs (interactive cards)
    if (data.suggestedClubs && data.suggestedClubs.length > 0) {
        html += '<div class="chat-clubs">';
        html += '<div class="chat-clubs-title">🏫 Ban chuyên môn phù hợp dành cho bạn:</div>';
        html += '<div class="chat-clubs-grid">';
        data.suggestedClubs.forEach(club => {
            const safeName = escapeHtml(club.tenClb);
            const safeReason = escapeHtml(club.lyDoGoiY);
            const safeId = escapeHtml(club.maDinhDanh || '');
            html += `
                <div class="chat-club-card" onclick="askAboutClub('${safeId}')" title="Bấm để tìm hiểu chi tiết về ${safeName}" role="button" tabindex="0">
                    <div class="chat-club-header">
                        <span class="chat-club-badge">Đề xuất</span>
                        ${safeId ? `<span class="chat-club-id">${safeId}</span>` : ''}
                    </div>
                    <div class="chat-club-name">${safeName}</div>
                    <div class="chat-club-reason">${safeReason}</div>
                    <div class="chat-club-action">👉 Bấm để hỏi thêm về ban này</div>
                </div>
            `;
        });
        html += '</div></div>';
    }

    // Action toolbar inside bot message
    html += `
        <div class="chat-bubble-actions">
            <button type="button" class="bubble-action-btn" onclick="copyBotAnswer(this)" title="Sao chép toàn bộ câu trả lời">
                📋 Sao chép
            </button>
            <button type="button" class="bubble-action-btn" onclick="toggleUseful(this)" title="Đánh giá câu trả lời hữu ích">
                👍 Hữu ích
            </button>
        </div>
    `;

    html += '</div>';

    // Follow-up questions (outside bubble)
    if (data.followUpQuestions && data.followUpQuestions.length > 0) {
        html += '<div class="chat-followups">';
        data.followUpQuestions.forEach(q => {
            html += `<button class="chat-followup-chip" onclick="askFollowUp(this)">${escapeHtml(q)}</button>`;
        });
        html += '</div>';
    }

    msgEl.innerHTML = html;
    container.appendChild(msgEl);

    // Animate entrance
    requestAnimationFrame(() => {
        msgEl.classList.add('chat-message-visible');
    });

    scrollToBottom();
}

// ==================== TYPING INDICATOR ====================
function showTypingIndicator() {
    const container = document.getElementById('chat-messages');

    const typingEl = document.createElement('div');
    typingEl.className = 'chat-message chat-message-bot chat-message-visible';
    typingEl.id = 'typing-indicator';
    typingEl.innerHTML = `
        <div class="chat-avatar chat-avatar-bot">🤖</div>
        <div class="chat-bubble chat-bubble-bot chat-typing">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    container.appendChild(typingEl);
    scrollToBottom();
    return typingEl;
}

// ==================== ACTIONS & CONVENIENCE BUTTONS ====================
function switchCategoryTab(category, tabBtn) {
    document.querySelectorAll('.category-tab-btn').forEach(btn => btn.classList.remove('active'));
    tabBtn.classList.add('active');

    const allButtons = document.querySelectorAll('.quick-topic-btn');
    allButtons.forEach(btn => {
        if (category === 'all' || btn.classList.contains(`group-${category}`)) {
            btn.style.display = 'inline-flex';
        } else {
            btn.style.display = 'none';
        }
    });
}

function resetChat() {
    const container = document.getElementById('chat-messages');
    container.innerHTML = '';
    showWelcomeMessage();
    const input = document.getElementById('chat-input');
    input.value = '';
    input.style.height = 'auto';
    input.focus();
}

function copyBotAnswer(btn) {
    const bubble = btn.closest('.chat-bubble-bot');
    if (!bubble) return;
    const textEl = bubble.querySelector('.chat-text');
    if (!textEl) return;

    const textToCopy = textEl.innerText || textEl.textContent;
    navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = btn.innerHTML;
        btn.innerHTML = 'Đã chép! ✓';
        btn.classList.add('active-action');
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('active-action');
        }, 2000);
    });
}

function toggleUseful(btn) {
    if (btn.classList.contains('active-action')) {
        btn.classList.remove('active-action');
        btn.innerHTML = '👍 Hữu ích';
    } else {
        btn.classList.add('active-action');
        btn.innerHTML = '❤️ Cảm ơn bạn!';
    }
}

function scrollToBottomSmooth() {
    const area = document.getElementById('chat-area');
    area.scrollTo({
        top: area.scrollHeight,
        behavior: 'smooth'
    });
}

function askFollowUp(btn) {
    const question = btn.textContent;
    quickAsk(question);
}

function askAboutClub(clubName) {
    const question = `Hãy tư vấn chi tiết hơn về ban ${clubName}, các hoạt động thực tế và yêu cầu tham gia.`;
    quickAsk(question);
}

function quickAsk(text) {
    const input = document.getElementById('chat-input');
    input.value = text;
    autoResizeTextarea();
    sendMessage();
}

// Sao chép khối mã / văn bản mẫu
function copyCode(btn) {
    const container = btn.closest('.chat-code-block');
    if (!container) return;
    const codeEl = container.querySelector('code');
    if (!codeEl) return;

    const textToCopy = codeEl.innerText || codeEl.textContent;
    navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = btn.innerHTML;
        btn.innerHTML = 'Đã sao chép! ✓';
        btn.classList.add('copied');
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('copied');
        }, 2000);
    }).catch(err => {
        console.error('Copy failed:', err);
    });
}

// ==================== HELPERS ====================
function initScrollWatcher() {
    const area = document.getElementById('chat-area');
    const scrollBtn = document.getElementById('btn-scroll-bottom');
    if (!area || !scrollBtn) return;

    area.addEventListener('scroll', () => {
        const distanceToBottom = area.scrollHeight - area.scrollTop - area.clientHeight;
        if (distanceToBottom > 150) {
            scrollBtn.classList.add('visible');
        } else {
            scrollBtn.classList.remove('visible');
        }
    });
}

// Gọi lắng nghe cuộn khi tải trang
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initScrollWatcher);
} else {
    initScrollWatcher();
}

// ==================== HELPERS ====================
function autoResizeTextarea() {
    const textarea = document.getElementById('chat-input');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function updateCharacterCount() {
    const input = document.getElementById('chat-input');
    const count = document.getElementById('chat-character-count');
    if (count) count.textContent = `${input.value.length}/500`;
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function updateSendButton() {
    const btn = document.getElementById('btn-send');
    if (isLoading) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner spinner-sm"></span>';
    } else {
        btn.disabled = false;
        btn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
        `;
    }
}

function scrollToBottom() {
    const area = document.getElementById('chat-area');
    setTimeout(() => {
        area.scrollTop = area.scrollHeight;
    }, 60);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderMarkdown(text) {
    if (!text) return '';

    // 1. Tách và bảo toàn các khối code blocks (```...```)
    const codeBlocks = [];
    let processed = text.replace(/```([a-zA-Z]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
        codeBlocks.push({ lang: lang || 'text', code });
        return placeholder;
    });

    // 2. Escape HTML các phần text thông thường
    processed = escapeHtml(processed);

    // 3. Headers: ### và ##
    processed = processed.replace(/^### (.*?)$/gm, '<h3 class="chat-h3">$1</h3>');
    processed = processed.replace(/^## (.*?)$/gm, '<h2 class="chat-h2">$1</h2>');

    // 4. Bold: **text**
    processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // 5. Italic: *text*
    processed = processed.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // 6. Inline code: `code`
    processed = processed.replace(/`([^`]+)`/g, '<code class="chat-inline-code">$1</code>');

    // 7. Bullet points: lines starting with - or *
    processed = processed.replace(/^[\-\*] (.*?)$/gm, '<div class="chat-list-item"><span class="chat-bullet">•</span> $1</div>');

    // 8. Numbered lists: 1. 2. 3.
    processed = processed.replace(/^(\d+)\. (.*?)$/gm, '<div class="chat-list-item"><span class="chat-num">$1.</span> $2</div>');

    // 9. Line breaks (giữ các thẻ khối div, h2, h3 sạch sẽ)
    processed = processed.replace(/\n\n/g, '<div class="chat-spacer"></div>');
    processed = processed.replace(/\n/g, '<br>');

    // 10. Khôi phục các khối code blocks với header và nút sao chép
    codeBlocks.forEach((block, idx) => {
        const placeholder = `__CODE_BLOCK_${idx}__`;
        const langLabel = block.lang.toUpperCase() || 'MẪU VĂN BẢN';
        const renderedBlock = `
            <div class="chat-code-block">
                <div class="chat-code-header">
                    <span>📋 ${langLabel}</span>
                    <button type="button" class="chat-code-copy-btn" onclick="copyCode(this)">📋 Sao chép</button>
                </div>
                <pre class="chat-code-pre"><code>${escapeHtml(block.code.trim())}</code></pre>
            </div>
        `;
        processed = processed.replace(placeholder, renderedBlock);
    });

    return processed;
}
