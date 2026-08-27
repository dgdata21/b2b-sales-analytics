import pandas as pd
from parquet_read_core import get_sample, cats_process, SALT, anon_id


def anonymize(df: pd.DataFrame) -> pd.DataFrame:
    """Псевдонимизация manager_id и customer_id. Возвращает копию df."""
    df = df.copy()
    df["manager_id"] = df["manager_id"].apply(lambda x: anon_id(x, SALT))
    df["customer_id"] = df["customer_id"].apply(lambda x: anon_id(x, SALT))
    return df


# ==================================================
# PREVIEW RANDOM SAMPLE
# ==================================================
def main() -> None:
    pre_sample = get_sample()

    print("\n", " ORIGINAL RANDOM SAMPLE INFO ".center(60, "="), "\n")
    pre_sample.info()

    print("\n", " ORIGINAL RANDOM SAMPLE HEAD ".center(180, "="), "\n")
    print(pre_sample.head(7).to_string(index=False))

    # ==================================================
    # TRANSFORM RANDOM SAMPLE
    # ==================================================

    pre_sample = cats_process(pre_sample)
    pre_sample = anonymize(pre_sample)

    # ==================================================
    # PREVIEW TRANSFORMED SAMPLE
    # ==================================================

    print("\n", " TRANSFORMED RANDOM SAMPLE INFO ".center(60, "="), "\n")
    pre_sample.info()

    print("\n", " TRANSFORMED RANDOM SAMPLE HEAD ".center(180, "="), "\n")
    print(pre_sample.head(7).to_string(index=False))


if __name__ == "__main__":
    main()
    
