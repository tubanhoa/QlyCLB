# Tài liệu Yêu cầu Hệ thống Quản lý Câu lạc bộ Sinh viên

> **Phiên bản:** 1.0  
> **Phạm vi tài liệu:** Backend FastAPI, frontend HTML/JavaScript và cơ sở dữ liệu SQLite hiện tại.  
> **Trạng thái:** Baseline yêu cầu và định hướng mở rộng.

## Cách đọc tài liệu

- **Đã triển khai:** Có mã nguồn hoặc endpoint tương ứng trong phiên bản hiện tại.
- **Đề xuất:** Yêu cầu cần bổ sung để hoàn thiện hệ thống nhiều CLB hoặc nghiệp vụ nâng cao.
- Các yêu cầu AI phải được đánh giá cùng dữ liệu nguồn; AI không thay thế phê duyệt của người có thẩm quyền.

## 1. Giới thiệu tổng quan

### 1.1. Mục đích

Hệ thống cung cấp một nền tảng tập trung để nhà trường và Ban chủ nhiệm quản lý hoạt động của các câu lạc bộ sinh viên. Hệ thống giúp số hóa việc quản lý thành viên, sự kiện, điểm danh, nhiệm vụ, tài chính, thông báo và hỗ trợ AI.

Mục tiêu chính:

- Giảm thao tác thủ công và dữ liệu phân tán.
- Tăng tính minh bạch trong quản lý thành viên, hoạt động và quỹ CLB.
- Cải thiện khả năng giao tiếp giữa Ban chủ nhiệm và hội viên.
- Cung cấp dữ liệu có cấu trúc để thống kê, báo cáo và hỗ trợ ra quyết định.
- Hỗ trợ AI trong sinh thông báo, tóm tắt hoạt động, phân công nhiệm vụ và tư vấn thông tin CLB.

### 1.2. Phạm vi

Hệ thống bao gồm:

- Quản lý tài khoản, vai trò và phân quyền.
- Quản lý thông tin CLB, ban chuyên môn và thành viên.
- Lập kế hoạch, quản lý và điểm danh sự kiện/hoạt động.
- Quản lý nhiệm vụ phát sinh từ hoạt động.
- Theo dõi thu, chi và tình trạng đóng quỹ.
- Gửi thông báo và hỗ trợ trao đổi thông tin.
- Cung cấp chatbot và các chức năng AI có kiểm soát.

Ngoài phạm vi phiên bản hiện tại:

- Tích hợp cổng thanh toán trực tuyến.
- Đồng bộ tự động với hệ thống quản lý sinh viên của nhà trường.
- Gửi SMS hoặc email qua nhà cung cấp bên thứ ba.
- Ứng dụng native cho iOS/Android.

## 2. Đối tượng người dùng

### 2.1. Admin trường

- Quản lý danh sách CLB trong phạm vi nhà trường.
- Quản lý tài khoản và vai trò cấp hệ thống.
- Xem báo cáo tổng hợp về thành viên, hoạt động và tài chính.
- Kiểm tra nhật ký thao tác và xử lý các yêu cầu quản trị.

### 2.2. Ban chủ nhiệm CLB

- Quản lý thông tin CLB và ban chuyên môn.
- Duyệt, thêm, cập nhật hoặc ngừng hoạt động thành viên.
- Tạo sự kiện, phân công nhiệm vụ và theo dõi tiến độ.
- Ghi nhận điểm danh.
- Quản lý thông báo, thu chi và quỹ CLB.
- Sử dụng AI để sinh nội dung, tóm tắt và phân tích dữ liệu.

### 2.3. Thành viên CLB

- Xem thông tin CLB, ban chuyên môn và hoạt động.
- Đăng ký hoặc xác nhận tham gia sự kiện.
- Xem lịch sử điểm danh và nhiệm vụ được giao.
- Nhận thông báo và cập nhật tiến độ nhiệm vụ.
- Xem thông tin tài chính được công khai theo quyền hạn.

### 2.4. Sinh viên chưa vào CLB

- Xem thông tin giới thiệu CLB và các ban.
- Xem hoạt động sắp tới và điều kiện tham gia.
- Gửi yêu cầu đăng ký tham gia.
- Sử dụng chatbot để hỏi thông tin chung về CLB.

## 3. Yêu cầu chức năng

### FR-01. Quản lý tài khoản và phân quyền

