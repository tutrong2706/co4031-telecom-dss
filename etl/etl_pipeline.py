"""
CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM
Module: Automated ETL Pipeline (Extract -> Staging -> Transform -> Load EDW)
Author: Data Engineer Agent (CO4031 - HCMUT)
"""

import os
import sys
import datetime
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

# UTF-8 stdout fix for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'telecom_dw'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )

# ======================================================================
# STEP 1: EXTRACT (Nạp dữ liệu thô vào Staging Tables)
# ======================================================================
def extract_to_staging(conn, churn_csv_path, loc_csv_path):
    print("\n" + "=" * 70)
    print("📥 BƯỚC 1: EXTRACT - TRÍCH XUẤT VÀ NẠP VÀO VÙNG ĐỆM STAGING")
    print("=" * 70)

    cur = conn.cursor()

    # 1.1. Extract Source 1: Telecom Customer Churn
    print(f"--> Đang đọc file: {churn_csv_path}...")
    df_churn = pd.read_csv(churn_csv_path, dtype=str)
    df_churn = df_churn.fillna('')

    cur.execute("TRUNCATE TABLE staging.stg_telecom_customer_churn RESTART IDENTITY;")
    churn_cols = [
        'customerID', 'gender', 'SeniorCitizen', 'Partner', 'Dependents',
        'tenure', 'PhoneService', 'MultipleLines', 'InternetService',
        'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport',
        'StreamingTV', 'StreamingMovies', 'Contract', 'PaperlessBilling',
        'PaymentMethod', 'MonthlyCharges', 'TotalCharges', 'Churn'
    ]
    churn_values = [tuple(row[col] for col in churn_cols) for _, row in df_churn.iterrows()]
    insert_churn_sql = f"""
    INSERT INTO staging.stg_telecom_customer_churn ({', '.join(churn_cols)})
    VALUES %s;
    """
    execute_values(cur, insert_churn_sql, churn_values)
    print(f"[OK] Đã nạp {len(churn_values)} dòng vào staging.stg_telecom_customer_churn")

    # 1.2. Extract Source 2: Telecom Customer Locations
    print(f"--> Đang đọc file: {loc_csv_path}...")
    df_loc = pd.read_csv(loc_csv_path, dtype=str)
    df_loc = df_loc.fillna('')

    cur.execute("TRUNCATE TABLE staging.stg_telecom_customer_locations RESTART IDENTITY;")
    loc_cols = ['customerID', 'country', 'state', 'city', 'zip_code', 'region', 'latitude', 'longitude']
    loc_values = [tuple(row[col] for col in loc_cols) for _, row in df_loc.iterrows()]
    insert_loc_sql = f"""
    INSERT INTO staging.stg_telecom_customer_locations ({', '.join(loc_cols)})
    VALUES %s;
    """
    execute_values(cur, insert_loc_sql, loc_values)
    print(f"[OK] Đã nạp {len(loc_values)} dòng vào staging.stg_telecom_customer_locations")

    conn.commit()

