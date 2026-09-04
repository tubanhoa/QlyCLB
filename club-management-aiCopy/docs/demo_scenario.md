# 🚀 Kịch Bản Kiểm Thử & Chạy Thử Nghiệm 10 Tiêu Chí (Demo Scenario)

Tài liệu này được thiết kế theo đúng **10 tiêu chí đánh giá** của đồ án, giúp người đánh giá (giảng viên / hội đồng) có thể kiểm tra toàn diện hệ thống trong vòng 5 - 10 phút.

---

## 📋 Bảng Tài Khoản Demo

| Vai trò | Tài khoản | Mật khẩu | Phạm vi quyền hạn |
|:---|:---|:---|:---|
| 👑 **Chủ nhiệm** (Admin) | `admin` | `admin123` | Toàn quyền quản trị hệ thống, thêm/sửa/xóa ban, thành viên, hoạt động, thông báo, AI |
| ⭐ **Trưởng ban** (Manager) | `truongban` | `truongban123` | Quản lý ban Truyền thông, giao việc trong ban, điểm danh, AI phân công |
| 💻 **Trưởng ban KT** | `cuong_tb` | `cuong123` | Quản lý ban Kỹ thuật, giao việc trong ban, điểm danh, AI phân công |
| 👤 **Thành viên** (Member) | `thanhvien` | `thanhvien123` | Xem/sửa thông tin cá nhân, cập nhật tiến độ nhiệm vụ của mình, xem thông báo |

---

## 🎯 Hướng Dẫn Kiểm Thử Từng Tiêu Chí

### Tiêu chí 1: Cấu trúc dự án hợp lý
- **Cách kiểm tra:**
  1. Mở thư mục dự án, kiểm tra phân chia rõ ràng:
     - `backend/`: Mã nguồn API FastAPI, models, schemas, auth, routers, services, database config.
     - `frontend/`: Các trang HTML, thư mục `css/` và `js/` module hóa.
     - `docs/`: Chứa các tài liệu thiết kế CSDL, yêu cầu kỹ thuật, use case, minh chứng AI.
     - `ai-evidence/`: Các thư mục minh chứng theo giai đoạn.
     - Gốc: `README.md`, `.env.example`, `club.db`.
- **Kết quả kỳ vọng:** Cấu trúc module hóa sạch sẽ, tách bạch giữa giao diện, logic backend và cơ sở dữ liệu.

---

### Tiêu chí 2: Xây dựng chức năng đăng nhập và phân quyền
- **Bước 1 (Đăng nhập):** Truy cập `http://localhost:8000/login.html`. Thử nhập sai mật khẩu -> Hệ thống thông báo lỗi "Tài khoản hoặc mật khẩu không đúng". Nhấp nút điền nhanh tài khoản `admin` và đăng nhập -> Vào trang Dashboard thành công.
- **Bước 2 (Kiểm tra quyền Chủ nhiệm):** Đăng nhập với `admin` -> Sidebar hiển thị đầy đủ tất cả menu (Ban chuyên môn, Điểm danh, AI Assistant, Thông báo). Có quyền Thêm, Sửa, Xóa trên tất cả các trang.
- **Bước 3 (Kiểm tra quyền Trưởng ban):** Đăng xuất, đăng nhập với `truongban / truongban123` -> Không thấy menu "Ban chuyên môn". Tại trang Thành viên chỉ nhìn thấy thành viên thuộc Ban Truyền thông.
- **Bước 4 (Kiểm tra quyền Thành viên):** Đăng xuất, đăng nhập với `thanhvien / thanhvien123` -> Ẩn menu Ban chuyên môn, Điểm danh, AI Assistant. Cố tình gõ URL `http://localhost:8000/departments.html` trên thanh địa chỉ -> Hệ thống hiển thị cảnh báo "Bạn không có quyền truy cập vào trang này!" và tự động điều hướng an toàn về Dashboard.
- **Kết quả kỳ vọng:** Xác thực JWT token hoạt động ổn định, phân quyền chặt chẽ ở cả backend API lẫn giao diện frontend.

---

### Tiêu chí 3: Hoàn thiện CRUD nghiệp vụ chính
- **Thành viên (Members):**
  - Thêm thành viên mới: Bấm `➕ Thêm thành viên`, nhập họ tên, email, chọn ban -> Thành viên mới xuất hiện trong bảng.
  - Xem chi tiết: Bấm biểu tượng 👁️ -> Modal hiển thị đầy đủ thông tin kỹ năng, lịch rảnh.
  - Sửa thành viên: Bấm ✏️ -> Cập nhật số điện thoại hoặc kỹ năng -> Bảng cập nhật tức thì.
  - Xóa thành viên: Bấm 🗑️ -> Xác nhận xóa -> Thành viên được gỡ bỏ an toàn.
