"""
Bootstrap confidence intervals (BCa, with percentile fallback) for the
median margin and median revenue of every manager, at order-id granularity.
 
If mngr_no_bonus is not passed in (script run standalone) — computes it via
eda05_manager01.main(). If passed in (called from an orchestrator like
main.py) — uses it directly, without recomputing eda05_manager01.
"""
 
import warnings
 
import numpy as np
import pandas as pd
from scipy.stats import bootstrap
 
from eda01_intro import print_section
from eda05_manager01 import main as eda05_manager01_main
 
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
 
N_BOOT = 5_000
ALPHA = 0.05
CONFIDENCE = 1 - ALPHA
MIN_ORDERS = 36
 
 
def _run_bootstrap(values, metric, n_boot, confidence):
    degenerate_flag = False
 
    # --- BCa ---
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = bootstrap(
                (values,),
                metric,
                confidence_level=confidence,
                n_resamples=n_boot,
                method="BCa",
                batch=100,
                vectorized=False,
            )
 
        degenerate_flag = any(
            "Degenerate" in str(w.message) or "invalid value" in str(w.message)
            for w in caught
        )
 
        lo, hi = result.confidence_interval.low, result.confidence_interval.high
 
        if not (np.isnan(lo) or np.isnan(hi)) and not degenerate_flag:
            return lo, hi, "BCa", False
    except Exception:
        pass
 
    # --- percentile (фолбэк) ---
    try:
        result = bootstrap(
            (values,),
            metric,
            confidence_level=confidence,
            n_resamples=n_boot,
            method="percentile",
            batch=100,
            vectorized=False,
        )
        return (
            result.confidence_interval.low,
            result.confidence_interval.high,
            "percentile",
            degenerate_flag,
        )
    except Exception:
        return (np.nan, np.nan, "failed", degenerate_flag)
 
 
def bootstrap_by_manager(df: pd.DataFrame) -> pd.DataFrame:
    results = []
 
    for mgr, grp in df.groupby("manager_id", observed=True):
        margins = grp["margin"].values
        revenues = grp["revenue"].values
        n = len(margins)
 
        if n < MIN_ORDERS:
            results.append(
                {
                    "manager": mgr,
                    "n_orders": n,
                    "marg_sum": np.sum(margins),
                    "marg_mean": np.mean(margins),
                    "marg_med": np.median(margins),
                    "marg_ci_lo": np.nan,
                    "marg_hi": np.nan,
                    "marg_width": np.nan,
                    "marg_error_pct": np.nan,
                    "marg_quality": "insufficient",
                    "marg_degenerate": False,
                    "rev_sum": np.sum(revenues),
                    "rev_mean": np.mean(revenues),
                    "rev_med": np.median(revenues),
                    "rev_ci_lo": np.nan,
                    "rev_hi": np.nan,
                    "rev_width": np.nan,
                    "rev_error_pct": np.nan,
                    "rev_quality": "insufficient",
                    "rev_degenerate": False,
                    "ci_method": "insufficient_data",
                }
            )
            continue
 
        m_lo, m_hi, m_method, m_degenerate = _run_bootstrap(
            margins, np.median, N_BOOT, CONFIDENCE
        )
        r_lo, r_hi, r_method, r_degenerate = _run_bootstrap(
            revenues, np.median, N_BOOT, CONFIDENCE
        )
 
        m_width = m_hi - m_lo if not np.isnan(m_hi) else np.nan
        r_width = r_hi - r_lo if not np.isnan(r_hi) else np.nan
 
        margin_med = np.median(margins)
        revenue_med = np.median(revenues)
 
        r_error = (r_width / abs(revenue_med) * 100.0) if revenue_med != 0 else np.nan
        m_error = (m_width / abs(margin_med) * 100.0) if margin_med != 0 else np.nan
 
        # --- QUALITY CATEGORIES (bounds 5% и 15%) ---
        if np.isnan(r_width) or np.isnan(r_error):
            r_quality = "failed"
        elif r_error < 5.0:
            r_quality = "high"
        elif r_error <= 15.0:
            r_quality = "medium"
        else:
            r_quality = "low"
 
        if np.isnan(m_width) or np.isnan(m_error):
            m_quality = "failed"
        elif m_error < 5.0:
            m_quality = "high"
        elif m_error <= 15.0:
            m_quality = "medium"
        else:
            m_quality = "low"
 
        results.append(
            {
                "manager": mgr,
                "n_orders": n,
                "marg_sum": np.sum(margins),
                "marg_mean": np.mean(margins),
                "marg_med": margin_med,
                "marg_ci_lo": m_lo,
                "marg_hi": m_hi,
                "marg_width": m_width,
                "marg_error_pct": m_error,
                "marg_quality": m_quality,
                "marg_degenerate": m_degenerate,
                "rev_sum": np.sum(revenues),
                "rev_mean": np.mean(revenues),
                "rev_med": revenue_med,
                "rev_ci_lo": r_lo,
                "rev_hi": r_hi,
                "rev_width": r_width,
                "rev_error_pct": r_error,
                "rev_quality": r_quality,
                "rev_degenerate": r_degenerate,
                # --- МЕТА ---
                "ci_method": f"{m_method}/{r_method}",  # margin/revenue
            }
        )
 
    return (
        pd.DataFrame(results)
        .sort_values("marg_sum", ascending=False)
        .reset_index(drop=True)
    )
 
 
def main(
    mngr_no_bonus: pd.DataFrame | None = None,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if mngr_no_bonus is None:
        mngr_no_bonus, _, _ = eda05_manager01_main(verbose=False)
 
    df_bootstrap = (
        mngr_no_bonus.groupby(by=["manager_id", "order_id"], observed=True)
        .agg(revenue=("revenue", "sum"), margin=("margin", "sum"))
        .reset_index()
    )
 
    ######################################################
    # BOOTSTRAP BCa CI BY MANAGER (margin median, revenue median)
    ######################################################
    bootstrap_df = bootstrap_by_manager(df_bootstrap)
 
    if verbose:
        print_section(" MANAGERS BOOTSTRAP ", width=260)
        print(bootstrap_df.to_string(index=False, float_format="%.2f"))
        print()
 
        # --- Сводка по деградировавшим случаям, чтобы не искать вручную ---
        degenerate_rows = bootstrap_df[
            bootstrap_df["marg_degenerate"] | bootstrap_df["rev_degenerate"]
        ]
        if not degenerate_rows.empty:
            print_section(
                " DEGENERATE BCa CASES (fell back to percentile) ", width=260
            )
            print(
                degenerate_rows[
                    [
                        "manager",
                        "n_orders",
                        "marg_degenerate",
                        "rev_degenerate",
                        "ci_method",
                    ]
                ].to_string(index=False)
            )
            print()
 
    return df_bootstrap, bootstrap_df
 
 
if __name__ == "__main__":
    df_bootstrap, bootstrap_df = main()
 
print()