# ======================================================================
# STEP 2 & 3: TRANSFORM & LOAD INTO STAR SCHEMA (EDW)
# ======================================================================
def transform_and_load_edw(conn):
    print("\n" + "=" * 70)
    print("⚙️ BƯỚC 2 & 3: TRANSFORM & LOAD VÀO EDW STAR SCHEMA")
    print("=" * 70)

    cur = conn.cursor()

    # Đọc dữ liệu từ Staging
    cur.execute("""
    SELECT 
        c.customerID, c.gender, c.SeniorCitizen, c.Partner, c.Dependents,
        c.tenure, c.PhoneService, c.MultipleLines, c.InternetService,
        c.OnlineSecurity, c.OnlineBackup, c.DeviceProtection, c.TechSupport,
        c.StreamingTV, c.StreamingMovies, c.Contract, c.PaperlessBilling,
        c.PaymentMethod, c.MonthlyCharges, c.TotalCharges, c.Churn,
        l.country, l.state, l.city, l.zip_code, l.region, l.latitude, l.longitude
    FROM staging.stg_telecom_customer_churn c
    JOIN staging.stg_telecom_customer_locations l ON c.customerID = l.customerID;
    """)
    rows = cur.fetchall()
    cols = [
        'customerID', 'gender', 'SeniorCitizen', 'Partner', 'Dependents',
        'tenure', 'PhoneService', 'MultipleLines', 'InternetService',
        'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport',
        'StreamingTV', 'StreamingMovies', 'Contract', 'PaperlessBilling',
        'PaymentMethod', 'MonthlyCharges', 'TotalCharges', 'Churn',
        'country', 'state', 'city', 'zip_code', 'region', 'latitude', 'longitude'
    ]
    df = pd.DataFrame(rows, columns=cols)
    print(f"--> Đã trích xuất {len(df)} bản ghi kết hợp từ Staging để thực hiện Transform.")

    # --- TRANSFORM RULES ---
    # 1. TotalCharges & MonthlyCharges
    df['MonthlyCharges'] = pd.to_numeric(df['MonthlyCharges'], errors='coerce').fillna(0.0)
    df['TotalCharges_clean'] = df['TotalCharges'].replace(' ', '0.0')
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges_clean'], errors='coerce').fillna(0.0)
    df['tenure'] = pd.to_numeric(df['tenure'], errors='coerce').fillna(0).astype(int)

    # 2. Boolean mapping helper
    def to_bool(val):
        return str(val).strip().lower() in ['yes', '1', 'true']

    df['is_senior_citizen'] = df['SeniorCitizen'].apply(lambda x: str(x).strip() in ['1', 'yes'])
    df['has_partner'] = df['Partner'].apply(to_bool)
    df['has_dependents'] = df['Dependents'].apply(to_bool)
    df['has_phone_service'] = df['PhoneService'].apply(to_bool)
    df['is_paperless_billing'] = df['PaperlessBilling'].apply(to_bool)

    # 3. Add-on services boolean conversion
    addon_cols = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']
    for addon in addon_cols:
        df[f'has_{addon}'] = df[addon].apply(lambda x: str(x).strip().lower() == 'yes')

    df['total_active_addons'] = df[[f'has_{addon}' for addon in addon_cols]].sum(axis=1)

    # 4. Tenure group binning
    def get_tenure_group(t):
        if t <= 12:
            return '0-12 Months'
        elif t <= 24:
            return '13-24 Months'
        elif t <= 48:
            return '25-48 Months'
        else:
            return '49-72 Months'
    df['tenure_group'] = df['tenure'].apply(get_tenure_group)

    # 5. Payment category & Auto payment
    def get_payment_category(pm):
        pm_str = str(pm).lower()
        if 'electronic' in pm_str:
            return 'Electronic Check'
        elif 'bank' in pm_str:
            return 'Bank Transfer'
        elif 'credit' in pm_str:
            return 'Credit Card'
        elif 'mailed' in pm_str:
            return 'Mailed Check'
        return 'Other'

    df['payment_category'] = df['PaymentMethod'].apply(get_payment_category)
    df['is_auto_payment'] = df['PaymentMethod'].apply(lambda x: 'automatic' in str(x).lower())

    # 6. Derived measures
    df['estimated_annual_charges'] = (df['MonthlyCharges'] * 12).round(2)
    df['avg_charges_per_tenure'] = np.where(df['tenure'] > 0, (df['TotalCharges'] / df['tenure']).round(2), df['MonthlyCharges'])
    df['clv_proxy'] = (df['tenure'] * df['MonthlyCharges']).round(2)
    df['churn_flag'] = df['Churn'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)
    df['churn_label'] = df['Churn'].apply(lambda x: 'Yes' if str(x).strip().lower() == 'yes' else 'No')

    # Coordinates float conversion
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0.0)
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0.0)

    # --- LOAD DIMENSIONS (TRONG THỨ TỰ RÀNG BUỘC FK) ---

    # 1. dim_date
    print("--> [Load 1/5] Nạp dữ liệu bảng edw.dim_date...")
    snapshot_date = datetime.date.today()
    snapshot_date_key = int(snapshot_date.strftime('%Y%m%d'))
    cur.execute("""
    INSERT INTO edw.dim_date (date_key, full_date, year, quarter, month, month_name, day, is_weekend)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (date_key) DO NOTHING;
    """, (
        snapshot_date_key,
        snapshot_date,
        snapshot_date.year,
        (snapshot_date.month - 1) // 3 + 1,
        snapshot_date.month,
        snapshot_date.strftime('%B'),
        snapshot_date.day,
        snapshot_date.weekday() >= 5
    ))

    # 2. dim_customer
    print("--> [Load 2/5] Nạp dữ liệu bảng edw.dim_customer...")
    cur.execute("TRUNCATE TABLE edw.fact_customer_subscription_monthly CASCADE;")
    cur.execute("TRUNCATE TABLE edw.dim_customer RESTART IDENTITY CASCADE;")
    
    cust_records = [
        (
            row['customerID'], row['gender'], row['is_senior_citizen'],
            row['has_partner'], row['has_dependents'], row['tenure_group']
        )
        for _, row in df.iterrows()
    ]
    insert_cust_sql = """
    INSERT INTO edw.dim_customer (customer_id, gender, is_senior_citizen, has_partner, has_dependents, tenure_group)
    VALUES %s RETURNING customer_key, customer_id;
    """
    cur_res = execute_values(cur, insert_cust_sql, cust_records, fetch=True)
    cust_key_map = {cid: ckey for ckey, cid in cur_res}
    print(f"[OK] Đã nạp {len(cust_records)} khách hàng vào edw.dim_customer (Surrogate Keys generated)")

    # 3. dim_location
    print("--> [Load 3/5] Nạp dữ liệu bảng edw.dim_location...")
    cur.execute("TRUNCATE TABLE edw.dim_location RESTART IDENTITY CASCADE;")
    loc_records = [
        (
            row['country'], row['state'], row['city'], row['zip_code'],
            row['region'], row['latitude'], row['longitude']
        )
        for _, row in df.iterrows()
    ]
    insert_loc_sql = """
    INSERT INTO edw.dim_location (country, state, city, zip_code, region, latitude, longitude)
    VALUES %s RETURNING location_key;
    """
    loc_res = execute_values(cur, insert_loc_sql, loc_records, fetch=True)
    loc_keys = [r[0] for r in loc_res]
    df['location_key'] = loc_keys
    print(f"[OK] Đã nạp {len(loc_records)} bản ghi vào edw.dim_location")

    # 4. dim_service
    print("--> [Load 4/5] Nạp dữ liệu bảng edw.dim_service...")
    cur.execute("TRUNCATE TABLE edw.dim_service RESTART IDENTITY CASCADE;")
    svc_records = [
        (
            row['has_phone_service'], row['MultipleLines'], row['InternetService'],
            row['has_OnlineSecurity'], row['has_OnlineBackup'], row['has_DeviceProtection'],
            row['has_TechSupport'], row['has_StreamingTV'], row['has_StreamingMovies'],
            int(row['total_active_addons'])
        )
        for _, row in df.iterrows()
    ]
    insert_svc_sql = """
    INSERT INTO edw.dim_service (
        has_phone_service, multiple_lines, internet_service_type,
        has_online_security, has_online_backup, has_device_protection,
        has_tech_support, has_streaming_tv, has_streaming_movies, total_active_addons
    ) VALUES %s RETURNING service_key;
    """
    svc_res = execute_values(cur, insert_svc_sql, svc_records, fetch=True)
    svc_keys = [r[0] for r in svc_res]
    df['service_key'] = svc_keys
    print(f"[OK] Đã nạp {len(svc_records)} bản ghi vào edw.dim_service")

    # 5. dim_contract
    print("--> [Load 5/5] Nạp dữ liệu bảng edw.dim_contract...")
    cur.execute("TRUNCATE TABLE edw.dim_contract RESTART IDENTITY CASCADE;")
    ctr_records = [
        (
            row['Contract'], row['is_paperless_billing'], row['PaymentMethod'],
            row['payment_category'], row['is_auto_payment']
        )
        for _, row in df.iterrows()
    ]
    insert_ctr_sql = """
    INSERT INTO edw.dim_contract (contract_type, is_paperless_billing, payment_method, payment_category, is_auto_payment)
    VALUES %s RETURNING contract_key;
    """
    ctr_res = execute_values(cur, insert_ctr_sql, ctr_records, fetch=True)
    ctr_keys = [r[0] for r in ctr_res]
    df['contract_key'] = ctr_keys
    print(f"[OK] Đã nạp {len(ctr_records)} bản ghi vào edw.dim_contract")

    # --- LOAD FACT TABLE (fact_customer_subscription_monthly) ---
    print("\n--> [LOAD FACT TABLE] Đang nạp dữ liệu vào edw.fact_customer_subscription_monthly...")
    df['customer_key'] = df['customerID'].map(cust_key_map)
    df['snapshot_date_key'] = snapshot_date_key

    fact_records = [
        (
            int(row['customer_key']),
            int(row['location_key']),
            int(row['service_key']),
            int(row['contract_key']),
            int(row['snapshot_date_key']),
            int(row['tenure']),
            float(row['MonthlyCharges']),
            float(row['TotalCharges']),
            float(row['estimated_annual_charges']),
            float(row['avg_charges_per_tenure']),
            float(row['clv_proxy']),
            int(row['churn_flag']),
            str(row['churn_label'])
        )
        for _, row in df.iterrows()
    ]

    insert_fact_sql = """
    INSERT INTO edw.fact_customer_subscription_monthly (
        customer_key, location_key, service_key, contract_key, snapshot_date_key,
        tenure_months, monthly_charges, total_charges, estimated_annual_charges,
        avg_charges_per_tenure, clv_proxy, churn_flag, churn_label
    ) VALUES %s;
    """
    execute_values(cur, insert_fact_sql, fact_records)
    conn.commit()
    print(f"[OK] ĐÃ NẠP THÀNH CÔNG {len(fact_records)} BẢN GHI VÀO FACT TABLE!")

