"""
Customer cohort retention analysis.
 
Groups the broad customer base (df_clean from eda06_customers01 — garbage
excluded, but NOT filtered by order volume/stability, to avoid survivorship
bias) into monthly acquisition cohorts starting from COHORT_START_DATE, then
computes and visualizes a month-over-month retention table (% of each
cohort still placing orders N months after acquisition).
 
If df is not passed in (script run standalone) — computes it via
eda06_customers01.main(). If passed in (called from an orchestrator like
main.py) — uses it directly, without recomputing the previous stage.
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from eda01_intro import print_section
from eda06_customers01 import main as eda06_customers01_main

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

# Only customers whose cohort_month (first-ever order) falls on/after this
# date are included — this keeps the analysis focused on genuinely new
# customers rather than long-standing ones who simply ordered again during
# this window.
COHORT_START_DATE = "2023-01-01"


def get_cohort_index(
    df: pd.DataFrame, current_col: str, cohort_col: str
) -> pd.Series:
    current_year = df[current_col].dt.year
    current_month = df[current_col].dt.month
    cohort_year = df[cohort_col].dt.year
    cohort_month = df[cohort_col].dt.month
    return (current_year - cohort_year) * 12 + (current_month - cohort_month)


def main(
    df: pd.DataFrame | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    if df is None:
        df_clean, _ = eda06_customers01_main(verbose=False)
        df = df_clean

    ######################################################
    # ASSIGN EACH CUSTOMER TO AN ACQUISITION COHORT
    ######################################################
    # IMPORTANT: cohort_month must be computed on the customer's FULL order
    # history, not on data already truncated to COHORT_START_DATE — otherwise
    # a long-standing customer whose first order after the cutoff happens to
    # fall in, say, 2024-01 would be mistaken for a brand-new customer
    # acquired that month, massively inflating that cohort's size and
    # retention. Likewise, df must NOT be pre-filtered by order volume —
    # that would only keep already-loyal, high-order-count customers and
    # make retention look artificially high (survivorship bias).
    df["order_month"] = df["period"].dt.to_period("M")
    df["cohort_month"] = df.groupby(by=["customer_id"], observed=True)[
        "order_month"
    ].transform("min")
    df["cohort_index"] = get_cohort_index(df, "order_month", "cohort_month")

    # Only now do we restrict to cohorts genuinely acquired on/after
    # COHORT_START_DATE — this keeps cohort ages/sizes meaningful instead of
    # lumping the entire pre-existing customer base into one inflated cohort.
    cohort_start_period = pd.Period(COHORT_START_DATE, freq="M")
    df = df[df["cohort_month"] >= cohort_start_period].reset_index(drop=True)

    cohort_data = (
        df.groupby(by=["cohort_month", "cohort_index"])["customer_id"]
        .nunique()
        .reset_index()
    )
    cohort_pivot = cohort_data.pivot(
        index="cohort_month", columns="cohort_index", values="customer_id"
    )
    cohort_size = cohort_pivot.iloc[:, 0]
    retention_table = cohort_pivot.divide(cohort_size, axis=0) * 100

    if verbose:
        print_section("COHORTS", width=190)
        print(cohort_pivot)
        print_section("RETENTION TABLE, %", width=220)
        print(retention_table.round(1))

        plt.figure(figsize=(13, 8))
        plt.title("COHORTS RETENTION, %", fontsize=16, pad=20)
        plt.ylabel("Cohort Birth Month", fontsize=12)
        plt.xlabel("Cohort Age (Months)", fontsize=12)
        sns.heatmap(
            data=retention_table,
            annot=True,
            fmt=".1f",
            cmap="YlGnBu",
        )
        plt.tight_layout()
        plt.show()

    return df


if __name__ == "__main__":
    df = main()
