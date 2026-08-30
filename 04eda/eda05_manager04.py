"""
Drill-down diagnostics for managers flagged with low-quality bootstrap
estimates (rev_quality == "low", see eda05_manager03): top orders and top
clients by revenue share, to help explain why the confidence interval is
wide for that manager.
 
If bootstrap_df/df_bootstrap/mngr_no_bonus are not passed in (script run
standalone) — computes them via eda05_manager01.main() and
eda05_manager03.main(). If passed in (called from an orchestrator like
main.py) — uses them directly, without recomputing earlier stages.
"""

import pandas as pd

from eda01_intro import print_section
from eda05_manager01 import main as eda05_manager01_main
from eda05_manager03 import main as eda05_manager03_main

FLAGGED_QUALITY = "low"


def drill_down_orders(manager_id: str, df: pd.DataFrame) -> pd.DataFrame:
    return df[df["manager_id"] == manager_id].sort_values("margin")


def drill_down_clients(manager_id: str, df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        df[df["manager_id"] == manager_id]
        .groupby("customer_id", observed=True)
        .agg(
            n_orders=("order_id", "nunique"),
            revenue_sum=("revenue", "sum"),
            margin_sum=("margin", "sum"),
        )
        .sort_values("revenue_sum", ascending=False)
    )
    grp["revenue_share_pct"] = (
        grp["revenue_sum"] / grp["revenue_sum"].sum() * 100
    )
    return grp


def diagnose_manager(
    manager_id: str,
    df_bootstrap: pd.DataFrame,
    mngr_no_bonus: pd.DataFrame,
    verbose: bool = True,
) -> dict:
    orders = drill_down_orders(manager_id, df_bootstrap)
    top_orders = orders.nlargest(5, "revenue")[
        ["order_id", "revenue", "margin"]
    ]

    top_clients = None
    if "customer_id" in mngr_no_bonus.columns:
        clients = drill_down_clients(manager_id, mngr_no_bonus)
        top_clients = clients.head(5)[
            ["n_orders", "revenue_sum", "revenue_share_pct"]
        ]

    if verbose:
        print_section(f" DIAGNOSIS: {manager_id} ", width=100)
        print(f"Заказов: {len(orders)}")
        print(orders[["order_id", "revenue", "margin"]].describe())

        print("\nTop 5 revenue orders:")
        print(top_orders)

        if top_clients is not None:
            print("\nTop 5 clients by revenue share:")
            print(top_clients)

        print()

    return {
        "manager_id": manager_id,
        "top_orders": top_orders,
        "top_clients": top_clients,
    }


def main(
    bootstrap_df: pd.DataFrame | None = None,
    df_bootstrap: pd.DataFrame | None = None,
    mngr_no_bonus: pd.DataFrame | None = None,
    verbose: bool = True,
) -> dict:
    if bootstrap_df is None or df_bootstrap is None:
        df_bootstrap, bootstrap_df = eda05_manager03_main(verbose=False)
    if mngr_no_bonus is None:
        mngr_no_bonus, _, _ = eda05_manager01_main(verbose=False)

    ######################################################
    # DIAGNOSE ALL MANAGERS FLAGGED AS LOW REVENUE QUALITY
    ######################################################
    flagged_managers = bootstrap_df.loc[
        bootstrap_df["rev_quality"] == FLAGGED_QUALITY, "manager"
    ]

    diagnoses = {
        manager_id: diagnose_manager(
            manager_id, df_bootstrap, mngr_no_bonus, verbose=verbose
        )
        for manager_id in flagged_managers
    }

    return diagnoses


if __name__ == "__main__":
    diagnoses = main()
