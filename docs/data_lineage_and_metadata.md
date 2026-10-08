# 🌳 DATA LINEAGE & METADATA CATALOG (CO4031)

**Dự án**: CO4031 - Telecom Data Warehouse & Decision Support System (DSS)  
**Nhánh**: `feature/data-engineering` | **Database**: PostgreSQL 18 (`telecom_dw`)

---

## 1. DÒNG CHẢY DỮ LIỆU ĐẦU - CUỐI (END-TO-END DATA LINEAGE)

```mermaid
graph TD
    subgraph SOURCELAYER [1. Raw Data Sources]
        S1["telecom_customer_churn.csv<br/>(CRM, 7,043 rows)"]
        S2["telecom_customer_locations.csv<br/>(GIS / Branch, 7,043 rows)"]
    end

    subgraph STAGINGLAYER [2. Middle-Tier Staging Area]
        STG1["staging.stg_telecom_customer_churn"]
        STG2["staging.stg_telecom_customer_locations"]
    end

    subgraph TRANSFORMLAYER [3. ETL Transformations]
        T1["Data Cleansing (TotalCharges float, SeniorCitizen bool)"]
        T2["Surrogate Key Generation (Identity Auto-Increment)"]
        T3["Business Calculations (CLV Proxy, Annual Charges)"]
    end

    subgraph EDWLAYER [4. Enterprise Data Warehouse - Star Schema]
        D_CUST["edw.dim_customer"]
        D_LOC["edw.dim_location"]
        D_SVC["edw.dim_service"]
        D_CTR["edw.dim_contract"]
        D_DATE["edw.dim_date"]
        FACT["edw.fact_customer_subscription_monthly<br/>(7,043 rows)"]
    end

    subgraph PRESENTATIONLAYER [5. Data Marts & Handoff]
        V_BI["edw.vw_bi_churn_analytics<br/>(Dashboard OLAP Mart)"]
        V_ML["edw.vw_ml_feature_store<br/>(ML MBMS Feature Store)"]
        F_BI["data/processed/telecom_bi_churn_analytics.csv"]
        F_ML["data/processed/telecom_ml_feature_store.csv"]
    end

    S1 --> STG1
    S2 --> STG2
    STG1 --> T1
    STG2 --> T1
    T1 --> T2
    T2 --> T3
    T3 --> D_CUST
    T3 --> D_LOC
    T3 --> D_SVC
    T3 --> D_CTR
    T3 --> D_DATE
    D_CUST --> FACT
    D_LOC --> FACT
    D_SVC --> FACT
    D_CTR --> FACT
    D_DATE --> FACT
    FACT --> V_BI
    FACT --> V_ML
    V_BI --> F_BI
    V_ML --> F_ML
```

---

## 2. METADATA CATALOG CỦA KHO DỮ LIỆU (EDW)

| Tên Bảng / View | Loại Đối Tượng | Số Cột | Khóa Chính (PK) | Mục Đích Nghiệp Vụ |
| :--- | :--- | :---: | :--- | :--- |
| `edw.dim_customer` | Dimension Table | 8 | `customer_key` (Surrogate) | Quản lý thuộc tính nhân khẩu học & phân nhóm thâm niên |
| `edw.dim_location` | Dimension Table | 8 | `location_key` (Surrogate) | Quản lý địa bàn, chi nhánh và tọa độ địa lý |
| `edw.dim_service` | Dimension Table | 11 | `service_key` (Surrogate) | Quản lý cấu hình gói cước thoại, internet & add-ons |
| `edw.dim_contract` | Dimension Table | 6 | `contract_key` (Surrogate) | Quản lý kỳ hạn hợp đồng & hình thức thanh toán |
| `edw.dim_date` | Dimension Table | 8 | `date_key` (YYYYMMDD) | Chiều thời gian phục vụ phân tích theo chu kỳ |
| `edw.fact_customer_subscription_monthly` | Fact Table | 14 | `fact_id` (BigSerial) | Lưu trữ các độ đo doanh thu, cước phí, CLV & cờ Churn |
| `edw.vw_bi_churn_analytics` | Data Mart View | 38 | N/A | Cung cấp dữ liệu đã JOIN hoàn chỉnh cho Streamlit Dashboard |
| `edw.vw_ml_feature_store` | Feature Store View | 27 | N/A | Cung cấp tập đặc trưng sạch cho 3 mô hình ML (MBMS) |
