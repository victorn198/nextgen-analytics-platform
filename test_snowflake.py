import os
from dotenv import load_dotenv
import snowflake.connector

try:
    print("--- Starting Snowflake connection test ---")

    load_dotenv()
    print(".env file loaded.")

    # Get credentials
    # SNOWFLAKE_ACCOUNT and SNOWFLAKE_DATABASE are hardcoded to bypass .env issues.
    snowflake_account = 'UZMOVYK-JJA45572'
    snowflake_database = 'ANALYTICS'
    snowflake_user = os.getenv('SNOWFLAKE_USER')
    snowflake_password = os.getenv('SNOWFLAKE_PASSWORD')
    snowflake_warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    snowflake_schema = os.getenv('SNOWFLAKE_SCHEMA')

    print(f"SNOWFLAKE_ACCOUNT (hardcoded): {snowflake_account}")
    print(f"SNOWFLAKE_DATABASE (hardcoded): {snowflake_database}")
    print(f"SNOWFLAKE_USER: {snowflake_user}")
    print(f"SNOWFLAKE_WAREHOUSE: {snowflake_warehouse}")
    print(f"SNOWFLAKE_SCHEMA: {snowflake_schema}")

    if not all([snowflake_account, snowflake_user, snowflake_password, snowflake_warehouse, snowflake_database, snowflake_schema]):
        print("\n!!! ERROR: One or more environment variables were not found. Check the .env file.")
    else:
        print("\n>>> All variables loaded. Attempting to connect...")
        
        conn = snowflake.connector.connect(
            account=snowflake_account,
            user=snowflake_user,
            password=snowflake_password,
            warehouse=snowflake_warehouse,
            database=snowflake_database,
            schema=snowflake_schema
        )
        print("✅ Snowflake connection successful!")

        conn.close()
        print("Connection closed.")

except Exception as e:
    print(f"\n❌ An error occurred during the test: {e}")

finally:
    print("\n--- Connection test finished ---")
