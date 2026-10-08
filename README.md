# 📡 CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM (DSS)

> **Trường Đại học Bách Khoa TP.HCM (HCMUT) - Khoa Khoa học & Kỹ thuật Máy tính**  
> **Môn học**: Kho dữ liệu và Hệ hỗ trợ ra quyết định (CO4031)  
> **Repository**: [tutrong2706/co4031-telecom-dss](https://github.com/tutrong2706/co4031-telecom-dss)  
> **Nhánh làm việc**: `feature/data-engineering`

---

## 📖 1. TỔNG QUAN DỰ ÁN (PROJECT OVERVIEW)

Hệ thống **Telecom DSS** là giải pháp hỗ trợ ra quyết định toàn diện cho doanh nghiệp viễn thông, được xây dựng theo kiến trúc 3 thành phần tiêu chuẩn:
1. **DBMS / Data Warehouse (EDW)**: Kho dữ liệu trung tâm thiết kế theo mô hình đa chiều **Star Schema** (Inmon 3-tier + Kimball modeling) trên **PostgreSQL 18**.
2. **MBMS (Model Management)**: 3 mô hình khai phá dữ liệu & học máy (Phân loại Churn, Phân cụm Khách hàng K-Means, Dự báo Giá trị vòng đời CLV).
3. **User Interface / DSS Dashboard**: Giao diện trực quan hóa **Streamlit** hỗ trợ phân tích đa chiều OLAP (Drill-down, Slice/Dice) và mô phỏng chính sách (**What-If Analysis**).

```mermaid
graph LR
    subgraph Data Sources [1. Nguồn Dữ Liệu Thô]
        S1["telecom_customer_churn.csv<br/>(CRM, 7,043 rows)"]
        S2["telecom_customer_locations.csv<br/>(GIS/Branch, 7,043 rows)"]
    end

    subgraph Data Warehouse [2. PostgreSQL Data Warehouse]
        STG["staging (Vùng đệm)"]
        EDW["edw (Star Schema - Surrogate Keys)"]
        MARTS["Views & Data Marts"]
    end

    subgraph DSS Applications [3. Ứng Dụng Hỗ Trợ Ra Quyết Định]
        ML["Machine Learning (MBMS)"]
        BI["Streamlit BI Dashboard (OLAP / What-If)"]
    end

    Data Sources -->|ETL Pipeline| STG
    STG -->|Transform & Cleansing| EDW
    EDW --> MARTS
    MARTS --> ML
    MARTS --> BI
```

---

## 🗂️ 2. CẤU TRÚC THƯ MỤC VÀ CHI TIẾT CÁC FILE CODE

```text
co4031-telecom-dss/
├── data/
│   ├── raw/                               # Chứa dữ liệu thô ban đầu (2 nguồn)
│   │   ├── telecom_customer_churn.csv     # Nguồn 1: Thuộc tính thuê bao, dịch vụ, hợp đồng, cước phí, Churn
│   │   └── telecom_customer_locations.csv # Nguồn 2: Dữ liệu phân cấp địa lý, vùng, tọa độ GPS
│   └── processed/                         # Chứa dữ liệu sạch đã xuất từ Data Marts
│       ├── telecom_bi_churn_analytics.csv # File dữ liệu phục vụ BI Dashboard
│       └── telecom_ml_feature_store.csv   # File tập đặc trưng sạch phục vụ 3 bài toán ML
│
├── sql/
│   └── ddl/                               # Tập kịch bản DDL khởi tạo cơ sở dữ liệu
│       ├── 01_staging_schema.sql          # DDL tạo Schema `staging` và 2 bảng lưu tạm dữ liệu thô
│       ├── 02_dw_star_schema.sql          # DDL tạo Schema `edw` gồm 5 bảng Dimension (Surrogate Keys) & 1 bảng Fact
│       └── 03_indexes_and_views.sql       # DDL tạo B-Tree Indexes và 2 Views/Data Marts chuẩn hóa
│
├── etl/
│   └── etl_pipeline.py                    # Script chạy toàn bộ pipeline ETL tự động (Extract -> Transform -> Load -> Audit)
│
├── scripts/                               # Các script tiện ích hỗ trợ vận hành
│   ├── data_profiling.py                  # Script khảo sát EDA, kiểm tra chất lượng dữ liệu thô
│   ├── db_manager.py                      # Module quản lý kết nối, tự động tạo DB `telecom_dw` và thực thi DDL
│   ├── test_postgres_connection.py        # Script kiểm tra kết nối PostgreSQL và hỗ trợ dò/lưu mật khẩu vào .env
│   ├── verify_db_schema.py                # Script kiểm tra cấu trúc bảng, khóa ngoại (FK) trong PostgreSQL
│   └── export_data_marts.py               # Script xuất dữ liệu từ SQL Views ra file CSV trong data/processed/
│
├── docs/                                  # Toàn bộ tài liệu báo cáo & đặc tả kỹ thuật
│   ├── data_profiling_report.md           # Báo cáo đánh giá chất lượng dữ liệu thô (Task 1)
│   ├── data_dictionary.md                 # Từ điển dữ liệu thô giải thích chi tiết từng trường
│   ├── dimensional_modeling_design.md     # Tài liệu thiết kế 4 bước Kimball, Bus Matrix, ERD Star Schema (Task 2)
│   ├── data_lineage_and_metadata.md       # Sơ đồ dòng chảy dữ liệu End-to-End & Metadata Catalog
│   ├── data_marts_handoff.md              # Biên bản bàn giao Data Mart cho team ML & Dashboard (Task 5)
│   └── data_engineering_report.md         # Báo cáo chuyên đề Data Engineering phục vụ nộp bài BTL
│
├── agents/                                # Hướng dẫn & tri thức môn học cho từng vai trò
│   ├── data_engineer_agent.md             # Quy chuẩn thiết kế DW, Surrogate Keys, ETL 3 tầng
│   ├── ml_engineer_agent.md               # Quy chuẩn 3 bài toán ML (Churn, Segmentation, CLV)
│   └── backend_dashboard_agent.md         # Quy chuẩn xây dựng Streamlit Dashboard & OLAP/What-If
│
├── skills/
│   └── co4031_project_workflow_skill.md   # Quy cách nộp bài, Branching Git, Quality Gates
│
├── checkpoints.md                         # Bảng theo dõi tiến độ chi tiết 6 tasks của đồ án
├── requirements.txt                       # Danh mục các thư viện Python cần thiết
├── .env.example                           # File cấu hình mẫu môi trường Database
├── .env                                   # File chứa thông tin mật khẩu DB (Đã được gitignore)
├── .gitignore                             # Cấu hình loại trừ cache, env, venv
└── README.md                              # Tài liệu hướng dẫn tổng quan dự án
```

---

## 🛠️ 3. MÔ TẢ CHI TIẾT TỪNG FILE CODE VÀ CHỨC NĂNG

### 📌 Nhóm Script ETL & Quản lý Database:

1. **[`etl/etl_pipeline.py`](file:///c:/Users/Admin/Desktop/Education/Year%204/HK261/Data%20Warehouse/telecom/co4031-telecom-dss/etl/etl_pipeline.py)**:
   - **Extract**: Đọc dữ liệu từ 2 nguồn CSV và nạp trung gian vào schema `staging`.
   - **Transform**: Xử lý 11 giá trị rỗng của `TotalCharges`, chuẩn hóa các cột boolean (`is_senior_citizen`, `has_partner`, các gói Add-ons), phân nhóm thâm niên `tenure_group`, phân loại hình thức thanh toán, tính toán các chỉ số kinh doanh phái sinh (`estimated_annual_charges`, `avg_charges_per_tenure`, `clv_proxy`).
   - **Load**: Nạp theo thứ tự toàn vẹn tham chiếu: `dim_date` $\rightarrow$ `dim_customer` $\rightarrow$ `dim_location` $\rightarrow$ `dim_service` $\rightarrow$ `dim_contract` $\rightarrow$ sinh **Surrogate Keys** $\rightarrow$ Tra cứu khóa ngoại và nạp **7,043 bản ghi** vào `fact_customer_subscription_monthly`.
   - **Quality Audit**: Tự động kiểm tra số lượng dòng, kiểm tra khóa ngoại mồ côi (0 orphan FKs) và tính sẵn sàng của các Views.

2. **[`scripts/db_manager.py`](file:///c:/Users/Admin/Desktop/Education/Year%204/HK261/Data%20Warehouse/telecom/co4031-telecom-dss/scripts/db_manager.py)**:
   - Tự động kết nối tới PostgreSQL, tạo cơ sở dữ liệu `telecom_dw` nếu chưa có.
   - Tự động thực thi tuần tự các file DDL (`01_staging_schema.sql`, `02_dw_star_schema.sql`, `03_indexes_and_views.sql`).

3. **[`scripts/test_postgres_connection.py`](file:///c:/Users/Admin/Desktop/Education/Year%204/HK261/Data%20Warehouse/telecom/co4031-telecom-dss/scripts/test_postgres_connection.py)**:
   - Kiểm tra kết nối tới PostgreSQL, hỗ trợ kiểm tra mật khẩu từ `.env` hoặc truyền danh sách mật khẩu qua CLI để tìm mật khẩu đúng và tự động ghi vào `.env`.

4. **[`scripts/export_data_marts.py`](file:///c:/Users/Admin/Desktop/Education/Year%204/HK261/Data%20Warehouse/telecom/co4031-telecom-dss/scripts/export_data_marts.py)**:
   - Trích xuất dữ liệu từ các SQL Views (`edw.vw_bi_churn_analytics` và `edw.vw_ml_feature_store`) ra các file CSV chuẩn hóa đặt tại `data/processed/` để phục vụ các thành viên làm ML và Dashboard.

5. **[`scripts/data_profiling.py`](file:///c:/Users/Admin/Desktop/Education/Year%204/HK261/Data%20Warehouse/telecom/co4031-telecom-dss/scripts/data_profiling.py)**:
   - Thực hiện EDA, kiểm tra kiểu dữ liệu, tỷ lệ rỗng, trùng lặp và tương hợp khóa giữa 2 nguồn dữ liệu thô.

---

## 🚀 4. HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY DỰ ÁN

### Bước 1: Cài đặt môi trường Python
```bash
pip install -r requirements.txt
```

### Bước 2: Cấu hình thông tin PostgreSQL trong file `.env`
Tạo file `.env` (hoặc sao chép từ `.env.example`) và điền mật khẩu PostgreSQL của bạn:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=telecom_dw
DB_USER=postgres
DB_PASSWORD=your_password
```

### Bước 3: Khởi tạo Database và Star Schema
```bash
python scripts/db_manager.py
```

### Bước 4: Chạy Pipeline ETL nạp dữ liệu vào Kho
```bash
python etl/etl_pipeline.py
```

### Bước 5: Xuất dữ liệu Data Marts phục vụ ML & Dashboard
```bash
python scripts/export_data_marts.py
```

---

## 📊 5. TIẾN ĐỘ THỰC HIỆN THEO CHECKPOINTS

Xem chi tiết tiến độ tại file [checkpoints.md](file:///c:/Users/Admin/Desktop/Education/Year%204/HK261/Data%20Warehouse/telecom/co4031-telecom-dss/checkpoints.md):
- [x] **Task 1**: Khảo sát & Khám phá dữ liệu thô (Data Profiling) - *Hoàn thành*
- [x] **Task 2**: Thiết kế Mô hình Đa chiều (Dimensional Modeling & Star Schema) - *Hoàn thành*
- [x] **Task 3**: Cài đặt Cơ sở dữ liệu Kho dữ liệu (DDL Implementation) - *Hoàn thành*
- [x] **Task 4**: Xây dựng Quy trình tự động ETL (Extract, Transform, Load) - *Hoàn thành*
- [x] **Task 5**: Xuất Data Marts & Views bàn giao cho ML và Dashboard - *Hoàn thành*
- [x] **Task 6**: Quản lý Metadata, Git & Viết Báo cáo chuyên đề - *Hoàn thành*