**Trạng thái hiện tại:** Đã triển khai một phần qua `auth.py`, JWT và các vai trò `chu_nhiem`, `truong_ban`, `thanh_vien`. Vai trò Admin trường và cơ chế phân quyền theo nhiều CLB là đề xuất mở rộng.

- Người dùng đăng nhập và đăng xuất hệ thống.
- Hệ thống phân quyền tối thiểu theo các vai trò: Admin trường, Chủ nhiệm, Trưởng ban và Thành viên.
- Mật khẩu phải được lưu dưới dạng băm, không lưu dạng văn bản thuần.
- Người dùng chỉ được truy cập dữ liệu và thao tác phù hợp với vai trò.

### FR-02. Quản lý thông tin CLB

- Tạo, xem, cập nhật và ngừng hoạt động một CLB.
- Quản lý tên, mô tả, thông tin liên hệ, lĩnh vực hoạt động và trạng thái CLB.
- Quản lý các ban chuyên môn trực thuộc.
- Gán trưởng ban và theo dõi số lượng thành viên theo ban.

### FR-03. Quản lý thành viên

- Sinh viên gửi yêu cầu tham gia CLB.
- Ban chủ nhiệm xem danh sách yêu cầu chờ duyệt.
- Người có quyền duyệt, từ chối hoặc yêu cầu bổ sung thông tin.
- Thêm thành viên trực tiếp, cập nhật hồ sơ hoặc chuyển trạng thái hoạt động.
- Xóa mềm/ngừng hoạt động thành viên nhưng vẫn giữ lịch sử liên quan.
- Tìm kiếm và lọc theo tên, email, ban và trạng thái.
- Lưu thông tin liên hệ, ngày tham gia, kỹ năng và lịch rảnh.

### FR-04. Quản lý sự kiện và hoạt động

**Trạng thái hiện tại:** Đã triển khai qua thực thể `activities` và các API hoạt động; đăng ký sự kiện độc lập là đề xuất mở rộng.

- Tạo, cập nhật, hủy và xem chi tiết sự kiện.
- Lưu tên, mô tả, thời gian, địa điểm, người phụ trách và trạng thái.
- Công bố sự kiện để thành viên đăng ký tham gia.
- Theo dõi danh sách đăng ký và số lượng người tham dự.
- Ghi nhận điểm danh với các trạng thái có mặt, vắng hoặc có phép.
- Lưu ghi chú, kết quả và phản hồi sau sự kiện.
- Liên kết nhiệm vụ với từng hoạt động.

### FR-05. Quản lý nhiệm vụ

- Tạo nhiệm vụ cho một hoạt động hoặc nhiệm vụ độc lập.
- Giao nhiệm vụ cho thành viên và đặt hạn hoàn thành.
- Theo dõi trạng thái, mức độ ưu tiên và phần trăm tiến độ.
- Cho phép người được giao cập nhật tiến độ.
- Cảnh báo nhiệm vụ quá hạn.

### FR-06. Quản lý tài chính/quỹ CLB

**Trạng thái hiện tại:** Đã có model `financial_transactions` và `member_fees`, đồng thời AI có quy tắc không bịa số liệu. Giao diện/API CRUD tài chính và báo cáo chính thức cần hoàn thiện.

- Ghi nhận các khoản thu và chi.
- Lưu nội dung, số tiền, loại giao dịch, thời gian và thành viên liên quan nếu có.
- Theo dõi số dư quỹ theo công thức: tổng thu trừ tổng chi.
- Quản lý khoản phí theo từng thành viên với trạng thái đã đóng/chưa đóng.
- Sinh báo cáo tài chính theo khoảng thời gian.
- Chỉ người có quyền mới được tạo hoặc sửa giao dịch tài chính.
- Không cho phép AI tự suy đoán số liệu khi không có dữ liệu nguồn.

### FR-07. Thông báo và nhắn tin

**Trạng thái hiện tại:** Thông báo CRUD đã có; `scheduled_posts` là nền tảng cho lịch đăng. Nhắn tin nội bộ và bộ phân phối email/SMS là đề xuất.

- Ban chủ nhiệm tạo, sửa, xóa và đăng thông báo.
- Thành viên xem danh sách thông báo và trạng thái đã đọc.
- Hỗ trợ lưu nội dung đăng theo lịch.
- Hỗ trợ gửi tin nhắn hoặc trao đổi trong phạm vi CLB theo quyền hạn.
- Có thể mở rộng tích hợp email, SMS hoặc kênh mạng xã hội.

