import eda01_intro
import eda02_general
import eda03_general
import eda04_general
import eda05_manager01
import eda05_manager02
import eda05_manager03
import eda05_manager04
import eda06_customers01
import eda06_customers02
import eda06_customers03

if __name__ == "__main__":
    eda01_intro.main()

    _, eda_clean, months_plot = eda02_general.main(verbose=True)
    eda_clean, monthly_stats = eda03_general.main(
        eda_clean=eda_clean, months_plot=months_plot, verbose=True
    )
    eda_clean, monthly_stats, period_bootstrap = eda04_general.main(
        eda_clean=eda_clean, monthly_stats=monthly_stats, verbose=True
    )

    mngr_no_bonus, mngr_monthly, mngr_stat = eda05_manager01.main(verbose=True)
    mngr_pareto_rev, mngr_pareto_mrg, gini_rev, gini_margin = (
        eda05_manager02.main(mngr_monthly=mngr_monthly, verbose=True)
    )
    df_bootstrap, bootstrap_df = eda05_manager03.main(
        mngr_no_bonus=mngr_no_bonus, verbose=True
    )
    manager_diagnoses = eda05_manager04.main(
        bootstrap_df=bootstrap_df,
        df_bootstrap=df_bootstrap,
        mngr_no_bonus=mngr_no_bonus,
        verbose=True,
    )

    df_clean, customers_df = eda06_customers01.main(verbose=True)
    df_clean = eda06_customers02.main(df=df_clean, verbose=True)
    df_clean = eda06_customers03.main(df=df_clean, verbose=True)

    print()

