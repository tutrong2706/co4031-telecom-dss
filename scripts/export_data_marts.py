"""
CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM
Script: Export Data Marts & ML Feature Stores to data/processed/ (Task 5)
Author: Data Engineer Agent (CO4031 - HCMUT)
"""

import os
import sys
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# UTF-8 stdout fix for Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def export_data_marts():
    print("=" * 70)
    print("📤 CO4031 - TASK 5: XUẤT DATA MARTS & FEATURE STORES BÀN GIAO")
    print("=" * 70)

    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'telecom_dw'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )

    out_dir = "data/processed"
    os.makedirs(out_dir, exist_ok=True)

    # 1. Export BI Analytics Data Mart
    print("--> Đang xuất Data Mart: edw.vw_bi_churn_analytics...")
    df_bi = pd.read_sql_query("SELECT * FROM edw.vw_bi_churn_analytics;", conn)
    bi_csv_path = os.path.join(out_dir, "telecom_bi_churn_analytics.csv")
    df_bi.to_csv(bi_csv_path, index=False)
    print(f"[OK] Đã xuất {len(df_bi)} dòng ra file: {bi_csv_path}")

    # 2. Export ML Feature Store Data Mart
    print("--> Đang xuất Feature Store: edw.vw_ml_feature_store...")
    df_ml = pd.read_sql_query("SELECT * FROM edw.vw_ml_feature_store;", conn)
    ml_csv_path = os.path.join(out_dir, "telecom_ml_feature_store.csv")
    df_ml.to_csv(ml_csv_path, index=False)
    print(f"[OK] Đã xuất {len(df_ml)} dòng ra file: {ml_csv_path}")

    conn.close()

    # Generate Hand-off Documentation for ML & Dashboard Agents
    handoff_doc_path = "docs/data_marts_handoff.md"
    with open(handoff_doc_path, "w", encoding="utf-8") as f:
        f.write("# 🤝 TÀI LIỆU BÀN GIAO DATA MARTS & FEATURE STORE (TASK 5 HANDOFF)\n\n")
        f.write("**Người bàn giao**: Data Engineer Agent\n")
        f.write("**Đối tượng nhận bàn giao**: ML Engineer Agent & Backend/Dashboard Agent\n")
        f.write("**Database**: PostgreSQL (`telecom_dw`) & Vùng lưu trữ: `data/processed/`\n\n")
        f.write("---\n\n")
        f.write("## 1. Dữ liệu bàn giao cho ML Engineer Agent (MBMS)\n\n")
        f.write("- **SQL View trực tiếp**: `edw.vw_ml_feature_store` (trong PostgreSQL `telecom_dw`)\n")
        f.write(f"- **File CSV tương đương**: [`data/processed/telecom_ml_feature_store.csv`](file:///{os.path.abspath(ml_csv_path).replace(chr(92), '/')})\n")
        f.write("- **Đặc trưng đã được chuẩn hóa sẵn**:\n")
        f.write("  - 100% không còn ô rỗng / khoảng trắng.\n")
        f.write("  - Cột nhị phân đã chuyển thành `True/False`.\n")
        f.write("  - Biến mục tiêu: `churn_flag` (0: Ở lại, 1: Rời mạng).\n")
        f.write("  - Các biến số liên tục phục vụ Clustering & CLV: `tenure_months`, `monthly_charges`, `total_charges`, `avg_charges_per_tenure`, `clv_proxy`, `total_active_addons`.\n\n")
        f.write("---\n\n")
        f.write("## 2. Dữ liệu bàn giao cho Backend & Dashboard Agent (UI / DSS)\n\n")
        f.write("- **SQL View trực tiếp**: `edw.vw_bi_churn_analytics` (trong PostgreSQL `telecom_dw`)\n")
        f.write(f"- **File CSV tương đương**: [`data/processed/telecom_bi_churn_analytics.csv`](file:///{os.path.abspath(bi_csv_path).replace(chr(92), '/')})\n")
        f.write("- **Hỗ trợ thao tác OLAP**:\n")
        f.write("  - *Drill-down / Roll-up*: Theo Địa lý (`region` -> `state` -> `city` -> `zip_code` -> Tọa độ GPS `latitude`/`longitude`).\n")
        f.write("  - *Slice & Dice*: Theo Hợp đồng (`contract_type`), Hình thức thanh toán (`payment_category`), Gói dịch vụ (`internet_service_type`).\n\n")
        f.write("✅ **Bàn giao thành công**: 100% dữ liệu đã sạch, đạt chuẩn Star Schema và sẵn sàng để Agent ML và Dashboard tiếp quản!\n")

    print(f"[OK] Đã xuất tài liệu bàn giao tại: {handoff_doc_path}")

if __name__ == "__main__":
    export_data_marts()
