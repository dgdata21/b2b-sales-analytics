"""
Manager Pareto analysis: concentration of revenue/margin, Gini coefficient,
and anonymized display labels for reporting.
 
If mngr_monthly is not passed in (script run standalone) — computes it via
eda05_manager01.main(). If passed in (called from an orchestrator like
main.py) — uses it directly, without recomputing eda05_manager01.
"""
 
import numpy as np
import pandas as pd
 
from eda01_intro import print_section
from eda05_manager01 import main as eda05_manager01_main
 
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
 
PARETO_THRESHOLD_PCT = 80
 
 
def add_display_labels(
    df: pd.DataFrame, id_column: str, target_column: str = "manager", word_length: int = 6
) -> pd.DataFrame:
    letters = list("петровский")
    random_letters = np.random.choice(letters, size=(len(df), word_length))
    df = df.copy()
    df[target_column] = ["".join(row) for row in random_letters]
    return df[[id_column, target_column]]
 
 
def compute_pareto(df: pd.DataFrame, value_col: str) -> tuple[pd.DataFrame, int, float]:
    total = (
        df.groupby(by=["manager_id"], observed=True)[value_col]
        .sum()
        .reset_index(name=f"{value_col}_total")
    )
    total = total.sort_values(by=f"{value_col}_total", ascending=False).reset_index(
        drop=True
    )
 
    grand_total = total[f"{value_col}_total"].sum()
    total["share"] = total[f"{value_col}_total"] / grand_total * 100.0
    total["cum_share"] = total["share"].cumsum()
 
    n_at_threshold = (total["cum_share"] <= PARETO_THRESHOLD_PCT).sum() + 1
    pct_at_threshold = n_at_threshold / len(total) * 100
 
    return total, n_at_threshold, pct_at_threshold
 
 
def gini_coeff(array) -> float:
    array = np.sort(np.array(array, dtype=np.float64))
    n = array.size
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * array) / (n * np.sum(array))) - (n + 1) / n
 
 
def main(
    mngr_monthly: pd.DataFrame | None = None,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, float, float]:
    if mngr_monthly is None:
        _, mngr_monthly, _ = eda05_manager01_main(verbose=False)
 
    ######################################################
    # PARETO: REVENUE & MARGIN CONCENTRATION BY MANAGER
    ######################################################
    mngr_pareto_rev, n_80_rev, pct_mgr_80_rev = compute_pareto(
        mngr_monthly, "revenue"
    )
    mngr_pareto_mrg, n_80_mrg, pct_mgr_80_mrg = compute_pareto(
        mngr_monthly, "margin"
    )
 
    if verbose:
        print_section("MANAGERS PARETO (REVENUE)")
        print(f"\nМенеджеров всего: {len(mngr_pareto_rev)}")
        print(
            f"{PARETO_THRESHOLD_PCT}% revenue: {n_80_rev} managers "
            f"({pct_mgr_80_rev:.1f}%)\n"
        )
        print(
            mngr_pareto_rev[
                ["manager_id", "revenue_total", "share", "cum_share"]
            ].to_string(index=False),
            "\n",
        )
 
    ######################################################
    # GINI COEFFICIENT (REVENUE & MARGIN)
    ######################################################
    gini_rev = gini_coeff(mngr_pareto_rev["revenue_total"].values)
    gini_margin = gini_coeff(mngr_pareto_mrg["margin_total"].values)
 
    if verbose:
        print(
            "Total Gini coefficient of managers (revenue):",
            round(gini_rev * 100.0, 0),
            "%",
        )
        print(
            "Total Gini coefficient of managers (margin):",
            round(gini_margin * 100.0, 0),
            "%\n",
        )
 
    ######################################################
    # ANONYMIZED DISPLAY LABELS FOR REPORTING
    ######################################################
    labels = add_display_labels(mngr_pareto_rev[["manager_id"]], "manager_id")
    labels["manager"] = labels["manager"].str.capitalize()
 
    mngr_pareto_rev = pd.merge(labels, mngr_pareto_rev, on="manager_id").sort_values(
        by=["cum_share"]
    )
    mngr_pareto_mrg = pd.merge(labels, mngr_pareto_mrg, on="manager_id").sort_values(
        by=["cum_share"]
    )
 
    return mngr_pareto_rev, mngr_pareto_mrg, gini_rev, gini_margin
 
 
if __name__ == "__main__":
    mngr_pareto_rev, mngr_pareto_mrg, gini_rev, gini_margin = main()
print()
