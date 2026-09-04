/**
 * chatbot.js - UniClub Assistant Chatbot Logic
 * Standalone — không yêu cầu auth.js
 */

const CHAT_API = 'http://localhost:8000/api/ai/chat';

// ==================== STATE ====================
let isLoading = false;

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    initChatbot();
});

function initChatbot() {
    // Auto-resize textarea
    const input = document.getElementById('chat-input');
    input.addEventListener('input', autoResizeTextarea);
    input.addEventListener('keydown', handleKeyDown);

    // Show welcome message
    showWelcomeMessage();
}

// ==================== WELCOME ====================
function showWelcomeMessage() {
    const welcomeData = {
        answer: (
            "Xin chào! 👋 Mình là **UniClub Assistant** — trợ lý ảo của Hệ thống Quản lý CLB Sinh viên!\n\n" +
            "Mình có thể giúp bạn:\n" +
            "- 📋 Tìm hiểu về **các ban chuyên môn** trong CLB\n" +
            "- 📅 Xem **lịch hoạt động, sự kiện** sắp tới\n" +
            "- 🎯 **Tư vấn ban phù hợp** dựa trên sở thích\n" +
            "- 📝 Hướng dẫn **đăng ký tham gia** CLB\n" +
            "- ✅ Giải đáp về **điểm danh, điểm rèn luyện**\n\n" +
            "Hãy hỏi mình bất cứ điều gì nhé! 😊"
        ),
        suggestedClubs: [],
        followUpQuestions: [
            "CLB có những ban chuyên môn nào?",
            "Sắp tới có hoạt động gì không?",
            "Mình thích lập trình thì nên vào ban gì?",
            "Làm sao để đăng ký tham gia CLB?"
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
        const response = await fetch(CHAT_API, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

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
        typingEl.remove();

        renderBotMessage({
            answer: "Xin lỗi bạn, mình đang gặp sự cố kết nối. 😥\n\nBạn hãy thử lại sau hoặc liên hệ trực tiếp Ban chủ nhiệm CLB nhé!",
            suggestedClubs: [],
            followUpQuestions: [
                "Thử lại câu hỏi trước",
                "CLB có những ban chuyên môn nào?"
            ]
        });
    } finally {
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

    // Suggested clubs
    if (data.suggestedClubs && data.suggestedClubs.length > 0) {
        html += '<div class="chat-clubs">';
        html += '<div class="chat-clubs-title">🏫 Gợi ý cho bạn:</div>';
        html += '<div class="chat-clubs-grid">';
        data.suggestedClubs.forEach(club => {
            html += `
                <div class="chat-club-card">
                    <div class="chat-club-name">${escapeHtml(club.tenClb)}</div>
                    <div class="chat-club-reason">${escapeHtml(club.lyDoGoiY)}</div>
                    <div class="chat-club-id">${escapeHtml(club.maDinhDanh)}</div>
                </div>
            `;
        });
        html += '</div></div>';
    }

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

// ==================== FOLLOW-UP ====================
function askFollowUp(btn) {
    const question = btn.textContent;
    document.getElementById('chat-input').value = question;
    sendMessage();
}

// ==================== HELPERS ====================
function autoResizeTextarea() {
    const textarea = document.getElementById('chat-input');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
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
    }, 50);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderMarkdown(text) {
    if (!text) return '';

    let html = escapeHtml(text);

    // Bold: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic: *text*
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Line breaks
    html = html.replace(/\n/g, '<br>');

    // Bullet points: lines starting with - or *
    html = html.replace(/^- (.*?)(<br>|$)/gm, '<span class="chat-bullet">•</span> $1$2');

    return html;
}
