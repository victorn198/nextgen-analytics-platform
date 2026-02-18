-- =====================================================================
-- Script: setup_data_quality_alerting.sql
-- Description: Creates automatic alerting on top of data quality audits.
--              - Alert table
--              - Alert processing procedure
--              - Chained task (runs after audit task)
-- =====================================================================

USE DATABASE ANALYTICS;

CREATE SCHEMA IF NOT EXISTS DATA_QUALITY
  COMMENT = 'Automated data quality auditing objects';

CREATE TABLE IF NOT EXISTS ANALYTICS.DATA_QUALITY.DATA_QUALITY_ALERTS (
  ALERT_ID NUMBER IDENTITY(1,1),
  RUN_ID STRING,
  ALERT_CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  ALERT_STATUS STRING DEFAULT 'OPEN',
  FAILED_ERROR_RULES NUMBER,
  ALERT_MESSAGE STRING,
  FAILED_RULES VARIANT,
  ALERT_SOURCE STRING DEFAULT 'SP_PROCESS_DATA_QUALITY_ALERTS',
  CONSTRAINT UQ_DATA_QUALITY_ALERTS_RUN_ID UNIQUE (RUN_ID)
);

CREATE OR REPLACE PROCEDURE ANALYTICS.DATA_QUALITY.SP_PROCESS_DATA_QUALITY_ALERTS()
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
  v_latest_run_id STRING;
  v_failed_error_rules NUMBER DEFAULT 0;
  v_existing_alerts NUMBER DEFAULT 0;
  v_failed_rules VARIANT;
BEGIN
  SELECT RUN_ID INTO :v_latest_run_id
  FROM ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT
  ORDER BY CHECKED_AT DESC, AUDIT_ID DESC
  LIMIT 1;

  IF (v_latest_run_id IS NULL) THEN
    RETURN 'No audit run found. Nothing to alert.';
  END IF;

  SELECT COUNT(*) INTO :v_failed_error_rules
  FROM ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT
  WHERE RUN_ID = :v_latest_run_id
    AND STATUS = 'FAIL'
    AND SEVERITY = 'ERROR';

  IF (v_failed_error_rules = 0) THEN
    RETURN 'Run ' || v_latest_run_id || ': no ERROR failures. No alert created.';
  END IF;

  SELECT COUNT(*) INTO :v_existing_alerts
  FROM ANALYTICS.DATA_QUALITY.DATA_QUALITY_ALERTS
  WHERE RUN_ID = :v_latest_run_id;

  IF (v_existing_alerts > 0) THEN
    RETURN 'Run ' || v_latest_run_id || ': alert already exists.';
  END IF;

  SELECT ARRAY_AGG(
           OBJECT_CONSTRUCT(
             'rule_name', RULE_NAME,
             'target_object', TARGET_OBJECT,
             'severity', SEVERITY,
             'error_count', ERROR_COUNT,
             'details', DETAILS
           )
         )
  INTO :v_failed_rules
  FROM ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT
  WHERE RUN_ID = :v_latest_run_id
    AND STATUS = 'FAIL'
    AND SEVERITY = 'ERROR';

  INSERT INTO ANALYTICS.DATA_QUALITY.DATA_QUALITY_ALERTS (
    RUN_ID,
    FAILED_ERROR_RULES,
    ALERT_MESSAGE,
    FAILED_RULES
  )
  VALUES (
    :v_latest_run_id,
    :v_failed_error_rules,
    'Data quality critical failure detected in run ' || :v_latest_run_id,
    :v_failed_rules
  );

  RETURN 'Run ' || v_latest_run_id || ': alert created with ' || v_failed_error_rules || ' failed ERROR rule(s).';
END;
$$;

CREATE OR REPLACE VIEW ANALYTICS.DATA_QUALITY.VW_OPEN_DATA_QUALITY_ALERTS AS
SELECT
  ALERT_ID,
  RUN_ID,
  ALERT_CREATED_AT,
  ALERT_STATUS,
  FAILED_ERROR_RULES,
  ALERT_MESSAGE,
  FAILED_RULES
FROM ANALYTICS.DATA_QUALITY.DATA_QUALITY_ALERTS
WHERE ALERT_STATUS = 'OPEN'
ORDER BY ALERT_CREATED_AT DESC;

ALTER TASK ANALYTICS.DATA_QUALITY.TASK_RUN_DATA_QUALITY_AUDIT_HOURLY SUSPEND;

CREATE OR REPLACE TASK ANALYTICS.DATA_QUALITY.TASK_PROCESS_DATA_QUALITY_ALERTS
  WAREHOUSE = COMPUTE_WH
  AFTER ANALYTICS.DATA_QUALITY.TASK_RUN_DATA_QUALITY_AUDIT_HOURLY
AS
  CALL ANALYTICS.DATA_QUALITY.SP_PROCESS_DATA_QUALITY_ALERTS();

ALTER TASK ANALYTICS.DATA_QUALITY.TASK_PROCESS_DATA_QUALITY_ALERTS RESUME;
ALTER TASK ANALYTICS.DATA_QUALITY.TASK_RUN_DATA_QUALITY_AUDIT_HOURLY RESUME;

-- Optional manual run:
-- CALL ANALYTICS.DATA_QUALITY.SP_PROCESS_DATA_QUALITY_ALERTS();

SELECT 'Data quality alerting setup complete.' AS status;
