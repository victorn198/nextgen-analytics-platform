-- =====================================================================
-- Script: setup_postgres.sql
-- Description: Prepares PostgreSQL schemas required for the pipeline.
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS snapshots;
CREATE SCHEMA IF NOT EXISTS data_quality;
CREATE SCHEMA IF NOT EXISTS monitoring;

SELECT 'PostgreSQL environment setup complete.' AS status;
