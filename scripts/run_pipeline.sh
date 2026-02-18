#!/bin/bash
# =================================================================
# Script: run_pipeline.sh
# Description: Executes the full data pipeline end-to-end.
#              1. Loads sample data using the Python script.
#              2. Runs the dbt transformations and tests.
# Usage: ./scripts/run_pipeline.sh
# =================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

# --- 1. Load Sample Data ---
echo "--- Starting Step 1: Loading Sample Data ---"
python scripts/loadsampledata.py
echo "--- Step 1 Completed ---"
echo

# --- 2. Run dbt Pipeline ---
echo "--- Starting Step 2: Running dbt Transformations ---"
# Navigate to the dbt project directory
cd dbtproject

# Install dbt dependencies (if any)
echo "Running dbt deps..."
dbt deps

# Run dbt models
echo "Running dbt run..."
dbt run

# Run dbt tests
echo "Running dbt test..."
dbt test

echo "--- Step 2 Completed ---"
echo

# --- Pipeline Finished ---
echo "✅ Data pipeline execution finished successfully!"
