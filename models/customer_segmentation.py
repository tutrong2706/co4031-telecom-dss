r"""
CO4031 - TELECOM DATA WAREHOUSE & DECISION SUPPORT SYSTEM (DSS)
Module: Model 2 - Telecom Customer Segmentation using K-Means Clustering (models/customer_segmentation.py)
Author: ML Engineer Agent (CO4031 - HCMUT)

=== ĐIỂM ĐẶC BIỆT CẦN CHÚ Ý (IMPORTANT DESIGN NOTES) ===
1. NHẠY CẢM VỚI QUY MÔ DỮ LIỆU (Scaling Sensitivity in K-Means):
   - Thuật toán K-Means sử dụng Khoảng cách Euclidean để tính toán khoảng cách giữa các điểm dữ liệu và Centroids.
   - Các biến có quy mô lớn như `total_charges` ($0 - $8,600) sẽ hoàn toàn áp đảo các biến như `tenure_months` (0 - 72) hoặc `total_active_addons` (0 - 6).
   - Giải pháp: **BẮT BUỘC** áp dụng `StandardScaler()` biến đổi 100% thuộc tính đầu vào về phân phối chuẩn $N(\mu=0, \sigma^2=1)$ trước khi phân cụm.

2. PHƯƠNG PHÁP XÁC ĐỊNH SỐ CỤM TỐI ƯU (Elbow Method & Silhouette Score):
   - Thử nghiệm $k$ từ 2 đến 8 cụm.
   - Elbow Method: Đo lường Tổng bình phương khoảng cách trong cụm (Inertia / Within-Cluster Sum of Squares - WCSS). Tìm điểm "khuỷu tay" nơi WCSS bắt đầu giảm chậm.
   - Silhouette Score: Đo lường độ chặt chẽ nội cụm so với độ tách biệt ngoại cụm. Chọn $k$ có Silhouette Score cao và cân bằng kích thước các cụm.

3. ĐÁNH GIÁ Ý NGHĨA NGHIỆP VỤ (Cluster Profiling & Interpretation):
   - Phân cụm chỉ có giá trị ra quyết định khi các cụm mô tả được hình ảnh khách hàng thực tế (Customer Personas):
     * Cụm Khách hàng Trung thành - Giá trị cao (High-Value Loyalists)
     * Cụm Khách hàng Mới - Rủi ro rời mạng cao (New High-Risk Customers)
     * Cụm Khách hàng Tiết kiệm (Low-Cost/Economy Segment)
     * Cụm Khách hàng Cao cấp (Premium Subscribers)

4. ĐÓNG GÓI MODEL (Deployment Artifacts):
   - Lưu `kmeans_model.pkl` và `kmeans_scaler.pkl` vào `models/saved/`.
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

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    silhouette_score, davies_bouldin_score, calinski_harabasz_score,
    adjusted_rand_score
)
from sklearn.decomposition import PCA

from utils import load_feature_store, MODEL_DIR, EVAL_DIR

def train_and_evaluate_kmeans():
    print("=" * 80)
    print("[RUN] BAT DAU HUAN LUYEN MODEL 2: CUSTOMER SEGMENTATION (K-MEANS)")
    print("=" * 80)

    # 1. Load dữ liệu từ Feature Store
    df = load_feature_store()

    # 2. Lựa chọn tập thuộc tính đặc trưng cho Phân cụm (Clustering Features)
    # Lựa chọn các thuộc tính phản ánh: Thâm niên, Cước phí, Giá trị CLV, Dịch vụ bổ sung, và Hợp đồng
    clustering_feature_names = [
        'tenure_months', 'monthly_charges', 'total_charges', 
        'avg_charges_per_tenure', 'clv_proxy', 'total_active_addons',
        'is_senior_citizen', 'has_partner', 'has_dependents',
        'is_paperless_billing', 'is_auto_payment'
    ]

    X_cluster_raw = df[clustering_feature_names].copy()
    
    # Ép kiểu boolean thành 0/1
    for col in X_cluster_raw.columns:
        if X_cluster_raw[col].dtype == 'bool':
            X_cluster_raw[col] = X_cluster_raw[col].astype(int)

    print(f"[FEATURE SELECTION] Da chon {len(clustering_feature_names)} thuoc tinh dac trung cho phan cum.")

    # 3. Chuẩn hóa dữ liệu bằng StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_cluster_raw)
    print("[SCALING] Da chuan hoa 100% features ve phan phoi N(0, 1) bang StandardScaler.")

    # 4. Thử nghiệm số lượng cụm k từ 2 đến 8 (Elbow & Silhouette Analysis)
    k_range = range(2, 9)
    inertias = []
    silhouette_scores = []
    davies_bouldin_scores = []
    calinski_harabasz_scores = []

    print("\n" + "-" * 80)
    print("[EVALUATION] PHUONG PHAP ELBOW & SILHOUETTE SCORE THEO K")
    print("-" * 80)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, init='k-means++', n_init=50, random_state=42)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        inertia = kmeans.inertia_
        sil = silhouette_score(X_scaled, cluster_labels)
        db = davies_bouldin_score(X_scaled, cluster_labels)
        ch = calinski_harabasz_score(X_scaled, cluster_labels)
        
        inertias.append(inertia)
        silhouette_scores.append(sil)
        davies_bouldin_scores.append(db)
        calinski_harabasz_scores.append(ch)
        
        print(
            f"  - k = {k} | Inertia (WCSS): {inertia:10.2f} | Silhouette: {sil:.4f} | "
            f"Davies-Bouldin: {db:.4f} | Calinski-Harabasz: {ch:.2f}"
        )

    pd.DataFrame({
        "k": list(k_range),
        "inertia": inertias,
        "silhouette": silhouette_scores,
        "davies_bouldin": davies_bouldin_scores,
        "calinski_harabasz": calinski_harabasz_scores,
    }).to_csv(os.path.join(EVAL_DIR, "kmeans_metrics.csv"), index=False)

    # 5. Vẽ đồ thị Elbow & Silhouette Score
    sns.set_theme(style="whitegrid")

    fig, ax1 = plt.subplots(figsize=(8, 5))

    color = 'tab:blue'
    ax1.set_xlabel('So luong cum (k)', fontsize=12)
    ax1.set_ylabel('Inertia (WCSS)', color=color, fontsize=12)
    ax1.plot(k_range, inertias, marker='o', color=color, linewidth=2, label='Inertia (Elbow)')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  
    color = 'tab:orange'
    ax2.set_ylabel('Silhouette Score', color=color, fontsize=12)
    ax2.plot(k_range, silhouette_scores, marker='s', linestyle='--', color=color, linewidth=2, label='Silhouette Score')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Elbow Method & Silhouette Score Analysis for K-Means', fontsize=14, fontweight='bold')
    fig.tight_layout()
    elbow_path = os.path.join(EVAL_DIR, "kmeans_elbow_silhouette.png")
    plt.savefig(elbow_path, dpi=300)
    plt.close()
    print(f"[PLOT] Da xuat bieu do Elbow & Silhouette: {elbow_path}")

    # 6. Lựa chọn k tối ưu (k = 4 cụm)
    # k = 4 được giữ theo Elbow, độ ổn định và khả năng diễn giải nghiệp vụ; Silhouette còn hạn chế
    k_best = 4
    print(f"\n[OPTIMAL K] Luot chon k = {k_best} cum toi uu cho mo hinh phan khuc khach hang.")

    final_kmeans = KMeans(n_clusters=k_best, init='k-means++', n_init=50, random_state=42)
    df['cluster'] = final_kmeans.fit_predict(X_scaled)

    stability_labels = []
    for seed in range(10):
        stability_model = KMeans(
            n_clusters=k_best, init='k-means++', n_init=25, random_state=seed
        )
        stability_labels.append(stability_model.fit_predict(X_scaled))
    stability_scores = [
        adjusted_rand_score(stability_labels[0], labels)
        for labels in stability_labels[1:]
    ]
    print(
        f"[STABILITY] k={k_best} mean ARI across seeds: "
        f"{np.mean(stability_scores):.4f} +/- {np.std(stability_scores):.4f}"
    )

    # 7. Cluster Profiling (Phân tích hồ sơ từng cụm)
    print("\n" + "=" * 80)
    print(f"[CLUSTER PROFILING] DAC TRUNG CUA {k_best} CUM KHACH HANG:")
    print("=" * 80)

    profile_cols = [
        'tenure_months', 'monthly_charges', 'total_charges', 
        'clv_proxy', 'total_active_addons', 'churn_flag'
    ]
    cluster_summary = df.groupby('cluster')[profile_cols].agg(['mean', 'count'])
    
    # Định nghĩa tên nghiệp vụ cho 4 cụm dựa trên phân tích giá trị trung bình
    cluster_names = {
        0: "Cum 0: Khach hang Moi - Mức cuoc Trung binh (New Standard)",
        1: "Cum 1: Khach hang Trung thanh - Gia tri Cao (High-Value Loyalists)",
        2: "Cum 2: Khach hang Tiet kiem - Cuoc thap (Economy / Low-Cost)",
        3: "Cum 3: Khach hang Cao cap - Cuoc cao & Addons (Premium Subscribers)"
    }
    
    df['cluster_name'] = df['cluster'].map(cluster_names)

    for c_id in range(k_best):
        c_df = df[df['cluster'] == c_id]
        count = len(c_df)
        pct = count / len(df) * 100
        avg_tenure = c_df['tenure_months'].mean()
        avg_mc = c_df['monthly_charges'].mean()
        avg_tc = c_df['total_charges'].mean()
        avg_addons = c_df['total_active_addons'].mean()
        churn_rate = c_df['churn_flag'].mean() * 100

        print(f"\n📌 CUM {c_id} ({cluster_names[c_id]}):")
        print(f"   - So luong: {count} khach hang ({pct:.2f}%)")
        print(f"   - Tham nien trung binh (Tenure): {avg_tenure:.1f} thang")
        print(f"   - Cuoc hang thang trung binh (Monthly Charges): ${avg_mc:.2f}")
        print(f"   - Tong cuoc tich luy (Total Charges): ${avg_tc:.2f}")
        print(f"   - So dich vu add-on trung binh: {avg_addons:.1f} dich vu")
        print(f"   - Ty le Roi mang (Churn Rate): {churn_rate:.2f}%")

    # 8. Đóng gói lưu trữ Model & Scaler
    kmeans_save_path = os.path.join(MODEL_DIR, "kmeans_model.pkl")
    scaler_save_path = os.path.join(MODEL_DIR, "kmeans_scaler.pkl")

    joblib.dump(final_kmeans, kmeans_save_path)
    joblib.dump(scaler, scaler_save_path)
    joblib.dump(clustering_feature_names, os.path.join(MODEL_DIR, "kmeans_features.pkl"))

    print(f"\n[SAVED] Da luu mo hinh K-Means tai: {kmeans_save_path}")
    print(f"[SAVED] Da luu Scaler phan cum tai: {scaler_save_path}")

    # 9. VẼ BIỂU ĐỒ TRỰC QUAN HOÁ PHÂN CỤM (PCA 2D & CLUSTER PROFILE BAR CHART)
    # 9.1 PCA 2D Scatter Plot
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    df['pca_1'] = X_pca[:, 0]
    df['pca_2'] = X_pca[:, 1]

    plt.figure(figsize=(9, 7))
    sns.scatterplot(
        x='pca_1', y='pca_2', hue='cluster', palette='Set1', 
        data=df, alpha=0.7, s=40, style='cluster'
    )
    plt.title(f'PCA 2D Visualization of {k_best} Customer Clusters', fontsize=14, fontweight='bold')
    plt.xlabel(f'PCA Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}% var)', fontsize=12)
    plt.ylabel(f'PCA Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}% var)', fontsize=12)
    plt.legend(title='Cluster ID', loc='best')
    plt.tight_layout()
    pca_path = os.path.join(EVAL_DIR, "kmeans_pca_scatter.png")
    plt.savefig(pca_path, dpi=300)
    plt.close()
    print(f"[PLOT] Da xuat PCA 2D Scatter Plot: {pca_path}")

    # 9.2 Cluster Profile Comparison Bar Chart
    profile_summary = df.groupby('cluster')[['tenure_months', 'monthly_charges', 'total_active_addons', 'churn_flag']].mean()
    profile_summary['churn_flag'] = profile_summary['churn_flag'] * 100 # Chuyển sang %

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    sns.barplot(x=profile_summary.index, y=profile_summary['tenure_months'], ax=axes[0, 0], palette='Blues_d')
    axes[0, 0].set_title('Average Tenure (Months)', fontweight='bold')
    axes[0, 0].set_xlabel('Cluster')

    sns.barplot(x=profile_summary.index, y=profile_summary['monthly_charges'], ax=axes[0, 1], palette='Greens_d')
    axes[0, 1].set_title('Average Monthly Charges ($)', fontweight='bold')
    axes[0, 1].set_xlabel('Cluster')

    sns.barplot(x=profile_summary.index, y=profile_summary['total_active_addons'], ax=axes[1, 0], palette='Purples_d')
    axes[1, 0].set_title('Average Active Add-ons', fontweight='bold')
    axes[1, 0].set_xlabel('Cluster')

    sns.barplot(x=profile_summary.index, y=profile_summary['churn_flag'], ax=axes[1, 1], palette='Reds_d')
    axes[1, 1].set_title('Churn Rate (%)', fontweight='bold')
    axes[1, 1].set_xlabel('Cluster')

    plt.suptitle('Comparison of Key Metrics Across Customer Clusters', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    profile_path = os.path.join(EVAL_DIR, "kmeans_cluster_profile.png")
    plt.savefig(profile_path, dpi=300)
    plt.close()
    print(f"[PLOT] Da xuat Cluster Profile Bar Chart: {profile_path}")

    print("\n[COMPLETE] HOAN THANH BAI TOAN 2: CUSTOMER SEGMENTATION (K-MEANS)!")
    return final_kmeans, k_best

if __name__ == "__main__":
    train_and_evaluate_kmeans()
