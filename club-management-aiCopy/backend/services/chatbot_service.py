"""
Chatbot Service - UniClub Assistant
Trợ lý ảo thông minh cho Hệ thống Quản lý Câu lạc bộ Sinh viên
"""
import json
import os
from datetime import datetime
from typing import Any, Callable
from sqlalchemy.orm import Session
from models import (
    Department, Activity, Member, Notification, Attendance, FAQ,
    ScheduledPost, FinancialTransaction, MemberFee
)
from services.ai_service import call_openai, call_openai_with_tools

# ==================== SYSTEM PROMPT ====================
CLUBAI_SYSTEM_PROMPT = """Bạn là ClubAI, một Trợ lý quản lý Câu lạc bộ thông minh. Nhiệm vụ của bạn là hỗ trợ Ban chủ nhiệm và Hội viên thông qua việc gọi các hàm (Function Calling/Tools) có sẵn trong hệ thống.

QUY TẮC HOẠT ĐỘNG:
1. Khi hỏi về tình trạng hội viên, gọi get_member_stats(member_id) và đánh giá gắn bó Cao/Trung bình/Thấp.
2. Khi được yêu cầu viết thông báo, viết ngắn gọn, chuyên nghiệp và gọi schedule_post(content, time). Câu hỏi thông tin chung dùng dữ liệu FAQ và database được cung cấp.
3. Khi lên kế hoạch sự kiện, gọi get_historical_events(type) để dự đoán số người và chi phí hậu cần.
4. Khi truy vấn quỹ, gọi get_financial_report(). Khi cần nhắc phí, gọi send_fee_reminder(member_id, amount).

QUY TẮC PHẢN HỒI:
- Chỉ cung cấp thông tin dựa trên dữ liệu hệ thống. Không tự bịa số liệu tài chính nếu tool không trả về kết quả.
- Chỉ trả lời các vấn đề liên quan đến câu lạc bộ.
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


def _tool_schema(name: str, description: str, properties: dict, required: list) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required}
        }
    }


CLUBAI_TOOLS = [
    _tool_schema("get_member_stats", "Lấy thống kê điểm danh và mức độ gắn bó của hội viên.",
                 {"member_id": {"type": "integer"}}, ["member_id"]),
    _tool_schema("analyze_member_engagement", "Tính điểm gắn bó dựa trên số lần tham gia sự kiện.",
                 {"member_id": {"type": "integer"}}, ["member_id"]),
    _tool_schema("schedule_post", "Lưu một thông báo để đăng vào thời gian chỉ định.",
                 {"content": {"type": "string"}, "time": {"type": "string"}}, ["content", "time"]),
    _tool_schema("get_historical_events", "Lấy dữ liệu hoạt động cũ theo loại để dự báo sự kiện.",
                 {"type": {"type": "string"}}, ["type"]),
    _tool_schema("get_financial_report", "Tổng hợp thu, chi và số dư từ sổ quỹ.", {}, []),
    _tool_schema("send_fee_reminder", "Tạo bản ghi nhắc phí thân thiện cho một hội viên.",
                 {"member_id": {"type": "integer"}, "amount": {"type": "number"}}, ["member_id", "amount"]),
    _tool_schema("generate_financial_reminder", "Sinh nội dung nhắc phí cá nhân hóa cho danh sách hội viên chưa đóng quỹ.",
                 {"user_list": {"type": "array", "items": {"type": "integer"}}}, ["user_list"]),
]


def _member_stats(db: Session, member_id: int) -> dict:
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        return {"error": "Không tìm thấy hội viên."}
    total = db.query(Attendance).filter(Attendance.member_id == member_id).count()
    present = db.query(Attendance).filter(
        Attendance.member_id == member_id, Attendance.status == "present"
    ).count()
    score = round(present / total * 100, 2) if total else 0
    level = "Cao" if score >= 75 else "Trung bình" if score >= 40 else "Thấp"
    return {"member_id": member_id, "member_name": member.name, "events_attended": present,
            "events_recorded": total, "engagement_score": score, "engagement_level": level}


def _tool_handlers(db: Session) -> dict[str, Callable[..., Any]]:
    def schedule_post(content: str, time: str) -> dict:
        try:
            scheduled_at = datetime.fromisoformat(time.replace("Z", "+00:00"))
        except ValueError:
            return {"error": "time phải là ISO-8601 hợp lệ."}
        post = ScheduledPost(content=content, scheduled_at=scheduled_at)
        db.add(post)
        db.commit()
        return {"scheduled_post_id": post.id, "status": post.status, "scheduled_at": time}

    def historical_events(event_type: str) -> dict:
        activities = db.query(Activity).filter(Activity.status == "completed").all()
        matching = [a for a in activities if not event_type or event_type.lower() in a.name.lower()]
        counts = []
        for activity in matching:
            present = db.query(Attendance).filter(
                Attendance.activity_id == activity.id, Attendance.status == "present"
            ).count()
            counts.append({"name": activity.name, "participants": present, "notes": activity.notes})
        average = round(sum(item["participants"] for item in counts) / len(counts), 2) if counts else 0
        return {"type": event_type, "events": counts, "average_participants": average}

    def financial_report() -> dict:
        transactions = db.query(FinancialTransaction).all()
        income = sum(t.amount for t in transactions if t.transaction_type == "income")
        expense = sum(t.amount for t in transactions if t.transaction_type == "expense")
        return {"income": income, "expense": expense, "balance": income - expense,
                "transaction_count": len(transactions)} if transactions else {"error": "Chưa có dữ liệu tài chính."}

    def fee_reminder(member_id: int, amount: float) -> dict:
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return {"error": "Không tìm thấy hội viên."}
        reminder = (f"Chào {member.name}, CLB thân mời bạn hoàn tất khoản quỹ "
                    f"{amount:,.0f} VNĐ. Cảm ơn bạn đã đồng hành cùng CLB!")
        return {"member_id": member_id, "amount": amount, "message": reminder, "status": "ready"}

    def financial_reminders(user_list: list[int]) -> dict:
        reminders = []
        for member_id in user_list:
            fee = db.query(MemberFee).filter(
                MemberFee.member_id == member_id, MemberFee.status == "unpaid"
            ).order_by(MemberFee.id.desc()).first()
            if fee:
                reminders.append(fee_reminder(member_id, fee.amount))
            else:
                reminders.append({"member_id": member_id, "error": "Không có khoản phí chưa thanh toán."})
        return {"reminders": reminders}

    return {
        "get_member_stats": lambda member_id: _member_stats(db, member_id),
        "analyze_member_engagement": lambda member_id: _member_stats(db, member_id),
        "schedule_post": schedule_post,
        "get_historical_events": historical_events,
        "get_financial_report": financial_report,
        "send_fee_reminder": fee_reminder,
        "generate_financial_reminder": financial_reminders,
    }


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

    # --- FAQ knowledge base (RAG context) ---
    faqs = db.query(FAQ).filter(FAQ.is_active == "active").all()
    if faqs:
        context_parts.append("\n=== FAQ / KIẾN THỨC CLB ===")
        for faq in faqs:
            context_parts.append(f"- {faq.question}: {faq.answer}")

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

    try:
        messages = [
            {"role": "system", "content": CLUBAI_SYSTEM_PROMPT},
            {"role": "user", "content": (
                f"DỮ LIỆU HỆ THỐNG (CLB Context Data):\n{club_context}\n\n"
                f"CÂU HỎI CỦA NGƯỜI DÙNG:\n{message}\n\n"
                "Hãy trả lời theo đúng định dạng JSON đã quy định."
            )}
        ]
        handlers = _tool_handlers(db)
        for _ in range(5):
            assistant_message = await call_openai_with_tools(messages, CLUBAI_TOOLS)
            tool_calls = assistant_message.get("tool_calls") or []
            if not tool_calls:
                return _parse_ai_response(assistant_message.get("content") or "")

            messages.append(assistant_message)
            for tool_call in tool_calls:
                function = tool_call["function"]
                name = function["name"]
                if name not in handlers:
                    result = {"error": f"Tool không tồn tại: {name}"}
                else:
                    try:
                        arguments = json.loads(function.get("arguments", "{}"))
                        result = handlers[name](**arguments)
                    except (json.JSONDecodeError, TypeError, ValueError) as error:
                        result = {"error": f"Tham số tool không hợp lệ: {error}"}
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": name,
                    "content": json.dumps(result, ensure_ascii=False)
                })
        return {"answer": "AI không hoàn tất được yêu cầu sau nhiều lần gọi tool.",
                "suggestedClubs": [], "followUpQuestions": []}

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