- **Ban chuyên môn (Departments):** Thêm ban mới, chỉnh sửa thông tin ban, gán trưởng ban, xóa ban (thành viên tự động chuyển về trạng thái Chưa phân ban mà không bị xóa mất dữ liệu).
- **Hoạt động (Activities):** Thêm hoạt động mới, xem chi tiết, sửa nội dung, xóa hoạt động (tự động cascade xóa các dữ liệu điểm danh liên kết).
- **Nhiệm vụ (Tasks):** Tạo nhiệm vụ mới, phân công thành viên, cập nhật tiến độ (0% -> 100%), đổi trạng thái.
- **Điểm danh (Attendance):** Chọn hoạt động -> Danh sách thành viên hiển thị -> Đánh dấu Có mặt/Vắng/Có phép -> Bấm "Lưu điểm danh" -> Tỷ lệ tham gia (%) cập nhật tức thì.
- **Thông báo (Notifications):** Tạo thông báo mới, sửa nội dung, xóa thông báo.
- **Kết quả kỳ vọng:** 100% chức năng Thêm, Xem, Sửa, Xóa của các đối tượng chính hoạt động chính xác, dữ liệu lưu xuống CSDL SQLite vĩnh viễn.

---

### Tiêu chí 4: Xây dựng chức năng tìm kiếm, lọc và sắp xếp
- **Tìm kiếm:**
  - Tại trang Thành viên: Gõ từ khóa "Cường" hoặc email "cuong" vào ô tìm kiếm -> Bảng lọc ngay lập tức còn 1 dòng của Lê Hoàng Cường.
  - Tại trang Nhiệm vụ: Gõ "Poster" -> Tìm ra nhiệm vụ Thiết kế Poster Hackathon.
  - Tại trang Thông báo: Gõ "Chào mừng" -> Tìm ra thông báo tương ứng.
- **Lọc (Filter):**
  - Lọc Thành viên theo Ban: Chọn "Ban Truyền thông" -> Chỉ hiển thị thành viên ban này.
  - Lọc theo Trạng thái: Chọn "Đang hoạt động" hoặc "Ngừng hoạt động".
  - Lọc Nhiệm vụ: Chọn trạng thái "Đang thực hiện" hoặc độ ưu tiên "Khẩn cấp".
- **Sắp xếp (Sort):**
  - Sắp xếp Thành viên: Chọn "Tên: A → Z" hoặc "Tên: Z → A", "Gia nhập: Mới nhất".
  - Sắp xếp Hoạt động: Chọn "Thời gian: Mới nhất" hoặc "Cũ nhất", "Tên: A → Z".
  - Sắp xếp Nhiệm vụ: Chọn "Hạn chót: Gần nhất", "Ưu tiên cao nhất", "Tiến độ cao nhất".
- **Kết quả kỳ vọng:** Dữ liệu phản hồi tức thì, kết hợp đồng thời cả tìm kiếm + lọc + sắp xếp mượt mà.

---

### Tiêu chí 5: Xây dựng thống kê / báo cáo cơ bản
- **Dashboard & Biểu đồ trực quan:**
  - 6 thẻ số liệu tổng quát (Thành viên hoạt động, Ban chuyên môn, Hoạt động, Nhiệm vụ, Hoàn thành, Thông báo).
  - **Biểu đồ 1 (Doughnut Chart):** Cơ cấu thành viên theo Ban chuyên môn.
  - **Biểu đồ 2 (Bar Chart):** Phân bổ số lượng nhiệm vụ theo 4 trạng thái.
  - **Biểu đồ 3 (Bar Chart):** Tỷ lệ chuyên cần tham gia điểm danh (%) của các hoạt động.
- **Xuất / In báo cáo nghiệp vụ:**
  - Nhấp nút `📄 Xuất Báo Cáo CLB` trên Topbar.
  - Modal Báo cáo tổng kết hiện ra với các số liệu tổng hợp chi tiết: nhân sự, tiến độ nhiệm vụ, tỷ lệ hoàn thành, bảng tỷ lệ chuyên cần.
  - Nhấp nút `🖨️ In / Xuất Báo Cáo` -> Trình duyệt mở hộp thoại in / lưu file PDF chuyên nghiệp.
