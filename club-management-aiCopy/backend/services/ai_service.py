"""
AI Service - Tích hợp OpenAI API
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


async def call_openai(system_prompt: str, user_prompt: str) -> str:
    """Gọi OpenAI API"""
    if not OPENAI_API_KEY:
        return "[AI Demo Mode] API Key chưa được cấu hình. Vui lòng thêm OPENAI_API_KEY vào file .env\n\n---\n\n" + _generate_demo_response(user_prompt)

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"Lỗi API: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Lỗi kết nối AI: {str(e)}"


async def call_openai_with_tools(messages: list, tools: list) -> dict:
    """Gọi Chat Completions API và giữ nguyên message/tool-call metadata."""
    if not OPENAI_API_KEY:
        return {"role": "assistant", "content": None}

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto",
                    "temperature": 0.3,
                    "max_tokens": 1200,
                    "response_format": {"type": "json_object"}
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]
    except Exception as e:
        raise RuntimeError(f"Lỗi kết nối AI: {str(e)}") from e


def _generate_demo_response(user_prompt: str) -> str:
    """Tạo response demo khi không có API key"""
    if "thông báo" in user_prompt.lower() or "thông báo" in user_prompt:
        return """**📢 THÔNG BÁO**

Kính gửi các thành viên Câu lạc bộ,

Câu lạc bộ trân trọng thông báo về hoạt động sắp tới. Mong tất cả thành viên sắp xếp thời gian tham gia đầy đủ.

Chi tiết sẽ được cập nhật qua các kênh liên lạc chính thức.

Trân trọng,
Ban Quản lý CLB

*[Đây là nội dung demo - Cần cấu hình OpenAI API Key để sử dụng AI thực tế]*"""

    elif "tóm tắt" in user_prompt.lower() or "summarize" in user_prompt.lower():
        return """**📋 TÓM TẮT HOẠT ĐỘNG**

**Kết quả đạt được:**
- Hoạt động đã được tổ chức thành công
- Các mục tiêu cơ bản đã hoàn thành

**Vấn đề tồn tại:**
- Cần đánh giá chi tiết hơn khi có đầy đủ dữ liệu

**Đề xuất cải thiện:**
- Lên kế hoạch chi tiết hơn cho lần tới
- Thu thập phản hồi từ thành viên

*[Đây là nội dung demo - Cần cấu hình OpenAI API Key để sử dụng AI thực tế]*"""

    else:
        return """**🤖 GỢI Ý PHÂN CÔNG NHIỆM VỤ**

| Nhiệm vụ | Thành viên đề xuất | Kỹ năng phù hợp | Lý do |
|-----------|-------------------|-----------------|-------|
| Nhiệm vụ 1 | Thành viên A | Kỹ năng liên quan | Phù hợp với chuyên môn |
| Nhiệm vụ 2 | Thành viên B | Kỹ năng liên quan | Có kinh nghiệm tương tự |

*Lưu ý: Đây là gợi ý dựa trên thông tin có sẵn. Quản lý nên xem xét thêm các yếu tố khác.*

*[Đây là nội dung demo - Cần cấu hình OpenAI API Key để sử dụng AI thực tế]*"""


async def generate_notification(activity_name: str, time: str = "", location: str = "",
                                content: str = "", target_audience: str = "") -> str:
    """AI sinh thông báo hoạt động"""
    system_prompt = (
        "Bạn là trợ lý quản lý câu lạc bộ sinh viên. "
        "Viết thông báo ngắn gọn, thân thiện, rõ ràng. "
        "Không tự thêm thông tin chưa được cung cấp. "
        "Viết bằng tiếng Việt."
    )

    activity_info = f"Tên hoạt động: {activity_name}"
    if time:
        activity_info += f"\nThời gian: {time}"
    if location:
        activity_info += f"\nĐịa điểm: {location}"
    if content:
        activity_info += f"\nNội dung: {content}"
    if target_audience:
        activity_info += f"\nĐối tượng nhận: {target_audience}"

    user_prompt = f"Hoạt động: {activity_info}\n\nHãy viết thông báo gửi đến thành viên câu lạc bộ."

    return await call_openai(system_prompt, user_prompt)


async def summarize_activity(activity_name: str, description: str = "",
                             notes: str = "", result: str = "", feedback: str = "") -> str:
    """AI tóm tắt kết quả hoạt động"""
    system_prompt = (
        "Bạn là trợ lý quản lý câu lạc bộ sinh viên. "
        "Hãy tóm tắt hoạt động dựa trên thông tin được cung cấp. "
        "Bao gồm: tóm tắt, kết quả đạt được, vấn đề tồn tại, đề xuất cải thiện (nếu có đủ dữ liệu). "
        "Không tự bịa thông tin. Nếu dữ liệu không đủ, hãy nói rõ. "
        "Viết bằng tiếng Việt."
    )

    activity_info = f"Tên hoạt động: {activity_name}"
    if description:
        activity_info += f"\nMô tả: {description}"
    if notes:
        activity_info += f"\nGhi chú: {notes}"
    if result:
        activity_info += f"\nKết quả: {result}"
    if feedback:
        activity_info += f"\nPhản hồi thành viên: {feedback}"

    user_prompt = f"{activity_info}\n\nHãy tóm tắt hoạt động này."

    return await call_openai(system_prompt, user_prompt)


async def suggest_task_assignment(activity_info: str, member_skills: str,
                                  availability: str, tasks: str) -> str:
    """AI gợi ý phân công nhiệm vụ"""
    system_prompt = (
        "Bạn là trợ lý quản lý câu lạc bộ sinh viên. "
        "Hãy gợi ý phân công nhiệm vụ dựa trên ban, kỹ năng và lịch rảnh của thành viên. "
        "Không tự thêm thông tin chưa có. "
        "Nếu dữ liệu không đủ, hãy nói rõ dữ liệu còn thiếu. "
        "Trình bày kết quả dạng bảng: Nhiệm vụ | Thành viên | Kỹ năng phù hợp | Lý do. "
        "Viết bằng tiếng Việt."
    )

    user_prompt = (
        f"Hoạt động:\n{activity_info}\n\n"
        f"Danh sách thành viên:\n{member_skills}\n\n"
        f"Lịch rảnh:\n{availability}\n\n"
        f"Danh sách nhiệm vụ:\n{tasks}\n\n"
        "Hãy gợi ý phân công nhiệm vụ phù hợp."
    )

    return await call_openai(system_prompt, user_prompt)
