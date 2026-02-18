-- =====================================================================
-- Script: setup_data_quality_audit.sql
-- Description: Creates automated data quality auditing objects in Snowflake.
--              - Audit table
--              - Validation procedure
--              - Scheduled task
-- =====================================================================

USE DATABASE ANALYTICS;

CREATE SCHEMA IF NOT EXISTS DATA_QUALITY
  COMMENT = 'Automated data quality auditing objects';

CREATE TABLE IF NOT EXISTS ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT (
  AUDIT_ID NUMBER IDENTITY(1,1),
  RUN_ID STRING,
  CHECKED_AT TIMESTAMP_NTZ,
  RULE_NAME STRING,
  TARGET_OBJECT STRING,
  STATUS STRING,
  ERROR_COUNT NUMBER,
  SEVERITY STRING,
  DETAILS STRING,
  EXECUTED_BY STRING
);

CREATE OR REPLACE PROCEDURE ANALYTICS.DATA_QUALITY.SP_RUN_DATA_QUALITY_AUDIT()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
  v_run_id STRING DEFAULT UUID_STRING();
  v_checked_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP();
  v_error_count NUMBER DEFAULT 0;
  v_failed_rules NUMBER DEFAULT 0;
BEGIN
  -- Rule 1: Critical nulls in fact grain/keys.
  SELECT COUNT(*) INTO :v_error_count
  FROM ANALYTICS.MARTS.FCT_SALES
  WHERE ORDER_ID IS NULL
     OR CUSTOMER_KEY IS NULL
     OR PRODUCT_KEY IS NULL
     OR ORDER_DATE IS NULL;

  INSERT INTO ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT (
    RUN_ID, CHECKED_AT, RULE_NAME, TARGET_OBJECT, STATUS, ERROR_COUNT, SEVERITY, DETAILS, EXECUTED_BY
  )
  VALUES (
    :v_run_id,
    :v_checked_at,
    'critical_null_keys_fact_sales',
    'ANALYTICS.MARTS.FCT_SALES',
    IFF(:v_error_count = 0, 'PASS', 'FAIL'),
    :v_error_count,
    'ERROR',
    'Checks nulls in ORDER_ID, CUSTOMER_KEY, PRODUCT_KEY, ORDER_DATE.',
    CURRENT_USER()
  );
  v_failed_rules := v_failed_rules + IFF(v_error_count = 0, 0, 1);

  -- Rule 2: Duplicate business key (ORDER_ID) in fact.
  SELECT COALESCE(SUM(dup_count), 0) INTO :v_error_count
  FROM (
    SELECT (COUNT(*) - 1) AS dup_count
    FROM ANALYTICS.MARTS.FCT_SALES
    GROUP BY ORDER_ID
    HAVING COUNT(*) > 1
  );

  INSERT INTO ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT (
    RUN_ID, CHECKED_AT, RULE_NAME, TARGET_OBJECT, STATUS, ERROR_COUNT, SEVERITY, DETAILS, EXECUTED_BY
  )
  VALUES (
    :v_run_id,
    :v_checked_at,
    'duplicate_order_id_fact_sales',
    'ANALYTICS.MARTS.FCT_SALES',
    IFF(:v_error_count = 0, 'PASS', 'FAIL'),
    :v_error_count,
    'ERROR',
    'Counts duplicate ORDER_ID rows in the fact table.',
    CURRENT_USER()
  );
  v_failed_rules := v_failed_rules + IFF(v_error_count = 0, 0, 1);

  -- Rule 3: Orphans in fact table against dimensions.
  SELECT COUNT(*) INTO :v_error_count
  FROM ANALYTICS.MARTS.FCT_SALES f
  LEFT JOIN ANALYTICS.MARTS.DIM_CUSTOMER dc ON f.CUSTOMER_KEY = dc.CUSTOMER_KEY
  LEFT JOIN ANALYTICS.MARTS.DIM_PRODUCT dp ON f.PRODUCT_KEY = dp.PRODUCT_KEY
  WHERE dc.CUSTOMER_KEY IS NULL
     OR dp.PRODUCT_KEY IS NULL;

  INSERT INTO ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT (
    RUN_ID, CHECKED_AT, RULE_NAME, TARGET_OBJECT, STATUS, ERROR_COUNT, SEVERITY, DETAILS, EXECUTED_BY
  )
  VALUES (
    :v_run_id,
    :v_checked_at,
    'orphan_dimension_keys_in_fact_sales',
    'ANALYTICS.MARTS.FCT_SALES',
    IFF(:v_error_count = 0, 'PASS', 'FAIL'),
    :v_error_count,
    'ERROR',
    'Verifies foreign keys in fact exist in customer/product dimensions.',
    CURRENT_USER()
  );
  v_failed_rules := v_failed_rules + IFF(v_error_count = 0, 0, 1);

  -- Rule 4: Future order dates.
  SELECT COUNT(*) INTO :v_error_count
  FROM ANALYTICS.MARTS.FCT_SALES
  WHERE ORDER_DATE > CURRENT_TIMESTAMP();

  INSERT INTO ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT (
    RUN_ID, CHECKED_AT, RULE_NAME, TARGET_OBJECT, STATUS, ERROR_COUNT, SEVERITY, DETAILS, EXECUTED_BY
  )
  VALUES (
    :v_run_id,
    :v_checked_at,
    'future_order_dates_fact_sales',
    'ANALYTICS.MARTS.FCT_SALES',
    IFF(:v_error_count = 0, 'PASS', 'FAIL'),
    :v_error_count,
    'ERROR',
    'Checks order dates greater than current timestamp.',
    CURRENT_USER()
  );
  v_failed_rules := v_failed_rules + IFF(v_error_count = 0, 0, 1);

  -- Rule 5: Amount consistency.
  SELECT COUNT(*) INTO :v_error_count
  FROM ANALYTICS.MARTS.FCT_SALES
  WHERE ABS(COALESCE(SALES_AMOUNT, 0) - ROUND(COALESCE(QUANTITY, 0) * COALESCE(UNIT_PRICE, 0), 2)) > 0.01;

  INSERT INTO ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT (
    RUN_ID, CHECKED_AT, RULE_NAME, TARGET_OBJECT, STATUS, ERROR_COUNT, SEVERITY, DETAILS, EXECUTED_BY
  )
  VALUES (
    :v_run_id,
    :v_checked_at,
    'order_amount_consistency_fact_sales',
    'ANALYTICS.MARTS.FCT_SALES',
    IFF(:v_error_count = 0, 'PASS', 'FAIL'),
    :v_error_count,
    'ERROR',
    'Checks if SALES_AMOUNT equals QUANTITY * UNIT_PRICE (tolerance 0.01).',
    CURRENT_USER()
  );
  v_failed_rules := v_failed_rules + IFF(v_error_count = 0, 0, 1);

  -- Rule 6: Customer email validity.
  SELECT COUNT(*) INTO :v_error_count
  FROM ANALYTICS.STAGING.STG_CUSTOMERS
  WHERE NOT REGEXP_LIKE(EMAIL, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

  INSERT INTO ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT (
    RUN_ID, CHECKED_AT, RULE_NAME, TARGET_OBJECT, STATUS, ERROR_COUNT, SEVERITY, DETAILS, EXECUTED_BY
  )
  VALUES (
    :v_run_id,
    :v_checked_at,
    'valid_customer_email_stg_customers',
    'ANALYTICS.STAGING.STG_CUSTOMERS',
    IFF(:v_error_count = 0, 'PASS', 'FAIL'),
    :v_error_count,
    'WARN',
    'Checks valid e-mail format in staging customers.',
    CURRENT_USER()
  );
  v_failed_rules := v_failed_rules + IFF(v_error_count = 0, 0, 1);

  RETURN 'Audit run_id=' || v_run_id || ' completed. Failed rules=' || v_failed_rules;
END;
$$;

CREATE OR REPLACE VIEW ANALYTICS.DATA_QUALITY.VW_DATA_QUALITY_AUDIT_LATEST AS
SELECT
  RUN_ID,
  CHECKED_AT,
  RULE_NAME,
  TARGET_OBJECT,
  STATUS,
  ERROR_COUNT,
  SEVERITY,
  DETAILS,
  EXECUTED_BY
FROM ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT
QUALIFY ROW_NUMBER() OVER (PARTITION BY RULE_NAME ORDER BY CHECKED_AT DESC, AUDIT_ID DESC) = 1;

CREATE OR REPLACE TASK ANALYTICS.DATA_QUALITY.TASK_RUN_DATA_QUALITY_AUDIT_HOURLY
  WAREHOUSE = COMPUTE_WH
  SCHEDULE = 'USING CRON 5 * * * * America/Sao_Paulo'
AS
  CALL ANALYTICS.DATA_QUALITY.SP_RUN_DATA_QUALITY_AUDIT();

ALTER TASK ANALYTICS.DATA_QUALITY.TASK_RUN_DATA_QUALITY_AUDIT_HOURLY RESUME;

-- Optional manual run:
-- CALL ANALYTICS.DATA_QUALITY.SP_RUN_DATA_QUALITY_AUDIT();

SELECT 'Data quality audit setup complete.' AS status;
