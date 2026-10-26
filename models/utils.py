"""
CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM (DSS)
Module: Shared ML Utilities & Preprocessing Pipeline (models/utils.py)
Author: ML Engineer Agent (CO4031 - HCMUT)

=== ĐIỂM ĐẶC BIỆT CẦN CHÚ Ý (IMPORTANT DESIGN NOTES) ===
1. LOẠI BỎ KHÓA VÀ ĐỊA DANH QUÁ CHI TIẾT (High Cardinality Drop):
   - 'customer_id': Khóa tự nhiên, không có giá trị tiên đoán, gây nhiễu nếu đưa vào mô hình.
   - 'city': Có hơn 1,100 thành phố (High Cardinality). Nếu One-Hot Encoding sẽ tạo ra hơn 1,100 cột thưa (sparse features),
     gây Overfitting nghiêm trọng và bùng nổ chiều dữ liệu (Curse of Dimensionality). Giữ lại 'region' (4 vùng) để đại diện cho địa lý.

2. PHÂN LOẠI FEATURE TYPES ĐỂ XỬ LÝ RIÊNG BIỆT:
   - Boolean (True/False): Chuyển thành 0/1 integer (không cần One-Hot Encoding).
   - Categorical (Nominal): Dùng One-Hot Encoding (drop='first' để tránh Đa cộng tuyến / Multicollinearity trong mô hình tuyến tính).
   - Numerical (Continuous): Dùng StandardScaler để đưa về phân phối N(0, 1) giúp các thuật toán nhạy cảm với khoảng cách (K-Means, Logistic Regression) hoạt động chính xác.

3. QUẢN LÝ THUẬT TOÁN TIỀN XỬ LÝ (Preprocessor Pipeline Persistence):
   - Đóng gói ColumnTransformer + LabelEncoders bằng joblib lưu vào `models/saved/preprocessor.pkl`.
   - Điều này đảm bảo khi Dashboard (Phase 3) nhận dữ liệu khách hàng mới để dự đoán Real-time, dữ liệu sẽ được Transform EXACTLY cùng định dạng với tập Train.
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# Utf-8 stdout fix for Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Đường dẫn mặc định
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'telecom_ml_feature_store.csv')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'saved')
EVAL_DIR = os.path.join(os.path.dirname(__file__), 'evaluation')

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)

def load_feature_store(csv_path=DATA_PATH):
    """
    Đọc dữ liệu từ Feature Store CSV đã được ETL làm sạch từ Data Warehouse.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Không tìm thấy dữ liệu Feature Store tại: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"[INFO] Đã nạp thành công {len(df)} bản ghi từ Feature Store với {len(df.columns)} cột.")
    return df

def build_preprocessor(df):
    """
    Xây dựng Sklearn ColumnTransformer dựa trên đặc tính các cột dữ liệu.
    
    === CÁC TẬP THUỘC TÍNH (FEATURE GROUPS) ===
    - Drop: customer_id, city, tenure_group (tenure_group trùng lặp thông tin với tenure_months)
    - Categorical (One-Hot): gender, multiple_lines, internet_service_type, contract_type, payment_method, region
    - Numerical (StandardScaler): tenure_months, monthly_charges, total_charges, avg_charges_per_tenure, total_active_addons
    - Boolean: is_senior_citizen, has_partner, has_dependents, has_phone_service, has_online_security, ...
    """
    categorical_cols = [
        'gender', 'multiple_lines', 'internet_service_type', 
        'contract_type', 'payment_method', 'region'
    ]
    
    numerical_cols = [
        'tenure_months', 'monthly_charges', 'total_charges', 
        'avg_charges_per_tenure', 'total_active_addons'
    ]
    
    boolean_cols = [
        'is_senior_citizen', 'has_partner', 'has_dependents', 'has_phone_service',
        'has_online_security', 'has_online_backup', 'has_device_protection',
        'has_tech_support', 'has_streaming_tv', 'has_streaming_movies',
        'is_paperless_billing', 'is_auto_payment'
    ]
    
    print(f"[INFO] Preprocessor Feature Setup:")
    print(f"  - Categorical Features ({len(categorical_cols)}): {categorical_cols}")
    print(f"  - Numerical Features ({len(numerical_cols)}): {numerical_cols}")
    print(f"  - Boolean Features ({len(boolean_cols)}): {boolean_cols}")
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), categorical_cols),
            ('bool', 'passthrough', boolean_cols)
        ],
        remainder='drop'  # Bỏ các cột như customer_id, city, tenure_group, clv_proxy, churn_flag...
    )
    
    return preprocessor, numerical_cols, categorical_cols, boolean_cols

def prepare_data_for_churn(df):
    """
    Chuẩn bị X (features) và y (target) cho Bài toán 1: Churn Classification.
    """
    X_raw = df.drop(columns=['churn_flag', 'clv_proxy'], errors='ignore')
    y = df['churn_flag'].astype(int).values
    
    bool_cols = [col for col in X_raw.columns if X_raw[col].dtype == 'bool']
    for col in bool_cols:
        X_raw[col] = X_raw[col].astype(int)
        
    return X_raw, y
