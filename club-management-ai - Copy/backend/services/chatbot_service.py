"""
Chatbot Service - UniClub Assistant
Trợ lý ảo thông minh cho Hệ thống Quản lý Câu lạc bộ Sinh viên
"""
import json
import os
from sqlalchemy.orm import Session
from models import Department, Activity, Member, Notification
from services.ai_service import call_openai

# ==================== SYSTEM PROMPT ====================
UNICLUB_SYSTEM_PROMPT = """Bạn là "UniClub Assistant" – Trợ lý ảo thông minh và thân thiện của Hệ thống Quản lý Câu lạc bộ Sinh viên.

NHIỆM VỤ CHÍNH:
1. Giải đáp các thắc mắc của sinh viên về quy chế hoạt động, quyền lợi, cách đăng ký, thời gian sinh hoạt, và các sự kiện của câu lạc bộ.
2. Tư vấn, định hướng câu lạc bộ phù hợp dựa trên sở thích, chuyên ngành, định hướng phát triển hoặc quỹ thời gian của sinh viên.
3. Hướng dẫn sinh viên cách sử dụng hệ thống (điểm danh QR code, nộp đơn ứng tuyển, theo dõi điểm rèn luyện).

QUY TẮC PHẢN HỒI:
- Giọng văn: Năng động, lịch sự, tích cực, gần gũi và mang đậm phong cách sinh viên đại học.
- Độ chính xác: Chỉ cung cấp thông tin dựa trên dữ liệu hệ thống được cung cấp (CLB Context Data). Nếu không có thông tin cụ thể, hãy hướng dẫn sinh viên liên hệ trực tiếp Fanpage hoặc Ban chủ nhiệm CLB đó.
- Định dạng câu trả lời: Rõ ràng, sử dụng bullet points (- hoặc *) cho các ý chính, tránh viết đoạn văn quá dài gây khó đọc.
- Giới hạn: Không bịa đặt thông tin về lệ phí quỹ, ban chủ nhiệm nếu chưa có trong dữ liệu; không trả lời các chủ đề ngoài phạm vi trường học/CLB.

ĐỊNH DẠNG ĐẦU RA BẮT BUỘC (JSON):
Bạn PHẢI trả về response theo đúng định dạng JSON sau (không thêm text bên ngoài JSON):
{
  "answer": "Câu trả lời chi tiết bằng văn bản gửi cho sinh viên (hỗ trợ định dạng Markdown)",
  "suggestedClubs": [
    {
      "maDinhDanh": "ID_BAN",
      "tenClb": "Tên ban/CLB",
      "lyDoGoiY": "Lý do gợi ý ngắn gọn"
    }
  ],
  "followUpQuestions": [
    "Câu hỏi gợi ý tiếp theo 1",
    "Câu hỏi gợi ý tiếp theo 2"
  ]
}

Lưu ý:
- suggestedClubs có thể là mảng rỗng [] nếu câu hỏi không liên quan đến gợi ý CLB/ban.
- followUpQuestions luôn có 2-3 câu hỏi gợi ý liên quan.
- answer hỗ trợ Markdown: **bold**, *italic*, - bullet points.
"""


