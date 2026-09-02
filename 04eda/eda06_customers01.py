"""
Customer-level statistics: preliminary and cleaned aggregates.
 
Loads the final EDA dataset and removes BONUS-category rows and a handful
of known garbage order_id values. Also computes a strict, low-volume/
unstable-customer filter used only for the top-customer statistics printed
in this module — NOT applied to the cohort/LTV analysis downstream (see
main()'s docstring for why).
 
Two datasets are returned: the broad, lightly-cleaned df_clean (for cohort/
LTV analysis in eda06_customers02/03) and the strictly-filtered
customers_df (for top-customer revenue/margin stats). Import main() from
other modules instead of rerunning this script.
"""

import pandas as pd

from eda01_intro import print_section

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

PARQUET_PATH = r"D:/code/data_science/data/processed_files/final_eda.parquet"

# Test/garbage order_id values found during EDA — excluded from the
# final customer-level analysis.
EXCLUDED_ORDER_IDS = [
    "85cd4c52-6243-aabe-11ec-9fb13867df78",
    "84e14c52-6243-aabe-11ec-b0d2cdf9346a",
    "008b4c52-6243-aabe-11eb-e08cfdac8ca0",
    "90434c52-6243-aabe-11f0-73700756df74",
]

# Customers with fewer orders than this, or with revenue std above this
# threshold, are treated as noise/outliers and excluded from the clean base.
MIN_ORDERS_THRESHOLD = 100
MAX_REVENUE_STD_THRESHOLD = 100

CUSTOMERS_AGG_SPEC = {
    "order_id": "nunique",
    "revenue": ["sum", "max", "min", "mean", "median", "std"],
    "margin": ["sum", "max", "min", "mean", "median", "std"],
    "margin_pct": ["max", "min", "mean", "median", "std"],
}


def aggregate_customers_stats(
    df: pd.DataFrame, group_cols: list[str] = ["customer_id"]
) -> pd.DataFrame:
    return (
        df.groupby(by=group_cols, observed=True)
        .agg(CUSTOMERS_AGG_SPEC)
        .reset_index()
    )


def main(verbose: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_parquet(PARQUET_PATH)
    df_clean = df[df["margin_category"] != "BONUS"]
    df_clean = df_clean[~df_clean["order_id"].isin(EXCLUDED_ORDER_IDS)]
    df_clean["year"] = df_clean["period"].dt.year
    df_clean["month"] = df_clean["period"].dt.month

    preliminary_stat = aggregate_customers_stats(df_clean)

    if verbose:
        print_section(
            "PRELIMENTARY PIVOT CUSTOMERS STATISTIC (TOP30)", width=175
        )
        print(
            preliminary_stat.sort_values(
                by=[("revenue", "sum")], ascending=False
            )
            .rename(
                columns={
                    "revenue": "revenue    ",
                    "margin": "margin    ",
                    "order_id": "n_orders   ",
                },
            )
            .head(30)
            .reset_index(drop=True)
            .to_string(float_format="%.2f")
        )

    ######################################################
    # STRICT CUSTOMER FILTER — FOR TOP-CUSTOMER STATS ONLY,
    # NOT FOR COHORT/LTV ANALYSIS (see docstring above)
    ######################################################
    customers_excluded_ids = preliminary_stat.loc[
        (preliminary_stat[("order_id", "nunique")] < MIN_ORDERS_THRESHOLD)
        | (preliminary_stat[("revenue", "std")] > MAX_REVENUE_STD_THRESHOLD),
        ("customer_id", ""),
    ].tolist()

    customers_df = df_clean[
        ~df_clean["customer_id"].isin(customers_excluded_ids)
    ]

    if verbose:
        customers_groupped = aggregate_customers_stats(customers_df)
        print_section("PIVOT CUSTOMERS STATISTIC (CLEAN TOP30)")
        print(
            customers_groupped.sort_values(
                by=[("revenue", "sum")], ascending=False
            )
            .rename(
                columns={
                    "revenue": "revenue    ",
                    "margin": "margin    ",
                    "order_id": "n_orders",
                },
            )
            .head(30)
            .to_string(index=False, float_format="%.2f")
        )

    return df_clean, customers_df


if __name__ == "__main__":
    df_clean, customers_df = main()

print()
