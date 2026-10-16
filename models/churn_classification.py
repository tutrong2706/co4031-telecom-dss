"""
CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM (DSS)
Module: Model 1 - Telecom Customer Churn Classification (models/churn_classification.py)
Author: ML Engineer Agent (CO4031 - HCMUT)

=== ĐIỂM ĐẶC BIỆT CẦN CHÚ Ý (IMPORTANT DESIGN NOTES) ===
1. XỬ LÝ LỆCH LỚP DỮ LIỆU (Class Imbalance Strategy):
   - Tỷ lệ Churn trong tập dữ liệu viễn thông xấp xỉ 26.5% (Churn=1) vs 73.5% (Churn=0).
   - Nếu huấn luyện thông thường, mô hình có xu hướng thiên vị dự đoán Churn=0 (Accuracy cao nhưng Recall thấp).
   - Giải pháp: Sử dụng `class_weight='balanced'` trong Random Forest & Decision Tree, đồng thời tinh chỉnh ngưỡng xác suất (Threshold Tuning).

2. LỰA CHỌN THƯỚC ĐO ĐÁNH GIÁ (Evaluation Metric Selection):
   - Trong bài toán kinh doanh viễn thông, chi phí bỏ sót 1 khách hàng rời mạng (False Negative) LỚN HƠN RẤT NHIỀU chi phí gọi điện/tặng quà giữ chân nhầm 1 khách hàng không rời mạng (False Positive).
   - Do đó, ưu tiên tối ưu **RECALL (Churn=1)** và **ROC-AUC**, thay vì chỉ nhìn vào Accuracy tổng thể.

3. SO SÁNH 3 THUẬT TOÁN (Model Benchmarking):
   - Decision Tree (CART / C4.5 theo chương trình học): Tính giải thích cao, baseline tốt.
   - Random Forest (Bagging Ensemble): Giảm variance, chống overfitting, cho Feature Importance chuẩn xác.
   - Gradient Boosting (Boosting Ensemble): Cho khả năng tối ưu AUC cao nhất.

4. ĐÓNG GÓI MODEL & PREPROCESSOR (Deployment Artifacts):
   - Lưu `churn_model.pkl` và `preprocessor.pkl` vào `models/saved/` để Backend Streamlit (Phase 3) tái sử dụng.
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, balanced_accuracy_score, confusion_matrix, roc_curve
)

from utils import load_feature_store, build_preprocessor, prepare_data_for_churn, MODEL_DIR, EVAL_DIR

def train_and_evaluate_churn_models():
    print("=" * 80)
    print("[RUN] BAT DAU HUAN LUYEN MODEL 1: CHURN CLASSIFICATION")
    print("=" * 80)

    # 1. Load dữ liệu từ Feature Store
    df = load_feature_store()
    X_raw, y = prepare_data_for_churn(df)

    # Kiểm tra phân bố lớp
    churn_count = np.bincount(y)
    churn_ratio = churn_count[1] / len(y) * 100
    print(f"[DATA AUDIT] Tong so mau: {len(y)} | No Churn (0): {churn_count[0]} | Churn (1): {churn_count[1]} ({churn_ratio:.2f}%)")

    # 2. Phân chia Train/Test set (80/20, Stratified theo target y)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"[SPLIT] Train set: {X_train_raw.shape[0]} mau | Test set: {X_test_raw.shape[0]} mau")

    # 3. Fit & Transform Preprocessor trên Train set
    preprocessor, num_cols, cat_cols, bool_cols = build_preprocessor(df)
    X_train = preprocessor.fit_transform(X_train_raw)
    X_test = preprocessor.transform(X_test_raw)

    # Lấy danh sách tên thuộc tính sau One-Hot Encoding
    ohe_feature_names = list(preprocessor.named_transformers_['cat'].get_feature_names_out(cat_cols))
    feature_names = num_cols + ohe_feature_names + bool_cols
    print(f"[FEATURE MATRIX] Tong so thuoc tinh sau khi ma hoa & chuan hoa: {X_train.shape[1]}")

    # 4. Định nghĩa 3 thuật toán huấn luyện
    models = {
        "Decision Tree": DecisionTreeClassifier(
            max_depth=6, class_weight='balanced', random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=150, max_depth=8, class_weight='balanced', random_state=42, n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42
        )
    }

    results = {}
    fitted_models = {}
    thresholds = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    print("\n" + "-" * 80)
    print("[TRAIN] HUAN LUYEN & THU NGHIEM 3 THUAT TOAN")
    print("-" * 80)

    for name, model in models.items():
        print(f"--> Dang huan luyen: {name}...")
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        cv_auc = cross_val_score(model, X_train, y_train, cv=cv, scoring='roc_auc', n_jobs=-1)
        oof_proba = cross_val_predict(
            model, X_train, y_train, cv=cv, method='predict_proba', n_jobs=-1
        )[:, 1]
        threshold_candidates = np.arange(0.20, 0.81, 0.01)
        threshold_scores = []
        for threshold in threshold_candidates:
            candidate_pred = (oof_proba >= threshold).astype(int)
            candidate_recall = recall_score(y_train, candidate_pred)
            candidate_f1 = f1_score(y_train, candidate_pred)
            threshold_scores.append((candidate_recall >= 0.75, candidate_f1, threshold))
        _, _, selected_threshold = max(threshold_scores)
        thresholds[name] = float(selected_threshold)
        tuned_pred = (y_proba >= selected_threshold).astype(int)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)

        results[name] = {
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1,
            "ROC-AUC": auc,
            "PR-AUC": average_precision_score(y_test, y_proba),
            "Balanced Accuracy": balanced_accuracy_score(y_test, y_pred),
            "CV ROC-AUC Mean": cv_auc.mean(),
            "CV ROC-AUC Std": cv_auc.std(),
            "Tuned Precision": precision_score(y_test, tuned_pred),
            "Tuned Recall": recall_score(y_test, tuned_pred),
            "Tuned F1-Score": f1_score(y_test, tuned_pred),
            "Tuned Threshold": selected_threshold
        }
        fitted_models[name] = model

        print(
            f"    [{name}] Acc: {acc:.4f} | Prec: {prec:.4f} | Recall: {rec:.4f} | "
            f"F1: {f1:.4f} | ROC-AUC: {auc:.4f} | PR-AUC: {results[name]['PR-AUC']:.4f} | "
            f"CV AUC: {cv_auc.mean():.4f} +/- {cv_auc.std():.4f} | "
            f"Tuned threshold: {selected_threshold:.2f}"
        )

    # 5. Bảng so sánh kết quả
    df_results = pd.DataFrame(results).T
    print("\n" + "=" * 80)
    print("[RESULTS] BANG SO SANH HIEU NANG CAC MO HINH CHURN:")
    print("=" * 80)
    print(df_results.to_string())
    df_results.to_csv(os.path.join(EVAL_DIR, "churn_metrics.csv"), index=True)

    # Chọn mô hình tốt nhất dựa trên ROC-AUC
    best_model_name = df_results['ROC-AUC'].idxmax()
    best_model = fitted_models[best_model_name]
    print(f"\n[BEST MODEL] Mo hinh xuat sac nhat duoc lua chon: {best_model_name} (ROC-AUC: {df_results.loc[best_model_name, 'ROC-AUC']:.4f})")

    # 6. Đóng gói lưu trữ Model & Preprocessor
    model_save_path = os.path.join(MODEL_DIR, "churn_model.pkl")
    prep_save_path = os.path.join(MODEL_DIR, "preprocessor.pkl")

    joblib.dump(best_model, model_save_path)
    joblib.dump(preprocessor, prep_save_path)
    joblib.dump(feature_names, os.path.join(MODEL_DIR, "feature_names.pkl"))
    joblib.dump(thresholds[best_model_name], os.path.join(MODEL_DIR, "churn_threshold.pkl"))

    print(f"[SAVED] Da luu mo hinh churn tai: {model_save_path}")
    print(f"[SAVED] Da luu bo tien xu ly tai: {prep_save_path}")

    # 7. VẼ CÁC BIỂU ĐỒ ĐÁNH GIÁ & LƯU HÌNH ẢNH (EVALUATION PLOTS)
    sns.set_theme(style="whitegrid")

    # 7.1 Confusion Matrix cho Best Model
    plt.figure(figsize=(6, 5))
    best_threshold = thresholds[best_model_name]
    best_test_proba = best_model.predict_proba(X_test)[:, 1]
    cm = confusion_matrix(y_test, (best_test_proba >= best_threshold).astype(int))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Stay (0)', 'Churn (1)'],
                yticklabels=['Stay (0)', 'Churn (1)'])
    plt.title(f'Confusion Matrix - {best_model_name}', fontsize=14, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=12)
    plt.ylabel('Actual Label', fontsize=12)
    plt.tight_layout()
    cm_path = os.path.join(EVAL_DIR, "churn_confusion_matrix.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"[PLOT] Da xuat Confusion Matrix: {cm_path}")

    # 7.2 Đường cong ROC Curve so sánh 3 thuật toán
    plt.figure(figsize=(8, 6))
    for name, model in fitted_models.items():
        y_proba = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        plt.plot(fpr, tpr, label=f'{name} (AUC = {results[name]["ROC-AUC"]:.3f})', linewidth=2)
    
    plt.plot([0, 1], [0, 1], 'k--', label='Random Guess (AUC = 0.500)')
    plt.xlabel('False Positive Rate (FPR)', fontsize=12)
    plt.ylabel('True Positive Rate (TPR / Recall)', fontsize=12)
    plt.title('ROC Curve Comparison - Churn Models', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right', fontsize=11)
    plt.tight_layout()
    roc_path = os.path.join(EVAL_DIR, "churn_roc_curve.png")
    plt.savefig(roc_path, dpi=300)
    plt.close()
    print(f"[PLOT] Da xuat ROC Curve: {roc_path}")

    # 7.3 Feature Importance (cho Random Forest / Gradient Boosting)
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        indices = np.argsort(importances)[::-1][:15] # Top 15 features

        top_features = [feature_names[i] for i in indices]
        top_scores = importances[indices]

        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_scores, y=top_features, palette='viridis')
        plt.title(f'Top 15 Most Important Features - {best_model_name}', fontsize=14, fontweight='bold')
        plt.xlabel('Importance Score', fontsize=12)
        plt.tight_layout()
        fi_path = os.path.join(EVAL_DIR, "churn_feature_importance.png")
        plt.savefig(fi_path, dpi=300)
        plt.close()
        print(f"[PLOT] Da xuat Feature Importance: {fi_path}")

    print("\n[COMPLETE] HOAN THANH BAI TOAN 1: CHURN CLASSIFICATION!")
    return df_results, best_model_name

if __name__ == "__main__":
    train_and_evaluate_churn_models()
