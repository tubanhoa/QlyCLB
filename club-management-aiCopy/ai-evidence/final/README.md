# Minh Chứng Sử Dụng AI - Giai Đoạn Cuối Kỳ (Final Evidence)

## 1. Mục Tiêu Sử Dụng AI
- Hoàn thiện toàn bộ 10 tiêu chí đánh giá chất lượng phần mềm.
- Tích hợp biểu đồ trực quan (Chart.js), tính năng xuất báo cáo CLB, kiểm tra bảo mật phân quyền RBAC và xử lý lỗi toàn cục.
- Hoàn thiện tài liệu hướng dẫn sử dụng, kịch bản chạy thử nghiệm (Demo Scenario) và tài liệu API.

## 2. Nhật Ký Prompt Tiêu Biểu
- **Prompt 1:** *"Xây dựng Global Exception Handler cho FastAPI để bắt RequestValidationError và SQLAlchemy IntegrityError, trả về thông điệp tiếng Việt dễ hiểu cho người dùng cuối mà không gây crash server."*
- **Prompt 2:** *"Thiết kế bảng biểu đồ phân tích trên Dashboard bằng Chart.js gồm: Phân bổ thành viên theo ban (Doughnut), Phân bổ trạng thái nhiệm vụ (Bar), Tỷ lệ điểm danh chuyên cần (Bar) tương thích Dark Theme."*
- **Prompt 3:** *"Viết kịch bản demo 10 bước chi tiết tương ứng 10 tiêu chí chấm điểm hệ thống quản lý câu lạc bộ sinh viên."*

## 3. Phần Code Được AI Hỗ Trợ
- Khung exception handlers trong `backend/main.py`.
- Khung cấu hình Chart.js trong `frontend/dashboard.html`.
- Các câu lệnh query lọc và sắp xếp động trong `backend/routers/`.

## 4. Phần Người Lập Trình Đã Rà Soát, Kiểm Tra & Sửa Đổi Thủ Công
- **Kiểm tra cú pháp & an toàn:** Đảm bảo các exception handler không che giấu lỗi nghiêm trọng khi debug.
- **Tối ưu bảng màu UI:** Thay đổi màu sắc mặc định của Chart.js thành bộ mã màu hiện đại phù hợp với Design System Dark Theme (`#6366f1`, `#06b6d4`, `#10b981`, `#f59e0b`, `#ef4444`).
- **Phân quyền chặt chẽ:** Bổ sung `requireRole` cấp trang và ẩn các nút thao tác tương ứng cho từng vai trò trên giao diện.
- **Dữ liệu mẫu:** Tự xây dựng file `backend/seed_data.py` độc lập để tạo dữ liệu thực tế, phong phú và phục vụ demo tức thì.

## 5. Kết Luận
Toàn bộ mã nguồn đã được kiểm thử, chạy thực tế ổn định và đáp ứng 100% yêu cầu kỹ thuật.
Chi tiết xem thêm tại [docs/ai_log.md](../../docs/ai_log.md).
