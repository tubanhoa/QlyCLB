# 📑 Nhật Ký Minh Chứng Sử Dụng AI Trong Phát Triển Dự Án (AI Development Log)

> **Dự án:** Hệ thống Quản lý Câu lạc bộ Sinh viên tích hợp AI  
> **Mục đích:** Tạo bằng chứng có thể kiểm tra về cách AI được dùng, phần nào đã được con người xác minh và phần nào còn cần hoàn thiện.

Tài liệu này ghi chép chi tiết, minh bạch và có hệ thống quá trình ứng dụng Trí tuệ Nhân tạo (AI) trong suốt vòng đời phân tích, thiết kế, lập trình, kiểm thử và tối ưu hóa hệ thống **Quản Lý Câu Lạc Bộ Sinh Viên Tích Hợp AI**.

---

## I. Mục Đích & Nguyên Tắc Đạo Đức Khi Sử Dụng AI

1. **Minh bạch (Transparency):** Ghi nhận rõ ràng công cụ AI được sử dụng, prompt đưa vào, kết quả phản hồi của AI và các đóng góp thực tế của lập trình viên.
2. **Kiểm soát & Tối ưu (Human-in-the-loop):** Mọi đoạn mã hoặc tài liệu do AI tạo ra đều bắt buộc phải được người phát triển trực tiếp đọc hiểu, kiểm tra bảo mật, tái cấu trúc (refactoring) và sửa lỗi logic trước khi tích hợp vào mã nguồn chính.
3. **Bảo mật dữ liệu (Data Privacy):** Tuyệt đối không cung cấp các khóa bí mật (Secret Key, API Key cá nhân), mật khẩu hoặc thông tin cá nhân nhạy cảm vào prompt của AI.

---

## II. Bảng Tổng Hợp Nhật Ký Prompt & Mức Độ Đóng Góp

> Không ghi API key, mật khẩu, token, dữ liệu cá nhân hoặc nội dung bí mật vào bảng log. Với mỗi dòng, cần lưu prompt ở mức tóm tắt và ghi rõ kết quả đã kiểm thử.

