# 🎓 Hệ Thống Quản Lý Câu Lạc Bộ Sinh Viên Có Tích Hợp AI

## Mô tả

Website quản lý câu lạc bộ sinh viên với đầy đủ chức năng:
- Quản lý thành viên, ban chuyên môn, hoạt động
- Điểm danh, quản lý nhiệm vụ, thông báo
- Tích hợp AI: sinh thông báo, tóm tắt hoạt động, gợi ý phân công

## Công nghệ

| Thành phần | Công nghệ |
|------------|-----------|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Frontend | HTML5, CSS3, JavaScript, Fetch API |
| Database | SQLite |
| AI | OpenAI API |

## Cấu trúc Project

```
club-management-ai/
├── backend/
│   ├── main.py              # Entry point
│   ├── database.py          # Database config
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication
│   ├── routers/             # API endpoints
│   │   ├── auth.py
│   │   ├── members.py
│   │   ├── departments.py
│   │   ├── activities.py
│   │   ├── attendance.py
│   │   ├── tasks.py
│   │   ├── notifications.py
│   │   └── ai.py
│   ├── services/
│   │   └── ai_service.py    # OpenAI integration
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── login.html
│   ├── dashboard.html
│   ├── members.html
│   ├── departments.html
│   ├── activities.html
│   ├── attendance.html
│   ├── tasks.html
│   ├── notifications.html
│   ├── ai.html
│   ├── css/style.css
│   └── js/
│       ├── auth.js
│       ├── members.js
│       ├── departments.js
│       ├── activities.js
│       ├── attendance.js
│       ├── tasks.js
│       ├── notifications.js
│       └── ai.js
├── club.db (tự động tạo)
└── README.md
```

## Hướng dẫn chạy

### Bước 1: Clone project
```bash
cd club-management-ai
```

### Bước 2: Tạo môi trường ảo (khuyến khích)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### Bước 3: Cài đặt thư viện
```bash
cd backend
pip install -r requirements.txt
```

### Bước 4: Cấu hình .env
```bash
# Sao chép file .env.example thành .env
copy .env.example .env       # Windows
# cp .env.example .env       # Mac/Linux
```

Mở file `.env` và thêm OpenAI API Key (nếu muốn dùng AI thực tế):
```
OPENAI_API_KEY=sk-your-key-here
```
> **Lưu ý:** Nếu không có API Key, hệ thống vẫn chạy bình thường. Chức năng AI sẽ trả về kết quả demo.

### Bước 5: Chạy Backend
```bash
cd backend
python main.py
```
Hoặc:
```bash
uvicorn main:app --reload --port 8000
```

### Bước 6: Truy cập website
Mở trình duyệt: **http://localhost:8000**

## Tài khoản demo

| Vai trò | Tài khoản | Mật khẩu |
|---------|-----------|-----------|
| 👑 Chủ nhiệm | admin | admin123 |
| ⭐ Trưởng ban | truongban | truongban123 |
| 👤 Thành viên | thanhvien | thanhvien123 |

## Chức năng chính

### 1. Quản lý thành viên
- Thêm, sửa, xóa thành viên
- Tìm kiếm, lọc theo ban
- Xem chi tiết, kỹ năng, lịch rảnh

### 2. Quản lý ban chuyên môn
- Tạo, sửa, xóa ban
- Phân thành viên, chọn trưởng ban

### 3. Quản lý hoạt động
- CRUD hoạt động
- Tìm kiếm, lọc theo trạng thái

### 4. Điểm danh
- Chọn hoạt động, điểm danh hàng loạt
- Thống kê tỷ lệ tham gia

### 5. Quản lý nhiệm vụ
- Tạo, phân công nhiệm vụ
- Theo dõi tiến độ, deadline
- Lọc theo trạng thái, ưu tiên

### 6. Thông báo
- Tạo, sửa, xóa thông báo
- Sinh thông báo bằng AI

### 7. AI Assistant
- **Sinh thông báo**: Nhập thông tin → AI viết thông báo
- **Tóm tắt hoạt động**: AI phân tích kết quả hoạt động
- **Gợi ý phân công**: AI đề xuất phân công dựa trên kỹ năng

## Phân quyền

| Chức năng | Chủ nhiệm | Trưởng ban | Thành viên |
|-----------|:---------:|:---------:|:---------:|
| Quản lý thành viên | ✅ Full | 👁️ Ban mình | 👁️ Cá nhân |
| Quản lý ban | ✅ | ❌ | ❌ |
| Quản lý hoạt động | ✅ | 👁️ | 👁️ |
| Điểm danh | ✅ | ✅ | ❌ |
| Nhiệm vụ | ✅ Full | ✅ Ban mình | 📝 Cập nhật |
| Thông báo | ✅ Full | 👁️ | 👁️ |
| AI | ✅ Full | 📋 Phân công | ❌ |

## API Documentation

Truy cập Swagger UI: **http://localhost:8000/docs**

## Thành viên nhóm

- [Tên thành viên 1]
- [Tên thành viên 2]
- ...

## License

Đồ án môn học - Sử dụng cho mục đích học tập.
