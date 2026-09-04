"""
Main Application - FastAPI Entry Point
Chạy: uvicorn main:app --reload --port 8000
"""
import os
import sys
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database và models
from database import engine, Base, SessionLocal
from models import User, Member, Department, Activity, Attendance, Task, Notification

# Import routers
from routers import auth, members, departments, activities, attendance, tasks, notifications, ai

# Import auth utilities
from auth import hash_password

# ==================== Tạo App ====================
app = FastAPI(
    title="Hệ Thống Quản Lý Câu Lạc Bộ Sinh Viên",
    description="API Backend cho hệ thống quản lý CLB sinh viên có tích hợp AI",
    version="1.0.0"
)

# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Đăng ký Routers ====================
app.include_router(auth.router)
app.include_router(members.router)
app.include_router(departments.router)
app.include_router(activities.router)
app.include_router(attendance.router)
app.include_router(tasks.router)
app.include_router(notifications.router)
app.include_router(ai.router)

# ==================== Serve Frontend ====================
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")


@app.get("/")
def serve_index():
    """Trang chủ -> redirect đến login"""
    return FileResponse(os.path.join(frontend_dir, "login.html"))


@app.get("/{page}.html")
def serve_page(page: str):
    """Serve các trang HTML"""
    file_path = os.path.join(frontend_dir, f"{page}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Page not found"}


