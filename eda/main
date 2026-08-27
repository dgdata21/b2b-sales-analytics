import eda01_intro
import eda02_general
import eda03_general
import eda04_general

if __name__ == "__main__":
    eda01_intro.main()

    _, eda_clean, months_plot = eda02_general.main(verbose=True)
    eda_clean, monthly_stats = eda03_general.main(
        eda_clean=eda_clean, months_plot=months_plot, verbose=True
    )
    eda_clean, monthly_stats, period_bootstrap = eda04_general.main(
        eda_clean=eda_clean, monthly_stats=monthly_stats, verbose=True
    )
    print()
