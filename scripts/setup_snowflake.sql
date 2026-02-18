-- =====================================================================
-- -- Script: setup_snowflake.sql
-- -- Description: Prepares the Snowflake environment by creating the
-- --              database, schemas, and warehouse required for the
-- --              data pipeline project.
-- -- Author: [Seu Nome]
-- -- Date: 2024-08-27
-- =====================================================================

-- Use a role with sufficient permissions to create databases and warehouses
-- For example, SYSADMIN or a custom role with these grants.
USE ROLE SYSADMIN;

-- ---------------------------------------------------------------------
-- 1. WAREHOUSE CREATION
-- ---------------------------------------------------------------------
-- Create the compute warehouse for running queries and dbt models.
-- The warehouse is created with auto-suspend and auto-resume to save costs.
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
  WITH
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60 -- Suspends after 60 seconds of inactivity
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Compute warehouse for the data pipeline project';

-- ---------------------------------------------------------------------
-- 2. DATABASE CREATION
-- ---------------------------------------------------------------------
-- Create the main database for the project.
CREATE DATABASE IF NOT EXISTS ANALYTICS
  COMMENT = 'Database for the data pipeline project, holding raw, transformed, and analytical data';

-- ---------------------------------------------------------------------
-- 3. SCHEMA CREATION
-- ---------------------------------------------------------------------
-- Switch to the newly created database.
USE DATABASE ANALYTICS;

-- Create the RAW schema for landing raw data from sources.
CREATE SCHEMA IF NOT EXISTS RAW
  COMMENT = 'Schema for raw, unprocessed data loaded from source systems (e.g., Fivetran simulator)';

-- Create the STAGING schema for staging models (cleaning, casting).
CREATE SCHEMA IF NOT EXISTS STAGING
  COMMENT = 'Schema for dbt staging models, responsible for basic cleaning and type casting';

-- Create the INTERMEDIATE schema for intermediate transformations.
CREATE SCHEMA IF NOT EXISTS INTERMEDIATE
  COMMENT = 'Schema for dbt intermediate models with applied business logic';

-- Create the MARTS schema for final, analytics-ready data models (facts and dimensions).
CREATE SCHEMA IF NOT EXISTS MARTS
  COMMENT = 'Schema for dbt marts models, containing facts and dimensions for BI and analysis';

-- ---------------------------------------------------------------------
-- 4. PERMISSIONS (Optional but Recommended)
-- ---------------------------------------------------------------------
-- It's best practice to create a specific role for your dbt user
-- and grant it only the necessary permissions.

-- Example:
/*
CREATE ROLE IF NOT EXISTS DBT_ROLE;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE DBT_ROLE;
GRANT USAGE ON DATABASE ANALYTICS TO ROLE DBT_ROLE;
GRANT USAGE ON ALL SCHEMAS IN DATABASE ANALYTICS TO ROLE DBT_ROLE;
GRANT SELECT ON ALL TABLES IN DATABASE ANALYTICS TO ROLE DBT_ROLE;
GRANT SELECT ON ALL VIEWS IN DATABASE ANALYTICS TO ROLE DBT_ROLE;
GRANT CREATE TABLE, CREATE VIEW ON SCHEMA ANALYTICS.RAW TO ROLE DBT_ROLE;
GRANT CREATE TABLE, CREATE VIEW ON SCHEMA ANALYTICS.STAGING TO ROLE DBT_ROLE;
GRANT CREATE TABLE, CREATE VIEW ON SCHEMA ANALYTICS.INTERMEDIATE TO ROLE DBT_ROLE;
GRANT CREATE TABLE, CREATE VIEW ON SCHEMA ANALYTICS.MARTS TO ROLE DBT_ROLE;

-- Grant this role to your dbt user
GRANT ROLE DBT_ROLE TO USER YOUR_DBT_USER;
*/

-- =====================================================================
-- -- END OF SCRIPT
-- =====================================================================
-- -- Confirmation message
SELECT 'Snowflake environment setup complete.' AS status;
