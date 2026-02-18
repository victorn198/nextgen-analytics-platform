-- dbt singular test: assert_positive_total_amount.sql
-- This test fails if any record in fct_sales has a total_amount less than or equal to zero.

SELECT
    sales_key,
    sales_amount
FROM {{ ref('fct_sales') }}
WHERE sales_amount <= 0
