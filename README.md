# B2B Sales Analytics (2021–2025)

Analysis of B2B sales performance for a single company over a 4.5-year period (Jan 2021 – Sep 2025): from raw database exploration to a cleaned, analysis-ready dataset, revenue/margin trend analysis, manager-level performance analysis, and customer cohort/LTV/segmentation analysis.

**Stack:** SQL · Python (pandas, NumPy, SciPy, scikit-learn) · Parquet · Matplotlib/Seaborn

---

## Table of Contents
- [Project Overview](#project-overview)
- [Data & Anonymization](#data--anonymization)
- [Project Structure](#project-structure)
- [01 — Database Exploration](#01--database-exploration)
- [02 — Data Extraction & Loading](#02--data-extraction--loading)
- [03 — Data Reading & Pre-Aggregation](#03--data-reading--pre-aggregation)
- [04 — Exploratory Data Analysis](#04--exploratory-data-analysis)
- [05 — Manager-Level Analysis](#05--manager-level-analysis)
- [06 — Customer Analysis](#06--customer-analysis)
- [Key Findings](#key-findings)
- [Next Steps](#next-steps)
- [How to Run](#how-to-run)

---

## Project Overview

This project analyzes real B2B sales transactions from a single company, covering January 2021 through September 2025. The raw data follows a **period → manager → client → order → revenue** hierarchy. The analysis covers aggregate revenue/margin trends, a manager-level breakdown of performance, and a customer-level view (retention, LTV, and behavioral segmentation), without SKU-level detail.

**Business questions answered:**
- How have total revenue, total margin, and margin % evolved year over year and quarter over quarter?
- How concentrated is revenue across managers, and how reliable are per-manager performance estimates?
- How well does the company retain customers over time, and what is a typical customer's lifetime value?
- Are there distinct customer segments with meaningfully different behavior, and which segments carry the most churn risk?

## Data & Anonymization

The underlying data comes from a real company's transactional database (1C Enterprise / PostgreSQL) and has been anonymized before publication:

- `manager_id` and `client_id` are original 1C-generated GUIDs, replaced with a **salted HMAC-SHA256 hash** (truncated hex). The mapping is deterministic, so any grouping remains internally consistent — but original identities cannot be recovered.
- The salt used for hashing is kept outside the repository (not committed).
- No client names, manager names, contact details, or other identifying fields are included anywhere in the repository.

> SKU-level detail was deliberately excluded — this analysis focuses on overall revenue, margin, manager-level, and customer-level dynamics, not product mix.

## Project Structure

```
├── 01db_exploring/   # exploring the source schema, keys, table relationships
├── 02data_load/      # SQL extraction from the source DB, saved as Parquet
├── 03data_read/      # reading Parquet, pre-aggregation, saved locally
├── 04eda/
│   ├── eda01_intro       # duplicate/missing-value checks, anonymization of sensitive fields
│   ├── eda02_general     # YoY & quarterly revenue/margin trends
│   ├── eda03_general     # outlier & anomaly detection (Z-score, robust Z-score)
│   ├── eda04_general     # bootstrap confidence intervals by period
│   ├── eda05_manager01   # manager-level cleaning & aggregation
│   ├── eda05_manager02   # manager Pareto & Gini analysis
│   ├── eda05_manager03   # manager-level bootstrap confidence intervals
│   ├── eda05_manager04   # drill-down diagnosis of low-quality manager estimates
│   ├── eda06_customers01 # customer-level cleaning & aggregation
│   ├── eda06_customers02 # customer cohort retention analysis
│   ├── eda06_customers03 # customer LTV by cohort
│   └── eda06_customers04 # RFM-style customer segmentation (KMeans)
├── main.py
├── results.txt
└── README.md
```

## 01 — Database Exploration
📂 [`01db_exploring/`](./01db_exploring)

Explored the source database schema behind the company's 1C Enterprise system to identify the relevant tables, keys, and relationships needed for the analysis.

## 02 — Data Extraction & Loading
📂 [`02data_load/`](./02data_load)

Extracted the relevant data via SQL and saved it locally in Parquet format for efficient, reproducible downstream processing.

## 03 — Data Reading & Pre-Aggregation
📂 [`03data_read/`](./03data_read)

Read the Parquet files, performed initial aggregation, and saved the resulting dataset locally for the analysis stage.

## 04 — Exploratory Data Analysis
📂 [`04eda/`](./04eda)

- Checked for duplicate records and missing values
- Anonymized sensitive fields (manager and client identifiers — see [Data & Anonymization](#data--anonymization))
- Detected outliers and monthly anomalies via Z-score and robust (MAD-based) Z-score
- Computed bootstrap (BCa) confidence intervals for median revenue and margin by period
- Analyzed revenue, margin, and margin % trends at two levels of granularity:

![Revenue by year](./04eda/Figure_1.png)
Fig. 1 — Year-over-year total revenue, total margin, and median margin %.

![Revenue by quarter](./04eda/Figure_2.png)
Fig. 2 — Quarterly total revenue, total margin, and median margin %.

## 05 — Manager-Level Analysis
📂 [`04eda/eda05_manager01–04`](./04eda)

Beyond the aggregate trends, the same dataset was broken down by manager (28 managers total) to understand how revenue is distributed across the sales team and how reliable per-manager estimates are.

**Methods:**
- **Pareto analysis** — revenue and margin concentration across managers
- **Gini coefficient** — inequality of revenue/margin distribution across the sales team
- **Bootstrap confidence intervals (BCa, with percentile fallback)** — for the median revenue and median margin of each manager, with automatic quality flags (`high` / `medium` / `low`) based on relative CI width
- **Drill-down diagnosis** — for every manager flagged `low` quality, an automatic breakdown of their top orders and top clients by revenue share, to explain *why* the estimate is unstable rather than just flagging that it is

## 06 — Customer Analysis
📂 [`04eda/eda06_customers01–04`](./04eda)

The same dataset was also analyzed from the customer side: how well the company retains customers over time, how much value a typical customer generates across their lifecycle, and whether distinct behavioral segments exist.

**Methods:**
- **Cohort retention analysis** — customers grouped by acquisition month (first-ever order), tracking what % of each cohort is still ordering N months later. Cohort assignment is computed on each customer's *full* order history (not on a pre-filtered window) to avoid mistaking long-standing customers for new ones, and no order-volume filter is applied before this stage — an early version of this analysis filtered out low-order customers first, which silently restricted retention measurement to already-loyal customers and made retention look artificially close to 100% (a classic survivorship-bias trap).
- **Customer LTV by cohort** — cumulative margin per customer over cohort age, visualized as a heatmap. Cohort-age cells beyond a cohort's actual observed lifetime are explicitly masked (not filled with 0), so young cohorts don't display a flat, falsely "predicted" LTV for months that haven't happened yet.
- **RFM-style segmentation (KMeans)** — customers clustered on order frequency, average check size, and margin %, after log-transforming skewed features and standardizing. Spearman rank correlation between customer-level features is computed first to understand relationships before clustering.

> Cluster count (k=5) was chosen for interpretability, not because it maximizes the silhouette score — the silhouette curve is close to flat across k=2–7 (all in the weak ~0.27–0.30 range, with k=2 technically scoring highest). KMeans is used here descriptively, to produce actionable business segments, rather than as a rigorously optimal partition.

![Cohort retention](./04eda/Figure_4.png)
Fig. 3 — Customer cohort retention heatmap (% of cohort still active by month).

![Customer LTV](./04eda/Figure_5.png)
Fig. 4 — Cumulative LTV per customer by acquisition cohort (based on margin).

![Customer segments](./04eda/Figure_6.png)
Fig. 5 — Spearman correlation map of customer-level features.

## Key Findings

- Revenue is relatively stable across 2021–2025 rather than showing strong linear growth, fluctuating in a ~110k–155k band per quarter — consistent with a mature, stable B2B revenue base.
- Q4 is consistently the strongest quarter each year (2021, 2022, 2024), pointing to a clear seasonal pattern useful for planning.
- Q2 2022 (specifically March–July) shows a sharp, one-off spike in both margin (~24.5k vs a typical 15–18k) and median margin % (~17.5% vs a ~13.5–14% baseline). This coincides with a period of sharp market volatility in the broader economy; margins normalized back to baseline from 2023 onward, confirming it was a temporary market-driven effect rather than a structural shift.
- Median margin % has drifted modestly upward in 2024–2025 (~14.5–15.5%) compared to 2021–2023 (~13.5%), suggesting a slight efficiency improvement despite flat revenue.
- **Revenue is heavily concentrated across managers:** just 10 of 28 managers (35.7%) generate 80% of total revenue.
- **The Gini coefficient for manager revenue is 63%** (61% for margin) — a very high concentration, pointing to significant key-person dependency in the sales structure.
- **9 of 28 managers (32%) have "low"-quality bootstrap estimates** (CI width >15% of the median), almost all with under ~2,000 orders in the period.
- **Drill-down diagnosis explains the instability:** for several low-quality managers, the wide confidence interval isn't a data problem — it's real single-client dependency. One manager's revenue is 98.6% dependent on a single client; another splits 77%/22% across just two clients. This is itself a business risk (client concentration / churn exposure) independent of the statistical noise it causes.
- **Customer retention declines gradually rather than falling off a cliff**, and varies noticeably by cohort — a healthier pattern than either near-100% retention (which turned out to be a measurement artifact in an earlier iteration) or a sharp early drop-off.
- **New customer acquisition spiked sharply in November 2024** (~70 new customers vs. a typical 1–10/month) — worth investigating as either a successful campaign, a new sales channel, or a one-off bulk signup, since it's a clear outlier against the rest of the period.
- **Average check size and margin % are inversely correlated (Spearman ≈ -52%):** larger orders consistently carry lower margin %, consistent with volume-based discounting typical in B2B pricing.
- **RFM segmentation surfaces a specific at-risk group:** one cluster combines the highest margin % (~19%) with the longest median recency (customers who haven't ordered in ~9 months) — i.e., the company's most profitable customer segment is also the one going quiet, making it a priority for re-engagement.

## Next Steps

- Revenue forecasting (Prophet) for near-term planning

## How to Run

```bash
git clone https://github.com/dgdata21/b2b-sales-analytics.git
cd b2b-sales-analytics
pip install -r requirements.txt
jupyter notebook
```

---

**Author:** Dmitrii Gorbachev — [LinkedIn](https://www.linkedin.com/in/dmitrii-gorbachev-0730811b8) — [GitHub](https://github.com/dgdata21/b2b-sales-analytics)
