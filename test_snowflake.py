import snowflake.connector
print("🔄 Testando Snowflake...")

conn = snowflake.connector.connect(
    account='UZQPXSP-DG14553',
    user='VICTORN198',
    password='7M@PQsn$#E!alj',
    warehouse='COMPUTE_WH',
    database='ANALYTICS',
    schema='RAW'
)

cur = conn.cursor()
print("✅ Conectado! Conta: BJ27889, Usuário: VICTORN198, Warehouse: COMPUTE_WH")

# === NOVO: CRIAR TABELA TESTE ===
print("📊 Criando tabela test_pipeline...")
cur.execute("""
    CREATE OR REPLACE TABLE ANALYTICS.RAW.test_pipeline (
        id INT,
        data TIMESTAMP,
        valor DECIMAL(10,2)
    )
""")
conn.commit()
print("✅ Tabela test_pipeline CRIADA!")

# === NOVO: INSERIR DADOS TESTE ===
cur.execute("""
    INSERT INTO ANALYTICS.RAW.test_pipeline (id, data, valor) 
    VALUES (1, CURRENT_TIMESTAMP(), 123.45)
""")
conn.commit()
print("✅ 1 registro inserido!")

# === VERIFICAR ===
cur.execute("SELECT COUNT(*) FROM ANALYTICS.RAW.test_pipeline;")
print(f"✅ Total registros: {cur.fetchone()[0]}")

# Listar tabelas (agora deve mostrar 1)
cur.execute("SHOW TABLES;")
tables = cur.fetchall()
print(f"📋 Tabelas no schema RAW: {len(tables)} encontradas")

cur.close()
conn.close()
print("🔚 Teste concluído!")
