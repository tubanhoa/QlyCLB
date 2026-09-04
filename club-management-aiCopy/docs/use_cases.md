# Tài liệu Use Case Hệ thống Quản lý Câu lạc bộ Sinh viên

> **Mục đích:** Mô tả hành vi người dùng và điều kiện nghiệm thu cho các phân hệ chính.  
> **Quy ước:** Các use case đánh dấu “mở rộng” mô tả nghiệp vụ mục tiêu, chưa nhất thiết đã có endpoint trong phiên bản hiện tại.

## 1. Danh sách tác nhân

| Tác nhân | Mô tả và quyền hạn chính |
|---|---|
| Admin trường | Quản lý danh sách CLB, tài khoản, vai trò và báo cáo ở cấp nhà trường. |
| Chủ nhiệm CLB | Quản trị toàn bộ một CLB: thành viên, ban, sự kiện, nhiệm vụ, thông báo và tài chính. |
| Trưởng ban | Quản lý thành viên, nhiệm vụ và hoạt động thuộc ban được phân công. |
| Thành viên CLB | Xem dữ liệu được cấp quyền, đăng ký sự kiện, xem điểm danh và cập nhật nhiệm vụ. |
| Sinh viên chưa vào CLB | Xem thông tin công khai, hỏi chatbot và gửi yêu cầu tham gia CLB. |
| Dịch vụ AI | Phân tích dữ liệu và sinh nội dung thông qua các tool được hệ thống cho phép; không tự quyết định nghiệp vụ tài chính. |
| Dịch vụ thông báo | Thành phần bên ngoài hoặc nội bộ chịu trách nhiệm phân phối thông báo theo lịch. |

## 2. Danh sách Use Case

### 2.1. Phân hệ Quản lý User

- UC-01: Đăng ký tài khoản.
- UC-02: Đăng nhập hệ thống.
- UC-03: Đăng xuất.
- UC-04: Cập nhật hồ sơ cá nhân.
- UC-05: Quản lý vai trò và phân quyền.
- UC-06: Khóa hoặc kích hoạt tài khoản.

### 2.2. Phân hệ Quản lý CLB và thành viên

- UC-07: Tạo thông tin CLB.
- UC-08: Cập nhật thông tin CLB.
- UC-09: Quản lý ban chuyên môn.
- UC-10: Xem danh sách thành viên.
- UC-11: Gửi yêu cầu tham gia CLB.
- UC-12: Duyệt yêu cầu tham gia CLB.
- UC-13: Thêm, sửa hoặc ngừng hoạt động thành viên.
- UC-14: Tra cứu mức độ gắn bó hội viên bằng AI.

### 2.3. Phân hệ Quản lý Sự kiện

- UC-15: Tạo sự kiện mới.
- UC-16: Cập nhật hoặc hủy sự kiện.
- UC-17: Đăng ký tham gia sự kiện.
- UC-18: Xem danh sách người đăng ký.
- UC-19: Điểm danh sự kiện.
- UC-20: Ghi nhận kết quả và phản hồi sự kiện.
- UC-21: Dự báo số người tham gia và hậu cần bằng AI.
- UC-22: Tạo và theo dõi nhiệm vụ của sự kiện.

### 2.4. Phân hệ Tài chính

- UC-23: Ghi nhận khoản thu.
- UC-24: Ghi nhận khoản chi.
- UC-25: Quản lý khoản phí thành viên.
- UC-26: Xem báo cáo thu chi và số dư.
- UC-27: Gửi nhắc phí cá nhân hóa.
- UC-28: Xuất báo cáo tài chính.

### 2.5. Phân hệ Truyền thông và AI

- UC-29: Tạo thông báo.
- UC-30: Lên lịch đăng thông báo.
- UC-31: Gửi và xem thông báo.
- UC-32: Nhắn tin trong phạm vi CLB.
- UC-33: Hỏi chatbot về thông tin CLB.
- UC-34: Sinh thông báo bằng AI.
- UC-35: Tóm tắt hoạt động bằng AI.
- UC-36: Gợi ý phân công nhiệm vụ bằng AI.
- UC-37: Xem lịch sử yêu cầu AI.

## 3. Đặc tả Use Case

### UC-11: Đăng ký tham gia CLB

**Tác nhân:** Sinh viên chưa vào CLB.

**Tiền điều kiện:**

- Sinh viên đã truy cập được trang đăng ký.
- CLB đang ở trạng thái tiếp nhận thành viên.
- Sinh viên chưa có yêu cầu đang chờ xử lý cho cùng CLB.

**Luồng cơ bản:**

1. Sinh viên chọn CLB muốn tham gia.
2. Hệ thống hiển thị thông tin CLB, các ban và điều kiện tham gia.
3. Sinh viên nhập họ tên, email, số điện thoại, kỹ năng và ban mong muốn.
4. Sinh viên gửi biểu mẫu.
5. Hệ thống kiểm tra dữ liệu bắt buộc và tính hợp lệ của email.
6. Hệ thống tạo yêu cầu tham gia với trạng thái `pending`.
7. Hệ thống thông báo gửi yêu cầu thành công.
8. Ban chủ nhiệm xem yêu cầu trong danh sách chờ duyệt.

**Luồng ngoại lệ:**

- 3a. Email đã tồn tại: hệ thống yêu cầu dùng email khác hoặc đăng nhập tài khoản hiện có.
- 5a. Thiếu dữ liệu hoặc dữ liệu không hợp lệ: hệ thống đánh dấu trường lỗi và không tạo yêu cầu.
- 5b. Đã có yêu cầu đang chờ: hệ thống không tạo bản ghi trùng.
- 6a. CLB đã đóng tuyển thành viên: hệ thống từ chối yêu cầu và hiển thị lý do.

