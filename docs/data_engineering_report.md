# 📄 BÁO CÁO CHUYÊN ĐỀ PHẦN DATA ENGINEERING & KHO DỮ LIỆU (CO4031)

**Dự án**: Telecom Data Warehouse & Decision Support System (DSS)  
**Trường**: Đại học Bách Khoa TP.HCM (HCMUT) - Khoa Khoa học & Kỹ thuật Máy tính  
**Học phần**: Kho dữ liệu và Hệ hỗ trợ ra quyết định (CO4031)  
**Nhánh**: `feature/data-engineering` | **Hệ quản trị**: PostgreSQL 18

---

## 1. TỔNG QUAN VÀ MỤC TIÊU KIẾN TRÚC
Dự án triển khai mô hình Kho dữ liệu doanh nghiệp (EDW) 3 tầng theo trường phái W.H. Inmon và mô hình đa chiều Star Schema theo Ralph Kimball:
- **Tầng Nguồn (Bottom Tier)**: Gồm 2 nguồn dữ liệu không đồng nhất (CRM thông tin thuê bao và Geolocation chi nhánh) với 7,043 bản ghi.
- **Tầng Trung gian (Middle Tier)**: Vùng đệm Staging (`staging`) và Pipeline ETL Python tự động hóa (`etl/etl_pipeline.py`).
- **Tầng Kho dữ liệu & Trình bày (Top Tier)**: Kho dữ liệu Star Schema (`edw`) kết hợp B-Tree Indexes và 2 Data Marts (`edw.vw_bi_churn_analytics`, `edw.vw_ml_feature_store`).

---

## 2. BỐN ĐẶC TÍNH TIÊU CHUẨN INMON
1. **Subject-Oriented (Hướng chủ đề)**: Tổ chức xoay quanh hoạt động kinh doanh viễn thông trọng tâm (Thuê bao, Cước phí, Gói cước và Trạng thái Rời mạng Churn).
2. **Integrated (Tính tích hợp)**: Thống nhất khóa liên kết `customerID`, giải quyết triệt để 11 giá trị rỗng trong `TotalCharges`, chuẩn hóa các giá trị boolean và danh mục.
3. **Time-Variant (Gắn với thời gian)**: Tổ chức hạt dữ liệu dạng Periodic Snapshot gắn liền với khóa ngày `snapshot_date_key` (YYYYMMDD) trong bảng `dim_date`.
4. **Non-Volatile (Không biến động)**: Dữ liệu được nạp vào Fact Table theo chu kỳ định kỳ, đóng vai trò chỉ đọc phục vụ phân tích OLAP và huấn luyện mô hình ML.

---

## 3. MÔ HÌNH STAR SCHEMA & SURROGATE KEYS
- **Hạt dữ liệu (Grain)**: Chi tiết nguyên tử cho từng thuê bao khách hàng trong một kỳ cước.
- **Bảng Chiều**: 100% sử dụng Surrogate Keys tự tăng:
  - `edw.dim_customer` (`customer_key`)
  - `edw.dim_location` (`location_key`)
  - `edw.dim_service` (`service_key`)
  - `edw.dim_contract` (`contract_key`)
  - `edw.dim_date` (`date_key`)
- **Bảng Fact**: `edw.fact_customer_subscription_monthly` chứa đầy đủ Measures định lượng (`monthly_charges`, `total_charges`, `estimated_annual_charges`, `avg_charges_per_tenure`, `clv_proxy`) và biến phân loại `churn_flag`.

---

## 4. KẾT QUẢ KIỂM ĐỊNH CHẤT LƯỢNG (QUALITY GATES)
- ✅ Số dòng Fact nạp thành công: **7,043 / 7,043** bản ghi (100.0%).
- ✅ Khóa ngoại mồ côi (Orphan Foreign Keys): **0**.
- ✅ Giá trị NULL trong các cột độ đo cốt lõi: **0**.
- ✅ Tốc độ thực thi ETL toàn phần: **~1.5 giây**.
- ✅ Đã xuất bản giao thành công 2 file sạch tại `data/processed/` và tài liệu bàn giao `docs/data_marts_handoff.md`.