def build_club_context(db: Session) -> str:
    """Xây dựng context data từ database để gửi kèm prompt"""
    context_parts = []

    # --- Departments (Bans) ---
    departments = db.query(Department).all()
    if departments:
        context_parts.append("=== CÁC BAN CHUYÊN MÔN ===")
        for dept in departments:
            leader_name = dept.leader.name if dept.leader else "Chưa có"
            member_count = len(dept.members) if dept.members else 0
            context_parts.append(
                f"- {dept.name} (ID: DEPT_{dept.id}): {dept.description or 'Chưa có mô tả'}\n"
                f"  Trưởng ban: {leader_name} | Số thành viên: {member_count}"
            )

    # --- Activities ---
    activities = db.query(Activity).all()
    if activities:
        context_parts.append("\n=== HOẠT ĐỘNG CLB ===")
        for act in activities:
            date_str = act.date.strftime("%d/%m/%Y %H:%M") if act.date else "Chưa xác định"
            status_map = {
                "upcoming": "Sắp diễn ra",
                "ongoing": "Đang diễn ra",
                "completed": "Đã hoàn thành",
                "cancelled": "Đã hủy"
            }
            status_vn = status_map.get(act.status, act.status)
            context_parts.append(
                f"- {act.name}: {act.description or ''}\n"
                f"  Thời gian: {date_str} | Địa điểm: {act.location or 'Chưa xác định'} | "
                f"Trạng thái: {status_vn}"
            )
            if act.result:
                context_parts.append(f"  Kết quả: {act.result}")

    # --- Members stats ---
    total_members = db.query(Member).filter(Member.status == "active").count()
    total_inactive = db.query(Member).filter(Member.status == "inactive").count()
    context_parts.append(f"\n=== THỐNG KÊ ===")
    context_parts.append(f"- Tổng thành viên hoạt động: {total_members}")
    context_parts.append(f"- Thành viên ngừng hoạt động: {total_inactive}")
    context_parts.append(f"- Tổng số ban chuyên môn: {len(departments)}")
    context_parts.append(f"- Tổng hoạt động: {len(activities)}")

    # --- Recent notifications ---
    notifications = db.query(Notification).order_by(
        Notification.created_at.desc()
    ).limit(5).all()
    if notifications:
        context_parts.append("\n=== THÔNG BÁO GẦN ĐÂY ===")
        for noti in notifications:
            date_str = noti.created_at.strftime("%d/%m/%Y") if noti.created_at else ""
            context_parts.append(f"- [{date_str}] {noti.title}: {noti.content[:100]}...")

    # --- System features ---
    context_parts.append("\n=== TÍNH NĂNG HỆ THỐNG ===")
    context_parts.append("- Điểm danh: Trưởng ban/Chủ nhiệm điểm danh qua hệ thống, thành viên có thể xem lịch sử điểm danh.")
    context_parts.append("- Nhiệm vụ: Chủ nhiệm/Trưởng ban phân công nhiệm vụ, thành viên cập nhật tiến độ.")
    context_parts.append("- Thông báo: Hệ thống gửi thông báo về hoạt động, sự kiện mới.")
    context_parts.append("- AI Assistant: Hỗ trợ sinh thông báo, tóm tắt hoạt động, gợi ý phân công nhiệm vụ.")
    context_parts.append("- Phân quyền: Chủ nhiệm (full quyền), Trưởng ban (quản lý ban mình), Thành viên (xem và cập nhật cá nhân).")

    return "\n".join(context_parts)