**Hậu điều kiện:**

- Một yêu cầu tham gia mới ở trạng thái `pending` được lưu.
- Ban chủ nhiệm có thể duyệt hoặc từ chối yêu cầu.
- Sinh viên có thể tra cứu trạng thái yêu cầu.

### UC-15: Tạo sự kiện mới

**Tác nhân:** Chủ nhiệm CLB hoặc Trưởng ban được phân quyền.

**Tiền điều kiện:**

- Tác nhân đã đăng nhập.
- Tác nhân có quyền tạo sự kiện.
- Thông tin CLB và người phụ trách đã tồn tại.

**Luồng cơ bản:**

1. Tác nhân mở chức năng tạo sự kiện.
2. Tác nhân nhập tên, mô tả, thời gian, địa điểm, người phụ trách và trạng thái.
3. Tác nhân lưu sự kiện.
4. Hệ thống kiểm tra tên, thời gian và các trường bắt buộc.
5. Hệ thống tạo sự kiện ở trạng thái `upcoming`.
6. Hệ thống cho phép công bố sự kiện và nhận đăng ký.
7. Thành viên xem sự kiện trong danh sách hoạt động.

**Luồng ngoại lệ:**

- 2a. Thời gian không hợp lệ hoặc nằm trong quá khứ: hệ thống yêu cầu chỉnh sửa.
- 4a. Thiếu tên hoặc thông tin bắt buộc: hệ thống không lưu và hiển thị lỗi.
- 4b. Người phụ trách không thuộc CLB: hệ thống từ chối người phụ trách.
- 5a. Có sự kiện trùng thời gian/địa điểm: hệ thống cảnh báo để tác nhân xác nhận hoặc điều chỉnh.

**Hậu điều kiện:**

- Sự kiện được lưu trong cơ sở dữ liệu.
- Thành viên có thể xem hoặc đăng ký nếu sự kiện được công bố.
- Sự kiện có thể được liên kết với điểm danh và nhiệm vụ.

### UC-23: Thu/chi quỹ CLB

**Tác nhân:** Chủ nhiệm CLB hoặc người được ủy quyền tài chính.

**Tiền điều kiện:**

- Tác nhân đã đăng nhập và có quyền tài chính.
- Sổ quỹ của CLB đã được khởi tạo.
- Giao dịch có chứng từ hoặc thông tin xác nhận phù hợp.

**Luồng cơ bản:**

1. Tác nhân chọn loại giao dịch: `income` hoặc `expense`.
2. Tác nhân nhập nội dung, số tiền, ngày giao dịch và thành viên liên quan nếu có.
3. Hệ thống kiểm tra số tiền là số dương và nội dung không rỗng.
4. Tác nhân xác nhận lưu giao dịch.
5. Hệ thống tạo bản ghi giao dịch.
6. Hệ thống tính lại tổng thu, tổng chi và số dư.
7. Hệ thống ghi nhận người tạo và thời điểm thao tác.
8. Người có quyền xem giao dịch trong báo cáo tài chính.

**Luồng ngoại lệ:**

- 2a. Số tiền không hợp lệ hoặc nhỏ hơn/equal 0: hệ thống không cho lưu.
- 3a. Chi phí lớn hơn hạn mức hoặc số dư được phép: hệ thống cảnh báo và yêu cầu phê duyệt bổ sung.
- 4a. Tác nhân hủy xác nhận: giao dịch không được tạo.
- 5a. Lỗi lưu dữ liệu: hệ thống rollback và không thay đổi số dư.
- 8a. Người xem không có quyền tài chính: hệ thống ẩn chi tiết hoặc từ chối truy cập.

**Hậu điều kiện:**

- Giao dịch hợp lệ được lưu với loại thu/chi rõ ràng.
- Số dư hiển thị phản ánh đúng các giao dịch đã ghi nhận.
- Có thể truy vết giao dịch để đối soát và xuất báo cáo.

## 4. Quy tắc nghiệp vụ chung

- Chỉ người có quyền mới được duyệt thành viên, sửa sự kiện đã công bố hoặc ghi nhận giao dịch tài chính.
- Thành viên ngừng hoạt động không bị xóa vật lý nếu còn lịch sử điểm danh, nhiệm vụ hoặc tài chính.
- AI chỉ được sử dụng các tool đã khai báo và dữ liệu do hệ thống cung cấp.
- Khi không có dữ liệu tài chính, AI phải thông báo thiếu dữ liệu thay vì ước lượng.

## 5. Ánh xạ Use Case với API hiện tại

| Use Case | API/Module hiện tại | Trạng thái |
|---|---|---|
| UC-02: Đăng nhập | `POST /api/auth/login` | Đã triển khai |
| UC-10/UC-13: Quản lý thành viên | `/api/members` | Đã triển khai |
| UC-15/UC-16: Quản lý hoạt động | `/api/activities` | Đã triển khai |
| UC-19: Điểm danh | `/api/attendance` | Đã triển khai |
| UC-22: Quản lý nhiệm vụ | `/api/tasks` | Đã triển khai |
| UC-29/UC-31: Thông báo | `/api/notifications` | Đã triển khai |
| UC-33: Chatbot | `POST /api/ai/chat` | Đã triển khai |
| UC-34: Sinh thông báo AI | `POST /api/ai/notification` | Đã triển khai |
| UC-35: Tóm tắt hoạt động | `POST /api/ai/summarize` | Đã triển khai |
| UC-36: Gợi ý phân công | `POST /api/ai/assign-task` | Đã triển khai |
| UC-11/UC-17/UC-23 | Module đăng ký sự kiện và tài chính đầy đủ | Mở rộng |
