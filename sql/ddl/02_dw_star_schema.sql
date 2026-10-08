-- ======================================================================
-- CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM (DSS)
-- Script: 02_dw_star_schema.sql
-- Description: DDL tạo Mô hình Star Schema cho Kho Dữ Liệu Trung Tâm (EDW)
-- Author: Data Engineer Agent (CO4031 - HCMUT)
-- ======================================================================

-- Tạo Schema cho Kho Dữ Liệu Trung Tâm
CREATE SCHEMA IF NOT EXISTS edw;

-- ======================================================================
-- PHẦN 1: CÁC BẢNG CHIỀU (DIMENSION TABLES) - SỬ DỤNG SURROGATE KEYS
-- ======================================================================

-- 1.1. Chiều Khách hàng (dim_customer)
DROP TABLE IF EXISTS edw.dim_customer CASCADE;

CREATE TABLE edw.dim_customer (
    customer_key SERIAL PRIMARY KEY,           -- Surrogate Key tự tăng
    customer_id VARCHAR(50) NOT NULL UNIQUE,   -- Natural Key từ hệ thống nguồn
    gender VARCHAR(10),
    is_senior_citizen BOOLEAN,
    has_partner BOOLEAN,
    has_dependents BOOLEAN,
    tenure_group VARCHAR(50),                  -- Phân nhóm thâm niên (0-12m, 13-24m, ...)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.2. Chiều Địa lý & Chi nhánh (dim_location)
DROP TABLE IF EXISTS edw.dim_location CASCADE;

CREATE TABLE edw.dim_location (
    location_key SERIAL PRIMARY KEY,           -- Surrogate Key tự tăng
    country VARCHAR(100) DEFAULT 'United States',
    state VARCHAR(100) DEFAULT 'California',
    city VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    region VARCHAR(100),                       -- Bay Area, SoCal, etc.
    latitude NUMERIC(10, 6),
    longitude NUMERIC(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.3. Chiều Dịch vụ & Gói cước (dim_service)
DROP TABLE IF EXISTS edw.dim_service CASCADE;

CREATE TABLE edw.dim_service (
    service_key SERIAL PRIMARY KEY,            -- Surrogate Key tự tăng
    has_phone_service BOOLEAN,
    multiple_lines VARCHAR(30),
    internet_service_type VARCHAR(30),         -- DSL, Fiber optic, None
    has_online_security BOOLEAN,
    has_online_backup BOOLEAN,
    has_device_protection BOOLEAN,
    has_tech_support BOOLEAN,
    has_streaming_tv BOOLEAN,
    has_streaming_movies BOOLEAN,
    total_active_addons INT CHECK (total_active_addons BETWEEN 0 AND 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.4. Chiều Hợp đồng & Thanh toán (dim_contract)
DROP TABLE IF EXISTS edw.dim_contract CASCADE;

CREATE TABLE edw.dim_contract (
    contract_key SERIAL PRIMARY KEY,           -- Surrogate Key tự tăng
    contract_type VARCHAR(50) NOT NULL,        -- Month-to-month, One year, Two year
    is_paperless_billing BOOLEAN,
    payment_method VARCHAR(100),
    payment_category VARCHAR(50),              -- Electronic Check, Bank Transfer, Credit Card, Mailed Check
    is_auto_payment BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1.5. Chiều Thời gian (dim_date)
DROP TABLE IF EXISTS edw.dim_date CASCADE;

CREATE TABLE edw.dim_date (
    date_key INT PRIMARY KEY,                  -- Định dạng YYYYMMDD (e.g. 20261008)
    full_date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    quarter INT NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month INT NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name VARCHAR(20) NOT NULL,
    day INT NOT NULL CHECK (day BETWEEN 1 AND 31),
    is_weekend BOOLEAN NOT NULL
);

-- ======================================================================
-- PHẦN 2: BẢNG SỰ KIỆN (FACT TABLE) - ATOMIC PERIODIC SNAPSHOT
-- ======================================================================

DROP TABLE IF EXISTS edw.fact_customer_subscription_monthly CASCADE;

CREATE TABLE edw.fact_customer_subscription_monthly (
    fact_id BIGSERIAL PRIMARY KEY,             -- Surrogate Key của Fact Table
    
    -- Khóa ngoại liên kết tới các Dimension Tables (Referential Integrity)
    customer_key INT NOT NULL REFERENCES edw.dim_customer(customer_key),
    location_key INT NOT NULL REFERENCES edw.dim_location(location_key),
    service_key INT NOT NULL REFERENCES edw.dim_service(service_key),
    contract_key INT NOT NULL REFERENCES edw.dim_contract(contract_key),
    snapshot_date_key INT NOT NULL REFERENCES edw.dim_date(date_key),
    
    -- Các độ đo định lượng (Quantitative Measures)
    tenure_months INT NOT NULL CHECK (tenure_months >= 0),
    monthly_charges NUMERIC(10, 2) NOT NULL CHECK (monthly_charges >= 0),
    total_charges NUMERIC(12, 2) NOT NULL CHECK (total_charges >= 0),
    estimated_annual_charges NUMERIC(12, 2),
    avg_charges_per_tenure NUMERIC(10, 2),
    clv_proxy NUMERIC(12, 2),
    
    -- Biến mục tiêu Churn (Degenerate Dimension / Classification Label)
    churn_flag INT NOT NULL CHECK (churn_flag IN (0, 1)),
    churn_label VARCHAR(10) NOT NULL CHECK (churn_label IN ('No', 'Yes')),
    
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
