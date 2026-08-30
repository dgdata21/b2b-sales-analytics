"""
Starting script of the EDA project.

Loads the prepared parquet file, calculates margin and margin categories,
optimizes data types, and saves the final dataset for further analysis.

Only the final dataframe df is needed from this script — import main()
from other modules instead of rerunning the whole preprocessing.
"""

import numpy as np
import pandas as pd

# ==================================================
# SETTINGS
# ==================================================
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

INPUT_PATH = r"/path/to/final_raw.parquet"
OUTPUT_PATH = r"/path/to/final_eda.parquet"

DIAG_COLS = ["period", "order_id", "revenue", "margin", "margin_pct"]

BONUS_REVENUE_THRESHOLD = 10
LOW_MARGIN_THRESHOLD = 10
MEDIUM_MARGIN_THRESHOLD = 20
EXTREME_MARGIN_PCT_THRESHOLD = 100


def print_section(title: str, width: int = 160, char: str = "=") -> None:
    print("\n", f" {title} ".center(width, char), "\n")


def show_extreme_margins(
    df: pd.DataFrame,
    label: str,
    threshold: float = EXTREME_MARGIN_PCT_THRESHOLD,
) -> None:
    extreme = df[df["margin_pct"].abs() > threshold]
    print_section(f"{label} (MARGIN PERCENT TOP 10)", width=82)
    print(
        extreme[DIAG_COLS]
        .sort_values("margin_pct")
        .head(10)
        .to_string(index=False)
    )


def main() -> pd.DataFrame:
    print_section("PRIMARY DATAFRAME STATISTIC", char="/")

    # ==================================================
    # LOAD AND FILTER DATA
    # ==================================================
    df = pd.read_parquet(INPUT_PATH)
    df = df[df["sale_cat"] == "sale"].reset_index(drop=True)

    print_section("DATAFRAME HEAD")
    print(df.head(10).to_string(index=False))

    print_section("DATAFRAME INFO", width=50)
    df.info()

    # ==================================================
    # CHECK NEGATIVE VALUES
    # ==================================================
    neg_revenue = df["revenue"] < 0
    neg_cost = df["cost"] < 0
    neg_logistic = df["logistic"] < 0

    print_section("NEGATIVE VALUES")
    print(f"Negative revenue:  {neg_revenue.sum():,}")
    print(f"Negative cost:     {neg_cost.sum():,}")
    print(f"Negative logistic: {neg_logistic.sum():,}")
    print(f"\nrevenue < 0 & cost < 0: {(neg_revenue & neg_cost).sum():,}")
    print(
        f"revenue < 0 & logistic < 0: {(neg_revenue & neg_logistic).sum():,}"
    )
    print(f"Revenue < 0: {(neg_revenue & ~neg_cost & ~neg_logistic).sum():,}")

    negative_revenue_only = df[neg_revenue & ~neg_cost & ~neg_logistic]

    print_section("NEGATIVE REVENUE WITH POSITIVE COSTS (TOP10)")
    print(
        negative_revenue_only[
            ["period", "order_id", "revenue", "cost", "logistic"]
        ]
        .sort_values(by=["revenue"])
        .head(10)
        .to_string(index=False)
    )

    # ==================================================
    # CALCULATE MARGIN
    # ==================================================
    df["margin"] = df["revenue"] - df["cost"] - df["logistic"]
    df["margin_pct"] = np.where(
        df["revenue"] != 0,
        df["margin"] / df["revenue"].abs() * 100,
        0,
    )

    print_section("PRELIMINARY DATAFRAME STATISTICS")
    print(df.describe())

    show_extreme_margins(df, "EXTREME VALUES")

    # ==================================================
    # CREATE MARGIN CATEGORIES
    # ==================================================
    conditions = [
        (df["revenue"] > 0) & (df["revenue"] < BONUS_REVENUE_THRESHOLD),
        df["margin"] < 0,
        (df["margin_pct"] >= 0) & (df["margin_pct"] < LOW_MARGIN_THRESHOLD),
        (df["margin_pct"] >= LOW_MARGIN_THRESHOLD)
        & (df["margin_pct"] < MEDIUM_MARGIN_THRESHOLD),
    ]
    choices = ["BONUS", "LOSS", "LOW_MARGIN", "MEDIUM_MARGIN"]
    df["margin_category"] = np.select(
        conditions, choices, default="HIGH_MARGIN"
    )

    df_no_bonus = df[df["margin_category"] != "BONUS"].reset_index(drop=True)

    # ==================================================
    # CHECK TRANSFORMED DATA
    # ==================================================
    print_section("TRANSFORMED DATAFRAME STATISTICS")
    print(df_no_bonus.describe())

    show_extreme_margins(df_no_bonus, "TRANSFORMED EXTREME VALUES")

    worst = df_no_bonus.loc[df_no_bonus["margin_pct"].idxmin()]
    print_section("WORST MARGIN PERCENT", width=60)
    print(worst)

    # ==================================================
    # OPTIMIZE DATA TYPES
    # ==================================================
    df["margin_category"] = df["margin_category"].astype("category")

    cat_cols = [
        "manager_id",
        "customer_id",
        "order_id",
        "sale_cat",
        "segment",
        "margin_category",
    ]
    for col in cat_cols:
        if col in df.columns and isinstance(
            df[col].dtype, pd.CategoricalDtype
        ):
            df[col] = df[col].cat.remove_unused_categories()

    # ==================================================
    # FINAL TRANSFORMATION
    # ==================================================
    df = df.drop(columns=["cost", "logistic", "sale_cat"])
    df[["revenue", "margin"]] = df[["revenue", "margin"]] / 1000.0

    print_section("TRANSFORMED DATAFRAME INFO", width=60)
    df_no_bonus.info()

    # ==================================================
    # SAVE EDA DATASET
    # ==================================================
    # df.to_parquet(
    #     OUTPUT_PATH, engine="pyarrow", index=False, compression="brotli"
    # )

    return df


if __name__ == "__main__":
    df = main()

print()

