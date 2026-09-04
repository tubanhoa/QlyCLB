"""
seed_data.py - Script độc lập khởi tạo và nạp dữ liệu mẫu cho hệ thống CLB Sinh viên
Chạy: python seed_data.py [--reset]
"""
import sys
import os
import io
from datetime import datetime, timedelta

# Đảm bảo UTF-8 khi in trên terminal Windows
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Đảm bảo đường dẫn import từ thư mục backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, SessionLocal
from models import User, Member, Department, Activity, Attendance, Task, Notification, AIRequest
from auth import hash_password


def seed_database(reset: bool = False):
    """Khởi tạo và nạp dữ liệu mẫu phong phú"""
    if reset:
        print("[*] Đang xóa và tạo lại toàn bộ bảng CSDL...")
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Nếu đã có dữ liệu và không reset thì dừng lại
        if db.query(User).count() > 0 and not reset:
            print("[INFO] Cơ sở dữ liệu đã có dữ liệu sẵn. Sử dụng 'python seed_data.py --reset' nếu muốn nạp lại từ đầu.")
            return

        print("[*] Đang khởi tạo dữ liệu mẫu phong phú...")

        # 1. Ban chuyên môn (Departments)
        dept_truyen_thong = Department(
            name="Ban Truyền thông",
            description="Phụ trách hình ảnh, thiết kế ấn phẩm truyền thông, video và marketing sự kiện CLB"
        )
        dept_ky_thuat = Department(
            name="Ban Kỹ thuật",
            description="Phụ trách hệ thống website, ứng dụng, thiết bị công nghệ và đào tạo kỹ thuật"
        )
        dept_su_kien = Department(
            name="Ban Sự kiện",
            description="Lập kế hoạch, quản lý hậu cần và tổ chức các hoạt động ngoại khóa, giải đấu, lễ hội"
        )
        dept_hoc_thuat = Department(
            name="Ban Học thuật",
            description="Nghiên cứu khoa học, tổ chức workshop chuyên môn, seminar và tài liệu học tập"
        )
        dept_doi_ngoai = Department(
            name="Ban Đối ngoại",
            description="Kết nối doanh nghiệp, tìm kiếm nhà tài trợ và giao lưu với các câu lạc bộ bạn"
        )

        db.add_all([dept_truyen_thong, dept_ky_thuat, dept_su_kien, dept_hoc_thuat, dept_doi_ngoai])
        db.flush()

        # 2. Thành viên (Members)
        members_data = [
            Member(
                name="Nguyễn Văn An",
                email="an.nguyen@email.com",
                phone="0901234567",
                department_id=None, # Chủ nhiệm
                skills="Lãnh đạo, Lập kế hoạch chiến lược, Quản trị rủi ro, Thuyết trình",
                availability="Thứ 2-6: 14h-17h, Thứ 7: Cả ngày",
                status="active"
            ),
            Member(
                name="Trần Thị Bình",
                email="binh.tran@email.com",
                phone="0912345678",
                department_id=dept_truyen_thong.id,
                skills="Thiết kế đồ họa, Adobe Photoshop, Figma, Sáng tạo nội dung TikTok",
                availability="Thứ 3,5: 14h-17h, Thứ 7: Sáng",
                status="active"
            ),
            Member(
                name="Lê Hoàng Cường",
                email="cuong.le@email.com",
                phone="0923456789",
                department_id=dept_ky_thuat.id,
                skills="Python, FastAPI, React, Quản trị hệ thống Linux, Docker",
                availability="Thứ 2,4,6: 15h-18h",
                status="active"
            ),
            Member(
                name="Phạm Thị Dung",
                email="dung.pham@email.com",
                phone="0934567890",
                department_id=dept_su_kien.id,
                skills="Tổ chức sự kiện, MC sự kiện, Quản lý hậu cần, Đàm phán địa điểm",
                availability="Thứ 4,5: 14h-17h, Chủ nhật: Cả ngày",
                status="active"
            ),
            Member(
                name="Hoàng Văn Em",
                email="em.hoang@email.com",
                phone="0945678901",
                department_id=dept_truyen_thong.id,
                skills="Quay phim, Dựng video Premiere, After Effects, Chụp ảnh sự kiện",
                availability="Thứ 2,3: 16h-19h, Thứ 7: Chiều",
                status="active"
            ),
            Member(
                name="Ngô Thị Phương",
                email="phuong.ngo@email.com",
                phone="0956789012",
                department_id=dept_ky_thuat.id,
                skills="Cơ sở dữ liệu SQL, Backend API, Viết tài liệu kỹ thuật",
                availability="Thứ 3,5,7: 14h-17h",
                status="active"
            ),
            Member(
                name="Đỗ Minh Quân",
                email="quan.do@email.com",
                phone="0967890123",
                department_id=dept_su_kien.id,
                skills="Âm thanh sân khấu, Ánh sáng, Quản trị thiết bị, Vận hành kỹ thuật",
                availability="Thứ 6: 15h-18h, Thứ 7 & CN: Cả ngày",
                status="active"
            ),
            Member(
                name="Vũ Thị Hồng",
                email="hong.vu@email.com",
                phone="0978901234",
                department_id=dept_hoc_thuat.id,
                skills="Nghiên cứu khoa học, Viết báo cáo học thuật, Training kiến thức",
                availability="Thứ 2-4: 14h-16h",
                status="active"
            ),
            Member(
                name="Bùi Đức Khánh",
                email="khanh.bui@email.com",
                phone="0989012345",
                department_id=dept_hoc_thuat.id,
                skills="Phân tích dữ liệu, Python Pandas, Excel nâng cao, Machine Learning",
                availability="Thứ 4,6: 15h-18h, Chủ nhật: Sáng",
                status="active"
            ),
            Member(
                name="Mai Thanh Lam",
                email="lam.mai@email.com",
                phone="0990123456",
                department_id=dept_doi_ngoai.id,
                skills="Kêu gọi tài trợ, Quan hệ doanh nghiệp, Giao tiếp tiếng Anh",
                availability="Thứ 2,5: 16h-19h",
                status="active"
            ),
            Member(
                name="Trương Văn Nam",
                email="nam.truong@email.com",
                phone="0901112233",
                department_id=dept_ky_thuat.id,
                skills="Mobile dev, Flutter, UI/UX Design",
                availability="Thứ 3,6: 14h-17h",
                status="inactive" # Cựu thành viên đã tốt nghiệp
            ),
            Member(
                name="Lý Thị Oanh",
                email="oanh.ly@email.com",
                phone="0912223344",
                department_id=dept_doi_ngoai.id,
                skills="Quản lý đối tác, Soạn thảo hợp đồng, Lễ tân đối ngoại",
                availability="Thứ 2,4: 15h-18h, Thứ 7: Sáng",
                status="active"
            )
        ]

        db.add_all(members_data)
        db.flush()

        # Gán Trưởng ban tương ứng
        dept_truyen_thong.leader_id = members_data[1].id  # Trần Thị Bình
        dept_ky_thuat.leader_id = members_data[2].id      # Lê Hoàng Cường
        dept_su_kien.leader_id = members_data[3].id       # Phạm Thị Dung
        dept_hoc_thuat.leader_id = members_data[7].id     # Vũ Thị Hồng
        dept_doi_ngoai.leader_id = members_data[9].id     # Mai Thanh Lam

        # 3. Tài khoản người dùng (Users)
        users_data = [
            User(
                username="admin",
                password=hash_password("admin123"),
                role="chu_nhiem",
                member_id=members_data[0].id
            ),
            User(
                username="truongban",
                password=hash_password("truongban123"),
                role="truong_ban",
                member_id=members_data[1].id
            ),
            User(
                username="cuong_tb",
                password=hash_password("cuong123"),
                role="truong_ban",
                member_id=members_data[2].id
            ),
            User(
                username="dung_tb",
                password=hash_password("dung123"),
                role="truong_ban",
                member_id=members_data[3].id
            ),
            User(
                username="thanhvien",
                password=hash_password("thanhvien123"),
                role="thanh_vien",
                member_id=members_data[4].id
            ),
            User(
                username="phuong_tv",
                password=hash_password("phuong123"),
                role="thanh_vien",
                member_id=members_data[5].id
            )
        ]

        db.add_all(users_data)
        db.flush()

        # 4. Hoạt động (Activities)
        now = datetime.now()
        activities_data = [
            Activity(
                name="Workshop Python & Ứng dụng AI",
                description="Khóa đào tạo nền tảng lập trình Python và cách gọi các mô hình AI phục vụ dự án sinh viên",
                date=now - timedelta(days=25),
                location="Phòng Lab A301, Tòa nhà CNTT",
                manager_id=members_data[2].id,
                status="completed",
                notes="Tổng cộng 28 sinh viên tham dự, đường truyền mạng ổn định",
                result="100% người tham dự hoàn thành mini-project, điểm đánh giá trung bình 4.9/5"
            ),
            Activity(
                name="Cuộc thi Hackathon Đổi Mới Sáng Tạo 2026",
                description="Cuộc thi lập trình 24 giờ liên tục với chủ đề Ứng dụng AI cho giáo dục và cộng đồng",
                date=now - timedelta(days=12),
                location="Hội trường Trung tâm, Tòa B",
                manager_id=members_data[0].id,
                status="completed",
                notes="12 đội thi tranh tài với sự cố vấn từ các kỹ sư công nghệ",
                result="Trao 1 giải Nhất, 2 giải Nhì và 3 giải Ba. Đội quán quân đại diện trường thi cấp Thành phố"
            ),
            Activity(
                name="Giao lưu & Tọa đàm cùng Doanh nghiệp Công nghệ",
                description="Buổi giao lưu hướng nghiệp, chia sẻ kinh nghiệm tuyển dụng từ các chuyên gia ngành IT",
                date=now + timedelta(days=5),
                location="Hội trường C205",
                manager_id=members_data[9].id,
                status="upcoming",
                notes="Đã chốt danh sách 3 diễn giả từ các tập đoàn công nghệ lớn, chuẩn bị 50 phần quà lưu niệm",
                result=None
            ),
            Activity(
                name="Training Kỹ Năng Thiết Kế & Tư Duy Đồ Họa",
                description="Chuỗi 2 buổi học thực hành Figma và Illustrator cho thành viên mới",
                date=now + timedelta(days=14),
                location="Phòng Đa phương tiện B102",
                manager_id=members_data[1].id,
                status="upcoming",
                notes="Cần chuẩn bị phòng máy cài sẵn Figma desktop",
                result=None
            ),
            Activity(
                name="Teambuilding Dã ngoại Gắn kết Thành viên",
                description="Chuyến dã ngoại 1 ngày tại khu sinh thái nhằm tăng tinh thần đoàn kết CLB",
                date=now + timedelta(days=28),
                location="Khu du lịch sinh thái BCR",
                manager_id=members_data[3].id,
                status="upcoming",
                notes="Dự kiến 35 thành viên tham gia, thuê xe đưa đón",
                result=None
            )
        ]

        db.add_all(activities_data)
        db.flush()

        # 5. Điểm danh (Attendance)
        attendance_data = []
        for i, member in enumerate(members_data[:10]):
            # Workshop Python
            status_1 = "present" if i < 8 else ("excused" if i == 8 else "absent")
            attendance_data.append(Attendance(
                activity_id=activities_data[0].id,
                member_id=member.id,
                status=status_1
            ))
            # Hackathon
            status_2 = "present" if i != 4 and i != 9 else "absent"
            attendance_data.append(Attendance(
                activity_id=activities_data[1].id,
                member_id=member.id,
                status=status_2
            ))

        db.add_all(attendance_data)
        db.flush()

        # 6. Nhiệm vụ (Tasks)
        tasks_data = [
            Task(
                name="Soạn giáo trình Workshop Python",
                description="Biên soạn slide và bài tập hands-on cho buổi workshop",
                activity_id=activities_data[0].id,
                assigned_to=members_data[2].id,
                assigned_by=members_data[0].id,
                deadline=now - timedelta(days=26),
                status="completed",
                progress=100,
                priority="high"
            ),
            Task(
                name="Thiết kế Poster & Banner Hackathon",
                description="Bộ ấn phẩm nhận diện truyền thông gồm avatar, cover, poster A1 và standee",
                activity_id=activities_data[1].id,
                assigned_to=members_data[1].id,
                assigned_by=members_data[0].id,
                deadline=now - timedelta(days=15),
                status="completed",
                progress=100,
                priority="urgent"
            ),
            Task(
                name="Vận động tài trợ Hackathon",
                description="Gửi thư mời tài trợ và làm việc với các doanh nghiệp đối tác",
                activity_id=activities_data[1].id,
                assigned_to=members_data[9].id,
                assigned_by=members_data[0].id,
                deadline=now - timedelta(days=14),
                status="completed",
                progress=100,
                priority="high"
            ),
            Task(
                name="Liên hệ diễn giả Tọa đàm Doanh nghiệp",
                description="Gửi thư mời và chốt timeline bài trình bày với 3 diễn giả",
                activity_id=activities_data[2].id,
                assigned_to=members_data[9].id,
                assigned_by=members_data[0].id,
                deadline=now + timedelta(days=2),
                status="in_progress",
                progress=75,
                priority="urgent"
            ),
            Task(
                name="Thiết kế slide và backdrop Tọa đàm",
                description="Hoàn thiện slide giới thiệu khách mời và backdrop sân khấu",
                activity_id=activities_data[2].id,
                assigned_to=members_data[1].id,
                assigned_by=members_data[0].id,
                deadline=now + timedelta(days=3),
                status="in_progress",
                progress=60,
                priority="high"
            ),
            Task(
                name="Chuẩn bị âm thanh ánh sáng phòng C205",
                description="Kiểm tra hệ thống micro không dây, máy chiếu và loa phòng hội trường",
                activity_id=activities_data[2].id,
                assigned_to=members_data[6].id,
                assigned_by=members_data[3].id,
                deadline=now + timedelta(days=4),
                status="not_started",
                progress=0,
                priority="medium"
            ),
            Task(
                name="Soạn tài liệu thực hành Figma",
                description="Chuẩn bị file Figma template mẫu cho học viên",
                activity_id=activities_data[3].id,
                assigned_to=members_data[1].id,
                assigned_by=members_data[0].id,
                deadline=now + timedelta(days=10),
                status="in_progress",
                progress=30,
                priority="medium"
            ),
            Task(
                name="Dựng video recap sự kiện Hackathon",
                description="Dựng video highlight 3 phút đăng fanpage và kênh YouTube CLB",
                activity_id=activities_data[1].id,
                assigned_to=members_data[4].id,
                assigned_by=members_data[1].id,
                deadline=now + timedelta(days=1),
                status="in_progress",
                progress=80,
                priority="medium"
            ),
            Task(
                name="Lập kế hoạch chi phí Teambuilding",
                description="Bảng dự trù kinh phí xe, ăn uống, vé vào cổng và trò chơi teambuilding",
                activity_id=activities_data[4].id,
                assigned_to=members_data[3].id,
                assigned_by=members_data[0].id,
                deadline=now + timedelta(days=18),
                status="not_started",
                progress=0,
                priority="low"
            )
        ]

        db.add_all(tasks_data)
        db.flush()

        # 7. Thông báo (Notifications)
        notifications_data = [
            Notification(
                title="🎉 Chào mừng năm học mới và chào đón tân thành viên CLB!",
                content="Ban Chủ nhiệm trân trọng chào mừng toàn thể thành viên mới gia nhập đại gia đình CLB Công nghệ. Chúc các bạn có một năm học gặt hái nhiều thành công và trải nghiệm đáng nhớ.",
                created_by=users_data[0].id
            ),
            Notification(
                title="📢 Thông báo: Tọa đàm Giao lưu cùng Doanh nghiệp Công nghệ tuần tới",
                content="Sự kiện sẽ diễn ra vào lúc 09:00 tại Hội trường C205. Đề nghị tất cả thành viên có mặt trước 15 phút, trang phục lịch sự hoặc áo đồng phục CLB. Điểm danh tại bàn lễ tân.",
                created_by=users_data[0].id
            ),
            Notification(
                title="🏆 Vinh danh thành tích xuất sắc tại Cuộc thi Hackathon 2026",
                content="Chúc mừng các đội thi đã hoàn thành xuất sắc 24h lập trình liên tục. Giải Nhất đã thuộc về đội AlphaTeam với đề tài Trợ lý AI hỗ trợ học tập sinh viên. Chi tiết kết quả đã được đăng tải trên Fanpage.",
                created_by=users_data[0].id
            ),
            Notification(
                title="📅 Khảo sát lịch rảnh và đăng ký tham gia Teambuilding tháng tới",
                content="Để công tác tổ chức teambuilding diễn ra thuận lợi, mời toàn thể thành viên cập nhật lại lịch rảnh cá nhân trên hệ thống trước ngày 15 hàng tháng.",
                created_by=users_data[0].id
            )
        ]

        db.add_all(notifications_data)
        db.commit()

        print("[OK] Đã nạp thành công toàn bộ dữ liệu mẫu!")
        print("=" * 60)
        print("Tài khoản demo sẵn sàng để kiểm thử:")
        print("  1. Chủ nhiệm (Admin):     admin     / admin123      (Toàn quyền)")
        print("  2. Trưởng ban:           truongban / truongban123  (Ban Truyền thông)")
        print("  3. Trưởng ban kỹ thuật:  cuong_tb  / cuong123      (Ban Kỹ thuật)")
        print("  4. Thành viên:           thanhvien / thanhvien123  (Thành viên)")
        print("=" * 60)

    except Exception as e:
        print(f"[ERROR] Có lỗi khi nạp dữ liệu mẫu: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    seed_database(reset=reset_flag)
