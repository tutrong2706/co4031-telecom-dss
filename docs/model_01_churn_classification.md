# 📄 ĐẶC TẢ KỸ THUẬT MODEL 1: CHURN CLASSIFICATION

> **Dự án**: CO4031 - Telecom Data Warehouse & DSS  
> **Tác giả**: ML Engineer Agent  
> **Ngày hoàn thành**: 2026-10-10  
> **Tệp mô hình đóng gói**: [`models/saved/churn_model.pkl`](file:///c:/Users/Admin/Documents/HocTap/University/261/DW%20&%20DSS/Assignment/co4031-telecom-dss/models/saved/churn_model.pkl)  
> **Bộ tiền xử lý đóng gói**: [`models/saved/preprocessor.pkl`](file:///c:/Users/Admin/Documents/HocTap/University/261/DW%20&%20DSS/Assignment/co4031-telecom-dss/models/saved/preprocessor.pkl)

---

## 1. MỤC TIÊU VÀ BÀI TOÁN NGHIỆP VỤ (BUSINESS OBJECTIVE)

- **Vấn đề**: Tỷ lệ rời mạng (Churn) của khách hàng viễn thông gây thiệt hại doanh thu lớn. Chi phí tìm kiếm 1 khách hàng mới gấp 5–7 lần chi phí giữ chân khách hàng cũ.
- **Mục tiêu**: Xây dựng mô hình phân loại học có giám sát (Supervised Classification) dựa trên 7,043 hồ sơ khách hàng đã được ETL sạch từ kho dữ liệu EDW (`edw.vw_ml_feature_store`).
- **Ứng dụng trong DSS**:
  - Dự báo xác suất Churn cho từng khách hàng theo thời gian thực (Real-time Prediction) trên Streamlit Dashboard.
  - Phân loại mức độ rủi ro (Rất cao, Cao, Trung bình, Thấp) để gửi cảnh báo sớm cho bộ phận Chăm sóc khách hàng (CRM).

---

## 2. NGUỒN DỮ LIỆU VÀ TIỀN XỬ LÝ (DATA & PREPROCESSING)

### 2.1. Phân bố biến mục tiêu (`churn_flag`)
- **Tổng số mẫu**: 7,043 bản ghi.
- **No Churn (`0`)**: 5,174 bản ghi (73.46%).
- **Churn (`1`)**: 1,869 bản ghi (26.54%).
- **Nhận xét**: Tập dữ liệu bị lệch lớp (Class Imbalance) ở mức vừa phải (tỷ lệ 1:2.77).

### 2.2. Chiến lược Tiền xử lý (Preprocessing Strategy)
- **Loại bỏ thuộc tính nhiễu/High-Cardinality**:
  - `customer_id`: Khóa tự nhiên, không có giá trị tiên đoán.
  - `city`: Hơn 1,100 thành phố → loại bỏ để tránh thưa dữ liệu và bùng nổ chiều dữ liệu (Curse of Dimensionality). Giữ lại `region` (4 vùng lớn).
  - `tenure_group`: Trùng lặp thông tin với `tenure_months`.
- **Mã hóa thuộc tính (Encoding)**:
  - Categoricals (`gender`, `multiple_lines`, `internet_service_type`, `contract_type`, `payment_method`, `region`): Sử dụng `OneHotEncoder(drop='first', sparse_output=False)`.
  - Booleans (12 cột như `is_senior_citizen`, `has_online_security`, `is_auto_payment`,...): Chuyển thành dạng 0/1 Integer.
- **Chuẩn hóa (Scaling)**:
  - Continuous Numericals (`tenure_months`, `monthly_charges`, `total_charges`, `avg_charges_per_tenure`, `total_active_addons`): Chuẩn hóa bằng `StandardScaler()`.
- **Ma trận thuộc tính sau xử lý**: 30 thuộc tính đầu vào (Input Features).

---

## 3. KẾT QUẢ HUẤN LUYỆN VÀ SO SÁNH 3 THUẬT TOÁN

Mô hình được chia theo tỷ lệ **80% Train / 20% Test** (Stratified Sampling).

| Thuật toán | Accuracy | Precision | Recall (Churn=1) | F1-Score | ROC-AUC | PR-AUC | CV ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Decision Tree (CART)** | 72.75% | 49.18% | **80.48%** | 0.6105 | 0.8249 | 0.6142 | 0.8242 +/- 0.0114 |
| **Random Forest (Ensemble)** | 75.87% | 53.20% | **75.67%** | **0.6247** | **0.8398** | 0.6452 | 0.8464 +/- 0.0108 |
| **Gradient Boosting** | **79.99%** | **65.65%** | 51.60% | 0.5778 | 0.8397 | **0.6462** | **0.8502 +/- 0.0095** |

> [!IMPORTANT]
> **Tại sao chọn Random Forest làm mô hình sản phẩm?**  
> Trong bài toán Churn, **Recall (tỷ lệ phát hiện đúng khách churn)** quan trọng hơn Accuracy tổng thể. Chi phí bỏ sót 1 khách rời mạng lớn hơn nhiều chi phí gọi điện chăm sóc nhầm. **Random Forest với `class_weight='balanced'`** đạt điểm **ROC-AUC = 0.8398** và **Recall = 75.67%**, là sự lựa chọn hoàn hảo nhất cho DSS.

---

## 4. BIỂU ĐỒ ĐÁNH GIÁ MÔ HÌNH (EVALUATION VISUALIZATIONS)

### 4.1. Confusion Matrix (Random Forest)
- **True Negatives (TN)**: 786 (Dự đoán đúng Stay)
- **False Positives (FP)**: 249 (Dự đoán nhầm Churn)
- **False Negatives (FN)**: 91 (Bỏ sót Churn - chỉ 6.4% tổng test set)
- **True Positives (TP)**: 283 (Phát hiện đúng Churn)

Ngưỡng dự đoán được chọn bằng out-of-fold predictions trên tập train, với mục tiêu giữ Recall của Churn tối thiểu 75%. Ngưỡng của Random Forest là `0.50`; file được lưu tại `models/saved/churn_threshold.pkl`.

![Confusion Matrix](file:///c:/Users/Admin/Documents/HocTap/University/261/DW%20&%20DSS/Assignment/co4031-telecom-dss/models/evaluation/churn_confusion_matrix.png)

### 4.2. Đường cong ROC (ROC Curves)
![ROC Curve](file:///c:/Users/Admin/Documents/HocTap/University/261/DW%20&%20DSS/Assignment/co4031-telecom-dss/models/evaluation/churn_roc_curve.png)

### 4.3. Các thuộc tính quan trọng nhất (Top 10 Feature Importances)
1. `tenure_months` (Thâm niên sử dụng dịch vụ) - Ảnh hưởng mạnh nhất.
2. `total_charges` (Tổng cước đã tích lũy).
3. `monthly_charges` (Cước phí định kỳ hàng tháng).
4. `contract_type_Two year` & `contract_type_One year` (Loại hợp đồng cam kết).
5. `internet_service_type_Fiber optic` (Gói cước cáp quang Fiber Optic).

![Feature Importance](file:///c:/Users/Admin/Documents/HocTap/University/261/DW%20&%20DSS/Assignment/co4031-telecom-dss/models/evaluation/churn_feature_importance.png)

---

## 5. HƯỚNG DẪN TÍCH HỢP CHO BACKEND & DASHBOARD (PHASE 3)

```python
import joblib
import pandas as pd

# Load Model và Preprocessor
model = joblib.load('models/saved/churn_model.pkl')
preprocessor = joblib.load('models/saved/preprocessor.pkl')
churn_threshold = joblib.load('models/saved/churn_threshold.pkl')

# Đưa dữ liệu đầu vào khách hàng mới (Dictionary / DataFrame)
input_data = pd.DataFrame([{
    'gender': 'Female',
    'is_senior_citizen': 0,
    'has_partner': True,
    'has_dependents': False,
    'region': 'Bay Area',
    'has_phone_service': True,
    'multiple_lines': 'No',
    'internet_service_type': 'Fiber optic',
    'has_online_security': False,
    'has_online_backup': True,
    'has_device_protection': False,
    'has_tech_support': False,
    'has_streaming_tv': True,
    'has_streaming_movies': True,
    'total_active_addons': 3,
    'contract_type': 'Month-to-month',
    'is_paperless_billing': True,
    'payment_method': 'Electronic check',
    'is_auto_payment': False,
    'tenure_months': 2,
    'monthly_charges': 85.5,
    'total_charges': 171.0,
    'avg_charges_per_tenure': 85.5
}])

# Transform & Predict Probability
X_trans = preprocessor.transform(input_data)
churn_proba = model.predict_proba(X_trans)[0][1]
churn_label = int(churn_proba >= churn_threshold)

print(f"Xác suất Rời mạng (Churn Probability): {churn_proba * 100:.2f}%")
```
