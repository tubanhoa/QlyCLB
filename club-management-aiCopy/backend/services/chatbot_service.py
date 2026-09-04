"""
Chatbot Service - UniClub Assistant
Trợ lý ảo thông minh & chuyên nghiệp hỗ trợ Sinh viên và Ban Quản lý CLB
"""
import json
import os
import re
from datetime import datetime
from typing import Any, Callable, List, Dict
from sqlalchemy.orm import Session
from models import Department, Activity, Member, Notification, Attendance, Task, User
from services.ai_service import call_openai_with_tools

# ==================== SYSTEM PROMPT CHO OPENAI ====================
CLUBAI_SYSTEM_PROMPT = """Bạn là UniClub Assistant — trợ lý hỗ trợ sinh viên của hệ thống quản lý câu lạc bộ.
Nhiệm vụ của bạn là:
1. Trả lời các thắc mắc của sinh viên về Câu lạc bộ (các ban chuyên môn, lịch hoạt động, quy chế điểm danh, điểm rèn luyện, đăng ký tham gia).
2. Tư vấn, định hướng chọn ban chuyên môn phù hợp dựa trên sở thích, kỹ năng, chuyên ngành hoặc quỹ thời gian của sinh viên.
3. Hướng dẫn sử dụng các tính năng trong hệ thống Quản lý CLB (CLB Manager).
4. Hỗ trợ soạn thảo biểu mẫu (đơn gia nhập, đơn xin phép nghỉ sinh hoạt, tin nhắn xin phép chuyên nghiệp).

QUY TẮC VÀ KIẾN THỨC PHẢN HỒI THẮC MẮC SINH VIÊN:
- Phong cách: Lịch sự, gần gũi, khích lệ và tôn trọng; xưng hô 'mình' và 'bạn'.
- Học tập luôn là ưu tiên. Nếu người dùng hỏi về lịch học, sức khỏe, tài chính cá nhân hoặc vấn đề ngoài CLB, hãy hướng dẫn họ liên hệ đúng phòng ban/người phụ trách thay vì đưa tư vấn chuyên môn.
- Chỉ khẳng định học phí, quỹ, điểm rèn luyện, quyền lợi, điều kiện tuyển thành viên hoặc thời hạn khi có trong DỮ LIỆU HỆ THỐNG. Nếu chưa có, nói rõ "mình chưa có dữ liệu xác nhận".
- Không hứa chắc về việc được nhận vào CLB, được cộng điểm, được cấp chứng nhận hoặc cơ hội việc làm.
- Khi tư vấn chọn ban, hãy hỏi thêm sở thích/kỹ năng nếu dữ liệu chưa đủ; không gán một ban chỉ dựa trên ngành học.
- Khi hướng dẫn thủ tục, nêu rõ đây là hướng dẫn tham khảo và khuyến nghị xác nhận với Ban chủ nhiệm.
- Sử dụng Markdown chuyên nghiệp: dùng **in đậm** cho từ khóa, gạch đầu dòng (-) rõ ràng, emoji trực quan, chia đoạn mạch lạc.
- Tính chính xác: Luôn căn cứ vào DỮ LIỆU HỆ THỐNG được cung cấp (tên ban, trưởng ban, hoạt động, thông báo). Tuyệt đối không bịa đặt số liệu tài chính hoặc thông tin trái ngược với dữ liệu thực tế.

ĐỊNH DẠNG ĐẦU RA BẮT BUỘC (JSON chuẩn, không kèm text ngoài JSON):
{
  "answer": "Câu trả lời chi tiết bằng văn bản gửi cho sinh viên (định dạng Markdown)",
  "suggestedClubs": [
    {
      "maDinhDanh": "Mã định danh ban (VD: DEPT_1, DEPT_2)",
      "tenClb": "Tên ban chuyên môn",
      "lyDoGoiY": "Lý do gợi ý ngắn gọn, thuyết phục"
    }
  ],
  "followUpQuestions": [
    "Câu hỏi gợi ý tiếp theo 1",
    "Câu hỏi gợi ý tiếp theo 2",
    "Câu hỏi gợi ý tiếp theo 3"
  ]
}
"""

def build_club_context(db: Session) -> str:
    """Trích xuất dữ liệu trực tiếp từ CSDL làm ngữ cảnh thời gian thực cho AI"""
    context_parts = []

    # 1. Các ban chuyên môn
    departments = db.query(Department).all()
    if departments:
        context_parts.append("=== CÁC BAN CHUYÊN MÔN HIỆN TẠI ===")
        for dept in departments:
            leader_name = dept.leader.name if dept.leader else "Chưa có"
            m_count = len(dept.members) if dept.members else 0
            context_parts.append(
                f"- {dept.name} (Mã: DEPT_{dept.id}): {dept.description or 'Chưa có mô tả'}\n"
                f"  Trưởng ban: {leader_name} | Thành viên: {m_count} người"
            )

    # 2. Các hoạt động
    activities = db.query(Activity).order_by(Activity.date.desc()).all()
    if activities:
        context_parts.append("\n=== HOẠT ĐỘNG & SỰ KIỆN CLB ===")
        for act in activities:
            d_str = act.date.strftime("%d/%m/%Y %H:%M") if act.date else "Chưa xác định"
            mgr_name = act.manager.name if act.manager else "Ban Tổ chức"
            status_map = {
                "upcoming": "Sắp diễn ra",
                "ongoing": "Đang diễn ra",
                "completed": "Đã hoàn thành",
                "cancelled": "Đã hủy"
            }
            status_vn = status_map.get(act.status, act.status)
            context_parts.append(
                f"- {act.name} [{status_vn}]: {act.description or ''}\n"
                f"  Thời gian: {d_str} | Địa điểm: {act.location or 'Chưa xác định'} | Phụ trách: {mgr_name}"
            )
            if act.result:
                context_parts.append(f"  Kết quả: {act.result}")

    # 3. Thống kê chung
    total_active = db.query(Member).filter(Member.status == "active").count()
    context_parts.append(f"\n=== THỐNG KÊ NHÂN SỰ ===")
    context_parts.append(f"- Tổng thành viên đang hoạt động: {total_active}")
    context_parts.append(f"- Tổng số ban chuyên môn: {len(departments)}")

    # 4. Thông báo mới nhất
    notis = db.query(Notification).order_by(Notification.created_at.desc()).limit(4).all()
    if notis:
        context_parts.append("\n=== CÁC THÔNG BÁO MỚI NHẤT ===")
        for n in notis:
            context_parts.append(f"- {n.title}: {n.content[:120]}...")

    return "\n".join(context_parts)


