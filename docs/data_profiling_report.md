# BÁO CÁO KHẢO SÁT & ĐÁNH GIÁ CHẤT LƯỢNG DỮ LIỆU (DATA PROFILING REPORT)

**Dự án**: CO4031 - Telecom Data Warehouse & DSS
**Ngày thực hiện**: 2026-10-08 | **Nhánh**: `feature/data-engineering`

---

## 1. Tổng quan Nguồn dữ liệu (Heterogeneous Sources)

- **Nguồn 1 (CRM & Subscriptions)**: `telecom_customer_churn.csv` (7043 dòng x 21 cột)
- **Nguồn 2 (Branch & Geolocation)**: `telecom_customer_locations.csv` (7043 dòng x 8 cột)
- **Độ tương hợp Khóa chính (customerID Match Rate)**: **100.0%** (7043/7043)

---

## 2. Thống kê chi tiết Bảng Nguồn 1 (`telecom_customer_churn.csv`)

| Column | Dtype | Null_Count | Blank_Spaces | Unique_Values | Sample_Values |
| --- | --- | --- | --- | --- | --- |
| customerID | str | 0 | 0 | 7043 | ['7590-VHVEG', '5575-GNVDE', '3668-QPYBK'] |
| gender | str | 0 | 0 | 2 | ['Female', 'Male'] |
| SeniorCitizen | int64 | 0 | 0 | 2 | [0, 1] |
| Partner | str | 0 | 0 | 2 | ['Yes', 'No'] |
| Dependents | str | 0 | 0 | 2 | ['No', 'Yes'] |
| tenure | int64 | 0 | 0 | 73 | [1, 34, 2] |
| PhoneService | str | 0 | 0 | 2 | ['No', 'Yes'] |
| MultipleLines | str | 0 | 0 | 3 | ['No phone service', 'No', 'Yes'] |
| InternetService | str | 0 | 0 | 3 | ['DSL', 'Fiber optic', 'No'] |
| OnlineSecurity | str | 0 | 0 | 3 | ['No', 'Yes', 'No internet service'] |
| OnlineBackup | str | 0 | 0 | 3 | ['Yes', 'No', 'No internet service'] |
| DeviceProtection | str | 0 | 0 | 3 | ['No', 'Yes', 'No internet service'] |
| TechSupport | str | 0 | 0 | 3 | ['No', 'Yes', 'No internet service'] |
| StreamingTV | str | 0 | 0 | 3 | ['No', 'Yes', 'No internet service'] |
| StreamingMovies | str | 0 | 0 | 3 | ['No', 'Yes', 'No internet service'] |
| Contract | str | 0 | 0 | 3 | ['Month-to-month', 'One year', 'Two year'] |
| PaperlessBilling | str | 0 | 0 | 2 | ['Yes', 'No'] |
| PaymentMethod | str | 0 | 0 | 4 | ['Electronic check', 'Mailed check', 'Bank transfer (automatic)'] |
| MonthlyCharges | float64 | 0 | 0 | 1585 | [29.85, 56.95, 53.85] |
| TotalCharges | str | 0 | 0 | 6531 | ['29.85', '1889.5', '108.15'] |
| Churn | str | 0 | 0 | 2 | ['No', 'Yes'] |


---

## 3. Thống kê chi tiết Bảng Nguồn 2 (`telecom_customer_locations.csv`)

| Column | Dtype | Null_Count | Unique_Values | Sample_Values |
| --- | --- | --- | --- | --- |
| customerID | str | 0 | 7043 | ['7590-VHVEG', '5575-GNVDE', '3668-QPYBK'] |
| country | str | 0 | 1 | ['United States'] |
| state | str | 0 | 1 | ['California'] |
| city | str | 0 | 10 | ['San Jose', 'Los Angeles', 'San Francisco'] |
| zip_code | int64 | 0 | 12 | [95113, 90012, 94110] |
| region | str | 0 | 4 | ['Bay Area', 'Southern California', 'Central Valley'] |
| latitude | float64 | 0 | 6952 | [37.338138, 34.041443, 34.053952] |
| longitude | float64 | 0 | 6918 | [-121.887299, -118.24755, -118.256009] |


---

## 4. Phân tích Phân phối Biến mục tiêu (Target Variable - Churn)

- **Khách hàng ở lại (No Churn)**: 5174 (73.46%)
- **Khách hàng rời mạng (Churn)**: 1869 (26.54%)
- **Nhận xét ML**: Tỷ lệ Churn ~26.54% là dạng mất cân bằng dữ liệu vừa phải (moderate class imbalance), phù hợp áp dụng kỹ thuật SMOTE / Class Weighting khi huấn luyện mô hình Classification.

---

## 5. Danh sách Vấn đề Chất lượng Dữ liệu & Giải pháp ETL

| STT | Thuộc tính / Vấn đề | Hiện tượng phát hiện | Quy tắc Xử lý ETL (Transformation Rule) |
| :--- | :--- | :--- | :--- |
| 1 | `TotalCharges` | Có 11 dòng chứa chuỗi rỗng `' '` ứng với khách hàng mới (`tenure = 0`) | Ép kiểu sang số thực (`FLOAT`), thay thế `' '` bằng `0.0` |
| 2 | `SeniorCitizen` | Định dạng số nguyên `0/1` trong khi các cột khác là `'Yes'/'No'` | Chuẩn hóa toàn bộ biến cờ nhị phân về `BOOLEAN` hoặc `0/1` đồng nhất |
| 3 | Multi-category Services | Giá trị `'No internet service'` và `'No phone service'` trong các cột Add-on | Chuẩn hóa thành `'No'` ở tầng Logic nghiệp vụ và gắn thuộc tính cờ vào bảng Dim Service |
| 4 | Primary Key | `customerID` dạng chuỗi (Natural Key) | Tạo **Surrogate Key** (`customer_key`, `dim_plan_key`, v.v.) tự tăng cho tất cả các bảng Dim theo chuẩn Star Schema |

---
### Kết luận Task 1: Dataset đầy đủ, sạch, có độ tin cậy cao và hoàn toàn đáp ứng đầy đủ yêu cầu của Đề bài BTL CO4031.
