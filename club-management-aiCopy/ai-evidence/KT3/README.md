# AI Evidence - KT3: Kiểm Thử & Tối Ưu Hóa Giao Diện

## 1. Mục Tiêu Sử Dụng AI
- Xây dựng giao diện Frontend nhất quán theo Dark Theme.
- Tích hợp AI Assistant (sinh thông báo, tóm tắt kết quả hoạt động, gợi ý phân công nhiệm vụ).
- Thiết kế các ca kiểm thử bảo mật và phân quyền vai trò.

## 2. Prompt Tiêu Biểu
- *"Xây dựng giao diện CSS Dark Premium Theme hiện đại cho trang quản lý CLB với biến màu CSS, thẻ glassmorphism và responsive mobile/desktop."*
- *"Tạo hàm gọi AI sinh thông báo hoạt động từ các tham số thời gian, địa điểm, nội dung mục tiêu."*
- *"Thiết kế kịch bản test kiểm tra phân quyền người dùng giữa Chủ nhiệm, Trưởng ban và Thành viên."*

## 3. Code Được AI Hỗ Trợ
- Giao diện CSS design system trong `frontend/css/style.css`.
- Client logic tương tác API trong `frontend/js/ai.js` và `frontend/js/attendance.js`.
- AI services backend trong `backend/services/ai_service.py`.

## 4. Phần Lập Trình Viên Đã Kiểm Tra & Tối Ưu Thủ Công
- Sửa lỗi UI responsiveness trên màn hình di động cho bảng dữ liệu và thanh điều hướng sidebar.
- Viết cơ chế Fallback Demo Mode khi không có OpenAI API Key, đảm bảo test và demo không bao giờ bị gián đoạn.
- Kiểm tra trực tiếp các ca kiểm thử: Thử gửi request trái quyền (thành viên xóa ban, thành viên sửa task của người khác) và xác nhận mã phản hồi trả về đúng 403 Forbidden.
- Bổ sung xác nhận trước khi xóa (Confirm dialog) và thông báo Toast phản hồi mọi thao tác.