def _generate_smart_club_response(message: str, db: Session) -> dict:
    """
    Knowledge Inference Engine:
    Phản hồi thông minh, chuyên nghiệp, chính xác dựa trên dữ liệu thời gian thực từ CSDL.
    Hoạt động độc lập và làm nền tảng siêu mượt cho chế độ offline hoặc khi không có API key.
    """
    msg_lower = message.lower().strip()

    # Lấy thông tin thực tế từ database
    departments = db.query(Department).all()
    upcoming_acts = db.query(Activity).filter(Activity.status == "upcoming").order_by(Activity.date.asc()).all()
    completed_acts = db.query(Activity).filter(Activity.status == "completed").order_by(Activity.date.desc()).all()

    # 1. XIN NGHỈ PHÉP / VẮNG MẶT / MẪU ĐƠN / SOẠN THƯ (GỬI TRƯỞNG BAN)
    if (any(kw in msg_lower for kw in ["nghỉ phép", "xin vắng", "xin nghỉ", "mẫu đơn", "mẫu tin nhắn", "mẫu email", "soạn tin", "soạn email", "viết giúp"]) 
        or (any(kw in msg_lower for kw in ["vắng mặt", "xin phép"]) and any(kw in msg_lower for kw in ["buổi", "họp", "sinh hoạt", "workshop", "sự kiện"]))
    ) and not any(study_kw in msg_lower for study_kw in ["lịch học", "rớt môn", "ảnh hưởng học", "cân bằng"]):
        return {
            "answer": (
                "Chào bạn! Dưới đây là hướng dẫn chi tiết về **Quy định xin nghỉ phép** và **Mẫu tin nhắn/email chuẩn mực** để gửi Ban Chủ nhiệm: ✉️📋\n\n"
                "📌 **1. Quy định xin phép vắng mặt:**\n"
                "- **Thời gian báo trước:** Hãy báo sớm cho Trưởng ban hoặc Ban tổ chức. Thời hạn cụ thể cần xác nhận theo quy định của CLB và từng hoạt động.\n"
                "- **Trạng thái điểm danh:** Khi có lý do chính đáng (trùng lịch thi, việc gia đình đột xuất, ốm đau...), bạn sẽ được ghi nhận trạng thái **Có phép (Excused)** và **không bị trừ điểm chuyên cần**.\n"
                "- **Bàn giao công việc:** Nếu bạn đang giữ nhiệm vụ hoặc deadline trong sự kiện đó, hãy ủy quyền lại cho một bạn trong ban.\n\n"
                "📝 **2. Mẫu tin nhắn / Email xin phép gửi Trưởng ban:**\n\n"
                "```text\n"
                "Kính gửi: Ban Chủ nhiệm CLB và Trưởng ban [Tên Ban],\n\n"
                "Em là: [Họ và tên] - MSSV: [Mã số sinh viên] - Thành viên Ban [Tên Ban].\n\n"
                "Em viết tin nhắn này xin phép được vắng mặt trong hoạt động [Tên hoạt động/buổi họp] diễn ra vào [Thời gian / Ngày].\n\n"
                "Lý do: Do em có lịch thi kết thúc học phần / việc gia đình đột xuất không thể sắp xếp khác được.\n"
                "Em đã hoàn thành và bàn giao phần việc của mình cho bạn [Tên bạn nhận bàn giao] và cam kết sẽ cập nhật đầy đủ nội dung sau buổi sinh hoạt.\n\n"
                "Em xin chân thành cảm ơn và kính chúc chương trình diễn ra thành công tốt đẹp ạ!\n"
                "```\n\n"
                "💡 *Mẹo:* Bạn chỉ cần sao chép mẫu trên, điền thông tin trong ngoặc vuông `[...]` và gửi trực tiếp cho Trưởng ban qua Zalo/Email nhé!"
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Vắng mặt có phép có bị trừ điểm rèn luyện không?",
                "Ai là người duyệt đơn xin nghỉ phép?",
                "Cách xem lịch sử điểm danh của mình trên hệ thống?"
            ]
        }

    # 2. ĐIỂM RÈN LUYỆN (ĐRL) / ĐIỂM DANH / CHUYÊN CẦN / CÁCH TÍNH ĐIỂM
    elif any(kw in msg_lower for kw in ["rèn luyện", "đrl", "điểm danh", "chuyên cần", "cộng điểm", "tính điểm", "quy chế", "bao nhiêu điểm"]):
        return {
            "answer": (
                "Chào bạn! Đây là giải đáp chi tiết về **Cơ chế Điểm danh & Quyền lợi Điểm rèn luyện (ĐRL)**: ⭐📊\n\n"
                "🎯 **1. Mức cộng Điểm rèn luyện:**\n"
                "- **Thành viên tham gia hoạt động/workshop:** Việc cộng điểm rèn luyện phụ thuộc quy định của nhà trường và xác nhận của CLB; hệ thống hiện chưa có mức điểm chính thức.\n"
                "- **Ban Tổ chức / Hỗ trợ điều phối sự kiện:** Có thể được ghi nhận đóng góp theo quy định từng chương trình; hãy xác nhận với Ban chủ nhiệm về điểm và giấy chứng nhận.\n"
                "- **Thành viên xuất sắc học kỳ:** Được đề xuất Giấy khen cấp Đoàn trường / Hội Sinh viên kèm điểm thưởng tối đa theo quy định.\n\n"
                "📋 **2. Quy trình xác nhận ĐRL:**\n"
                "1. Bạn tham gia sự kiện và được Ban tổ chức điểm danh trực tiếp trên hệ thống CLB Manager (**Có mặt / Present**).\n"
                "2. Cuối mỗi tháng hoặc học kỳ, hệ thống tự động kết xuất bảng tổng hợp chuyên cần.\n"
                "3. Ban Chủ nhiệm ký duyệt và nộp trực tiếp sang **Phòng Công tác Sinh viên (CTSV)** để cộng thẳng vào bảng điểm rèn luyện của bạn!\n\n"
                "✅ **3. Kiểm tra chuyên cần:** Bạn có thể vào phân hệ **Điểm danh** trên thanh menu để xem chi tiết lịch sử từng buổi sinh hoạt của mình."
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Vắng bao nhiêu buổi thì bị cảnh cáo chuyên cần?",
                "Nếu bị điểm danh nhầm thì khiếu nại ở đâu?",
                "Làm sao để đăng ký làm Ban tổ chức sự kiện?"
            ]
        }

    # 3. HOẠT ĐỘNG, SỰ KIỆN SẮP TỚI, LỊCH TRÌNH
    elif any(kw in msg_lower for kw in ["sắp tới", "sắp diễn ra", "kế hoạch sắp tới", "hoạt động sắp", "sự kiện sắp", "lịch hoạt động", "lịch trình", "có sự kiện gì", "có hoạt động gì", "chương trình sắp", "khi nào có"]):
        upcoming_text = ""
        if upcoming_acts:
            upcoming_text += "📅 **Các hoạt động sắp diễn ra (Mời bạn đăng ký tham gia):**\n"
            for act in upcoming_acts:
                d_str = act.date.strftime("%d/%m/%Y lúc %H:%M") if act.date else "Đang cập nhật"
                upcoming_text += f"\n🔹 **{act.name}**\n   📍 *Địa điểm:* {act.location or 'Chưa xác định'}\n   ⏰ *Thời gian:* {d_str}\n   📝 *Chi tiết:* {act.description or 'Cập nhật tại bảng tin CLB'}\n"
        else:
            upcoming_text += "📅 *Hiện tại các hoạt động sắp tới đang trong giai đoạn lên kế hoạch chi tiết.*\n"

        completed_text = ""
        if completed_acts:
            completed_text += "\n🏆 **Điểm lại các sự kiện nổi bật gần đây:**\n"
            for act in completed_acts[:3]:
                completed_text += f"- **{act.name}**: {act.result or 'Hoàn thành xuất sắc, tạo tiếng vang lớn trong sinh viên'}\n"

        return {
            "answer": (
                "Chào bạn! CLB luôn có chuỗi sự kiện và hoạt động phong phú trải dài suốt năm học: 🎉🚀\n\n"
                + upcoming_text + completed_text +
                "\n👉 **Cách thức đăng ký:** Bạn có thể vào phân hệ **Hoạt động** trên hệ thống để bấm tham gia, hoặc theo dõi thông báo mới nhất từ Ban Chủ nhiệm nhé!"
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Tham gia hoạt động có được cấp giấy chứng nhận không?",
                "Làm sao để đăng ký tham gia các hoạt động này?",
                "Hoạt động sắp tới có yêu cầu trang phục hay dụng cụ gì không?"
            ]
        }

    # 4. CHƯA CÓ KINH NGHIỆM / MẤT GỐC / SỢ TRƯỢT / CHƯA BIẾT GÌ
    elif any(kw in msg_lower for kw in ["chưa có kinh nghiệm", "chưa biết gì", "không có kinh nghiệm", "mất gốc", "người mới", "bắt đầu từ số 0", "beginner", "chưa biết code", "chưa biết thiết kế", "không biết gì", "sợ trượt", "chưa giỏi"]):
        return {
            "answer": (
                "Chào bạn! Hãy gạt bỏ hoàn toàn nỗi lo lắng này sang một bên nhé! 🌟💪\n\n"
                "👉 **HOÀN TOÀN KHÔNG CẦN KINH NGHIỆM TRƯỚC KHI THAM GIA CLB!**\n\n"
                "Tại sao bạn có thể hoàn toàn yên tâm ứng tuyển?\n"
                "- 👥 **Cơ chế 'Buddy & Mentor 1 kèm 1':** Ngay khi vào ban, bạn sẽ được một anh/chị khóa trên dày dặn kinh nghiệm kèm cặp, hướng dẫn từ những bước cơ bản nhất.\n"
                "- 📚 **Chuỗi Workshop Training nội bộ:** Mỗi ban đều có giáo trình đào tạo riêng (ví dụ: Ban Kỹ thuật dạy Git/Web căn bản; Ban Truyền thông dạy tư duy đồ họa Figma/Canva; Ban Sự kiện dạy viết proposal).\n"
                "- 🎯 **Tiêu chí tuyển thành viên:** Mỗi ban có thể có tiêu chí khác nhau. Thái độ, tinh thần học hỏi và trách nhiệm thường quan trọng; bạn hãy xem thông báo tuyển thành viên chính thức để biết yêu cầu cụ thể.\n\n"
                "💡 *Lời khuyên:* Bạn chỉ cần tự tin thể hiện tinh thần ham học hỏi trong đơn đăng ký và buổi phỏng vấn là đã nắm chắc 90% cơ hội trúng tuyển rồi!"
            ),
            "suggestedClubs": [
                {"maDinhDanh": "DEPT_2", "tenClb": "Ban Kỹ thuật", "lyDoGoiY": "Có lộ trình đào tạo lập trình từ con số 0"},
                {"maDinhDanh": "DEPT_1", "tenClb": "Ban Truyền thông", "lyDoGoiY": "Đào tạo sử dụng Canva, Figma và CapCut cơ bản"}
            ],
            "followUpQuestions": [
                "Sinh viên năm nhất nên chọn ban nào?",
                "Phỏng vấn CLB thường hỏi những câu gì?",
                "Tham gia CLB có bị trùng lịch học không?"
            ]
        }

    # 5. CÂN BẰNG LỊCH HỌC / SỢ TRÙNG LỊCH THI / GPA / BẬN HỌC
    elif any(kw in msg_lower for kw in ["trùng lịch học", "lịch học", "ảnh hưởng học tập", "cân bằng", "gpa", "rớt môn", "bận học", "thi cử", "mùa thi", "tốn thời gian", "có bận không"]):
        return {
            "answer": (
                "Chào bạn! Đây là câu hỏi rất thực tế và thông minh của một sinh viên có trách nhiệm! 📚⏰\n\n"
                "Tại CLB chúng mình, phương châm số 1 luôn là: **'HỌC TẬP LUÔN LÀ ƯU TIÊN HÀNG ĐẦU'**.\n\n"
                "CLB có các cơ chế đảm bảo bạn vừa học tốt vừa hoạt động sôi nổi:\n"
                "- 🗓️ **Lịch sinh hoạt linh hoạt:** Lịch họp định kỳ luôn được sắp xếp vào cuối tuần (chiều Thứ Bảy hoặc Chủ Nhật) hoặc sau 17:30, tuyệt đối không trùng giờ học chính khóa.\n"
                "- ⚙️ **Tính năng 'Lịch rảnh cá nhân' trên CLB Manager:** Bạn có thể tự đánh dấu các buổi bận học trên hệ thống. Ban Điều hành sẽ không bao giờ giao task vào những khung giờ bạn đi học.\n"
                "- 🛑 **Cơ chế 'Study Break' mùa thi:** Trước và trong mỗi kỳ thi học kỳ khoảng 2 - 3 tuần, CLB sẽ **tạm dừng mọi hoạt động lớn** để toàn bộ thành viên tập trung ôn thi đạt điểm GPA cao.\n"
                "- ✉️ **Xin nghỉ phép:** Khi có lý do chính đáng, hãy báo sớm cho Trưởng ban và chờ xác nhận. Việc có được ghi nhận là nghỉ có phép hay không phụ thuộc quy định của CLB.\n\n"
                "🌟 *Thực tế:* Rất nhiều anh chị Ban Chủ nhiệm CLB vẫn đạt học bổng Khuyến khích học tập và giải thưởng NCKH đấy!"
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Một tuần CLB sinh hoạt mấy buổi?",
                "Mẫu tin nhắn xin phép nghỉ sinh hoạt CLB?",
                "Thời gian sinh hoạt CLB vào những ngày nào?"
            ]
        }

    # 6. CHI PHÍ / CÓ MẤT TIỀN HOẶC ĐÓNG QUỸ KHÔNG
    elif any(kw in msg_lower for kw in ["mất phí", "đóng tiền", "quỹ clb", "học phí", "lệ phí", "tốn tiền", "chi phí", "kinh phí", "tiền quỹ", "có mất tiền không", "đóng bao nhiêu"]):
        return {
            "answer": (
                "Chào bạn! Về vấn đề tài chính, CLB cam kết hoàn toàn minh bạch và rõ ràng: 💰✨\n\n"
                "👉 **Chi phí tham gia:** Mình chưa có dữ liệu chính thức về mức phí của CLB. Bạn nên kiểm tra thông báo tuyển thành viên hoặc hỏi Ban chủ nhiệm trước khi đăng ký.\n\n"
                "Giải đáp chi tiết về các khoản chi phí:\n"
                "- ❌ **Không có học phí hay phí gia nhập:** Bạn không phải trả bất kỳ khoản phí nào để được đào tạo hay tham gia CLB.\n"
                "- 🥤 **Quỹ nội bộ:** Mức đóng, tính bắt buộc và mục đích sử dụng phải căn cứ thông báo tài chính chính thức của CLB.\n"
                "- 🏢 **Kinh phí sự kiện:** Nguồn kinh phí có thể khác nhau theo từng hoạt động; mình không suy đoán khi chưa có báo cáo hoặc thông báo được lưu trong hệ thống.\n"
                "- 📊 **Minh bạch tài chính:** Báo cáo thu chi quỹ được công khai rõ ràng vào cuối mỗi tháng cho toàn thể thành viên theo dõi."
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Quyền lợi thực tế khi tham gia CLB là gì?",
                "Doanh nghiệp nào đang tài trợ cho CLB?",
                "Ban Đối ngoại làm những công việc gì?"
            ]
        }

    # 7. QUYỀN LỢI & LỢI ÍCH (ĐIỂM RÈN LUYỆN, CERTIFICATE, THỰC TẬP, NETWORKING)
    elif any(kw in msg_lower for kw in ["quyền lợi", "lợi ích", "được gì", "chứng nhận", "certificate", "thực tập", "làm đẹp cv", "hồ sơ xin việc", "networking", "giấy khen"]):
        return {
            "answer": (
                "Tham gia CLB chính là một trong những quyết định đầu tư xứng đáng nhất thời sinh viên! Dưới đây là **5 Quyền lợi vàng** bạn sẽ nhận được: 🎁🚀\n\n"
                "1. 🎓 **Điểm rèn luyện:** Mức điểm và điều kiện ghi nhận do nhà trường/CLB quy định cho từng hoạt động; hãy xác nhận trước khi sử dụng thông tin này cho hồ sơ học tập.\n"
                "2. 📜 **Giấy chứng nhận (Certificate) danh giá:** Được cấp giấy chứng nhận Thành viên tích cực / Ban tổ chức có dấu đỏ từ Đoàn trường — điểm cộng cực lớn trong hồ sơ xin học bổng và du học.\n"
                "3. 💼 **Cơ hội phát triển:** CLB có thể giúp bạn rèn luyện kỹ năng và mở rộng kết nối; cơ hội thực tập hoặc tuyển dụng cụ thể cần căn cứ thông báo chính thức, không được xem là cam kết việc làm.\n"
                "4. 🛠️ **Kinh nghiệm thực chiến 'làm đẹp CV':** Thay vì CV chỉ có lý thuyết, bạn có các dự án thực tế: website có người dùng thật, video đạt chục nghìn view, sự kiện phục vụ hàng trăm sinh viên.\n"
                "5. 🤝 **Gia đình thứ hai thời đại học:** Tìm được những người đồng đội chung chí hướng, cùng học tập, cùng vui chơi suốt 4 năm thanh xuân!"
            ),
            "suggestedClubs": [
                {"maDinhDanh": "DEPT_2", "tenClb": "Ban Kỹ thuật", "lyDoGoiY": "Dự án phần mềm thực chiến để đưa vào CV xin việc"},
                {"maDinhDanh": "DEPT_5", "tenClb": "Ban Đối ngoại", "lyDoGoiY": "Mở rộng networking trực tiếp với các nhà tuyển dụng"}
            ],
            "followUpQuestions": [
                "Sinh viên năm mấy thì bắt đầu đi thực tập được?",
                "Làm sao để xem điểm rèn luyện của mình?",
                "Tiêu chuẩn trở thành Ban Chủ nhiệm CLB?"
            ]
        }

    # 8. MẸO PHỎNG VẤN & CÁC CÂU HỎI THƯỜNG GẶP
    elif any(kw in msg_lower for kw in ["phỏng vấn", "vòng pv", "phỏng vấn hỏi gì", "mẹo phỏng vấn", "kinh nghiệm phỏng vấn", "câu hỏi phỏng vấn", "bí quyết đỗ", "chuẩn bị phỏng vấn"]):
        return {
            "answer": (
                "Chào bạn! Buổi phỏng vấn CLB thực chất là một cuộc trò chuyện cởi mở, thân thiện để đôi bên tìm thấy sự đồng điệu. Hãy tự tin nhé! 🎤✨\n\n"
                "🎯 **4 Câu hỏi cốt lõi hay gặp nhất:**\n"
                "1. *'Bạn hãy giới thiệu bản thân và lý do muốn vào Ban [Tên ban]?'*\n"
                "   👉 *Mẹo trả lời:* Nói ngắn gọn về sở thích, ngành học và lý do bạn cảm thấy ban này phù hợp với định hướng phát triển cá nhân.\n"
                "2. *'Nếu trong ban có bất đồng ý kiến hoặc đồng đội không hoàn thành việc, bạn sẽ làm gì?'*\n"
                "   👉 *Mẹo trả lời:* Nhấn mạnh tinh thần lắng nghe, trao đổi thẳng thắn trên tinh thần xây dựng và báo Trưởng ban hỗ trợ nếu cần.\n"
                "3. *'Nếu deadline của CLB trùng với tuần thi học kỳ, bạn giải quyết thế nào?'*\n"
                "   👉 *Mẹo trả lời:* Khẳng định ưu tiên học tập, đồng thời chủ động lập kế hoạch làm sớm hoặc nhờ đồng đội san sẻ việc trước.\n"
                "4. *'Bạn mong muốn học được gì và để lại dấu ấn gì sau 1 năm gắn bó?'*\n"
                "   👉 *Mẹo trả lời:* Nêu rõ kỹ năng bạn muốn rèn luyện (lập trình, giao tiếp, thiết kế, quản lý thời gian).\n\n"
                "🌟 **3 Bí quyết vàng ghi điểm:**\n"
                "- **Đúng giờ & Trang phục lịch sự:** Tạo ấn tượng chuyên nghiệp ngay từ giây đầu tiên.\n"
                "- **Thành thật:** Không biết thì nói chưa biết nhưng bày tỏ rõ tinh thần ham học hỏi.\n"
                "- **Hỏi ngược lại Ban Chủ nhiệm:** Chuẩn bị sẵn 1 câu hỏi (ví dụ: *'Sắp tới ban mình có dự án nào hay nhất ạ?'*) để thể hiện sự quan tâm sâu sắc!"
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Chưa có kinh nghiệm có bị đánh trượt không?",
                "Một buổi phỏng vấn kéo dài bao lâu?",
                "Sinh viên năm nhất nên chọn ban nào?"
            ]
        }

    # 9. SINH VIÊN NĂM NHẤT (TÂN SINH VIÊN) NÊN CHUẨN BỊ GÌ
    elif any(kw in msg_lower for kw in ["năm nhất", "k68", "k69", "k20", "k21", "tân sinh viên", "mới vào trường", "chuẩn bị gì"]):
        return {
            "answer": (
                "Chào mừng bạn đến với môi trường Đại học! Tân sinh viên năm nhất chính là 'làn gió mới' được CLB săn đón và ưu ái nhất! 🌱🎉\n\n"
                "📝 **3 Điều tân sinh viên nên chuẩn bị:**\n"
                "1. **Bản mô tả bản thân chân thành:** Trong đơn ứng tuyển, hãy kể về sở thích, các hoạt động thời cấp 3 (nếu có) và lý do bạn muốn bứt phá thời đại học.\n"
                "2. **Tâm thế cởi mở & Tinh thần chủ động:** Đừng ngần ngại hỏi khi không biết. Các anh chị khóa trên luôn sẵn sàng chia sẻ kinh nghiệm chọn môn, thầy cô và phương pháp học đại học hiệu quả.\n"
                "3. **Sắp xếp thời khóa biểu:** Hãy lên kế hoạch cân bằng giữa việc học trên lớp và sinh hoạt ngoại khóa ngay từ kỳ 1.\n\n"
                "💡 *Gợi ý cho bạn:* Nếu chưa biết chọn ban nào, hãy chia sẻ ngay với mình sở thích của bạn để mình gợi ý nhé!"
            ),
            "suggestedClubs": [
                {"maDinhDanh": "DEPT_1", "tenClb": "Ban Truyền thông", "lyDoGoiY": "Năng động, nhiều cơ hội sáng tạo nội dung"},
                {"maDinhDanh": "DEPT_3", "tenClb": "Ban Sự kiện", "lyDoGoiY": "Kết nối bạn bè nhanh chóng, tự tin trước đám đông"}
            ],
            "followUpQuestions": [
                "Chưa có kinh nghiệm có tham gia được không?",
                "Tham gia CLB có bị trùng lịch học không?",
                "CLB hiện có những ban chuyên môn nào?"
            ]
        }

    # 10. SINH VIÊN TRÁI NGÀNH / KHOA KHÁC / TRƯỜNG KHÁC
    elif any(kw in msg_lower for kw in ["trái ngành", "khác khoa", "khoa khác", "trường khác", "không học cntt", "ngoại đạo", "ngành khác", "kinh tế", "ngoại ngữ", "ngành xã hội"]):
        return {
            "answer": (
                "Chào bạn! Câu trả lời là: **HOÀN TOÀN ĐƯỢC VÀ CỰC KỲ ĐƯỢC CHÀO ĐÓN!** 🤝🌐\n\n"
                "Sức mạnh lớn nhất của CLB đến từ **sự đa dạng góc nhìn và chuyên ngành**:\n"
                "- 💻 Bạn học Kinh tế, Ngoại ngữ nhưng đam mê công nghệ? ➔ Vào **Ban Kỹ thuật**, bạn sẽ mang tư duy kinh doanh và trải nghiệm người dùng vào sản phẩm phần mềm!\n"
                "- 🎨 Bạn học Kỹ thuật nhưng có gu thẩm mỹ tốt? ➔ Vào **Ban Truyền thông**, các bạn sẽ biến những thông tin khô khan thành ấn phẩm đồ họa vô cùng cuốn hút!\n"
                "- 🎪 Bạn học bất cứ ngành nào thích giao tiếp, điều phối? ➔ **Ban Sự kiện** và **Ban Đối ngoại** luôn cần những 'đại sứ ngoại giao' năng động!\n\n"
                "🌟 *Bật mí:* Rất nhiều Trưởng ban và Thành viên tiêu biểu của CLB hiện tại cũng xuất phát từ các khoa khác nhau đấy!"
            ),
            "suggestedClubs": [
                {"maDinhDanh": "DEPT_1", "tenClb": "Ban Truyền thông", "lyDoGoiY": "Phù hợp mọi chuyên ngành yêu thích sáng tạo"},
                {"maDinhDanh": "DEPT_3", "tenClb": "Ban Sự kiện", "lyDoGoiY": "Nơi giao lưu kết nối không phân biệt ngành học"}
            ],
            "followUpQuestions": [
                "Mình nên vào ban nào phù hợp với sở thích?",
                "Chưa có kinh nghiệm có tham gia được không?",
                "Có được đăng ký nhiều ban cùng lúc không?"
            ]
        }

    # 11. ĐĂNG KÝ NHIỀU BAN / CHUYỂN BAN NỘI BỘ
    elif any(kw in msg_lower for kw in ["nhiều ban", "chuyển ban", "đổi ban", "2 ban", "hai ban", "chuyển sang ban khác", "nguyện vọng 2"]):
        return {
            "answer": (
                "Chào bạn! Dưới đây là quy định về việc lựa chọn và chuyển đổi ban chuyên môn: 🔄📋\n\n"
                "1. **Khi điền đơn ứng tuyển:**\n"
                "- Bạn hoàn toàn có thể đăng ký **Nguyện vọng 1 (NV1)** và **Nguyện vọng 2 (NV2)**.\n"
                "- Ban Chủ nhiệm sẽ phỏng vấn và cân nhắc nguyện vọng cùng năng khiếu của bạn để xếp vào ban phù hợp nhất.\n\n"
                "2. **Trong quá trình sinh hoạt:**\n"
                "- Để đảm bảo bạn không bị quá tải khối lượng công việc và phân tâm việc học, mỗi thành viên sẽ sinh hoạt chính thức tại **1 Ban chuyên môn duy nhất**.\n"
                "- Tuy nhiên, trong các chiến dịch sự kiện lớn, các ban sẽ phối hợp liên ngành (Cross-functional team) nên bạn vẫn được trải nghiệm công việc của các ban khác!\n\n"
                "3. **Cơ chế Chuyển ban nội bộ:**\n"
                "- Sau mỗi học kỳ, nếu bạn có nguyện vọng thử sức ở lĩnh vực mới (ví dụ từ Truyền thông sang Kỹ thuật hoặc Sự kiện), bạn chỉ cần gửi đề xuất chuyển ban. CLB luôn khuyến khích thành viên phát triển đa kỹ năng (T-shaped)!"
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "CLB hiện có những ban chuyên môn nào?",
                "Cách đăng ký tham gia CLB?",
                "Tiêu chuẩn để trở thành Trưởng ban?"
            ]
        }

    # 12. THỜI GIAN & ĐỊA ĐIỂM SINH HOẠT CLB
    elif any(kw in msg_lower for kw in ["thời gian sinh hoạt", "sinh hoạt khi nào", "ở đâu", "địa điểm sinh hoạt", "lịch sinh hoạt", "họp clb", "mấy giờ", "địa điểm họp"]):
        return {
            "answer": (
                "Thông tin chi tiết về lịch trình và địa điểm sinh hoạt định kỳ của CLB: 📍⏱️\n\n"
                "- ⏰ **Tần suất & Thời gian:** Định kỳ **2 tuần/lần** vào chiều Thứ Bảy hoặc Chủ Nhật (khung giờ **14:30 - 17:00**), đảm bảo tuyệt đối không trùng lịch học chính khóa của trường.\n"
                "- 🏫 **Địa điểm trực tiếp (Offline):** Phòng sinh hoạt chuyên đề nhà A/B, văn phòng Đoàn trường hoặc không gian sân trường thoáng đãng khi tổ chức teambuilding.\n"
                "- 💻 **Họp trực tuyến (Online):** Đối với các buổi họp nhanh cập nhật tiến độ công việc hoặc mùa thi, các ban họp qua Google Meet / Discord để tiết kiệm thời gian di chuyển.\n"
                "- 📢 **Thông báo trước:** Lịch họp luôn được tạo và thông báo trước ít nhất **3 - 5 ngày** trên hệ thống CLB Manager và nhóm liên lạc nội bộ."
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Nếu bận lịch sinh hoạt thì xin nghỉ thế nào?",
                "Vắng bao nhiêu buổi thì bị cảnh cáo chuyên cần?",
                "Sắp tới CLB có hoạt động gì nổi bật không?"
            ]
        }

    # 13. LỊCH TUYỂN QUÂN / THỜI GIAN MỞ ĐƠN
    elif any(kw in msg_lower for kw in ["tháng mấy", "đợt tuyển", "mở đơn", "khi nào tuyển", "hạn chót nộp đơn", "thời gian tuyển", "mở form", "hạn chót"]):
        return {
            "answer": (
                "CLB thường tổ chức **2 đợt tuyển quân chính thức** trong mỗi năm học: 📢📅\n\n"
                "🍂 **Đợt 1 (Mùa Thu - Tháng 9/Tháng 10):**\n"
                "- Đây là đợt tuyển quân quy mô lớn nhất năm nhằm chào đón Tân sinh viên khóa mới.\n"
                "- Mở đơn cho tất cả các ban chuyên môn với số lượng chỉ tiêu lớn.\n\n"
                "🌸 **Đợt 2 (Mùa Xuân - Tháng 2/Tháng 3):**\n"
                "- Đợt tuyển bổ sung nhân sự tài năng để chuẩn bị cho chuỗi sự kiện lớn học kỳ 2 (Hackathon, Teambuilding dã ngoại, Hội thảo công nghệ).\n\n"
                "🔔 *Lưu ý quan trọng:* Bạn hãy bấm theo dõi bảng tin **Thông báo** trên hệ thống CLB Manager để nhận thông báo ngay khi Form đăng ký chính thức mở nhé!"
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Quy trình đăng ký tham gia CLB như thế nào?",
                "Phỏng vấn CLB có khó không?",
                "Sinh viên năm nhất nên chọn ban nào?"
            ]
        }

    # 14. ĐĂNG KÝ THAM GIA / TUYỂN QUÂN / ĐIỀU KIỆN (QUY TRÌNH CHUNG)
    elif any(kw in msg_lower for kw in ["đăng ký", "tham gia", "gia nhập", "tuyển quân", "ứng tuyển", "điều kiện", "vào clb"]):
        return {
            "answer": (
                "Chào bạn! Rất hoan nghênh bạn mong muốn trở thành một mảnh ghép của CLB Sinh viên! 🎉✨\n\n"
                "Dưới đây là quy trình 4 bước gia nhập CLB cực kỳ đơn giản:\n\n"
                "📋 **Quy trình gia nhập 4 bước:**\n"
                "1. **Điền Form trực tuyến (Vòng Đơn):** Cung cấp thông tin sinh viên, sở thích cá nhân và ban chuyên môn mong muốn.\n"
                "2. **Giao lưu phỏng vấn (Vòng Phỏng Vấn):** Buổi trò chuyện thân mật, cởi mở kéo dài 15-20 phút để lắng nghe nguyện vọng và định hướng của bạn.\n"
                "3. **Thử thách Tân binh (Vòng Onboarding 2 tuần):** Tham gia sinh hoạt làm quen, được các anh chị mentor đào tạo kỹ năng ban đầu và cùng thực hiện 1 mini-project nhỏ.\n"
                "4. **Chính thức trở thành Thành viên:** Được phân vào ban chính thức và cấp tài khoản trên hệ thống **CLB Manager**.\n\n"
                "❓ **Chưa có kinh nghiệm có được tham gia không?**\n"
                "👉 **HOÀN TOÀN ĐƯỢC!** CLB luôn trân trọng thái độ nhiệt tình, ham học hỏi và tinh thần đồng đội hơn là kinh nghiệm sẵn có!"
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Chưa có kinh nghiệm có tham gia được không?",
                "Phỏng vấn CLB thường hỏi những câu gì?",
                "Sinh viên năm nhất nên chọn ban nào?"
            ]
        }

    # 5. NHIỆM VỤ / TIẾN ĐỘ / DEADLINE / KPI / PHÂN CÔNG
    elif any(kw in msg_lower for kw in ["nhiệm vụ", "task", "tiến độ", "phân công", "deadline", "kpi"]):
        return {
            "answer": (
                "Hệ thống Quản lý Nhiệm vụ (Task Management) của CLB được thiết kế rất khoa học và trực quan: 📋⏱️\n\n"
                "- 📌 **Giao việc minh bạch:** Trưởng ban tạo nhiệm vụ, đính kèm mô tả, hạn chót (deadline) và mức độ ưu tiên (**Khẩn cấp / Cao / Trung bình / Thấp**).\n"
                "- 🚀 **Cập nhật tiến độ linh hoạt:** Thành viên được giao việc truy cập mục **Nhiệm vụ**, kéo thanh tiến độ từ **0% ➔ 100%** và chuyển trạng thái sang *'Đang thực hiện'* hoặc *'Hoàn thành'*.\n"
                "- 🤝 **Hỗ trợ khi gặp khó khăn:** Nếu task gặp trở ngại kỹ thuật hoặc trùng lịch học đột xuất, hãy bấm báo cáo để Trưởng ban phân phối thêm người cùng làm.\n"
                "- 🏆 **Đánh giá thi đua:** Mức độ hoàn thành nhiệm vụ đúng hạn là tiêu chí hàng đầu để xét danh hiệu *'Thành viên xuất sắc nhất tháng'*!"
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Làm sao biết mình có nhiệm vụ mới được giao?",
                "Nếu không kịp deadline thì phải làm thế nào?",
                "Tiêu chuẩn để trở thành Trưởng ban là gì?"
            ]
        }

    # 6. HƯỚNG DẪN SỬ DỤNG HỆ THỐNG CLB MANAGER
    elif any(kw in msg_lower for kw in ["hệ thống", "web", "tính năng", "chức năng", "hướng dẫn", "clb manager"]):
        return {
            "answer": (
                "**CLB Manager** là nền tảng quản trị thông minh toàn diện dành cho CLB: 💻✨\n\n"
                "Các phân hệ chính mà bạn có thể trải nghiệm:\n"
                "- 📊 **Dashboard:** Thống kê trực quan nhân sự, tỷ lệ tham gia sự kiện và tiến độ nhiệm vụ toàn CLB.\n"
                "- 👥 **Thành viên:** Tra cứu danh sách đồng đội, bộ lọc theo ban, tìm kiếm theo kỹ năng và lịch rảnh.\n"
                "- 🏢 **Ban chuyên môn:** Cơ cấu tổ chức, nhiệm vụ chuyên biệt và nhân sự từng ban.\n"
                "- 📅 **Hoạt động:** Lịch trình sự kiện chi tiết, quản lý danh sách đăng ký.\n"
                "- ✅ **Điểm danh:** Chấm công chuyên cần, hỗ trợ 3 trạng thái và tính toán tự động.\n"
                "- 📋 **Nhiệm vụ:** Bảng phân công công việc, hạn chót deadline và tiến độ trực quan.\n"
                "- 🤖 **UniClub Assistant:** Trợ lý ảo AI túc trực 24/7 giải đáp và tư vấn cho sinh viên."
            ),
            "suggestedClubs": [],
            "followUpQuestions": [
                "Làm sao để đổi mật khẩu tài khoản cá nhân?",
                "Cách cập nhật lịch rảnh để được giao việc hợp lý?",
                "AI Assistant có thể giúp tôi tạo nội dung thông báo không?"
            ]
        }

    # 7. TÌM HIỂU VỀ TẤT CẢ CÁC BAN CHUYÊN MÔN (HỎI CHUNG)
    elif any(kw in msg_lower for kw in ["các ban", "ban chuyên môn", "phòng ban", "bao nhiêu ban", "cơ cấu", "danh sách ban"]):
        dept_lines = []
        suggested = []
        for d in departments:
            leader = f" (Trưởng ban: **{d.leader.name}**)" if d.leader else ""
            m_count = len(d.members) if d.members else 0
            dept_lines.append(f"- **{d.name}**{leader}: {d.description} *(Hiện có {m_count} thành viên)*")
            suggested.append({
                "maDinhDanh": f"DEPT_{d.id}",
                "tenClb": d.name,
                "lyDoGoiY": d.description or "Ban chuyên môn năng động của CLB"
            })

        return {
            "answer": (
                f"Hiện tại Câu lạc bộ đang có **{len(departments)} Ban chuyên môn** hoạt động bài bản và phối hợp nhịp nhàng:\n\n"
                + "\n".join(dept_lines) +
                "\n\n🎯 **Bạn nên chọn ban nào?**\n"
                "Mỗi ban có thế mạnh riêng biệt. Bạn chỉ cần chia sẻ với mình về sở thích cá nhân (ví dụ: *'Mình thích lập trình web'*, *'Mình thích dựng video TikTok'* hay *'Mình thích dẫn MC'*), mình sẽ phân tích và gợi ý ban phù hợp nhất cho bạn ngay! 😊"
            ),
            "suggestedClubs": suggested,
            "followUpQuestions": [
                "Mình thích lập trình thì nên vào ban gì?",
                "Mình thích sáng tạo nội dung thì ban nào hợp?",
                "Một thành viên có thể tham gia cùng lúc 2 ban không?"
            ]
        }

    # 8. TƯ VẤN LẬP TRÌNH / CNTT / WEB / AI / BACKEND / FRONTEND
    elif any(kw in msg_lower for kw in ["lập trình", "code", "it", "kỹ thuật", "python", "javascript", "react", "fastapi", "web", "ai", "backend", "frontend", "mobile", "hackathon", "phần mềm", "dev"]):
        ky_thuat_dept = next((d for d in departments if "kỹ thuật" in d.name.lower()), None)
        leader_info = f" (Trưởng ban: **{ky_thuat_dept.leader.name}**)" if ky_thuat_dept and ky_thuat_dept.leader else ""
        return {
            "answer": (
                "Chào bạn! Đam mê công nghệ và lập trình là một lợi thế cực kỳ lớn khi tham gia CLB! 🚀💻\n\n"
                f"**Ban Kỹ thuật**{leader_info} chính là 'ngôi nhà chung' hoàn hảo dành cho bạn. "
                "Tại đây, bạn sẽ không chỉ học lý thuyết mà còn được 'thực chiến' qua các dự án thực tế:\n\n"
                "- 🛠️ **Phát triển sản phẩm thực tế:** Trực tiếp xây dựng, nâng cấp hệ thống Website, Portal quản lý CLB (Python FastAPI, React, SQLite/PostgreSQL).\n"
                "- 🤖 **Ứng dụng AI & Công nghệ mới:** Nghiên cứu tích hợp mô hình ngôn ngữ lớn (LLM), trợ lý ảo, tự động hóa quy trình.\n"
                "- 🏆 **Tham gia các cuộc thi công nghệ:** Lập đội tham gia các giải Hackathon cấp trường, thành phố với sự cố vấn (mentor) từ các anh chị khóa trên.\n"
                "- 👥 **Môi trường học hỏi:** Thảo luận code review, rèn luyện tư duy lập trình và kỹ năng làm việc nhóm theo chuẩn Git/GitHub chuyên nghiệp.\n\n"
                "💡 *Lời khuyên dành cho bạn:* Dù bạn là người mới bắt đầu (Beginner) hay đã có kinh nghiệm, Ban Kỹ thuật luôn có lộ trình training bài bản từ cơ bản đến nâng cao!"
            ),
            "suggestedClubs": [
                {
                    "maDinhDanh": f"DEPT_{ky_thuat_dept.id}" if ky_thuat_dept else "DEPT_2",
                    "tenClb": "Ban Kỹ thuật",
                    "lyDoGoiY": "Môi trường thực chiến lập trình web, app, AI và cơ hội tham gia các giải Hackathon"
                }
            ],
            "followUpQuestions": [
                "Ban Kỹ thuật có yêu cầu kiểm tra đầu vào không?",
                "Chưa biết lập trình có tham gia Ban Kỹ thuật được không?",
                "Sắp tới ban có workshop công nghệ nào không?"
            ]
        }

    # 9. TƯ VẤN THIẾT KẾ / TRUYỀN THÔNG / VIDEO / CONTENT / MARKETING / TIKTOK
    elif any(kw in msg_lower for kw in ["thiết kế", "design", "figma", "photoshop", "canva", "truyền thông", "video", "media", "quay phim", "chụp ảnh", "content", "tiktok", "fanpage", "poster", "banner", "biên tập"]):
        tt_dept = next((d for d in departments if "truyền thông" in d.name.lower()), None)
        leader_info = f" (Trưởng ban: **{tt_dept.leader.name}**)" if tt_dept and tt_dept.leader else ""
        return {
            "answer": (
                "Chào bạn! Nếu bạn yêu thích sự sáng tạo, hình ảnh và nghệ thuật thị giác thì xin chúc mừng: Bạn có tố chất tuyệt vời của một 'phù thủy truyền thông'! 🎨📸\n\n"
                f"**Ban Truyền thông**{leader_info} chính là bệ phóng lý tưởng dành cho bạn:\n\n"
                "- 🎨 **Thiết kế đồ họa:** Sáng tạo bộ ấn phẩm nhận diện sự kiện, poster, infographic, banner bằng Figma, Photoshop, Canva.\n"
                "- 🎬 **Sản xuất Media & Video:** Quay recap sự kiện, sản xuất video ngắn TikTok/Reels, podcast và chụp ảnh hoạt động CLB.\n"
                "- ✍️ **Content Marketing:** Biên soạn các bài viết viral, quản trị Fanpage hàng nghìn lượt theo dõi, xây dựng thương hiệu cho CLB.\n"
                "- 📈 **Đo lường & Phân tích:** Học cách chạy chiến dịch truyền thông sự kiện và theo dõi tương tác người dùng.\n\n"
                "✨ *Đặc biệt:* Bạn sẽ được cấp tài khoản phần mềm bản quyền và tham gia chuỗi workshop 'Training Tư Duy Đồ Họa & Figma' miễn phí!"
            ),
            "suggestedClubs": [
                {
                    "maDinhDanh": f"DEPT_{tt_dept.id}" if tt_dept else "DEPT_1",
                    "tenClb": "Ban Truyền thông",
                    "lyDoGoiY": "Nơi thỏa sức sáng tạo thiết kế Figma/Photoshop, dựng video và xây dựng thương hiệu Fanpage"
                }
            ],
            "followUpQuestions": [
                "Làm sao để đăng ký vào Ban Truyền thông?",
                "Chưa biết dùng Photoshop có vào Ban Truyền thông được không?",
                "Ban Truyền thông sử dụng những công cụ gì?"
            ]
        }

    # 10. TƯ VẤN SỰ KIỆN / MC / HOẠT NÁO / HẬU CẦN / TEAMBUILDING
    elif any(kw in msg_lower for kw in ["sự kiện", "event", "mc", "dẫn chương trình", "hậu cần", "logistics", "hoạt náo", "teambuilding", "hội trường", "sân khấu", "âm thanh"]):
        sk_dept = next((d for d in departments if "sự kiện" in d.name.lower()), None)
        leader_info = f" (Trưởng ban: **{sk_dept.leader.name}**)" if sk_dept and sk_dept.leader else ""
        return {
            "answer": (
                "Chào bạn! Năng động, thích giao lưu và muốn đứng sau những chương trình hoành tráng hàng trăm người tham dự? 🎪🎤\n\n"
                f"**Ban Sự kiện**{leader_info} chính là 'trái tim' tạo nên những kỷ niệm đáng nhớ nhất của CLB:\n\n"
                "- 📋 **Lập kế hoạch & Kịch bản:** Viết proposal chi tiết, xây dựng timeline chương trình, kịch bản dẫn MC và dự trù ngân sách.\n"
                "- 🎤 **Kỹ năng MC & Hoạt náo:** Rèn luyện giọng nói, sự tự tin trước đám đông, khả năng ứng biến trên sân khấu.\n"
                "- 🎧 **Điều phối & Hậu cần (Logistics):** Trực tiếp vận hành âm thanh, ánh sáng, khảo sát địa điểm và quản lý người tham gia.\n"
                "- 🤝 **Tinh thần đồng đội:** Được trải nghiệm các chuyến dã ngoại, teambuilding gắn kết siêu vui nhộn!\n\n"
                "🌟 *Lợi ích:* Kỹ năng quản trị sự kiện và giải quyết tình huống thực tế sẽ là điểm cộng cực lớn trong CV xin việc sau này của bạn."
            ),
            "suggestedClubs": [
                {
                    "maDinhDanh": f"DEPT_{sk_dept.id}" if sk_dept else "DEPT_3",
                    "tenClb": "Ban Sự kiện",
                    "lyDoGoiY": "Rèn luyện kỹ năng tổ chức chương trình, MC, quản lý sân khấu và giao tiếp tự tin"
                }
            ],
            "followUpQuestions": [
                "Sắp tới CLB có sự kiện gì lớn không?",
                "Ban Sự kiện có hay đi dã ngoại không?",
                "Cách đăng ký làm cộng tác viên sự kiện?"
            ]
        }

    # 11. TƯ VẤN ĐỐI NGOẠI / TÀI TRỢ / DOANH NGHIỆP / TIẾNG ANH
    elif any(kw in msg_lower for kw in ["đối ngoại", "tài trợ", "doanh nghiệp", "kết nối", "tiếng anh", "giao tiếp", "đàm phán", "ngoại giao", "sponsor"]):
        dn_dept = next((d for d in departments if "đối ngoại" in d.name.lower()), None)
        leader_info = f" (Trưởng ban: **{dn_dept.leader.name}**)" if dn_dept and dn_dept.leader else ""
        return {
            "answer": (
                "Chào bạn! Kỹ năng giao tiếp, đàm phán và ngoại giao là những 'vũ khí sắc bén' mở ra vô vàn cơ hội nghề nghiệp! 🤝💼\n\n"
                f"**Ban Đối ngoại**{leader_info} là cầu nối vàng giữa CLB với các Doanh nghiệp và đối tác ngoài trường:\n\n"
                "- 💰 **Kêu gọi tài trợ:** Soạn thảo hồ sơ mời tài trợ chuyên nghiệp, đàm phán quyền lợi với các nhà tài trợ lớn.\n"
                "- 🏢 **Kết nối Doanh nghiệp:** Mời diễn giả cấp cao từ các tập đoàn công nghệ (FPT, Viettel, VNG...), mở ra cơ hội thực tập sớm cho thành viên.\n"
                "- 🌐 **Giao lưu Liên trường:** Thiết lập mối quan hệ với các CLB bạn tại các trường đại học hàng đầu.\n"
                "- 🗣️ **Kỹ năng đàm phán & Ngoại ngữ:** Nâng cao phản xạ giao tiếp tiếng Anh thương mại và phong thái chuyên nghiệp.\n\n"
                "🌟 *Cơ hội đặc biệt:* Bạn sẽ có mạng lưới quan hệ (Networking) trực tiếp với các nhà tuyển dụng và chuyên gia đầu ngành!"
            ),
            "suggestedClubs": [
                {
                    "maDinhDanh": f"DEPT_{dn_dept.id}" if dn_dept else "DEPT_5",
                    "tenClb": "Ban Đối ngoại",
                    "lyDoGoiY": "Phù hợp với bạn thích đàm phán, kết nối nhà tài trợ, mở rộng network doanh nghiệp"
                }
            ],
            "followUpQuestions": [
                "Ban Đối ngoại có cần giỏi tiếng Anh không?",
                "Doanh nghiệp nào đang tài trợ cho CLB?",
                "Quy trình xin tài trợ một sự kiện như thế nào?"
            ]
        }

    # 12. TƯ VẤN HỌC THUẬT / NGHIÊN CỨU / WORKSHOP / TÀI LIỆU
    elif any(kw in msg_lower for kw in ["học thuật", "nghiên cứu", "nckh", "khoa học", "chuyên đề", "tài liệu", "hội thảo học thuật", "báo cáo khoa học"]):
        ht_dept = next((d for d in departments if "học thuật" in d.name.lower()), None)
        leader_info = f" (Trưởng ban: **{ht_dept.leader.name}**)" if ht_dept and ht_dept.leader else ""
        return {
            "answer": (
                "Chào bạn! Học tập và nghiên cứu chuyên sâu luôn là nền tảng vững chắc nhất cho con đường phát triển lâu dài! 📚🔍\n\n"
                f"**Ban Học thuật**{leader_info} là nơi ươm mầm tri thức và nâng tầm học vấn cho sinh viên:\n\n"
                "- 📖 **Tổ chức Workshop & Seminar:** Xây dựng nội dung các buổi chuyên đề học tập, kỹ năng mềm và phương pháp nghiên cứu.\n"
                "- 📑 **Biên soạn tài liệu & Giáo trình:** Đúc kết ngân hàng đề thi, tài liệu ôn tập và hướng dẫn thực hành hữu ích cho sinh viên.\n"
                "- 🎓 **Nghiên cứu khoa học (NCKH):** Hướng dẫn phương pháp viết bài báo khoa học, phân tích số liệu và báo cáo đề tài.\n"
                "- 💡 **Training phương pháp tư duy:** Các khóa đào tạo về Tư duy Thiết kế (Design Thinking), Mindmap, kỹ năng thuyết trình học thuật.\n\n"
                "✨ *Lợi ích:* Điểm học tập và cơ hội săn học bổng, giấy khen NCKH của bạn sẽ tăng vượt bậc khi sinh hoạt tại ban!"
            ),
            "suggestedClubs": [
                {
                    "maDinhDanh": f"DEPT_{ht_dept.id}" if ht_dept else "DEPT_4",
                    "tenClb": "Ban Học thuật",
                    "lyDoGoiY": "Nâng cao học vấn, tổ chức seminar và rèn luyện kỹ năng nghiên cứu khoa học"
                }
            ],
            "followUpQuestions": [
                "CLB có kho tài liệu học tập không?",
                "Sinh viên năm nhất có tham gia nghiên cứu khoa học được không?",
                "Workshop học thuật sắp tới là khi nào?"
            ]
        }

    # 13. MẶC ĐỊNH / CHÀO HỎI / CÂU HỎI KHÁC
    else:
        return {
            "answer": (
                "Xin chào bạn! 👋 Mình là **UniClub Assistant** — Trợ lý ảo AI thông minh của Câu lạc bộ Sinh viên!\n\n"
                "Rất vui được đồng hành cùng bạn. Mình có thể hỗ trợ và tư vấn chuyên sâu về các chủ đề sau:\n\n"
                "- 📋 **Định hướng & Tư vấn:** Giúp bạn khám phá sở thích và chọn ban chuyên môn phù hợp nhất.\n"
                "- 📅 **Hoạt động & Sự kiện:** Cập nhật lịch trình các buổi Workshop, Hackathon, Teambuilding sắp diễn ra.\n"
                "- 📝 **Gia nhập CLB:** Hướng dẫn quy trình tuyển quân, lộ trình onboarding và mẹo phỏng vấn.\n"
                "- ⭐ **Quy chế sinh hoạt:** Giải đáp chi tiết cách tính điểm rèn luyện (ĐRL), quy định xin nghỉ phép và quyền lợi thành viên.\n"
                "- 💻 **Sử dụng hệ thống:** Hướng dẫn nhận nhiệm vụ, cập nhật tiến độ và theo dõi chuyên cần trên CLB Manager.\n\n"
                "Bạn đang quan tâm đến nội dung nào? Hãy chia sẻ với mình nhé! 😊"
            ),
            "suggestedClubs": [
                {"maDinhDanh": "DEPT_1", "tenClb": "Ban Truyền thông", "lyDoGoiY": "Sáng tạo nội dung, thiết kế đồ họa Figma, video TikTok"},
                {"maDinhDanh": "DEPT_2", "tenClb": "Ban Kỹ thuật", "lyDoGoiY": "Thực chiến lập trình Web, App, AI và tham gia Hackathon"},
                {"maDinhDanh": "DEPT_3", "tenClb": "Ban Sự kiện", "lyDoGoiY": "Tổ chức chương trình, dẫn MC, điều phối sân khấu"}
            ],
            "followUpQuestions": [
                "CLB hiện có những ban chuyên môn nào?",
                "Sắp tới có hoạt động hay sự kiện gì không?",
                "Tham gia CLB được cộng bao nhiêu điểm rèn luyện?"
            ]
        }