def _generate_demo_chat_response(message: str) -> dict:
    """Tạo demo response khi không có API key"""
    msg_lower = message.lower()

    # Default follow-up questions
    default_followups = [
        "CLB có những ban chuyên môn nào?",
        "Làm sao để đăng ký tham gia CLB?",
        "Sắp tới CLB có hoạt động gì không?"
    ]

    if any(kw in msg_lower for kw in ["ban", "chuyên môn", "phòng ban", "department"]):
        return {
            "answer": (
                "Chào bạn! 🎉 CLB hiện đang có **4 ban chuyên môn** nè:\n\n"
                "- **Ban Truyền thông** 📢: Phụ trách truyền thông, marketing và hình ảnh CLB\n"
                "- **Ban Kỹ thuật** 💻: Phụ trách hệ thống IT, website và công nghệ\n"
                "- **Ban Sự kiện** 🎪: Tổ chức các sự kiện, hoạt động ngoại khóa\n"
                "- **Ban Học thuật** 📚: Tổ chức workshop, seminar, training\n\n"
                "Mỗi ban đều có trưởng ban phụ trách riêng. Bạn có thể chọn ban phù hợp với sở thích và kỹ năng của mình nhé! 💪\n\n"
                "*[Đây là phản hồi demo — Cần cấu hình OpenAI API Key để dùng AI thực tế]*"
            ),
            "suggestedClubs": [
                {"maDinhDanh": "DEPT_1", "tenClb": "Ban Truyền thông", "lyDoGoiY": "Phù hợp nếu bạn thích sáng tạo nội dung, thiết kế"},
                {"maDinhDanh": "DEPT_2", "tenClb": "Ban Kỹ thuật", "lyDoGoiY": "Phù hợp nếu bạn đam mê lập trình, công nghệ"},
                {"maDinhDanh": "DEPT_3", "tenClb": "Ban Sự kiện", "lyDoGoiY": "Phù hợp nếu bạn thích tổ chức, giao tiếp"},
                {"maDinhDanh": "DEPT_4", "tenClb": "Ban Học thuật", "lyDoGoiY": "Phù hợp nếu bạn thích nghiên cứu, học hỏi"}
            ],
            "followUpQuestions": [
                "Ban nào đang thiếu thành viên nhất?",
                "Mình thích lập trình thì nên vào ban gì?",
                "Làm sao để đăng ký vào một ban?"
            ]
        }
    elif any(kw in msg_lower for kw in ["lập trình", "code", "it", "kỹ thuật", "python", "javascript", "web"]):
        return {
            "answer": (
                "Ồ bạn thích lập trình hả? Tuyệt vời! 🚀\n\n"
                "**Ban Kỹ thuật** là nơi dành cho bạn đó!\n\n"
                "Tại Ban Kỹ thuật, bạn sẽ được:\n"
                "- Tham gia phát triển website, ứng dụng cho CLB\n"
                "- Học hỏi các công nghệ mới: Python, JavaScript, React, FastAPI...\n"
                "- Tham gia các Workshop, Hackathon\n"
                "- Làm việc nhóm với các bạn cùng đam mê\n\n"
                "Hiện tại ban đang có các thành viên với kỹ năng đa dạng từ Backend, Frontend đến Mobile dev. "
                "Bạn sẽ có cơ hội học hỏi rất nhiều! 💡\n\n"
                "*[Đây là phản hồi demo — Cần cấu hình OpenAI API Key để dùng AI thực tế]*"
            ),
            "suggestedClubs": [
                {"maDinhDanh": "DEPT_2", "tenClb": "Ban Kỹ thuật", "lyDoGoiY": "Phù hợp với đam mê lập trình và làm dự án thực tế"}
            ],
            "followUpQuestions": [
                "Ban Kỹ thuật sinh hoạt vào thời gian nào?",
                "Tham gia Ban Kỹ thuật có được cộng điểm rèn luyện không?",
                "Workshop Python sắp tới là khi nào?"
            ]
        }
    elif any(kw in msg_lower for kw in ["hoạt động", "sự kiện", "event", "workshop", "hackathon"]):
        return {
            "answer": (
                "Hay quá, bạn quan tâm đến hoạt động CLB! 🎊\n\n"
                "Dưới đây là **một số hoạt động** của CLB:\n\n"
                "✅ **Đã hoàn thành:**\n"
                "- Workshop Python cơ bản — Phòng A301\n"
                "- Cuộc thi Hackathon 2024 — Hội trường lớn\n\n"
                "📅 **Sắp diễn ra:**\n"
                "- Giao lưu CLB công nghệ — Sảnh chính, Khu A\n"
                "- Training Design Thinking — Phòng Lab 205\n"
                "- Teambuilding cuối năm — Khu du lịch sinh thái\n\n"
                "Bạn hãy theo dõi thông báo trên hệ thống để không bỏ lỡ nhé! 📣\n\n"
                "*[Đây là phản hồi demo — Cần cấu hình OpenAI API Key để dùng AI thực tế]*"
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Tham gia hoạt động có bắt buộc không?",
                "Làm sao để đăng ký tham gia hoạt động?",
                "CLB có tổ chức Hackathon nữa không?"
            ]
        }
    elif any(kw in msg_lower for kw in ["đăng ký", "tham gia", "gia nhập", "đơn", "ứng tuyển"]):
        return {
            "answer": (
                "Bạn muốn tham gia CLB? Chào mừng bạn! 🥳\n\n"
                "Để **đăng ký tham gia**, bạn thực hiện theo các bước:\n\n"
                "1. **Liên hệ Ban chủ nhiệm** qua Fanpage CLB hoặc trực tiếp\n"
                "2. **Điền đơn đăng ký** theo form trên hệ thống\n"
                "3. **Tham gia phỏng vấn** (nếu có đợt tuyển quân)\n"
                "4. **Nhận kết quả** và được phân vào ban phù hợp\n\n"
                "Sau khi được duyệt, bạn sẽ có tài khoản trên hệ thống để:\n"
                "- Xem lịch hoạt động\n"
                "- Theo dõi nhiệm vụ được phân công\n"
                "- Nhận thông báo từ CLB\n\n"
                "*[Đây là phản hồi demo — Cần cấu hình OpenAI API Key để dùng AI thực tế]*"
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Đợt tuyển quân sắp tới là khi nào?",
                "CLB có yêu cầu gì đặc biệt khi đăng ký không?",
                "Mình chưa có kinh nghiệm có đăng ký được không?"
            ]
        }
    elif any(kw in msg_lower for kw in ["điểm danh", "qr", "rèn luyện", "điểm"]):
        return {
            "answer": (
                "Bạn hỏi về điểm danh phải không? Mình giải thích nhé! ✅\n\n"
                "**Hệ thống điểm danh** hoạt động như sau:\n\n"
                "- Trưởng ban hoặc Chủ nhiệm sẽ **điểm danh qua hệ thống** tại mỗi hoạt động\n"
                "- Trạng thái điểm danh gồm: ✅ Có mặt, ❌ Vắng, ⚠️ Có phép\n"
                "- Thành viên có thể **xem lịch sử điểm danh** của mình trên hệ thống\n\n"
                "**Về điểm rèn luyện:**\n"
                "- Tham gia hoạt động CLB có thể được **cộng điểm rèn luyện** theo quy định của nhà trường\n"
                "- Chi tiết cụ thể về điểm rèn luyện, bạn nên liên hệ trực tiếp Ban chủ nhiệm để được tư vấn chính xác nhé!\n\n"
                "*[Đây là phản hồi demo — Cần cấu hình OpenAI API Key để dùng AI thực tế]*"
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Vắng bao nhiêu buổi thì bị cảnh báo?",
                "Làm sao để xin nghỉ phép?",
                "Mỗi hoạt động được cộng bao nhiêu điểm rèn luyện?"
            ]
        }
    else:
        # Default greeting / generic response
        return {
            "answer": (
                "Chào bạn! 👋 Mình là **UniClub Assistant** — trợ lý ảo của CLB Sinh viên!\n\n"
                "Mình có thể giúp bạn:\n"
                "- 📋 Tìm hiểu về **các ban chuyên môn** trong CLB\n"
                "- 📅 Xem **lịch hoạt động, sự kiện** sắp tới\n"
                "- 🎯 **Tư vấn ban phù hợp** dựa trên sở thích của bạn\n"
                "- 📝 Hướng dẫn **đăng ký tham gia** CLB\n"
                "- ✅ Giải đáp về **điểm danh, điểm rèn luyện**\n\n"
                "Bạn cứ hỏi mình bất cứ điều gì liên quan đến CLB nhé! 😊\n\n"
                "*[Đây là phản hồi demo — Cần cấu hình OpenAI API Key để dùng AI thực tế]*"
            ),
            "suggestedClubs": [
                {"maDinhDanh": "DEPT_1", "tenClb": "Ban Truyền thông", "lyDoGoiY": "Sáng tạo nội dung, thiết kế đồ họa"},
                {"maDinhDanh": "DEPT_2", "tenClb": "Ban Kỹ thuật", "lyDoGoiY": "Lập trình, phát triển ứng dụng"},
                {"maDinhDanh": "DEPT_3", "tenClb": "Ban Sự kiện", "lyDoGoiY": "Tổ chức sự kiện, giao tiếp"},
                {"maDinhDanh": "DEPT_4", "tenClb": "Ban Học thuật", "lyDoGoiY": "Nghiên cứu, workshop, seminar"}
            ],
            "followUpQuestions": default_followups
        }