# ==================== Tạo Database & Seed Data ====================
@app.on_event("startup")
def startup():
    """Khởi tạo database và dữ liệu mẫu"""
    # Tạo bảng
    Base.metadata.create_all(bind=engine)

    # Seed data
    db = SessionLocal()
    try:
        # Kiểm tra đã có dữ liệu chưa
        if db.query(User).count() > 0:
            return

        print("[*] Dang tao du lieu mau...")

        # --- Tạo Departments ---
        dept_truyen_thong = Department(name="Ban Truyền thông", description="Phụ trách truyền thông, marketing và hình ảnh CLB")
        dept_ky_thuat = Department(name="Ban Kỹ thuật", description="Phụ trách hệ thống IT, website và công nghệ")
        dept_su_kien = Department(name="Ban Sự kiện", description="Tổ chức các sự kiện, hoạt động ngoại khóa")
        dept_hoc_thuat = Department(name="Ban Học thuật", description="Tổ chức workshop, seminar, training")

        db.add_all([dept_truyen_thong, dept_ky_thuat, dept_su_kien, dept_hoc_thuat])
        db.flush()

        # --- Tạo Members ---
        members_data = [
            Member(name="Nguyễn Văn An", email="an.nguyen@email.com", phone="0901234567",
                   department_id=None, skills="Quản lý, Lãnh đạo, Lập kế hoạch",
                   availability="Thứ 2-6: 14h-17h, Thứ 7: cả ngày", status="active"),
            Member(name="Trần Thị Bình", email="binh.tran@email.com", phone="0912345678",
                   department_id=dept_truyen_thong.id, skills="Thiết kế đồ họa, Photoshop, Canva, Viết content",
                   availability="Thứ 3,5: 14h-17h, Thứ 7: sáng", status="active"),
            Member(name="Lê Hoàng Cường", email="cuong.le@email.com", phone="0923456789",
                   department_id=dept_ky_thuat.id, skills="Python, JavaScript, HTML/CSS, React",
                   availability="Thứ 2,4,6: 15h-18h", status="active"),
            Member(name="Phạm Thị Dung", email="dung.pham@email.com", phone="0934567890",
                   department_id=dept_su_kien.id, skills="Tổ chức sự kiện, MC, Giao tiếp",
                   availability="Thứ 4,5: 14h-17h, CN: cả ngày", status="active"),
            Member(name="Hoàng Văn Em", email="em.hoang@email.com", phone="0945678901",
                   department_id=dept_truyen_thong.id, skills="Quay phim, Chỉnh sửa video, Premiere, After Effects",
                   availability="Thứ 2,3: 16h-19h, Thứ 7: chiều", status="active"),
            Member(name="Ngô Thị Phương", email="phuong.ngo@email.com", phone="0956789012",
                   department_id=dept_ky_thuat.id, skills="Database, SQL, Backend, FastAPI",
                   availability="Thứ 3,5,7: 14h-17h", status="active"),
            Member(name="Đỗ Minh Quân", email="quan.do@email.com", phone="0967890123",
                   department_id=dept_su_kien.id, skills="Âm thanh, Ánh sáng, Logistics",
                   availability="Thứ 6: 15h-18h, Thứ 7,CN: cả ngày", status="active"),
            Member(name="Vũ Thị Hồng", email="hong.vu@email.com", phone="0978901234",
                   department_id=dept_hoc_thuat.id, skills="Nghiên cứu, Viết báo cáo, Thuyết trình",
                   availability="Thứ 2-4: 14h-16h", status="active"),
            Member(name="Bùi Đức Khánh", email="khanh.bui@email.com", phone="0989012345",
                   department_id=dept_hoc_thuat.id, skills="Data Analysis, Excel, PowerPoint",
                   availability="Thứ 4,6: 15h-18h, CN: sáng", status="active"),
            Member(name="Mai Thanh Lam", email="lam.mai@email.com", phone="0990123456",
                   department_id=dept_truyen_thong.id, skills="Social media, SEO, Content marketing",
                   availability="Thứ 2,5: 16h-19h", status="active"),
            Member(name="Trương Văn Nam", email="nam.truong@email.com", phone="0901112233",
                   department_id=dept_ky_thuat.id, skills="Mobile dev, Flutter, UI/UX",
                   availability="Thứ 3,6: 14h-17h", status="inactive"),
            Member(name="Lý Thị Oanh", email="oanh.ly@email.com", phone="0912223344",
                   department_id=dept_su_kien.id, skills="Quan hệ công chúng, Gây quỹ, Networking",
                   availability="Thứ 2,4: 15h-18h, Thứ 7: sáng", status="active"),
        ]

        db.add_all(members_data)
        db.flush()

        # Cập nhật trưởng ban
        dept_truyen_thong.leader_id = members_data[1].id  # Trần Thị Bình
        dept_ky_thuat.leader_id = members_data[2].id      # Lê Hoàng Cường
        dept_su_kien.leader_id = members_data[3].id       # Phạm Thị Dung
        dept_hoc_thuat.leader_id = members_data[7].id     # Vũ Thị Hồng

        # --- Tạo Users ---
        users_data = [
            User(username="admin", password=hash_password("admin123"),
                 role="chu_nhiem", member_id=members_data[0].id),
            User(username="truongban", password=hash_password("truongban123"),
                 role="truong_ban", member_id=members_data[1].id),
            User(username="thanhvien", password=hash_password("thanhvien123"),
                 role="thanh_vien", member_id=members_data[4].id),
            User(username="cuong_tb", password=hash_password("cuong123"),
                 role="truong_ban", member_id=members_data[2].id),
            User(username="dung_tb", password=hash_password("dung123"),
                 role="truong_ban", member_id=members_data[3].id),
        ]

        db.add_all(users_data)
        db.flush()

        # --- Tạo Activities ---
        activities_data = [
            Activity(
                name="Workshop Python cơ bản",
                description="Workshop hướng dẫn Python cho người mới bắt đầu, bao gồm cú pháp, kiểu dữ liệu và vòng lặp",
                date=datetime(2024, 12, 15, 14, 0),
                location="Phòng A301, Tòa nhà CNTT",
                manager_id=members_data[2].id,
                status="completed",
                notes="Có 25 sinh viên tham gia, chất lượng tốt",
                result="90% học viên hoàn thành bài tập, phản hồi tích cực"
            ),
            Activity(
                name="Cuộc thi Hackathon 2024",
                description="Cuộc thi lập trình 24h với chủ đề AI for Education",
                date=datetime(2025, 1, 20, 8, 0),
                location="Hội trường lớn, Tòa nhà B",
                manager_id=members_data[0].id,
                status="completed",
                notes="10 đội tham gia, 3 mentor hỗ trợ",
                result="3 sản phẩm xuất sắc, 1 đội đại diện trường thi cấp thành phố"
            ),
            Activity(
                name="Giao lưu CLB công nghệ",
                description="Giao lưu với CLB IT trường Đại học Bách Khoa",
                date=datetime(2025, 3, 10, 9, 0),
                location="Sảnh chính, Khu A",
                manager_id=members_data[3].id,
                status="upcoming",
                notes="Cần chuẩn bị banner, standee và quà tặng",
                result=None
            ),
            Activity(
                name="Training Design Thinking",
                description="Khóa training về phương pháp Design Thinking cho thành viên CLB",
                date=datetime(2025, 4, 5, 14, 0),
                location="Phòng Lab 205",
                manager_id=members_data[7].id,
                status="upcoming",
                notes="Mời diễn giả từ công ty FPT",
                result=None
            ),
            Activity(
                name="Teambuilding cuối năm",
                description="Hoạt động teambuilding gắn kết thành viên CLB",
                date=datetime(2025, 5, 25, 7, 0),
                location="Khu du lịch sinh thái Vườn Xoài",
                manager_id=members_data[3].id,
                status="upcoming",
                notes="Dự kiến 30 thành viên, thuê xe bus",
                result=None
            ),
        ]

        db.add_all(activities_data)
        db.flush()

        # --- Tạo Attendance (cho hoạt động đã hoàn thành) ---
        attendance_data = []
        for i, member in enumerate(members_data[:10]):
            # Workshop Python
            status = "present" if i < 7 else ("excused" if i == 7 else "absent")
            attendance_data.append(Attendance(
                activity_id=activities_data[0].id,
                member_id=member.id,
                status=status
            ))
            # Hackathon
            status = "present" if i < 8 else "absent"
            attendance_data.append(Attendance(
                activity_id=activities_data[1].id,
                member_id=member.id,
                status=status
            ))

        db.add_all(attendance_data)
        db.flush()

        # --- Tạo Tasks ---
        tasks_data = [
            Task(name="Chuẩn bị tài liệu Workshop", description="Soạn slide và bài tập cho workshop Python",
                 activity_id=activities_data[0].id, assigned_to=members_data[2].id,
                 assigned_by=members_data[0].id, deadline=datetime(2024, 12, 13),
                 status="completed", progress=100, priority="high"),
            Task(name="Thiết kế poster Hackathon", description="Thiết kế poster quảng bá cuộc thi",
                 activity_id=activities_data[1].id, assigned_to=members_data[1].id,
                 assigned_by=members_data[0].id, deadline=datetime(2025, 1, 10),
                 status="completed", progress=100, priority="high"),
            Task(name="Liên hệ sponsor", description="Tìm và liên hệ nhà tài trợ cho Hackathon",
                 activity_id=activities_data[1].id, assigned_to=members_data[3].id,
                 assigned_by=members_data[0].id, deadline=datetime(2025, 1, 5),
                 status="completed", progress=100, priority="urgent"),
            Task(name="Thiết kế banner giao lưu", description="Thiết kế banner và standee cho buổi giao lưu",
                 activity_id=activities_data[2].id, assigned_to=members_data[1].id,
                 assigned_by=members_data[0].id, deadline=datetime(2025, 3, 5),
                 status="in_progress", progress=60, priority="high"),
            Task(name="Liên hệ CLB đối tác", description="Liên hệ CLB IT Bách Khoa để xác nhận chương trình",
                 activity_id=activities_data[2].id, assigned_to=members_data[3].id,
                 assigned_by=members_data[0].id, deadline=datetime(2025, 2, 28),
                 status="in_progress", progress=40, priority="medium"),
            Task(name="Setup hệ thống âm thanh", description="Chuẩn bị và test hệ thống âm thanh, mic",
                 activity_id=activities_data[2].id, assigned_to=members_data[6].id,
                 assigned_by=members_data[0].id, deadline=datetime(2025, 3, 9),
                 status="not_started", progress=0, priority="medium"),
            Task(name="Mời diễn giả", description="Liên hệ diễn giả từ FPT cho training Design Thinking",
                 activity_id=activities_data[3].id, assigned_to=members_data[7].id,
                 assigned_by=members_data[0].id, deadline=datetime(2025, 3, 20),
                 status="in_progress", progress=30, priority="high"),
            Task(name="Quay video sự kiện", description="Quay và biên tập video cho các hoạt động",
                 activity_id=None, assigned_to=members_data[4].id,
                 assigned_by=members_data[1].id, deadline=datetime(2025, 4, 1),
                 status="not_started", progress=0, priority="low"),
        ]

        db.add_all(tasks_data)
        db.flush()

        # --- Tạo Notifications ---
        notifications_data = [
            Notification(
                title="Chào mừng thành viên mới!",
                content="Chào mừng tất cả thành viên mới gia nhập CLB IT. Hãy cập nhật thông tin cá nhân và kỹ năng của bạn để chúng tôi phân công nhiệm vụ phù hợp nhé!",
                created_by=users_data[0].id
            ),
            Notification(
                title="📢 Thông báo Workshop Python",
                content="CLB sẽ tổ chức Workshop Python cơ bản vào ngày 15/12/2024 tại phòng A301. Mong tất cả thành viên sắp xếp thời gian tham gia. Đăng ký qua link: ...",
                created_by=users_data[0].id
            ),
            Notification(
                title="🏆 Kết quả Hackathon 2024",
                content="Chúc mừng 3 đội đạt giải trong cuộc thi Hackathon 2024! Đặc biệt chúc mừng đội AlphaCode sẽ đại diện trường thi cấp thành phố. Chi tiết xem tại fanpage CLB.",
                created_by=users_data[0].id
            ),
            Notification(
                title="📅 Lịch hoạt động tháng 3",
                content="Tháng 3 CLB có các hoạt động: Giao lưu CLB công nghệ (10/3), Training Design Thinking (5/4). Mong các bạn sắp xếp tham gia đầy đủ!",
                created_by=users_data[0].id
            ),
        ]

        db.add_all(notifications_data)
        db.commit()

        print("[OK] Tao du lieu mau thanh cong!")
        print("Tai khoan demo:")
        print("   - Chu nhiem: admin / admin123")
        print("   - Truong ban: truongban / truongban123")
        print("   - Thanh vien: thanhvien / thanhvien123")

    except Exception as e:
        print(f"[ERROR] Loi tao du lieu mau: {e}")
        db.rollback()
    finally:
        db.close()


# ==================== Dashboard Stats API ====================
@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    """API thống kê cho dashboard"""
    db = SessionLocal()
    try:
        total_members = db.query(Member).filter(Member.status == "active").count()
        total_departments = db.query(Department).count()
        total_activities = db.query(Activity).count()
        upcoming_activities = db.query(Activity).filter(Activity.status == "upcoming").count()
        total_tasks = db.query(Task).count()
        completed_tasks = db.query(Task).filter(Task.status == "completed").count()
        in_progress_tasks = db.query(Task).filter(Task.status == "in_progress").count()
        total_notifications = db.query(Notification).count()

        return {
            "total_members": total_members,
            "total_departments": total_departments,
            "total_activities": total_activities,
            "upcoming_activities": upcoming_activities,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "total_notifications": total_notifications
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
