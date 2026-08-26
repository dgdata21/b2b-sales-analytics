import pandas as pd

from parquet_read_core import load_columns, cats_process
from parquet_read_01 import anonymize

# ==================================================
# SETTINGS
# ==================================================
OUTPUT_PATH = r"/path_to_save/final_raw.parquet"

CHOSEN_COLS = [
    "period",
    "manager_id",
    "customer_id",
    "order_id",
    "sale_cat",
    "segment",
    "revenue",
    "cost",
    "logistic",
]

GROUP_COLS = [
    "period",
    "manager_id",
    "customer_id",
    "order_id",
    "sale_cat",
    "segment",
]

AGG_COLS = {
    "revenue": "sum",
    "cost": "sum",
    "logistic": "sum",
}


# ==================================================
# LOAD AND TRANSFORM DATA
# ==================================================
def main(where: str | None = None) -> pd.DataFrame:

    sample = load_columns(CHOSEN_COLS, where=where)

    print(
        "\n",
        " ORIGINAL SAMPLE INFO (CHOSEN COLUMNS) ".center(60, "="),
        "\n",
    )
    sample.info()

    sample = anonymize(sample)
    sample = cats_process(sample)

    print(
        "\n",
        " TRANSFORMED SAMPLE INFO (CHOSEN COLUMNS) ".center(60, "="),
        "\n",
    )
    sample.info()

    # ==================================================
    # AGGREGATE DATA
    # ==================================================
    final = (
        sample.groupby(GROUP_COLS, observed=True).agg(AGG_COLS).reset_index()
    )

    # ==================================================
    # FINAL DATAFRAME PREVIEW
    # ==================================================
    print("\n", " FINAL DATAFRAME HEAD ".center(130, "*"), "\n")
    print(final.head(10).to_string(index=False))

    print("\n", " FINAL DATAFRAME TAIL ".center(130, "*"), "\n")
    print(final.tail(10).to_string(index=False))

    print("\n", " FINAL DATAFRAME INFO ".center(50, "="), "\n")
    final.info()

    print("\n", " FINAL DATAFRAME DTYPES ".center(50, "="), "\n")
    print(final.dtypes)

    # ==================================================
    # DATA QUALITY CHECKS
    # ==================================================
    missing_summary = pd.DataFrame(
        {
            "missing_count": final.isna().sum(),
            "missing_percent": final.isna().mean() * 100,
        }
    )

    print("\n", " FINAL MISSING VALUES ".center(50, "-"), "\n")
    print(missing_summary)

    duplicate_orders = final[final.duplicated(subset=["order_id"], keep=False)]

    print("\n", " FINAL DUPLICATES ".center(80, "-"), "\n")
    print(duplicate_orders.round(2).sort_values("order_id"))

    # ==================================================
    # SAVE FINAL DATASET
    # ==================================================

    final.to_parquet(
        OUTPUT_PATH,
        engine="pyarrow",
        index=False,
    )

    return final


if __name__ == "__main__":
    main()