async def chat_with_assistant(message: str, db: Session) -> dict:
    """
    Xử lý tin nhắn từ sinh viên, trả về JSON response
    """
    # Build context from database
    club_context = build_club_context(db)

    # Check if OpenAI API key is configured
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        # Demo mode
        return _generate_demo_chat_response(message)

    # Build user prompt with context
    user_prompt = (
        f"DỮ LIỆU HỆ THỐNG (CLB Context Data):\n"
        f"{club_context}\n\n"
        f"---\n\n"
        f"CÂU HỎI CỦA SINH VIÊN:\n{message}\n\n"
        f"Hãy trả lời theo đúng định dạng JSON đã quy định."
    )

    try:
        raw_result = await call_openai(UNICLUB_SYSTEM_PROMPT, user_prompt)

        # Try to parse JSON from response
        return _parse_ai_response(raw_result)

    except Exception as e:
        # Fallback to demo response on error
        return _generate_demo_chat_response(message)


def _parse_ai_response(raw: str) -> dict:
    """Parse AI response, extract JSON if wrapped in text"""
    # Try direct parse
    try:
        result = json.loads(raw)
        return _validate_response(result)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code block
    import re
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group(1))
            return _validate_response(result)
        except json.JSONDecodeError:
            pass

    # Try to find JSON object in text
    json_match = re.search(r'\{[^{}]*"answer"[^{}]*\}', raw, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group(0))
            return _validate_response(result)
        except json.JSONDecodeError:
            pass

    # Fallback: wrap raw text as answer
    return {
        "answer": raw,
        "suggestedClubs": [],
        "followUpQuestions": [
            "CLB có những ban chuyên môn nào?",
            "Sắp tới có hoạt động gì không?",
            "Làm sao để đăng ký tham gia CLB?"
        ]
    }


def _validate_response(data: dict) -> dict:
    """Ensure response has all required fields"""
    if "answer" not in data:
        data["answer"] = "Mình chưa có thông tin về câu hỏi này. Bạn hãy liên hệ Ban chủ nhiệm CLB nhé!"
    if "suggestedClubs" not in data or not isinstance(data["suggestedClubs"], list):
        data["suggestedClubs"] = []
    if "followUpQuestions" not in data or not isinstance(data["followUpQuestions"], list):
        data["followUpQuestions"] = [
            "CLB có những ban chuyên môn nào?",
            "Sắp tới có hoạt động gì không?",
            "Làm sao để đăng ký tham gia CLB?"
        ]
    return data
