import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from eda01_intro import print_section
from eda06_customers01 import EXCLUDED_ORDER_IDS

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

PARQUET_PATH = r"D:/code/data_science/data/processed_files/final_eda.parquet"
MIN_ORDERS_FOR_RFM = 10
EXCLUDED_CUSTOMER_IDS = "3804cd0faee4e9d230ac18e7"


def main(verbose: bool = True) -> pd.DataFrame:
    ##########################################################################
    # DATA LOADING & PRE-PROCESSING
    ##########################################################################
    primary_df = pd.read_parquet(PARQUET_PATH)

    # if verbose:
    #     print_section("PRIMARY DATAFRAME HEAD", width=150)
    #     print(
    #         primary_df.head().to_string(index=False, float_format="%.1f")
    #     )
    # print()

    # Filter out bonus records and corrupted/excluded orders
    filtered_df = primary_df[primary_df["margin_category"] != "BONUS"]
    filtered_df = filtered_df[
        ~filtered_df["order_id"].isin(EXCLUDED_ORDER_IDS)
    ]

    # Get the global maximum date for Recency reference point
    max_date = primary_df["period"].max()

    # Aggregate behavioral features at the customer level
    # FIXED: Grouping filtered_df instead of primary_df to keep filters active
    client_df = (
        filtered_df.groupby("customer_id", observed=True)
        .agg(
            revenue_sum=("revenue", "sum"),
            margin_sum=("margin", "sum"),
            orders_cnt=("order_id", "nunique"),
            margin_pct_median=("margin_pct", "median"),
            margin_median=("margin", "median"),
            last_order_date=("period", "max"),
        )
        .reset_index()
    )

    # Remove the anomaly customer discovered during early EDA iterations
    client_df = client_df[client_df["customer_id"] != EXCLUDED_CUSTOMER_IDS]

    # Drop single-purchase or low-activity buyers
    client_df = client_df[client_df["orders_cnt"] > MIN_ORDERS_FOR_RFM]

    # Calculate derived financial features
    client_df["avg_check"] = client_df["revenue_sum"] / client_df["orders_cnt"]
    client_df["recency"] = (
        (max_date - client_df["last_order_date"]).dt.days / 30.44
    ).round(1)

    ##########################################################################
    # CORRELATION ANALYSIS (SPEARMAN)
    ##########################################################################
    corr_features = [
        "revenue_sum",
        "orders_cnt",
        "margin_pct_median",
        "avg_check",
        "margin_sum",
        "margin_median",
        "recency",
    ]

    spearman_corr = client_df[corr_features].corr(method="spearman")

    if verbose:
        print_section("SPEARMAN CORRELATION MATRIX", width=102)
        print(spearman_corr.map(lambda x: f"{x:.2%}").to_string(), "\n")

    ##########################################################################
    # VISUALIZATION
    ##########################################################################
    if verbose:
        plt.figure(figsize=(13, 8))
        sns.heatmap(
            spearman_corr,
            annot=True,
            cmap="coolwarm",
            fmt=".2%",
            cbar_kws={"label": "Spearman Rank Correlation Coefficient"},
        )
        plt.yticks(rotation=0)
        plt.title(
            "CUSTOMER FEATURES: SPEARMAN RANK CORRELATION MAP",
            pad=20,
            fontsize=14,
            weight="bold",
        )
        plt.tight_layout()
        plt.show()

    ##########################################################################
    # FEATURE TRANSFORMATION & SCALING
    ##########################################################################
    # Apply log1p transformation to fix heavily skewed distributions
    client_df["orders_cnt_log"] = np.log1p(client_df["orders_cnt"])
    client_df["avg_check_log"] = np.log1p(client_df["avg_check"])

    # Initialize standard scaler for distance-based clustering algorithms
    scaler = StandardScaler()
    clustering_features = [
        "orders_cnt_log",
        "avg_check_log",
        "margin_pct_median",
    ]
    X = scaler.fit_transform(client_df[clustering_features])

    # Evaluate optimal cluster counts using mathematical Silhouette Scores
    if verbose:
        print_section("SILHOUETTE METRICS EVALUATION", width=40)
        for k in range(2, 8):
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = km.fit_predict(X)
            print(
                f"Clusters: {k} | Silhouette Score:"
                f"{silhouette_score(X, labels):.4f}"
            )
        print()

    ##########################################################################
    # FINAL CLUSTERING EXECUTION & PROFILING
    ##########################################################################
    # Run the production KMeans model with the optimal 5 clusters setup
    # 5 clusters chosen based on silhouette analysis — see scores above")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    kmeans.fit(X)

    # FIXED: Optimized label generation via .labels_ attribute
    client_df["cluster"] = kmeans.labels_

    cluster_profile = (
        client_df.groupby("cluster")
        .agg(
            clients_cnt=("customer_id", "nunique"),
            avg_orders=("orders_cnt", "mean"),
            median_check=("avg_check", "median"),
            median_margin_pct=("margin_pct_median", "median"),
            recency_median=("recency", "median"),
            recency_mean=("recency", "mean"),
        )
        .round(1)
    )

    if verbose:
        print_section("FINAL CLUSTERS COMPREHENSIVE PROFILE", width=95)
        print(cluster_profile, "\n")

    return client_df


if __name__ == "__main__":
    client_df = main()

print()
