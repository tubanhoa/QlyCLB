# 🎓 Hệ Thống Quản Lý Câu Lạc Bộ Sinh Viên Có Tích Hợp AI (CLB Manager)

> **Dự án Đồ án Chuyên ngành / Môn học:** Xây dựng hệ thống quản lý câu lạc bộ sinh viên toàn diện với kiến trúc hiện đại, phân quyền đa cấp, nghiệp vụ chuyên sâu và tích hợp Trí tuệ Nhân tạo (AI Assistant & Chatbot).

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red?style=flat)](https://www.sqlalchemy.org)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat&logo=sqlite)](https://www.sqlite.org)
[![Chart.js](https://img.shields.io/badge/Charts-Chart.js-FF6384?style=flat&logo=chartdotjs)](https://www.chartjs.org)
[![Theme](https://img.shields.io/badge/UI-Dark%20Premium-6366f1?style=flat)](#)

---

## 📑 Bảng Đối Chiếu 10 Tiêu Chí Đánh Giá

| STT | Tiêu chí đánh giá | Trạng thái | Vị trí triển khai / Tài liệu kiểm chứng |
|:---:|:---|:---:|:---|
| **1** | **Cấu trúc dự án hợp lý** | ✅ Đạt | Tách bạch rõ `backend/`, `frontend/`, `docs/`, `ai-evidence/`, `.env.example` |
| **2** | **Đăng nhập & phân quyền (RBAC)** | ✅ Đạt | JWT token, băm mật khẩu, 3 vai trò (Chủ nhiệm, Trưởng ban, Thành viên), bảo vệ API & router guard |
| **3** | **CRUD nghiệp vụ chính** | ✅ Đạt | Đầy đủ Thêm, Xem, Sửa, Xóa cho Thành viên, Ban, Hoạt động, Nhiệm vụ, Điểm danh, Thông báo |
| **4** | **Tìm kiếm, lọc và sắp xếp** | ✅ Đạt | Tìm kiếm đa trường (keyword), lọc theo phòng ban/trạng thái/độ ưu tiên, sắp xếp động (A-Z, thời gian, hạn chót) |
| **5** | **Thống kê / Báo cáo cơ bản** | ✅ Đạt | 6 thẻ KPI, 3 biểu đồ Chart.js (Cơ cấu ban, Nhiệm vụ, Điểm danh), chức năng Xuất/In báo cáo tổng hợp |
| **6** | **Giao diện rõ ràng, dễ sử dụng** | ✅ Đạt | Dark Theme hiện đại, responsive, thông báo Toast thời gian thực, hộp thoại xác nhận an toàn |
| **7** | **Kết nối & thao tác CSDL ổn định** | ✅ Đạt | SQLite + SQLAlchemy ORM, cascade delete, script nạp dữ liệu mẫu phong phú `backend/seed_data.py` |
| **8** | **Xử lý lỗi cơ bản** | ✅ Đạt | Global Exception Handlers (RequestValidationError, IntegrityError, SQLAlchemyError), validate email/SĐT |
| **9** | **Minh chứng sử dụng AI** | ✅ Đạt | Nhật ký prompt, phản hồi AI, case study human-in-the-loop tại [docs/ai_log.md](docs/ai_log.md) và [ai-evidence/](ai-evidence/) |
| **10** | **Quản lý mã nguồn & tài liệu chạy** | ✅ Đạt | `README.md`, `.env.example`, kịch bản demo 10 bước [docs/demo_scenario.md](docs/demo_scenario.md) |

---

## 🏛️ Cấu Trúc Thư Mục Dự Án

```
club-management-ai/
├── backend/                        # Mã nguồn Backend API (FastAPI)
│   ├── main.py                     # Entry point chính, Exception Handlers & Dashboard API
│   ├── database.py                 # Cấu hình kết nối SQLAlchemy & SQLite engine
│   ├── models.py                   # ORM Models (8 bảng dữ liệu quan hệ)
│   ├── schemas.py                  # Pydantic schemas (Validation dữ liệu vào/ra)
│   ├── auth.py                     # Xác thực JWT, Hash mật khẩu & Dependency phân quyền
│   ├── seed_data.py                # Script độc lập reset & nạp dữ liệu mẫu phong phú
│   ├── requirements.txt            # Danh sách thư viện phụ thuộc Python
│   ├── .env.example                # File mẫu biến môi trường backend
│   ├── routers/                    # Các API Endpoints chia theo đối tượng nghiệp vụ
│   │   ├── auth.py                 # Đăng nhập & xem thông tin user
│   │   ├── members.py              # CRUD thành viên, lọc & sắp xếp
│   │   ├── departments.py          # CRUD ban chuyên môn
│   │   ├── activities.py           # CRUD hoạt động CLB
│   │   ├── attendance.py           # Điểm danh đơn lẻ & điểm danh hàng loạt
│   │   ├── tasks.py                # Quản lý & cập nhật tiến độ nhiệm vụ
│   │   ├── notifications.py        # Quản lý thông báo CLB
│   │   └── ai.py                   # Tích hợp AI Assistant & Chatbot
│   └── services/                   # Các dịch vụ tích hợp bên ngoài
│       ├── ai_service.py           # Gọi OpenAI API & Fallback Demo Mode
│       └── chatbot_service.py      # Trợ lý ảo hỏi đáp sinh viên
├── frontend/                       # Giao diện người dùng (HTML5, CSS3, Vanilla JS)
│   ├── login.html                  # Màn hình đăng nhập kèm nút test tài khoản nhanh
│   ├── dashboard.html              # Trang tổng quan số liệu, biểu đồ Chart.js & xuất báo cáo
│   ├── members.html                # Quản lý thành viên (tìm kiếm, lọc ban, lọc trạng thái, sắp xếp)
│   ├── departments.html            # Quản lý ban chuyên môn & danh sách thành viên
│   ├── activities.html             # Quản lý hoạt động, sự kiện
│   ├── attendance.html             # Giao diện điểm danh chuyên cần theo hoạt động
│   ├── tasks.html                  # Quản lý nhiệm vụ, lọc ưu tiên/trạng thái, cập nhật tiến độ
│   ├── notifications.html          # Danh sách thông báo nội bộ
│   ├── ai.html                     # AI Assistant: sinh thông báo, tóm tắt, gợi ý phân công
│   ├── chatbot.html                # Chatbot hỏi đáp sinh viên UniClub Assistant
│   ├── css/
│   │   └── style.css               # Design System Dark Premium Theme
│   └── js/                         # Logic xử lý gọi API & thao tác DOM
│       ├── auth.js                 # Quản lý token, phân quyền route guard, Toast, Sidebar
│       ├── members.js              # Logic CRUD, tìm kiếm, lọc, sắp xếp thành viên
│       ├── departments.js          # Logic quản lý ban
│       ├── activities.js           # Logic quản lý hoạt động
│       ├── attendance.js           # Logic điểm danh
│       ├── tasks.js                # Logic nhiệm vụ & phân quyền giao diện
│       ├── notifications.js        # Logic thông báo
│       └── ai.js                   # Logic tương tác AI
├── docs/                           # Tài liệu thiết kế & minh chứng
│   ├── requirements.md             # Tài liệu đặc tả yêu cầu phần mềm
│   ├── database_design.md          # Thiết kế CSDL chi tiết kèm sơ đồ quan hệ ERD
│   ├── use_cases.md                # Đặc tả ca sử dụng (Use Cases)
│   ├── ai_log.md                   # Nhật ký chi tiết minh chứng sử dụng AI
│   └── demo_scenario.md            # Kịch bản kiểm thử 10 tiêu chí trong 5-10 phút
├── ai-evidence/                    # Bằng chứng AI theo các đợt kiểm tra (KT1, KT2, KT3, Final)
│   ├── KT1/README.md               # Minh chứng phân tích thiết kế
│   ├── KT2/README.md               # Minh chứng lập trình backend & CSDL
│   ├── KT3/README.md               # Minh chứng kiểm thử & tối ưu giao diện
│   └── final/README.md             # Minh chứng tổng kết cuối kỳ
├── club.db                         # Cơ sở dữ liệu SQLite (tự động tạo)
├── .env.example                    # File mẫu cấu hình ở thư mục gốc
├── .gitignore                      # Cấu hình bỏ qua file nhị phân, venv, cache
└── README.md                       # Tài liệu hướng dẫn chính của dự án
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### Yêu cầu môi trường:
- **Python 3.9+** (đã kiểm thử ổn định trên Python 3.11, 3.12)
- Trình duyệt web hiện đại (Google Chrome, Microsoft Edge, Firefox)

### Bước 1: Di chuyển vào thư mục dự án
```bash
cd club-management-ai
```

### Bước 2: Tạo và kích hoạt môi trường ảo (Khuyến nghị)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt thư viện phụ thuộc
```bash
cd backend
pip install -r requirements.txt
```

### Bước 4: Cấu hình biến môi trường
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
> **Ghi chú về AI:** Nếu có OpenAI API Key, hãy điền `OPENAI_API_KEY=sk-...` vào file `.env`. Nếu **không có API Key**, hệ thống vẫn chạy 100% trơn tru nhờ cơ chế **Fallback Demo Mode thông minh** tích hợp sẵn!

### Bước 5: Nạp dữ liệu mẫu phong phú
```bash
python seed_data.py --reset
```

### Bước 6: Khởi chạy máy chủ Backend
```bash
python main.py
```
Hoặc dùng `uvicorn`:
```bash
uvicorn main:app --reload --port 8000
```

### Bước 7: Mở ứng dụng trên trình duyệt
👉 Mở trình duyệt web và truy cập địa chỉ: **http://localhost:8000** (tự động điều hướng đến trang Đăng nhập).

---

## 🔑 Tài Khoản Demo Để Chấm Điểm & Kiểm Thử

Hệ thống đã chuẩn bị sẵn các tài khoản demo đại diện cho 3 vai trò với dữ liệu nghiệp vụ đầy đủ:

| Vai trò | Tài khoản | Mật khẩu | Quyền hạn nổi bật |
|:---|:---|:---|:---|
| 👑 **Chủ nhiệm (Admin)** | `admin` | `admin123` | Toàn quyền quản trị hệ thống, CRUD thành viên, CRUD ban, duyệt hoạt động, xuất báo cáo, AI Assistant |
| ⭐ **Trưởng ban Truyền thông** | `truongban` | `truongban123` | Quản lý thành viên Ban Truyền thông, giao nhiệm vụ ban mình, điểm danh hoạt động, AI phân công |
| 💻 **Trưởng ban Kỹ thuật** | `cuong_tb` | `cuong123` | Quản lý thành viên Ban Kỹ thuật, giao nhiệm vụ ban mình, điểm danh hoạt động |
| 👤 **Thành viên** | `thanhvien` | `thanhvien123` | Xem/sửa thông tin cá nhân, cập nhật tiến độ công việc được giao, xem thông báo |

*Mẹo: Tại trang đăng nhập (`/login.html`), có sẵn các nút bấm một chạm để tự động điền tài khoản demo nhanh chóng.*

---

## 🛡️ Ma Trận Phân Quyền Vai Trò (Role-Based Access Control)

| Chức năng hệ thống | Chủ nhiệm (`chu_nhiem`) | Trưởng ban (`truong_ban`) | Thành viên (`thanh_vien`) | Khách / Sinh viên vãng lai |
|:---|:---:|:---:|:---:|:---:|
| **Quản lý Thành viên** | Toàn quyền CRUD | Xem/sửa thành viên ban mình | Chỉ xem & sửa thông tin cá nhân | ❌ Bị chặn (chuyển hướng Login) |
| **Quản lý Ban chuyên môn** | Toàn quyền CRUD | Xem danh sách ban | ❌ Không có quyền (Bị chặn) | ❌ Bị chặn |
| **Quản lý Hoạt động** | Toàn quyền CRUD | Xem chi tiết | Xem chi tiết | ❌ Bị chặn |
| **Điểm danh chuyên cần** | Toàn quyền chấm công | Chấm công cho hoạt động | ❌ Không có quyền (Bị chặn) | ❌ Bị chặn |
| **Quản lý Nhiệm vụ** | Toàn quyền tạo/sửa/xóa | Tạo/sửa/xóa cho ban mình | Cập nhật tiến độ & trạng thái task mình | ❌ Bị chặn |
| **Quản lý Thông báo** | Toàn quyền CRUD | Xem thông báo | Xem thông báo | ❌ Bị chặn |
| **AI Assistant (Nội bộ)** | Toàn bộ 3 công cụ AI | Dùng AI gợi ý phân công | ❌ Không có quyền | ❌ Bị chặn |
| **Xuất báo cáo CLB** | ✅ Toàn quyền | ✅ Có thể xem & in | ❌ Không có quyền | ❌ Bị chặn |
| **UniClub Assistant (Chatbot)** | ✅ Sử dụng | ✅ Sử dụng | ✅ Sử dụng | ✅ **Truy cập công khai 24/7** |

---

## 🤖 Trợ Lý Ảo Sinh Viên (UniClub Assistant)

Hệ thống tích hợp **UniClub Assistant** (`/chatbot.html`) — trợ lý ảo chuyên nghiệp dành cho sinh viên và thành viên:

1. **Truy xuất ngữ cảnh thực tế (RAG Context Retrieval):**
   - Tự động lấy dữ liệu thời gian thực từ CSDL: danh sách các ban, tên Trưởng ban, số lượng thành viên, hoạt động sắp tới và các sự kiện vừa hoàn thành để đưa ra câu trả lời chính xác 100%.
2. **Động cơ phân tích ý định (Smart Intent Inference Engine):**
   - Phân tầng ưu tiên chặt chẽ:
     - ✉️ **Xin nghỉ phép / Vắng mặt:** Hướng dẫn quy định báo trước 12 tiếng, trạng thái *Có phép* và cung cấp mẫu tin nhắn/email chuẩn chỉnh kèm nút **📋 Sao chép**.
     - ⭐ **Điểm rèn luyện & Điểm danh:** Giải đáp mức cộng 3 - 5 ĐRL, quy trình gửi danh sách sang Phòng CTSV.
     - 📅 **Lịch hoạt động sắp tới:** Cung cấp thông tin địa điểm, thời gian và nội dung chi tiết.
     - 📝 **Quy trình gia nhập & Onboarding:** Lộ trình 4 bước đơn giản, định hướng tân binh.
     - 💡 **Tư vấn chọn ban chuyên môn:** Phân tích thế mạnh theo đam mê (CNTT/Web/AI -> Ban Kỹ thuật, Design/TikTok -> Ban Truyền thông, MC/Hậu cần -> Ban Sự kiện, Đối tác/Ngoại ngữ -> Ban Đối ngoại, Nghiên cứu khoa học -> Ban Học thuật).
3. **Giao diện tương tác cao cấp:**
   - Hàng chip chủ đề nhanh (Quick Topic Buttons) bấm hỏi tức thì.
   - Thẻ gợi ý ban chuyên môn tương tác trực tiếp (`chat-club-card`), bấm vào để trò chuyện sâu hơn.
   - Hộp mã định dạng đẹp kèm nút copy 1 chạm.
   - Floating AI Launcher hiển thị ở góc dưới mọi trang giúp sinh viên truy cập trợ lý ảo bất kỳ lúc nào.

---

## 🧪 Kịch Bản Kiểm Thử Nhanh (5 Phút)

Vui lòng tham khảo kịch bản kiểm thử chi tiết từng bước tại:
👉 **[docs/demo_scenario.md](docs/demo_scenario.md)**

Tài liệu này hướng dẫn chi tiết các thao tác:
1. Đăng nhập với các vai trò khác nhau và kiểm tra bảo vệ phân quyền.
2. Thêm, sửa, xóa thành viên, ban, hoạt động, nhiệm vụ.
3. Thử nghiệm tìm kiếm thời gian thực, lọc theo ban/trạng thái và sắp xếp theo nhiều tiêu chí.
4. Xem Dashboard, tương tác 3 biểu đồ trực quan Chart.js và bấm nút Xuất Báo Cáo CLB.
5. Kiểm tra khả năng bắt lỗi: nhập sai email, nhập trùng email, vi phạm quyền hạn -> hệ thống không bị crash.

---

## 📚 API Documentation (Swagger UI)

FastAPI tự động sinh tài liệu API chuẩn OpenAPI:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 👥 Nhóm Tác Giả & Cam Kết Sử Dụng AI

Dự án được xây dựng với sự hỗ trợ của các công cụ AI hiện đại (GitHub Copilot, ChatGPT, Claude) tuân thủ quy chuẩn học thuật và đạo đức lập trình:
- Toàn bộ prompt và phản hồi được lưu vết tại [docs/ai_log.md](docs/ai_log.md).
- Toàn bộ mã nguồn đã được lập trình viên trực tiếp review, sửa đổi các lỗ hổng bảo mật, tối ưu truy vấn CSDL và hoàn thiện nghiệp vụ.