| STT | Giai đoạn / Chức năng | Công cụ AI | Prompt tóm tắt | Kết quả do AI sinh ra | Phần người lập trình đã kiểm tra, sửa đổi & tối ưu (Human-in-the-loop) |
|:---|:---|:---|:---|:---|:---|
| **1** | **Thiết kế CSDL & Models** | ChatGPT / Claude | *"Thiết kế mô hình dữ liệu quan hệ cho hệ thống quản lý CLB sinh viên gồm users, members, departments, activities, attendances, tasks, notifications bằng SQLAlchemy"* | Khung schema 8 bảng, các khóa chính, khóa ngoại ban đầu | - Bổ sung ràng buộc `unique=True` cho email, username, department name.<br>- Xử lý quan hệ 2 chiều `relationship(..., back_populates=...)`.<br>- Thêm cascade delete an toàn cho `activities -> attendances, tasks`. |
| **2** | **Xác thực JWT & Phân quyền RBAC** | GitHub Copilot | *"Viết module auth.py trong FastAPI sử dụng JWT token và dependency require_role để bảo vệ endpoint theo vai trò chu_nhiem, truong_ban, thanh_vien"* | Hàm tạo/giải mã token JWT, dependency kiểm tra vai trò | - Bổ sung thuật toán hash mật khẩu SHA-256 an toàn.<br>- Bổ sung bắt lỗi khi token hết hạn hoặc sai chữ ký (trả về 401 Unauthorized thay vì 500).<br>- Thêm kiểm tra quyền sở hữu dữ liệu (Trưởng ban chỉ xem ban mình, Thành viên chỉ xem bản thân). |
| **3** | **CRUD & Nghiệp vụ chính** | GitHub Copilot | *"Xây dựng các APIRouter FastAPI cho Members, Departments, Activities, Tasks, Attendance, Notifications kèm Pydantic schemas"* | Các hàm CRUD chuẩn RESTful API | - Sửa logic xóa ban: khi xóa ban thì chuyển `member.department_id = None` thay vì làm mất dữ liệu thành viên.<br>- Kiểm tra trùng lặp email trước khi thêm và trước khi sửa.<br>- Giới hạn các trường thành viên được phép cập nhật (chỉ được cập nhật phone, skills, availability). |
| **4** | **Tìm kiếm, Lọc & Sắp xếp** | Claude / Copilot | *"Thêm query parameters cho FastAPI để hỗ trợ tìm kiếm đa trường (name, email, phone), lọc trạng thái và sắp xếp động (sort_by, order)"* | Cú pháp query filter và order_by của SQLAlchemy | - Xây dựng cơ chế whitelist các cột được phép sắp xếp để chống SQL Injection.<br>- Kết hợp tìm kiếm không phân biệt hoa thường và tìm kiếm theo địa điểm hoạt động.<br>- Đồng bộ hóa giao diện frontend với các dropdown sắp xếp thời gian thực. |
| **5** | **Dashboard & Biểu đồ Chart.js** | ChatGPT | *"Tạo giao diện Dashboard hiển thị thẻ số liệu tổng quan và nhúng thư viện Chart.js vẽ 3 biểu đồ: thành viên theo ban, trạng thái nhiệm vụ, tỷ lệ điểm danh"* | Đoạn mã HTML/JS khởi tạo Chart.js cơ bản | - Chỉnh sửa bảng màu biểu đồ theo đúng chuẩn Dark Theme hiện đại (`#6366f1`, `#06b6d4`, `#10b981`, `#f59e0b`, `#ef4444`).<br>- Mở rộng API backend `/api/dashboard/stats` để tính toán chính xác dữ liệu gom nhóm (group by).<br>- Xây dựng tính năng "Xuất Báo Cáo CLB" kèm hỗ trợ chế độ in chuyên nghiệp (`window.print()`). |
| **6** | **Xử lý lỗi toàn cục (Global Exception Handlers)** | GitHub Copilot | *"Cách viết exception_handler trong FastAPI để xử lý RequestValidationError và SQLAlchemy IntegrityError thành thông điệp tiếng Việt thân thiện"* | Khung hàm `@app.exception_handler` | - Bóc tách lỗi Pydantic để lấy tên trường tiếng Việt và thông báo lỗi rõ ràng.<br>- Bắt lỗi SQLite constraint (`UNIQUE`, `FOREIGN KEY`) và trả về mã lỗi 400 có hướng dẫn thay vì làm server crash.<br>- Thêm client-side regex email và số điện thoại trước khi gửi API. |
| **7** | **AI Assistant & Chatbot UniClub** | OpenAI API & Copilot | *"Xây dựng trợ lý ảo thông minh cho sinh viên có khả năng trả lời về CLB, tư vấn ban chuyên môn, giải đáp điểm rèn luyện và sinh thông báo/phân công"* | Code API gọi OpenAI và chat completion | - Xây dựng cơ chế **RAG Context Retrieval (`build_club_context`)**: tự động truy vấn danh sách ban, hoạt động sắp tới, nhiệm vụ và thông báo thực tế từ CSDL để đưa vào ngữ cảnh AI.<br>- Xây dựng **Smart Inference Engine**: phân loại ý định học sinh theo thứ tự ưu tiên chặt chẽ (nghỉ phép/mẫu đơn -> điểm rèn luyện -> hoạt động sắp tới -> tuyển quân -> nhiệm vụ -> ban chuyên môn) giúp phản hồi tức thì cả khi offline.<br>- Thiết kế UI Chatbot hiện đại với các chip chủ đề nhanh, thẻ gợi ý ban tương tác trực tiếp và khối mã có nút sao chép (copy-to-clipboard).<br>- Tích hợp Floating AI Widget trên toàn bộ các trang để sinh viên truy cập trợ lý mọi lúc. |
| **8** | **Tài liệu & Kịch bản Chạy thử** | ChatGPT | *"Soạn kịch bản demo 10 bước tương ứng 10 tiêu chí đánh giá để giảng viên kiểm thử đồ án trong 5-10 phút"* | Bố cục kịch bản kiểm thử | - Bổ sung chính xác các tài khoản demo, thông tin đăng nhập, dữ liệu kiểm tra và kết quả kỳ vọng.<br>- Viết file `backend/seed_data.py` độc lập phục vụ việc reset dữ liệu mẫu tức thì. |

---

## III. Các Tình Huống Cụ Thể (Case Studies) Minh Chứng "Human-in-the-Loop"

### 📌 Tình huống 1: Phát hiện và xử lý lỗ hổng phân quyền (RBAC)
- **Mã do AI đề xuất ban đầu:**
  AI gợi ý router `tasks.py` cho phép người dùng gửi request cập nhật bất kỳ nhiệm vụ nào nếu đã đăng nhập (`Depends(get_current_user)`).
- **Phát hiện của sinh viên:**
  Thành viên thông thường (`thanh_vien`) có thể sửa đổi cả tên nhiệm vụ, người được giao và hạn chót deadline của người khác, gây sai lệch phân công.
