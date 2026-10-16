# 📄 ĐẶC TẢ KỸ THUẬT MODEL 2: CUSTOMER SEGMENTATION (K-MEANS CLUSTERING)

> **Dự án**: CO4031 - Telecom Data Warehouse & DSS  
> **Tác giả**: ML Engineer Agent  
> **Ngày hoàn thành**: 2026-10-10  
> **Tệp mô hình đóng gói**: [`models/saved/kmeans_model.pkl`](file:///c:/Users/Admin/Documents/HocTap/University/261/DW%20&%20DSS/Assignment/co4031-telecom-dss/models/saved/kmeans_model.pkl)  
> **Tệp Scaler đóng gói**: [`models/saved/kmeans_scaler.pkl`](file:///c:/Users/Admin/Documents/HocTap/University/261/DW%20&%20DSS/Assignment/co4031-telecom-dss/models/saved/kmeans_scaler.pkl)

---

## 1. MỤC TIÊU VÀ BÀI TOÁN NGHIỆP VỤ (BUSINESS OBJECTIVE)

- **Vấn đề**: Tập khách hàng hơn 7,000 người có nhu cầu, hành vi tiêu dùng và mức độ trung thành rất khác nhau. Doanh nghiệp không thể áp dụng một chính sách chăm sóc/khuyến mãi cào bằng cho tất cả khách hàng.
- **Mục tiêu**: Sử dụng thuật toán học không giám sát (Unsupervised K-Means Clustering) để phân khúc khách hàng thành **4 nhóm hành vi kinh tế rõ rệt**.
- **Ứng dụng trong DSS**:
  - Tích hợp vào BI Dashboard để nhà quản lý thực hiện thao tác **OLAP Drill-down & Slice/Dice** theo từng phân khúc.
  - Hỗ trợ xây dựng chiến lược Marketing mục tiêu (Targeted Marketing Campaigns) và chính sách chăm sóc riêng biệt cho từng cụm.

---

## 2. LỰA CHỌN THUỘC TÍNH VÀ TIỀN XỬ LÝ (FEATURE SELECTION & SCALING)

### 2.1. Danh sách 11 thuộc tính đầu vào (Input Features)
1. `tenure_months`: Thâm niên gắn bó (số tháng).
2. `monthly_charges`: Cước phí hàng tháng ($).
3. `total_charges`: Tổng cước đã tích lũy ($).
4. `avg_charges_per_tenure`: Cước bình quân theo tháng ($).
5. `clv_proxy`: Chỉ số proxy giá trị vòng đời khách hàng.
6. `total_active_addons`: Số lượng dịch vụ giá trị gia tăng đang sử dụng (0 - 6).
7. `is_senior_citizen`: Khách hàng cao tuổi (0/1).
8. `has_partner`: Có người phụ thuộc/bạn đời (0/1).
9. `has_dependents`: Có con cái/người nuôi dưỡng (0/1).
10. `is_paperless_billing`: Đăng ký hóa đơn điện tử (0/1).
11. `is_auto_payment`: Thanh toán tự động qua Ngân hàng/Thẻ (0/1).

### 2.2. Chuẩn hóa dữ liệu (Scaling)
- **Phương pháp**: Bắt buộc áp dụng `StandardScaler()` đưa 100% thuộc tính về phân phối chuẩn $N(\mu=0, \sigma^2=1)$.
- **Lý do**: K-Means tính khoảng cách theo khoảng cách Euclidean. Nếu không scale, thuộc tính `total_charges` (quy mô tới $8,600) sẽ hoàn toàn làm méo lệch kết quả phân cụm.

---

## 3. ĐÁNH GIÁ SỐ CỤM TỐI ƯU (OPTIMAL K SELECTION)

Thử nghiệm số cụm $k \in [2, 8]$:

| Số cụm ($k$) | Inertia (WCSS) | Silhouette Score | Davies-Bouldin | Calinski-Harabasz | Nhận xét |
| :---: | :---: | :---: | :---: | :---: | :---: |
| $k = 2$ | 53,172.32 | **0.2843** | 1.3990 | 3217.86 | Phân loại tốt hơn về mặt tách biệt nhưng quá thô cho DSS |
| $k = 3$ | 44,614.09 | 0.2224 | 1.6169 | 2592.53 | Ít cụm nhưng chưa tạo persona đủ rõ |
| **$k = 4$** | **40,512.18** | **0.2231** | **1.5557** | **2140.65** | **Cân bằng giữa Elbow, kích thước cụm và khả năng diễn giải nghiệp vụ** |
| $k = 5$ | 36,843.39 | 0.2151 | 1.5187 | 1940.32 | Bắt đầu phân mảnh thêm |

![Elbow & Silhouette](file:///c:/Users/Admin/Documents/HocTap/University/261/DW%20&%20DSS/Assignment/co4031-telecom-dss/models/evaluation/kmeans_elbow_silhouette.png)

Silhouette của `k=4` chỉ ở mức thấp-trung bình, do đó các cụm có vùng giao nhau. Tuy nhiên, nghiệm `k=4` ổn định qua nhiều lần khởi tạo với Adjusted Rand Index trung bình `0.9444 +/- 0.1454`, và tạo ra bốn nhóm có ý nghĩa rõ ràng cho chiến lược chăm sóc khách hàng.

---

## 4. BẢO TẢNH HỒ SƠ 4 CỤM KHACH HÀNG (CLUSTER PROFILING)

| Chỉ số / Đặc trưng | Cụm 0 (New Standard) | Cụm 1 (High-Risk Loyalists) | Cụm 2 (Economy / Low-Cost) | Cụm 3 (Premium Subscribers) |
| :--- | :---: | :---: | :---: | :---: |
| **Tên định danh nghiệp vụ** | **Khách hàng Mới - Cước cơ bản** | **Khách hàng Rủi ro cao** | **Khách hàng Tiết kiệm** | **Khách hàng Cao cấp - Trung thành** |
| **Số lượng khách hàng** | 2,070 (29.39%) | 830 (11.78%) | 2,175 (30.88%) | 1,968 (27.94%) |
| **Thâm niên TB (`tenure`)** | 27.7 tháng | 23.5 tháng | 15.8 tháng | **59.3 tháng** |
| **Cước hàng tháng (`Monthly`)**| **$26.64** | $76.82 | $72.96 | **$90.71** |
| **Tổng cước tích lũy (`Total`)**| $717.15 | $1,806.16 | $1,141.17 | **$5,381.35** |
| **Số Add-on dịch vụ TB** | 0.3 dịch vụ | 1.8 dịch vụ | 1.9 dịch vụ | **4.1 dịch vụ** |
| **Tỷ lệ Churn (%)** | **12.22%** (Thấp) | **50.72%** (Rất cao!) | **42.62%** (Cao) | **13.62%** (Rất thấp) |

### Chi tiết Chiến lược DSS theo từng Cụm:
1. **Cụm 0 (New Standard - 29.39%)**: Khách hàng mới sử dụng gói cước cơ bản (thoại cố định, internet tốc độ vừa phải). Tỷ lệ churn thấp (12.22%).
   - *Chiến lược DSS*: Upsell khuyến mãi dùng thử các dịch vụ Add-on (Security, Backup) với giá ưu đãi để tăng Monthly Charges.
2. **Cụm 1 (High-Risk Loyalists - 11.78%)**: Khách hàng có cước trung bình cao ($76.82) nhưng thâm niên ngắn và tỷ lệ rời mạng báo động (**50.72%**).
   - *Chiến lược DSS*: Can thiệp cấp bách! Tặng voucher giảm giá hợp đồng 1-2 năm, gọi điện chăm sóc ngay lập tức.
3. **Cụm 2 (Economy / Low-Cost - 30.88%)**: Nhóm dùng ngắn hạn (15.8 tháng), tỷ lệ churn cao (42.62%).
   - *Chiến lược DSS*: Đưa ra gói cước Combo tiết kiệm và khuyến khích đăng ký Thanh toán tự động (Auto-payment).
4. **Cụm 3 (Premium Subscribers - 27.94%)**: "Xương sống doanh thu" của công ty. Gắn bó lâu năm (59.3 tháng), cước cao ($90.71), sử dụng nhiều add-ons (4.1/6), churn rất thấp (13.62%).
   - *Chiến lược DSS*: Chương trình tri ân VIP, hỗ trợ kỹ thuật ưu tiên 24/7 (Tech Support VIP) để giữ vững sự trung thành.

---

## 5. TRỰC QUAN HÓA PHÂN CỤM (VISUALIZATION)

### 5.1. Phân bố 2D bằng Giảm chiều dữ liệu PCA
![PCA 2D Cluster Scatter Plot](file:///c:/Users/Admin/Documents/HocTap/University/261/DW%20&%20DSS/Assignment/co4031-telecom-dss/models/evaluation/kmeans_pca_scatter.png)

### 5.2. So sánh các chỉ số giữa 4 Cụm
![Cluster Profile Comparison](file:///c:/Users/Admin/Documents/HocTap/University/261/DW%20&%20DSS/Assignment/co4031-telecom-dss/models/evaluation/kmeans_cluster_profile.png)

---

## 6. HƯỚNG DẪN TÍCH HỢP CHO BACKEND & DASHBOARD (PHASE 3)

```python
import joblib
import pandas as pd

# Load K-Means Model & Scaler
kmeans_model = joblib.load('models/saved/kmeans_model.pkl')
kmeans_scaler = joblib.load('models/saved/kmeans_scaler.pkl')

# Map tên cụm nghiệp vụ
cluster_names = {
    0: "Khách hàng Mới - Cước cơ bản",
    1: "Khách hàng Rủi ro cao",
    2: "Khách hàng Tiết kiệm",
    3: "Khách hàng Cao cấp - Trung thành"
}

# Dữ liệu khách hàng mới
input_data = pd.DataFrame([{
    'tenure_months': 60,
    'monthly_charges': 95.0,
    'total_charges': 5700.0,
    'avg_charges_per_tenure': 95.0,
    'clv_proxy': 5700.0,
    'total_active_addons': 4,
    'is_senior_citizen': 0,
    'has_partner': 1,
    'has_dependents': 1,
    'is_paperless_billing': 1,
    'is_auto_payment': 1
}])

# Scale & Predict Cluster
input_scaled = kmeans_scaler.transform(input_data)
cluster_id = kmeans_model.predict(input_scaled)[0]

print(f"Phân khúc Khách hàng: {cluster_names[cluster_id]} (Cluster ID: {cluster_id})")
```
