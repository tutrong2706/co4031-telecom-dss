# CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM (DSS)
# CÁC NGUYÊN TẮC VÀ YÊU CẦU BẮT BUỘC CHO AGENT

## 1. TỔNG QUAN VÀ MỤC TIÊU BÀI TẬP LỚN (CO4031 - HCMUT)
- **Trọng số**: 35% tổng điểm môn học.
- **Deadline nộp**: Trước 23:59 ngày 15/11/2026 (Chủ nhật, Tuần 12).
- **Quy cách nộp bài**: 1 file ZIP chứa `Report.pdf`, `src/`, `data/`, `Slides.pdf`, Link Video thuyết trình (10–15 phút).
- **Hệ thống mục tiêu**: Xây dựng hoàn chỉnh Hệ hỗ trợ ra quyết định (DSS) ngành Viễn thông (Telecom) gồm 3 thành phần cốt lõi:
  1. **DBMS / Data Warehouse (EDW)**: Thiết kế Star Schema, DDL, ETL Pipeline tự động, Data Marts / Views.
  2. **MBMS (Model Management)**: 3 mô hình ML (Classification Churn Prediction, Clustering Customer Segmentation, Regression CLV/Billing).
  3. **User Interface / DSS Dashboard**: Giao diện trực quan hóa OLAP, What-If Analysis cho nhà quản lý.

## 2. QUY TRÌNH PHỐI HỢP 3 VAI TRÒ (3 AGENTS)
Luôn tuân thủ thứ tự làm việc và tài liệu hướng dẫn chi tiết tại:
- **Data Engineer Agent**: Xem [docs/roles/data_engineer_agent.md](file:///c:/Users/Admin/Desktop/Education/Year%204/HK261/Data%20Warehouse/telecom/co4031-telecom-dss/docs/roles/data_engineer_agent.md)
  - Kiến trúc DW 3 tầng (Inmon), Grain ở mức Atomic, Staging Table, Star Schema với **Surrogate Keys** cho Dim Tables.
  - Viết DDL (`sql/ddl/`), Pipeline ETL (`etl/`), xuất SQL Views (`sql/views/` hoặc `data/processed/`).
- **ML Engineer Agent**: Xem [docs/roles/ml_engineer_agent.md](file:///c:/Users/Admin/Desktop/Education/Year%204/HK261/Data%20Warehouse/telecom/co4031-telecom-dss/docs/roles/ml_engineer_agent.md)
  - Đọc dữ liệu ĐỘC QUYỀN từ SQL Views / Data Marts do Data Engineer xuất (không đọc raw file chưa qua DW).
  - Đạt chuẩn 3 bài toán: Churn Classification, K-Means Clustering, CLV Regression. Đóng gói file `.pkl`.
- **Backend & Dashboard Agent**: Xem [docs/roles/backend_dashboard_agent.md](file:///c:/Users/Admin/Desktop/Education/Year%204/HK261/Data%20Warehouse/telecom/co4031-telecom-dss/docs/roles/backend_dashboard_agent.md)
  - Xây dựng Streamlit Dashboard + API tích hợp DW và ML models. Hỗ trợ OLAP (Drill-down, Slice/Dice) và What-If Analysis.
- **Workflow & Quality Gates**: Xem [docs/roles/co4031_project_workflow_skill.md](file:///c:/Users/Admin/Desktop/Education/Year%204/HK261/Data%20Warehouse/telecom/co4031-telecom-dss/docs/roles/co4031_project_workflow_skill.md)

## 3. CHECKPOINTS & TIẾN ĐỘ
Theo dõi chi tiết các task tại [checkpoints.md](file:///c:/Users/Admin/Desktop/Education/Year%204/HK261/Data%20Warehouse/telecom/co4031-telecom-dss/checkpoints.md).
Đã hoàn thành Phase 1 (Data Engineering) và sẵn sàng chuyển sang Phase 2 (Machine Learning).