- **Chỉnh sửa thủ công của sinh viên:**
  - Bổ sung kiểm tra logic: Nếu `role == 'thanh_vien'`, chỉ cho phép sửa nhiệm vụ được giao cho chính họ (`task.assigned_to == current_user.member_id`), và chỉ được phép cập nhật 2 trường `status` và `progress`.
  - Trên giao diện Frontend (`tasks.js`), tự động khóa (`disabled`) các ô nhập tên, mô tả, người phụ trách và deadline khi người dùng là thành viên.

### 📌 Tình huống 2: Sửa lỗi Crash Server do IntegrityError trong CSDL
- **Mã do AI đề xuất ban đầu:**
  Khi người dùng sửa email của thành viên thành một email đã thuộc về thành viên khác, câu lệnh `db.commit()` phát sinh ngoại lệ `sqlite3.IntegrityError: UNIQUE constraint failed: members.email` khiến FastAPI trả về mã lỗi HTTP 500 Internal Server Error và in traceback dài ra console.
- **Phát hiện của sinh viên:**
  Lỗi nhập trùng email là lỗi người dùng phổ biến, không được để sập hoặc trả về lỗi 500.
- **Chỉnh sửa thủ công của sinh viên:**
  - Thêm bước kiểm tra chủ động trong router:
    ```python
    if "email" in update_data and update_data["email"] != member.email:
        duplicate = db.query(Member).filter(Member.email == update_data["email"], Member.id != member_id).first()
        if duplicate:
            raise HTTPException(status_code=400, detail="Email này đã được sử dụng bởi thành viên khác")
    ```
  - Bổ sung Global Exception Handler cho `IntegrityError` trong `main.py` để luôn trả về phản hồi JSON 400 rõ ràng.

### 📌 Tình huống 3: Tối ưu cơ chế Fallback khi không có OpenAI API Key
- **Mã do AI đề xuất ban đầu:**
  Hàm gọi OpenAI trực tiếp báo lỗi kết nối `HTTPException 500` hoặc làm gián đoạn màn hình nếu biến môi trường `OPENAI_API_KEY` bị trống.
- **Chỉnh sửa thủ công của sinh viên:**
  - Viết hàm `_generate_demo_response(prompt)` nội bộ.
  - Khi không có API Key, hệ thống tự động phân tích từ khóa của yêu cầu (thông báo, tóm tắt, phân công) và trả về nội dung mẫu định dạng Markdown chuyên nghiệp. Người dùng và ban giám khảo vẫn trải nghiệm đầy đủ luồng nghiệp vụ mà không bị lỗi.

### 📌 Tình huống 4: Xử lý trùng lặp ý định và trích xuất dữ liệu thực tế cho Trợ lý ảo UniClub
- **Mã do AI đề xuất ban đầu:**
  Bộ lọc từ khóa ban đầu kiểm tra từ `"sự kiện"` hoặc `"workshop"` trước và lập tức trả về thông tin của Ban Sự kiện hoặc Ban Học thuật, ngay cả khi sinh viên đang hỏi xin nghỉ phép vì trùng lịch thi hoặc hỏi về lịch trình sự kiện sắp tới.
- **Phát hiện của sinh viên:**
  Thứ tự ưu tiên trong chuỗi điều kiện nếu phân loại thiếu phân tầng sẽ khiến các câu hỏi nghiệp vụ đặc thù (nghỉ phép, mẫu đơn, điểm rèn luyện) bị nhận diện nhầm sang ban chuyên môn.
- **Chỉnh sửa thủ công của sinh viên:**
  - Thiết kế lại cấu trúc phân tầng ưu tiên (Intent Hierarchy): Ý định hành động đặc thù (Nghỉ phép -> Điểm rèn luyện -> Lịch hoạt động sắp tới -> Tuyển quân) được ưu tiên xử lý trước ý định hỏi chung về ban.
  - Tích hợp dữ liệu thời gian thực từ CSDL: Truy vấn trực tiếp các bảng `departments`, `activities`, `tasks` và `notifications` để đưa vào câu trả lời, đảm bảo tên Trưởng ban, thời gian tổ chức sự kiện thực tế luôn chính xác 100% theo dữ liệu trong hệ thống.
  - Bổ sung giao diện thẻ tương tác và tính năng sao chép mẫu tin nhắn trực tiếp giúp sinh viên sử dụng thuận tiện.

---

## IV. Kết Luận

Việc ứng dụng AI đã giúp đẩy nhanh tiến độ viết mã nguồn khung, thiết kế giao diện và xây dựng các tài liệu ban đầu. Tuy nhiên, **chất lượng, độ tin cậy, tính bảo mật và tính đúng đắn nghiệp vụ** của toàn bộ hệ thống hoàn toàn được đảm bảo thông qua quá trình đánh giá, rà soát mã nguồn và kiểm thử nghiêm ngặt của người phát triển.

