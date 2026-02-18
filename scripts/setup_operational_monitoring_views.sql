-- =====================================================================
-- Script: setup_operational_monitoring_views.sql
-- Description: Creates monitoring views for an operational Power BI dashboard.
-- =====================================================================

USE DATABASE ANALYTICS;

CREATE SCHEMA IF NOT EXISTS MONITORING
  COMMENT = 'Operational monitoring views for pipeline observability';

CREATE OR REPLACE VIEW ANALYTICS.MONITORING.VW_RAW_TABLE_COUNTS AS
SELECT 'RAW.CUSTOMERS_RAW' AS table_name, COUNT(*) AS record_count FROM ANALYTICS.RAW.CUSTOMERS_RAW
UNION ALL
SELECT 'RAW.PRODUCTS_RAW' AS table_name, COUNT(*) AS record_count FROM ANALYTICS.RAW.PRODUCTS_RAW
UNION ALL
SELECT 'RAW.ORDERS_RAW' AS table_name, COUNT(*) AS record_count FROM ANALYTICS.RAW.ORDERS_RAW;

CREATE OR REPLACE VIEW ANALYTICS.MONITORING.VW_SCD2_SNAPSHOT_STATUS AS
SELECT
  (SELECT COUNT(*) FROM ANALYTICS.SNAPSHOTS.CUSTOMERS_SCD2) AS scd2_total_rows,
  (SELECT COUNT(*) FROM ANALYTICS.SNAPSHOTS.VW_CUSTOMERS_SCD2_CURRENT) AS scd2_current_rows,
  (SELECT COUNT(*) FROM ANALYTICS.SNAPSHOTS.VW_CUSTOMERS_SCD2_HISTORY WHERE SNAPSHOT_STATE = 'historical') AS scd2_historical_rows,
  CURRENT_TIMESTAMP() AS measured_at;

CREATE OR REPLACE VIEW ANALYTICS.MONITORING.VW_DATA_QUALITY_LATEST AS
SELECT
  RULE_NAME,
  TARGET_OBJECT,
  STATUS,
  ERROR_COUNT,
  SEVERITY,
  CHECKED_AT,
  RUN_ID
FROM ANALYTICS.DATA_QUALITY.VW_DATA_QUALITY_AUDIT_LATEST;

CREATE OR REPLACE VIEW ANALYTICS.MONITORING.VW_DATA_QUALITY_RUNS AS
SELECT
  RUN_ID,
  MIN(CHECKED_AT) AS run_started_at,
  MAX(CHECKED_AT) AS run_finished_at,
  SUM(IFF(STATUS = 'FAIL', 1, 0)) AS failed_rules_total,
  SUM(IFF(STATUS = 'FAIL' AND SEVERITY = 'ERROR', 1, 0)) AS failed_error_rules,
  SUM(IFF(STATUS = 'FAIL' AND SEVERITY = 'WARN', 1, 0)) AS failed_warn_rules,
  COUNT(*) AS rules_checked
FROM ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT
GROUP BY RUN_ID;

CREATE OR REPLACE VIEW ANALYTICS.MONITORING.VW_OPEN_DATA_QUALITY_ALERTS AS
SELECT
  ALERT_ID,
  RUN_ID,
  ALERT_CREATED_AT,
  ALERT_STATUS,
  FAILED_ERROR_RULES,
  ALERT_MESSAGE,
  FAILED_RULES
FROM ANALYTICS.DATA_QUALITY.VW_OPEN_DATA_QUALITY_ALERTS;

CREATE OR REPLACE VIEW ANALYTICS.MONITORING.VW_PIPELINE_OPERATIONAL_KPIS AS
WITH raw_counts AS (
  SELECT
    MAX(IFF(table_name = 'RAW.CUSTOMERS_RAW', record_count, NULL)) AS raw_customers,
    MAX(IFF(table_name = 'RAW.PRODUCTS_RAW', record_count, NULL)) AS raw_products,
    MAX(IFF(table_name = 'RAW.ORDERS_RAW', record_count, NULL)) AS raw_orders
  FROM ANALYTICS.MONITORING.VW_RAW_TABLE_COUNTS
),
latest_run AS (
  SELECT
    RUN_ID,
    run_finished_at,
    failed_rules_total,
    failed_error_rules,
    failed_warn_rules
  FROM ANALYTICS.MONITORING.VW_DATA_QUALITY_RUNS
  QUALIFY ROW_NUMBER() OVER (ORDER BY run_finished_at DESC, RUN_ID DESC) = 1
),
open_alerts AS (
  SELECT COUNT(*) AS open_alerts_count
  FROM ANALYTICS.MONITORING.VW_OPEN_DATA_QUALITY_ALERTS
),
scd2 AS (
  SELECT scd2_total_rows, scd2_current_rows, scd2_historical_rows
  FROM ANALYTICS.MONITORING.VW_SCD2_SNAPSHOT_STATUS
)
SELECT
  CURRENT_TIMESTAMP() AS measured_at,
  r.raw_customers,
  r.raw_products,
  r.raw_orders,
  s.scd2_total_rows,
  s.scd2_current_rows,
  s.scd2_historical_rows,
  lr.RUN_ID AS latest_dq_run_id,
  lr.run_finished_at AS latest_dq_run_finished_at,
  COALESCE(lr.failed_rules_total, 0) AS latest_dq_failed_rules_total,
  COALESCE(lr.failed_error_rules, 0) AS latest_dq_failed_error_rules,
  COALESCE(lr.failed_warn_rules, 0) AS latest_dq_failed_warn_rules,
  oa.open_alerts_count
FROM raw_counts r
CROSS JOIN scd2 s
LEFT JOIN latest_run lr ON TRUE
CROSS JOIN open_alerts oa;

SELECT 'Operational monitoring views setup complete.' AS status;
