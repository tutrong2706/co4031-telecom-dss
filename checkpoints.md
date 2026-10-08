# 📌 Tiến độ Dự án CO4031 - Data Warehouse & Telecom DSS

Nhánh làm việc: `feature/data-engineering`  
Repository: `https://github.com/tutrong2706/co4031-telecom-dss`

---

## 📋 Danh sách Task & Checkpoints

### 🔍 Task 1: Khảo sát & Khám phá dữ liệu thô (Data Profiling)
- [x] 1.1 Thu thập và tổng hợp các nguồn dữ liệu thô (Telco Churn, Usage, Customer Demographics, Billing, Geolocation) vào thư mục `data/raw/`.
- [x] 1.2 Thực hiện EDA & Data Profiling (Kiểm tra schema, kiểu dữ liệu, phân bố, missing values, anomalies, duplicates qua `scripts/data_profiling.py`).
- [x] 1.3 Đánh giá chất lượng dữ liệu (Data Quality Assessment) và chọn dataset / data source phù hợp với bài toán DSS & ML.
- [x] 1.4 Viết tài liệu Data Dictionary / Metadata sơ bộ cho các tập dữ liệu thô (`docs/data_profiling_report.md` & `docs/data_dictionary.md`).

---

### 📐 Task 2: Thiết kế Mô hình Đa chiều (Dimensional Modeling & Star Schema)
- [x] 2.1 Xác định các Business Process & Bus Matrix (Billing, Subscriptions, Customer Calls/Usage, Churn events).
- [x] 2.2 Xác định Grain (độ mịn) của các bảng Fact (Atomic Customer Periodic Snapshot).
- [x] 2.3 Thiết kế các bảng Chiều (Dimension Tables): `dim_customer`, `dim_contract`, `dim_service`, `dim_location`, `dim_date` (100% áp dụng Surrogate Keys tự tăng).
- [x] 2.4 Thiết kế các bảng Sự kiện (Fact Tables): `fact_customer_subscription_monthly` với đầy đủ Additive, Derived Measures & Churn target.
- [x] 2.5 Vẽ sơ đồ Star Schema ERD dạng Mermaid & đặc tả chi tiết lưu tại `docs/dimensional_modeling_design.md`.

---

### 🗄️ Task 3: Cài đặt Cơ sở dữ liệu Kho dữ liệu (DDL Implementation)
- [x] 3.1 Viết script DDL tạo Staging Schema / Tables (`sql/ddl/01_staging_schema.sql`).
- [x] 3.2 Viết script DDL tạo Data Warehouse Star Schema (`sql/ddl/02_dw_star_schema.sql` - 100% Surrogate Keys, PKs, FKs, Constraints).
- [x] 3.3 Thiết lập kết nối cơ sở dữ liệu (PostgreSQL 18) và khởi tạo database `telecom_dw`, bảng Staging, bảng EDW, Indexes & Views thành công.

---

### ⚙️ Task 4: Xây dựng Quy trình tự động ETL (Extract, Transform, Load)
- [x] 4.1 **Extract**: Viết module đọc dữ liệu từ các nguồn CSV vào Staging (`etl/etl_pipeline.py`).
- [x] 4.2 **Transform**:
  - Làm sạch dữ liệu: xử lý ô trống `TotalCharges`, chuẩn hóa boolean cho `is_senior_citizen` và các cờ dịch vụ.
  - Xử lý business logic: tạo surrogate keys, phân đoạn `tenure_group`, phân loại thanh toán, tính toán derived metrics (`estimated_annual_charges`, `avg_charges_per_tenure`, `clv_proxy`).
- [x] 4.3 **Load**: Nạp dữ liệu vào Staging -> Nạp vào Dimension Tables (`dim_date`, `dim_customer`, `dim_location`, `dim_service`, `dim_contract`) -> Tra cứu khóa ngoại và nạp vào `fact_customer_subscription_monthly` (100% Referential Integrity).
- [x] 4.4 Tích hợp Logging, Error Handling và Data Quality Checks (Quality Gates đạt chuẩn 7,043 dòng, 0 orphan FKs).

---

### 📊 Task 5: Xuất Data Marts & Views bàn giao cho thành viên ML và Dashboard
- [x] 5.1 Thiết kế và tạo Views / Data Marts phục vụ BI Dashboard (`edw.vw_bi_churn_analytics`).
- [x] 5.2 Chuẩn bị Feature Store / View phục vụ ML Churn Prediction (`edw.vw_ml_feature_store`).
- [x] 5.3 Chuẩn bị Feature Store / View phục vụ ML Customer Segmentation / CLV.
- [x] 5.4 Xuất dữ liệu sạch (`data/processed/telecom_bi_churn_analytics.csv`, `data/processed/telecom_ml_feature_store.csv`) và tài liệu bàn giao tại `docs/data_marts_handoff.md`.

---

### 📝 Task 6: Quản lý Metadata, Git & Viết Báo cáo chuyên đề
- [x] 6.1 Quản lý phiên bản mã nguồn, commit rõ ràng theo Git flow trên nhánh `feature/data-engineering`.
- [x] 6.2 Hoàn thiện Data Lineage & Metadata Catalog tại `docs/data_lineage_and_metadata.md`.
- [x] 6.3 Viết báo cáo chuyên đề phần Data Engineering tại `docs/data_engineering_report.md`.
- [ ] 6.4 Tạo Pull Request merge vào `dev` / `main` sau khi nhóm review.

---

*Cập nhật lần cuối: 2026-10-08 | Hoàn tất Phase 1 (Data Engineering) 100%*
