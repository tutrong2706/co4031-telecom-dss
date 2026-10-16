# Model 3 — Churn Risk Scoring & Retention Prioritization

## 1. Vai trò trong DSS

Model 3 là **decision layer** xây dựng trên xác suất churn của Model 1. Đây không phải là một mô hình dự báo độc lập hoàn toàn. Mục tiêu là giúp doanh nghiệp xếp hạng khách hàng để chọn nhóm nên tiếp cận trước trong chiến dịch giữ chân.

```text
Model 1: churn_probability
        + monthly_charges
        + contract opportunity
        + service opportunity
        ↓
Retention priority score and rank
```

## 2. Input và công thức

Input chính:

- `churn_probability`: xác suất churn từ `models/saved/churn_model.pkl`.
- `monthly_charges`: giá trị doanh thu hàng tháng.
- `contract_type`: cơ hội can thiệp hợp đồng; Month-to-month có điểm cao hơn Two year.
- `total_active_addons`: cơ hội bán thêm dịch vụ; khách hàng có ít add-on có điểm cao hơn.
- `internet_service_type`: được xuất trong score output để phân tích chiến dịch theo dịch vụ.

Các thành phần được chuẩn hóa về khoảng `[0, 1]` và kết hợp:

```text
priority_score = 100 × (
    0.80 × churn_risk
  + 0.12 × monthly_value
  + 0.04 × contract_opportunity
  + 0.04 × service_opportunity
)
```

Trọng số là business assumptions có thể thay đổi trong config, không phải trọng số được học tự động từ target chiến dịch.

## 3. Đánh giá xếp hạng

Để tránh đánh giá trên xác suất in-sample, metrics được tính bằng xác suất churn **out-of-fold từ 5-fold Stratified CV**.

- `Precision@K`: tỷ lệ khách hàng churn thật trong nhóm top K được chọn.
- `Recall@K`: tỷ lệ toàn bộ khách hàng churn được bắt trong nhóm top K.
- `Lift@K`: Precision@K chia cho churn prevalence toàn bộ tập dữ liệu.
- `Campaign benefit`: chưa tính được vì dataset chưa có chi phí liên hệ, chi phí ưu đãi và kết quả treatment.

K được báo cáo ở top `5%`, `10%` và `20%` khách hàng.

Kết quả trên 5-fold out-of-fold probabilities:

| Nhóm ưu tiên | Số khách hàng | Precision@K | Recall@K | Lift@K |
|---:|---:|---:|---:|---:|
| Top 5% | 353 | 83.29% | 15.73% | 3.14x |
| Top 10% | 705 | 74.89% | 28.25% | 2.82x |
| Top 20% | 1,409 | 66.50% | 50.13% | 2.51x |

Các kết quả này cho thấy scoring layer tập trung được khách hàng churn vào nhóm đầu bảng tốt hơn đáng kể so với chọn ngẫu nhiên. Chưa thể tính lợi ích tài chính vì chưa có chi phí liên hệ, chi phí ưu đãi và treatment outcome.

## 4. Artifact

- Source: `models/churn_risk_prioritization.py`
- Score output: `models/evaluation/churn_priority_scores.csv`
- Ranking metrics: `models/evaluation/churn_priority_metrics.csv`
- Business assumptions: `models/saved/churn_priority_config.json`
- Churn model dependency: `models/saved/churn_model.pkl`

Chạy từ thư mục `models/`:

```powershell
python churn_risk_prioritization.py
```

## 5. Diễn giải nghiệp vụ

- Top 5%: nhóm ưu tiên rất cao, phù hợp gọi điện hoặc ưu đãi cá nhân hóa.
- Top 10%: nhóm chiến dịch giữ chân trọng tâm.
- Top 20%: nhóm mở rộng khi ngân sách lớn hơn.

Priority score chỉ hỗ trợ phân bổ nguồn lực. Nó không chứng minh rằng một ưu đãi cụ thể sẽ làm khách hàng không churn. Muốn tính lợi ích chiến dịch cần thêm treatment outcome và cost data.
