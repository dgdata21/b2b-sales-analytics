import numpy as np
import pandas as pd
from scipy.stats import median_abs_deviation

from eda01_intro import print_section
from eda02_general import main as eda02_main

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

DISTRIBUTION_COLS = ["revenue", "margin"]
ROW_Z_SCORE_THRESHOLD = 3

MONTHLY_Z_SCORE_THRESHOLD = 2
MONTHLY_ROBUST_Z_THRESHOLD = 3

ROBUST_Z_SCALE = 0.6745


def add_z_scores(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in cols:
        mean = df[col].mean()
        std = df[col].std()
        df[f"{col}_zscore"] = (df[col] - mean) / std

        median = df[col].median()
        mad = (df[col] - median).abs().median()
        df[f"{col}_robust_zscore"] = np.where(
            mad != 0, ROBUST_Z_SCALE * (df[col] - median) / mad, 0
        )
    return df


def calc_robust_z(series: pd.Series) -> pd.Series:
    median = series.median()
    mad = median_abs_deviation(series, scale="normal")
    if mad == 0:
        return pd.Series(0.0, index=series.index)
    return (series - median) / mad


def main(
    eda_clean: pd.DataFrame | None = None,
    months_plot: pd.DataFrame | None = None,
    verbose: bool = True,
):
    if eda_clean is None or months_plot is None:
        _, eda_clean, months_plot = eda02_main(verbose=False)

    ######################################################
    # ROW-LEVEL DISTRIBUTION DIAGNOSTICS (NO BONUS)
    ######################################################
    distribution_shape = eda_clean[DISTRIBUTION_COLS].agg(["skew", "kurtosis"])
    if verbose:
        print_section("DISTRIBUTION SHAPE: SKEW & KURTOSIS (No BONUS)")
        print(distribution_shape.to_string())
        print()

    eda_clean = add_z_scores(eda_clean, DISTRIBUTION_COLS)

    if verbose:
        print_section(
            "ROW-LEVEL OUTLIERS: Z-SCORE VS ROBUST Z-SCORE (No BONUS)"
        )
        for col in DISTRIBUTION_COLS:
            n_outliers_z = (
                eda_clean[f"{col}_zscore"].abs() > ROW_Z_SCORE_THRESHOLD
            ).sum()
            n_outliers_robust = (
                eda_clean[f"{col}_robust_zscore"].abs() > ROW_Z_SCORE_THRESHOLD
            ).sum()
            print(
                f"{col}: Z-score outliers = {n_outliers_z:,} | "
                f"Robust Z-score outliers = {n_outliers_robust:,}"
            )
        print()

    ######################################################
    # MONTHLY-LEVEL Z-SCORE (revenue & margin, summed by period)
    ######################################################
    monthly_stats = months_plot.copy()
    monthly_stats["period"] = monthly_stats["period"].astype(str)

    monthly_stats["revenue_z"] = (
        monthly_stats["revenue"] - monthly_stats["revenue"].mean()
    ) / monthly_stats["revenue"].std()
    monthly_stats["margin_z"] = (
        monthly_stats["margin"] - monthly_stats["margin"].mean()
    ) / monthly_stats["margin"].std()

    if verbose:
        revenue_anomalies = monthly_stats[
            monthly_stats["revenue_z"].abs() > MONTHLY_Z_SCORE_THRESHOLD
        ].sort_values("revenue_z", ascending=False)
        margin_anomalies = monthly_stats[
            monthly_stats["margin_z"].abs() > MONTHLY_Z_SCORE_THRESHOLD
        ].sort_values("margin_z", ascending=False)

        print_section(
            f"MONTHLY REVENUE ANOMALIES (|Z| > {MONTHLY_Z_SCORE_THRESHOLD})"
        )
        if revenue_anomalies.empty:
            print("No revenue anomalies.")
        else:
            print(
                revenue_anomalies[["period", "revenue", "revenue_z"]]
                .round(2)
                .to_string(index=False)
            )
        print()

        print_section(
            f"MONTHLY MARGIN ANOMALIES (|Z| > {MONTHLY_Z_SCORE_THRESHOLD})"
        )
        if margin_anomalies.empty:
            print("No margin anomalies.")
        else:
            print(
                margin_anomalies[["period", "margin", "margin_z"]]
                .round(2)
                .to_string(index=False)
            )
        print()

    ######################################################
    # MONTHLY-LEVEL ROBUST Z-SCORE (revenue & margin, summed by period)
    ######################################################
    monthly_stats["revenue_robust_z"] = calc_robust_z(monthly_stats["revenue"])
    monthly_stats["margin_robust_z"] = calc_robust_z(monthly_stats["margin"])

    if verbose:
        robust_revenue_anomalies = monthly_stats[
            monthly_stats["revenue_robust_z"].abs()
            > MONTHLY_ROBUST_Z_THRESHOLD
        ]
        robust_margin_anomalies = monthly_stats[
            monthly_stats["margin_robust_z"].abs() > MONTHLY_ROBUST_Z_THRESHOLD
        ]

        print_section(
            f"MONTHLY REVENUE ANOMALIES (ROBUST |Z| > {MONTHLY_ROBUST_Z_THRESHOLD})"
        )
        if robust_revenue_anomalies.empty:
            print("No robust revenue anomalies.")
        else:
            print(
                robust_revenue_anomalies[
                    ["period", "revenue", "revenue_z", "revenue_robust_z"]
                ]
                .round(2)
                .to_string(index=False)
            )
        print()

        print_section(
            f"MONTHLY MARGIN ANOMALIES (ROBUST |Z| > {MONTHLY_ROBUST_Z_THRESHOLD})"
        )
        if robust_margin_anomalies.empty:
            print("No robust margin anomalies.")
        else:
            print(
                robust_margin_anomalies[
                    ["period", "margin", "margin_z", "margin_robust_z"]
                ]
                .round(2)
                .to_string(index=False)
            )
        print()

    return eda_clean, monthly_stats


if __name__ == "__main__":
    main()