### FR-08. Chức năng AI

**API hiện tại:**

- `POST /api/ai/chat`: chatbot công khai, trả `answer`, `suggestedClubs` và `followUpQuestions`.
- `POST /api/ai/notification`: sinh nội dung thông báo, yêu cầu quyền Chủ nhiệm.
- `POST /api/ai/summarize`: tóm tắt hoạt động, yêu cầu quyền Chủ nhiệm.
- `POST /api/ai/assign-task`: gợi ý phân công, dành cho Chủ nhiệm/Trưởng ban.
- `GET /api/ai/history`: xem lịch sử yêu cầu AI, dành cho Chủ nhiệm.

**Trạng thái hiện tại:** Chatbot dùng context thời gian thực từ database và có fallback nội bộ khi thiếu API key hoặc OpenAI gặp lỗi. Các tool tài chính/lên lịch cần được hoàn thiện thành endpoint và job phân phối thực tế trước khi công bố production.

- Chatbot trả lời câu hỏi liên quan đến CLB dựa trên dữ liệu hệ thống và FAQ.
- Gọi tool `get_member_stats` để phân tích mức độ gắn bó hội viên.
- Gọi tool `schedule_post` khi người dùng yêu cầu lên lịch thông báo.
- Gọi tool `get_historical_events` để hỗ trợ dự báo số người và hậu cần.
- Gọi tool `get_financial_report` khi truy vấn quỹ.
- Gọi tool `send_fee_reminder` hoặc `generate_financial_reminder` khi nhắc phí.
- Ghi lịch sử yêu cầu AI, đầu vào và kết quả trả về.
- Chỉ người dùng được cấp quyền mới được gọi các chức năng AI quản trị.

## 4. Yêu cầu phi chức năng

### NFR-01. Bảo mật

- Tất cả endpoint quản trị phải yêu cầu xác thực và kiểm tra quyền.
- Mật khẩu được băm bằng thuật toán phù hợp.
- Khóa API và thông tin nhạy cảm chỉ được lưu qua biến môi trường.
- Dữ liệu đầu vào phải được kiểm tra và chuẩn hóa.
- Chống truy cập trái phép, SQL injection, XSS và lộ thông tin cá nhân.
- Nhật ký không được ghi mật khẩu, token hoặc khóa API.
- Dữ liệu tài chính và dữ liệu cá nhân phải giới hạn theo vai trò.

### NFR-02. Hiệu năng

- API thông thường phản hồi trong tối đa 2 giây ở tải bình thường.
- Danh sách lớn phải hỗ trợ phân trang, lọc và sắp xếp.
- Các lời gọi AI phải có timeout, xử lý lỗi và cơ chế phản hồi dự phòng.
- Truy vấn thường xuyên phải có chỉ mục phù hợp.

### NFR-03. Tính khả dụng

- Giao diện hoạt động trên trình duyệt hiện đại ở máy tính và thiết bị di động.
- Thông báo lỗi phải rõ ràng và không làm mất dữ liệu người dùng đã nhập.
- Hệ thống vẫn cung cấp chức năng cơ bản khi AI hoặc dịch vụ bên ngoài tạm thời không khả dụng.
- Có tài liệu hướng dẫn chạy, cấu hình và sử dụng hệ thống.

### NFR-04. Khả năng mở rộng và bảo trì

- Backend, frontend và tầng dữ liệu được tổ chức tách biệt.
- Có thể thay SQLite bằng PostgreSQL mà không thay đổi nghiệp vụ cốt lõi.
- Có thể bổ sung CLB, vai trò, loại sự kiện và kênh thông báo mới.
- Tool AI có schema rõ ràng và có thể thêm tool mà không phá vỡ API hiện có.
- Có log, kiểm thử tự động và quy trình migration cho thay đổi schema.

## 5. Tiêu chí nghiệm thu tổng quát

- Người dùng đúng vai trò có thể hoàn thành các nghiệp vụ được cấp quyền.
- Dữ liệu sau mỗi thao tác được lưu và hiển thị nhất quán.
- Người dùng không có quyền bị từ chối với mã lỗi phù hợp.
- Báo cáo tài chính khớp với dữ liệu giao dịch.
- Điểm danh và lịch sử thành viên không bị mất khi thành viên ngừng hoạt động.
- AI chỉ sử dụng dữ liệu được cung cấp và thông báo rõ khi thiếu dữ liệu.
