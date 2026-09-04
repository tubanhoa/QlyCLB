# AI Evidence - KT2: Lập Trình Backend & Cơ Sở Dữ Liệu

## 1. Mục Tiêu Sử Dụng AI
Xây dựng khung ứng dụng FastAPI, mô hình dữ liệu SQLAlchemy ORM, phân quyền JWT và các router nghiệp vụ chính.

## 2. Prompt Tiêu Biểu
- *"Tạo các models SQLAlchemy cho hệ thống quản lý câu lạc bộ gồm User, Member, Department, Activity, Attendance, Task, Notification với các quan hệ khóa ngoại và indexes."*
- *"Xây dựng API xác thực JWT trong FastAPI với hàm băm mật khẩu, tạo token và dependency kiểm tra vai trò người dùng."*

## 3. Code Được AI Hỗ Trợ
- Khung ORM models trong `backend/models.py`.
- Các Pydantic schemas trong `backend/schemas.py`.
- Module xác thực cơ bản trong `backend/auth.py`.

## 4. Phần Lập Trình Viên Đã Tự Kiểm Tra & Chỉnh Sửa
- Bổ sung kiểm tra trùng lặp email và tài khoản trước khi commit vào CSDL.
- Sửa quan hệ Department - Leader và thiết lập liên kết thành viên an toàn khi xóa ban chuyên môn.
- Bổ sung cơ chế bảo vệ phân quyền: Trưởng ban chỉ xem dữ liệu thành viên ban mình; Thành viên chỉ xem dữ liệu cá nhân.
- Tự viết hàm kiểm thử kết nối CSDL SQLite đa luồng an toàn.
