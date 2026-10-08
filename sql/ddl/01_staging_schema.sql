-- ======================================================================
-- CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM (DSS)
-- Script: 01_staging_schema.sql
-- Description: DDL tạo Vùng đệm Staging (Data Staging Area)
-- Author: Data Engineer Agent (CO4031 - HCMUT)
-- ======================================================================

-- Tạo Staging Schema riêng biệt (Kiến trúc 3 tầng - Middle Tier Staging)
CREATE SCHEMA IF NOT EXISTS staging;

-- 1. Bảng Staging cho Nguồn 1 (CRM & Subscriptions)
DROP TABLE IF EXISTS staging.stg_telecom_customer_churn CASCADE;

CREATE TABLE staging.stg_telecom_customer_churn (
    stg_id SERIAL PRIMARY KEY,
    customerID VARCHAR(50),
    gender VARCHAR(20),
    SeniorCitizen VARCHAR(10),
    Partner VARCHAR(10),
    Dependents VARCHAR(10),
    tenure VARCHAR(10),
    PhoneService VARCHAR(10),
    MultipleLines VARCHAR(50),
    InternetService VARCHAR(50),
    OnlineSecurity VARCHAR(50),
    OnlineBackup VARCHAR(50),
    DeviceProtection VARCHAR(50),
    TechSupport VARCHAR(50),
    StreamingTV VARCHAR(50),
    StreamingMovies VARCHAR(50),
    Contract VARCHAR(50),
    PaperlessBilling VARCHAR(10),
    PaymentMethod VARCHAR(100),
    MonthlyCharges VARCHAR(50),
    TotalCharges VARCHAR(50),
    Churn VARCHAR(10),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bảng Staging cho Nguồn 2 (Branch & Geolocation)
DROP TABLE IF EXISTS staging.stg_telecom_customer_locations CASCADE;

CREATE TABLE staging.stg_telecom_customer_locations (
    stg_id SERIAL PRIMARY KEY,
    customerID VARCHAR(50),
    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),
    zip_code VARCHAR(20),
    region VARCHAR(100),
    latitude VARCHAR(50),
    longitude VARCHAR(50),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
