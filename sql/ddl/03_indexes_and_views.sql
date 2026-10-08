-- ======================================================================
-- CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM (DSS)
-- Script: 03_indexes_and_views.sql
-- Description: Đánh B-Tree Indexes & Tạo Presentation Views / Data Marts
-- Author: Data Engineer Agent (CO4031 - HCMUT)
-- ======================================================================

-- 1. B-TREE INDEXES CHO TOÀN BỘ FOREIGN KEYS VÀ THUỘC TÍNH LỌC OLAP
CREATE INDEX IF NOT EXISTS idx_fact_cust_key ON edw.fact_customer_subscription_monthly(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_loc_key ON edw.fact_customer_subscription_monthly(location_key);
CREATE INDEX IF NOT EXISTS idx_fact_svc_key ON edw.fact_customer_subscription_monthly(service_key);
CREATE INDEX IF NOT EXISTS idx_fact_ctr_key ON edw.fact_customer_subscription_monthly(contract_key);
CREATE INDEX IF NOT EXISTS idx_fact_date_key ON edw.fact_customer_subscription_monthly(snapshot_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_churn ON edw.fact_customer_subscription_monthly(churn_flag);

-- 2. DATA MART / VIEW PHỤC VỤ BI DASHBOARD (OLAP SLICE/DICE & DRILL-DOWN)
CREATE OR REPLACE VIEW edw.vw_bi_churn_analytics AS
SELECT 
    f.fact_id,
    c.customer_id,
    c.gender,
    c.is_senior_citizen,
    c.has_partner,
    c.has_dependents,
    c.tenure_group,
    l.country,
    l.state,
    l.city,
    l.zip_code,
    l.region,
    l.latitude,
    l.longitude,
    s.has_phone_service,
    s.multiple_lines,
    s.internet_service_type,
    s.has_online_security,
    s.has_online_backup,
    s.has_device_protection,
    s.has_tech_support,
    s.has_streaming_tv,
    s.has_streaming_movies,
    s.total_active_addons,
    k.contract_type,
    k.is_paperless_billing,
    k.payment_method,
    k.payment_category,
    k.is_auto_payment,
    d.full_date AS snapshot_date,
    d.year,
    d.quarter,
    d.month,
    f.tenure_months,
    f.monthly_charges,
    f.total_charges,
    f.estimated_annual_charges,
    f.avg_charges_per_tenure,
    f.clv_proxy,
    f.churn_flag,
    f.churn_label
FROM edw.fact_customer_subscription_monthly f
JOIN edw.dim_customer c ON f.customer_key = c.customer_key
JOIN edw.dim_location l ON f.location_key = l.location_key
JOIN edw.dim_service s ON f.service_key = s.service_key
JOIN edw.dim_contract k ON f.contract_key = k.contract_key
JOIN edw.dim_date d ON f.snapshot_date_key = d.date_key;

-- 3. DATA MART / FEATURE STORE PHỤC VỤ MACHINE LEARNING (MBMS)
CREATE OR REPLACE VIEW edw.vw_ml_feature_store AS
SELECT 
    c.customer_id,
    c.gender,
    c.is_senior_citizen,
    c.has_partner,
    c.has_dependents,
    c.tenure_group,
    l.region,
    l.city,
    s.has_phone_service,
    s.multiple_lines,
    s.internet_service_type,
    s.has_online_security,
    s.has_online_backup,
    s.has_device_protection,
    s.has_tech_support,
    s.has_streaming_tv,
    s.has_streaming_movies,
    s.total_active_addons,
    k.contract_type,
    k.is_paperless_billing,
    k.payment_method,
    k.is_auto_payment,
    f.tenure_months,
    f.monthly_charges,
    f.total_charges,
    f.avg_charges_per_tenure,
    f.clv_proxy,
    f.churn_flag
FROM edw.fact_customer_subscription_monthly f
JOIN edw.dim_customer c ON f.customer_key = c.customer_key
JOIN edw.dim_location l ON f.location_key = l.location_key
JOIN edw.dim_service s ON f.service_key = s.service_key
JOIN edw.dim_contract k ON f.contract_key = k.contract_key;
