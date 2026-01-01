import snowflake.connector
import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np

print('🚀 Carregando dados de exemplo no Snowflake RAW...')

conn = snowflake.connector.connect(
    account='UZQPXSP-DG14553',
    user='VICTORN198',
    password='7M@PQsn$#E!alj',
    warehouse='COMPUTE_WH',
    database='ANALYTICS',
    schema='RAW'
)

cursor = conn.cursor()

# CLIENTES (500)
print('📥 Gerando 500 clientes...')
customers = []
for i in range(1, 501):
    customers.append({
        'customer_id': f'CUST_{i:04d}',
        'customer_name': f'Cliente {i}',
        'email': f'cliente{i}@exemplo.com',
        'city': random.choice(['SP', 'RJ', 'BH', 'POA', 'CUR']),
        'state': random.choice(['SP', 'RJ', 'MG', 'RS', 'PR']),
        'created_date': datetime.now()
    })
pd.DataFrame(customers).to_sql('customers_raw', conn, schema='RAW', if_exists='replace', index=False)

# PRODUTOS (100)
print('📦 Gerando 100 produtos...')
products = []
for i in range(1, 101):
    products.append({
        'product_id': f'PROD_{i:04d}',
        'product_name': f'Produto {i}',
        'category': random.choice(['Eletrônicos', 'Roupas', 'Casa']),
        'unit_price': round(random.uniform(10.0, 500.0), 2),
        'stock_quantity': random.randint(0, 100)
    })
pd.DataFrame(products).to_sql('products_raw', conn, schema='RAW', if_exists='replace', index=False)

# PEDIDOS (1000)
print('🛒 Gerando 1000 pedidos...')
orders = []
customer_ids = [f'CUST_{i:04d}' for i in range(1, 501)]
product_ids = [f'PROD_{i:04d}' for i in range(1, 101)]
base_date = datetime(2025, 1, 1)

for i in range(1000):
    orders.append({
        'order_id': f'ORD_{i+1:06d}',
        'customer_id': random.choice(customer_ids),
        'product_id': random.choice(product_ids),
        'order_date': base_date + timedelta(days=random.randint(0, 365)),
        'quantity': random.randint(1, 5),
        'unit_price': 99.99,
        'total_amount': round(random.randint(1, 5) * 99.99, 2),
        'status': random.choice(['completed', 'pending', 'cancelled'])
    })

pd.DataFrame(orders).to_sql('orders_raw', conn, schema='RAW', if_exists='replace', index=False)

# Verifica
cursor.execute('SELECT COUNT(*) FROM RAW.orders_raw')
orders_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM RAW.customers_raw')
customers_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM RAW.products_raw')
products_count = cursor.fetchone()[0]

print(f'✅ CARREGADO!')
print(f'   📋 Pedidos: {orders_count}')
print(f'   👥 Clientes: {customers_count}')
print(f'   📦 Produtos: {products_count}')
print('🎉 Dados RAW prontos para dbt!')

cursor.close()
conn.close()