- **Kết quả kỳ vọng:** Dashboard cung cấp cái nhìn toàn diện về hoạt động CLB; báo cáo xuất ra rõ ràng, phục vụ họp ban chủ nhiệm.

---

### Tiêu chí 6: Thiết kế giao diện rõ ràng, dễ sử dụng
- **Tính nhất quán:** Giao diện thiết kế theo phong cách Dark Premium Theme với màu sắc hài hòa (`#0f172a`, `#1e293b`, `#6366f1`, `#06b6d4`), font chữ Inter hiện đại, bo góc mềm mại.
- **Phản hồi người dùng (User Feedback):**
  - Mọi thao tác thành công hiển thị Toast xanh (VD: *"Thêm thành viên thành công!"*).
  - Khi có lỗi hiển thị Toast đỏ kèm nguyên nhân chi tiết.
  - Hộp thoại xác nhận (Confirm modal) trước khi thực hiện xóa.
- **Trạng thái bảng biểu:** Có thanh tiến độ trực quan (Progress bar nhiều màu theo % hoàn thành), huy hiệu trạng thái (Badges), thông báo trạng thái trống (Empty state) kèm icon đẹp mắt khi không tìm thấy kết quả.

---

### Tiêu chí 7: Kết nối và thao tác CSDL ổn định
- **Kết nối SQLite + SQLAlchemy ORM:** Không cần cấu hình server CSDL phức tạp, file `club.db` lưu trữ toàn vẹn dữ liệu.
- **Script nạp dữ liệu mẫu:**
  ```bash
  cd backend
  python seed_data.py --reset
  ```
  Nạp lại toàn bộ dữ liệu mẫu gồm 5 ban, 12 thành viên, 6 tài khoản người dùng, 5 hoạt động, bản ghi điểm danh và 9 nhiệm vụ đa dạng.
- **Toàn vẹn dữ liệu:** Ràng buộc khóa chính, khóa ngoại, không bị lỗi dữ liệu mồ côi khi xóa ban hoặc xóa hoạt động.

---

### Tiêu chí 8: Xử lý lỗi cơ bản (Không để ứng dụng crash)
- **Input sai / Dữ liệu thiếu:**
  - Thử tạo thành viên để trống họ tên hoặc email -> Hệ thống báo lỗi "Vui lòng nhập họ tên và email".
  - Thử nhập email không đúng định dạng (`abcxyz`) -> Hệ thống báo lỗi "Định dạng email không hợp lệ".
- **Dữ liệu trùng lặp (IntegrityError):**
  - Thử thêm hoặc sửa thành viên với email đã tồn tại (`an.nguyen@email.com`) -> Backend bắt lỗi và trả về thông điệp thân thiện: *"Email này đã được sử dụng bởi thành viên khác"* (không bị crash server 500).
- **Lỗi phân quyền:**
  - Thành viên cố tình gửi request xóa thành viên hoặc sửa nhiệm vụ người khác -> Backend chặn và trả về HTTP 403 *"Bạn không có quyền thực hiện thao tác này"*.
- **Global Exception Handlers:** Đã được cài đặt đầy đủ trong `backend/main.py`, ứng dụng luôn trả về JSON có cấu trúc `{ "detail": "..." }`, không bao giờ bị sập tiến trình.

---

### Tiêu chí 9: Minh chứng sử dụng AI khi lập trình
- **Xem tài liệu:** Mở file [docs/ai_log.md](ai_log.md) và thư mục [ai-evidence/](../ai-evidence/).
- **Nội dung minh chứng:**
  - Bảng tổng hợp prompt, công cụ AI (Copilot, ChatGPT, Claude) qua từng giai đoạn phát triển.
  - Các case study cụ thể chỉ rõ: Code do AI đề xuất ban đầu -> Lỗi/lỗ hổng do sinh viên phát hiện -> Code tối ưu và an toàn do sinh viên sửa đổi thủ công (Human-in-the-loop).

---

### Tiêu chí 10: Quản lý mã nguồn và tài liệu chạy thử
- File [README.md](../README.md) đầy đủ thông tin: Giới thiệu hệ thống, bảng phân quyền vai trò, danh sách công nghệ, hướng dẫn cài đặt từng bước cho Windows & Linux, hướng dẫn cấu hình `.env`, danh sách tài khoản demo.
- File [.env.example](../.env.example) cung cấp sẵn các biến mẫu.
- Script khởi tạo `seed_data.py` độc lập.
