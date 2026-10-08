# 🤝 TÀI LIỆU BÀN GIAO DATA MARTS & FEATURE STORE (TASK 5 HANDOFF)

**Người bàn giao**: Data Engineer Agent
**Đối tượng nhận bàn giao**: ML Engineer Agent & Backend/Dashboard Agent
**Database**: PostgreSQL (`telecom_dw`) & Vùng lưu trữ: `data/processed/`

---

## 1. Dữ liệu bàn giao cho ML Engineer Agent (MBMS)

- **SQL View trực tiếp**: `edw.vw_ml_feature_store` (trong PostgreSQL `telecom_dw`)
- **File CSV tương đương**: [`data/processed/telecom_ml_feature_store.csv`](file:///C:/Users/Admin/Desktop/Education/Year 4/HK261/Data Warehouse/telecom/co4031-telecom-dss/data/processed/telecom_ml_feature_store.csv)
- **Đặc trưng đã được chuẩn hóa sẵn**:
  - 100% không còn ô rỗng / khoảng trắng.
  - Cột nhị phân đã chuyển thành `True/False`.
  - Biến mục tiêu: `churn_flag` (0: Ở lại, 1: Rời mạng).
  - Các biến số liên tục phục vụ Clustering & CLV: `tenure_months`, `monthly_charges`, `total_charges`, `avg_charges_per_tenure`, `clv_proxy`, `total_active_addons`.

---

## 2. Dữ liệu bàn giao cho Backend & Dashboard Agent (UI / DSS)

- **SQL View trực tiếp**: `edw.vw_bi_churn_analytics` (trong PostgreSQL `telecom_dw`)
- **File CSV tương đương**: [`data/processed/telecom_bi_churn_analytics.csv`](file:///C:/Users/Admin/Desktop/Education/Year 4/HK261/Data Warehouse/telecom/co4031-telecom-dss/data/processed/telecom_bi_churn_analytics.csv)
- **Hỗ trợ thao tác OLAP**:
  - *Drill-down / Roll-up*: Theo Địa lý (`region` -> `state` -> `city` -> `zip_code` -> Tọa độ GPS `latitude`/`longitude`).
  - *Slice & Dice*: Theo Hợp đồng (`contract_type`), Hình thức thanh toán (`payment_category`), Gói dịch vụ (`internet_service_type`).

✅ **Bàn giao thành công**: 100% dữ liệu đã sạch, đạt chuẩn Star Schema và sẵn sàng để Agent ML và Dashboard tiếp quản!