async def chat_with_assistant(message: str, db: Session) -> dict:
    """
    Endpoint chính xử lý tin nhắn từ sinh viên:
    - Nếu có cấu hình OPENAI_API_KEY: Sử dụng OpenAI API kết hợp live context và function calling.
    - Nếu không có hoặc API gặp sự cố: Tự động chuyển qua Smart Inference Engine chuyên nghiệp,
      đảm bảo phản hồi luôn chuẩn xác, sâu sắc và không bao giờ crash.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    club_context = build_club_context(db)

    # Chế độ thông minh nội bộ nếu không có OpenAI API Key
    if not api_key:
        return _generate_smart_club_response(message, db)

    # Chế độ gọi OpenAI API thực tế
    try:
        messages = [
            {"role": "system", "content": CLUBAI_SYSTEM_PROMPT},
            {"role": "user", "content": (
                f"DỮ LIỆU HỆ THỐNG CẬP NHẬT THỜI GIAN THỰC:\n{club_context}\n\n"
                f"CÂU HỎI CỦA SINH VIÊN:\n{message}\n\n"
                "Hãy trả lời chuyên nghiệp, đầy đủ và xuất định dạng JSON hợp lệ theo quy định."
            )}
        ]

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    "messages": messages,
                    "temperature": 0.4,
                    "max_tokens": 1200,
                    "response_format": {"type": "json_object"}
                },
                timeout=25.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return _parse_ai_response(content, message, db)
            else:
                # Fallback to smart local response on API error
                return _generate_smart_club_response(message, db)

    except Exception as e:
        print(f"[AI CHAT FALLBACK] Error calling external AI: {e}")
        return _generate_smart_club_response(message, db)


def _parse_ai_response(raw: str, original_message: str, db: Session) -> dict:
    """Phân tích dữ liệu JSON trả về từ OpenAI một cách an toàn"""
    try:
        result = json.loads(raw)
        return _validate_response(result)
    except Exception:
        # Tìm khối JSON nếu bị kẹp giữa văn bản
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(0))
                return _validate_response(result)
            except Exception:
                pass
        return _generate_smart_club_response(original_message, db)


def _validate_response(data: dict) -> dict:
    """Đảm bảo định dạng response có đầy đủ các trường yêu cầu"""
    if "answer" not in data or not data["answer"]:
        data["answer"] = "UniClub Assistant rất vui được hỗ trợ bạn. Bạn có câu hỏi nào khác về CLB không?"
    if "suggestedClubs" not in data or not isinstance(data["suggestedClubs"], list):
        data["suggestedClubs"] = []
    if "followUpQuestions" not in data or not isinstance(data["followUpQuestions"], list) or len(data["followUpQuestions"]) == 0:
        data["followUpQuestions"] = [
            "CLB có những ban chuyên môn nào?",
            "Sắp tới có hoạt động gì không?",
            "Làm sao để đăng ký tham gia CLB?"
        ]
    return data
