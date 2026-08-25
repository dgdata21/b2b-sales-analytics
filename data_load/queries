query_clickhouse = """
SELECT toYear(ans.date)                   AS extract_year
     , toMonth(ans.date)                  AS extract_month
     , toString(ans.date)                 AS date
     , toString(toStartOfMonth(ans.date)) AS period
     , ans.agent_link                     AS manager_id
     , anp.kag_link                       AS customer_id
     , toString(ans.record_id)            AS order_id
     , ans.product_folder                 AS sku
     , ans.product_folder_link            AS sku_id
     , anp.partner_reg_date               AS customer_reg
     , sum(amount)                        AS amount
     , sum(revenue_gross)                 AS revenue
     , sum(cost_gross)                    AS cost
     , sum(add_cost_gross)                AS logistic
FROM analytics.sales ans
         LEFT JOIN analytics.partners anp USING (partner_link)
WHERE ans.date >= '2021-01-01'
  AND ans.date < '2025-10-01'
  AND ans.agent_link != ''
  AND ans.partner_link != ''
  AND anp.partner_inn != ''
  AND NOT like(lower(anp.partner_inn), '00%')
GROUP BY extract_year,
         extract_month,
         date,
         period,
         manager_id,
         customer_id,
         order_id,
         sku,
         sku_id,
         customer_reg
ORDER BY date, order_id, sku_id
"""

query_pgsql = """
SELECT EXTRACT(YEAR FROM ae.date)::int    AS extract_year
     , EXTRACT(MONTH FROM ae.date)::int   AS extract_month
     , ae.date                            AS date
     , DATE_TRUNC('month', ae.date)::date AS period
     , ae.agent_link                      AS manager_id
     , ap.kag_link                        AS customer_id
     , ae.record_id                       AS order_id
     , ae.product_folder                  AS sku
     , ae.product_folder_link             AS sku_id
     , ap.partner_reg_date                AS customer_reg
     , SUM(ae.amount)                     AS amount
     , SUM(ae.revenue_gross)              AS revenue
     , SUM(ae.cost_gross)                 AS cost
     , SUM(ae.add_cost_gross)             AS logistic
FROM air_efficiency ae
         LEFT JOIN air_partners ap USING (partner_link)
WHERE ae.date BETWEEN '2021-01-01' AND '2025-09-30'
  AND ae.agent_link != ''
  AND ae.partner_link != ''
  AND ap.partner_inn != ''
  AND ap.partner_inn::text NOT ILIKE '00%'  
GROUP BY extract_year,
         extract_month,
         date,
         period,
         manager_id,
         customer_id, 
         order_id, 
         sku, 
         sku_id,
         customer_reg
ORDER BY date, order_id, sku_id
"""