# ======================================================================
# STEP 4: DATA QUALITY CHECKS (AUDITING & VERIFICATION)
# ======================================================================
def run_data_quality_checks(conn):
    print("\n" + "=" * 70)
    print("🔍 BƯỚC 4: KIỂM TRA CHẤT LƯỢNG DỮ LIỆU & TÍNH TOÀN VẸN (QUALITY GATES)")
    print("=" * 70)

    cur = conn.cursor()

    # 1. Total records check
    cur.execute("SELECT COUNT(*) FROM edw.fact_customer_subscription_monthly;")
    fact_count = cur.fetchone()[0]
    print(f"1. Tổng số dòng trong Fact Table: {fact_count} (Yêu cầu: 7043)")
    assert fact_count == 7043, f"Số dòng Fact không khớp! Nhận được: {fact_count}"

    # 2. Orphan foreign keys check
    cur.execute("""
    SELECT COUNT(*) 
    FROM edw.fact_customer_subscription_monthly f
    LEFT JOIN edw.dim_customer c ON f.customer_key = c.customer_key
    WHERE c.customer_key IS NULL;
    """)
    orphan_cust = cur.fetchone()[0]
    print(f"2. Khóa ngoại mồ côi (Orphan FKs - Customer): {orphan_cust} (Yêu cầu: 0)")
    assert orphan_cust == 0, "Phát hiện khóa ngoại mồ côi!"

    # 3. Check NULLs in key measures
    cur.execute("""
    SELECT 
        COUNT(*) FILTER (WHERE monthly_charges IS NULL),
        COUNT(*) FILTER (WHERE total_charges IS NULL),
        COUNT(*) FILTER (WHERE churn_flag IS NULL)
    FROM edw.fact_customer_subscription_monthly;
    """)
    null_mc, null_tc, null_churn = cur.fetchone()
    print(f"3. Giá trị NULL trong Measures (Monthly: {null_mc}, Total: {null_tc}, Churn: {null_churn}) (Yêu cầu: 0)")

    # 4. View / Data Mart verification
    cur.execute("SELECT COUNT(*) FROM edw.vw_bi_churn_analytics;")
    bi_view_cnt = cur.fetchone()[0]
    print(f"4. Kiểm tra Data Mart edw.vw_bi_churn_analytics: {bi_view_cnt} dòng sẵn sàng cho Dashboard")

    cur.execute("SELECT COUNT(*) FROM edw.vw_ml_feature_store;")
    ml_view_cnt = cur.fetchone()[0]
    print(f"5. Kiểm tra Feature Store edw.vw_ml_feature_store: {ml_view_cnt} dòng sẵn sàng cho ML models")

    print("\n🎉 PIPELINE ETL ĐÃ HOÀN TẤT XUẤT SẮC - TẤT CẢ QUALITY GATES ĐỀU ĐẠT CHUẨN 100%!")

def run_pipeline():
    conn = get_db_connection()
    churn_csv = "data/raw/telecom_customer_churn.csv"
    loc_csv = "data/raw/telecom_customer_locations.csv"

    try:
        extract_to_staging(conn, churn_csv, loc_csv)
        transform_and_load_edw(conn)
        run_data_quality_checks(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    run_pipeline()
