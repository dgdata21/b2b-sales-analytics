"""
Manager-level statistics: preliminary and final aggregates.
 
Loads the final EDA dataset, removes BONUS-category rows and known
test/garbage manager_id and order_id values, then computes per-manager
order-count, revenue, margin, and margin_pct aggregates — both before
and after cleaning, for comparison.
 
Only mngr_no_bonus, mngr_monthly and mngr_stat are needed downstream —
import main() from other modules instead of rerunning this script.
"""
 
import pandas as pd
 
from eda01_intro import print_section
 
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
 
PARQUET_PATH = r"D:/code/data_science/data/processed_files/final_eda.parquet"
 
# Test/garbage manager_id values found during EDA — excluded from the
# final manager-level analysis (see mngr_no_bonus below).
EXCLUDED_MANAGER_IDS = [
    "1b3ceda85b1393bcaf7c18e9",
    "1f4703819501294873b92324",
    "284b231f8b56540606ae95ee",
    "51c05ae333327444a65c7dd1",
    "61680597251f097d64beb537",
    "",
    "0b853fe59777f78de8578c4f",
    "1a9d5914486e614ae1e7b9f8",
    "2428355982bbe513cfc9b72e",
    "333cb0189f94b2450f122dff",
    "386f3a7bace3f92d505e8cf7",
    "5aefe8053e0f23073a0932cd",
    "8781982b2067274ff822da33",
    "df4f08b61dfe37019ad15493",
    "",
    "5c5fa43d858f90b91b46cb2c",
]
 
# Test/garbage order_id values found during EDA — same reasoning as above.
EXCLUDED_ORDER_IDS = [
    "85cd4c52-6243-aabe-11ec-9fb13867df78",
    "84e14c52-6243-aabe-11ec-b0d2cdf9346a",
    "008b4c52-6243-aabe-11eb-e08cfdac8ca0",
]
 
MANAGER_AGG_SPEC = {
    "order_id": "nunique",
    "revenue": ["sum", "max", "min", "mean", "median", "std"],
    "margin": ["sum", "max", "min", "mean", "median", "std"],
    "margin_pct": ["max", "min", "mean", "median", "std"],
}
 
 
def aggregate_manager_stats(
    df: pd.DataFrame, group_cols: list[str] = ["manager_id"]
) -> pd.DataFrame:
    return (
        df.groupby(by=group_cols, observed=True)
        .agg(MANAGER_AGG_SPEC)
        .reset_index()
    )
 
 
def main(
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.read_parquet(PARQUET_PATH)
    mngr_no_bonus = df[df["margin_category"] != "BONUS"]
 
    preliminary_stat = aggregate_manager_stats(mngr_no_bonus)
 
    if verbose:
        print_section("PRIMARY MANAGER DATAFRAME STATISTIC", char="$")
 
        print_section("MANAGER DATAFRAME HEAD")
        print(
            mngr_no_bonus.head().to_string(index=False, float_format="%.2f")
        )
 
        print_section("MANAGER DATAFRAME TAIL")
        print(
            mngr_no_bonus.tail().to_string(index=False, float_format="%.2f")
        )
 
        print_section("MANAGER DATAFRAME INFO", width=50)
        mngr_no_bonus.info()
 
        print_section("PRELIMINARY MANAGER STATISTIC")
        print(preliminary_stat.round(2).to_string(index=False))
 
    ######################################################
    # REMOVE TEST/GARBAGE MANAGER & ORDER IDS
    ######################################################
    mngr_no_bonus = mngr_no_bonus[
        ~mngr_no_bonus["manager_id"].isin(EXCLUDED_MANAGER_IDS)
    ]
    mngr_no_bonus = mngr_no_bonus[
        ~mngr_no_bonus["order_id"].isin(EXCLUDED_ORDER_IDS)
    ]
    mngr_no_bonus = mngr_no_bonus.drop(
        columns=["segment", "margin_category"]
    ).reset_index(drop=True)
 
    ######################################################
    # MONTHLY AGGREGATES (used by Pareto/Gini in eda05_manager02)
    ######################################################
    mngr_monthly = (
        mngr_no_bonus.groupby(by=["manager_id", "period"], observed=True)
        .agg({"revenue": "sum", "margin": "sum", "margin_pct": "median"})
        .reset_index()
    )
 
    mngr_stat = aggregate_manager_stats(mngr_no_bonus)
 
    if verbose:
        print_section("FINAL MANAGER STATISTIC")
        print(mngr_stat.round(2).to_string(index=False))
        print()
 
    return mngr_no_bonus, mngr_monthly, mngr_stat
 
 
if __name__ == "__main__":
    mngr_no_bonus, mngr_monthly, mngr_stat = main()
 
print()
