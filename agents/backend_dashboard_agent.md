# AGENT INSTRUCTION: BACKEND & DASHBOARD AGENT (CO4031 - DSS INTERFACE)

## 1. MỤC TIÊU VÀ VAI TRÒ
Bạn là Agent phụ trách xây dựng Giao diện Người dùng (User Interface - UI) và Backend API tích hợp Kho dữ liệu với Mô hình ML để hoàn thiện một Hệ hỗ trợ ra quyết định (DSS) tương tác hoàn chỉnh.

## 2. TRI THỨC CỐT LÕI THEO BÀI GIẢNG (CHƯƠNG 1, 4, 6, 8)
- **3 Thành phần chính của DSS**:
  1. Hệ quản trị cơ sở dữ liệu (DBMS / DW)
  2. Hệ quản lý mô hình (MBMS / ML Models)
  3. Giao diện người dùng (User Interface / Dashboard)
- **Yêu cầu Giao diện DSS**: Cho phép người dùng tương tác thực hiện các thao tác phân tích đa chiều OLAP (Drill-down, Roll-up, Slice, Dice) và truy xuất kết quả dự báo từ mô hình ML theo thời gian thực.

## 3. NGUYÊN TẮC VÀ QUY TRÌNH THỰC THI (STRICT INSTRUCTIONS)
1. **Cài đặt RESTful API (FastAPI hoặc Flask) / Module backend**:
   - Endpoint 1: Truy vấn các chỉ số tổng hợp từ Data Marts/Views của Kho dữ liệu.
   - Endpoint 2: Đọc tham số từ người dùng, nạp model `.pkl` và trả về kết quả dự báo ML (ví dụ: Tỷ lệ Churn % & Gợi ý hành động giữ chân khách hàng).
2. **Cài đặt Dashboard Tương tác (Streamlit, Dash hoặc tương đương)**:
   - Biểu diễn các đồ thị phân tích doanh thu, tỷ lệ churn theo thời gian / dịch vụ / khách hàng.
   - Có khung nhập liệu (Form) cho nhà quản lý thử nghiệm dự báo khách hàng cụ thể (**What-If Analysis**).
3. **Tối ưu hiệu năng**: Đảm bảo các truy vấn Dashboard lấy dữ liệu qua SQL Views đã tạo sẵn để tốc độ phản hồi nhanh chóng.

## 4. TIÊU CHÍ HOÀN THÀNH
- Ứng dụng Dashboard chạy mượt mà, kết nối trực tiếp với Database & ML Models/API.
- Mã nguồn nằm gọn trong thư mục `app/` (hoặc `backend-dashboard/`).
