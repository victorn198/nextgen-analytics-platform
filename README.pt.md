# README.pt.md - Projeto de PortfÃ³lio de Pipeline de Dados

## ðŸŽ¯ Projeto: Pipeline de Engenharia de Dados End-to-End

Um **projeto de engenharia de dados de ponta a ponta, pronto para produÃ§Ã£o**, que demonstra as melhores prÃ¡ticas do stack de dados moderno com Snowflake, dbt, Fivetran (simulado), Power BI e integraÃ§Ã£o MCP.

**Perfeito para apresentar suas habilidades em engenharia de dados a futuros empregadores! ðŸ“Š**

---

## ðŸ—ï¸ VisÃ£o Geral da Arquitetura

```
Fontes de Dados (APIs)
    â†“
Extração com Python (conector Fake Store API)
    â†“
Camada RAW no Snowflake (Landing Zone)
    â†“
TransformaÃ§Ãµes com dbt
    â”œâ”€ STAGING (Limpeza)
    â”œâ”€ INTERMEDIATE (LÃ³gica de NegÃ³cio)
    â””â”€ MARTS (Pronto para AnÃ¡lise)
    â†“
Dashboards no Power BI + AnÃ¡lises
    â†“
MCP + Gemini CLI (Insights com IA)
```

---

## ðŸš€ Guia RÃ¡pido (5 Minutos)

### 1. PrÃ©-requisitos
```bash
# Instalar Python 3.10+
# Instalar Git
# Conta Snowflake (teste gratuito disponÃ­vel)
```

### 2. Clonar & Configurar
```bash
git clone https://github.com/seu-usuario/data-pipeline-portfolio
cd data-pipeline-portfolio
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar o Snowflake
Crie o arquivo `.env` na raiz do projeto:
```env
SNOWFLAKE_ACCOUNT=sua_conta
SNOWFLAKE_USER=seu_usuario
SNOWFLAKE_PASSWORD=sua_senha
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=ANALYTICS
SNOWFLAKE_SCHEMA=RAW
```

### 4. Executar Script de Setup
```bash
# Volte para a raiz do projeto, caso esteja em outro diretÃ³rio
python scripts/loadsampledata.py
cd dbtproject
dbt run
dbt test
```

### 5. Verificar Resultados
```bash
dbt docs generate
dbt docs serve  # Abre a documentaÃ§Ã£o interativa
```

---

## ðŸ“ Estrutura do Projeto

```
data-pipeline-portfolio/
â”‚
â”œâ”€â”€ fivetran_simulator/          # Camada de extraÃ§Ã£o de dados
â”‚   â”œâ”€â”€ extract_orders.py        # Simula a API de pedidos
â”‚   â”œâ”€â”€ extract_customers.py     # Simula o CRM de clientes
â”‚   â””â”€â”€ extract_products.py      # Simula o catÃ¡logo de produtos
â”‚
â”œâ”€â”€ dbtproject/                 # Camada de transformaÃ§Ã£o
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ staging/             # Bruto â†’ Limpo
â”‚   â”‚   â”œâ”€â”€ intermediate/        # LÃ³gica de negÃ³cio
â”‚   â”‚   â””â”€â”€ marts/               # Tabelas para anÃ¡lise
â”‚   â”œâ”€â”€ tests/                   # Testes de qualidade de dados
â”‚   â””â”€â”€ macros/                  # Componentes reutilizÃ¡veis
â”‚
â”œâ”€â”€ mcp_tools/                   # IntegraÃ§Ã£o com IA
â”‚   â”œâ”€â”€ data_analyzer.py         # Servidor MCP para insights
â”‚   â””â”€â”€ mcp_server_config.json   # ConfiguraÃ§Ã£o
â”‚
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ setup_snowflake.sql      # Scripts DDL
â”‚   â”œâ”€â”€ load_sample_data.py      # Carregador de dados de exemplo
â”‚   â””â”€â”€ run_pipeline.sh          # Executor do pipeline completo
â”‚
â”œâ”€â”€ docs/                        # DocumentaÃ§Ã£o
â”‚   â”œâ”€â”€ ARCHITECTURE.md
â”‚   â”œâ”€â”€ DBT_MODELS.md
â”‚   â””â”€â”€ DATA_LINEAGE.md
â”‚
â”œâ”€â”€ .github/workflows/
â”‚   â””â”€â”€ dbt_run.yml             # AutomaÃ§Ã£o de CI/CD
â”‚
â””â”€â”€ power_bi/
    â””â”€â”€ sales_dashboard.pbix    # VisualizaÃ§Ã£o de BI
```

---

## ðŸ”„ Etapas do Pipeline de Dados

### Etapa 1: EXTRAIR (Conector Fake Store API)
Extrai dados de mÃºltiplas fontes:
- **API de Pedidos**: Dados de transaÃ§Ãµes
- **CRM de Clientes**: InformaÃ§Ãµes de clientes
- **CatÃ¡logo de Produtos**: Dados mestres de produtos

**Arquivos**: `fivetran_simulator/*.py` (`extract_customers.py`, `extract_products.py`, `extract_orders.py`) agora fazem chamadas para a Fake Store API.

```python
# Exemplo: extract_orders.py
from fivetran_simulator import OrdersExtractor

extractor = OrdersExtractor(api_url="https://api.example.com")
orders = extractor.fetch_recent_orders()
orders.to_snowflake(table="RAW.ORDERS")
```

---

### Etapa 2: CARREGAR (Snowflake)
Carrega os dados brutos no Snowflake:
- **Schema**: `RAW`
- **Tabelas**: `ORDERS`, `CUSTOMERS`, `PRODUCTS`
- **PadrÃ£o**: Append/Merge para cargas incrementais

```sql
-- Estrutura da Camada RAW
CREATE SCHEMA RAW;

CREATE TABLE RAW.ORDERS (
    order_id STRING,
    customer_id STRING,
    order_date TIMESTAMP,
    total_amount DECIMAL(10,2),
    _fivetran_synced TIMESTAMP
);
```

---

### Etapa 3: TRANSFORMAR (dbt)

#### 3a. Camada STAGING - Limpeza & PadronizaÃ§Ã£o
```sql
-- models/staging/stg_orders.sql
with source as (
    select * from {{ source('raw', 'orders') }}
),
cleaned as (
    select
        order_id::STRING as order_id,
        customer_id::STRING as customer_id,
        order_date::DATE as order_date,
        total_amount::DECIMAL(10,2) as total_amount,
        CASE WHEN total_amount > 0 THEN 'valid' ELSE 'invalid' END as status,
        _fivetran_synced::TIMESTAMP as loaded_at
    from source
    where _fivetran_synced >= DATEADD(day, -1, CURRENT_TIMESTAMP)
)
select * from cleaned
```

#### 3b. Camada INTERMEDIATE - LÃ³gica de NegÃ³cio
```sql
-- models/intermediate/int_orders_enhanced.sql
with orders as (
    select * from {{ ref('stg_orders') }}
),
customers as (
    select * from {{ ref('stg_customers') }}
),
enhanced as (
    select
        o.order_id,
        o.customer_id,
        c.customer_name,
        c.segment,
        o.order_date,
        o.total_amount,
        DATEDIFF(day, o.order_date, CURRENT_DATE) as days_since_order
    from orders o
    left join customers c on o.customer_id = c.customer_id
)
select * from enhanced
```

#### 3c. Camada MARTS - Pronta para AnÃ¡lise
```sql
-- models/marts/fct_sales.sql
with orders as (
    select * from {{ ref('int_orders_enhanced') }}
),
products as (
    select * from {{ ref('stg_products') }}
),
facts as (
    select
        o.order_id as sales_key,
        o.customer_id,
        p.product_id,
        o.segment,
        o.order_date,
        o.total_amount,
        p.category,
        p.price,
        o.total_amount / NULLIF(p.price, 0) as units_sold
    from orders o
    left join products p on o.product_id = p.product_id
)
select * from facts
```

---

### Etapa 4: TESTAR (Qualidade de Dados)
```sql
-- tests/assert_positive_revenue.sql
select count(*) as failure_count
from {{ ref('fct_sales') }}
where total_amount <= 0
having count(*) > 0
```

```bash
dbt test  # Executa todos os testes
```

---

### Etapa 5: ANALISAR (Power BI)
Conecte o Power BI ao schema MARTS do Snowflake:
- **fct_sales**: TransaÃ§Ãµes de vendas
- **dim_customer**: DimensÃµes de clientes
- **dim_product**: DimensÃµes de produtos
- **dim_date**: DimensÃ£o de datas

**Dashboards**:
- ðŸ“ˆ VisÃ£o Geral de Vendas
- ðŸ’° TendÃªncias de Receita
- ðŸ‘¥ SegmentaÃ§Ã£o de Clientes
- ðŸŽ¯ Desempenho de Produtos

---

### Etapa 6: INSIGHTS COM IA (MCP + Gemini CLI)
AnÃ¡lise de dados automatizada e detecÃ§Ã£o de padrÃµes:

```bash
gemini-cli --mcp data_analyzer \
  --query "Analise as tendÃªncias de vendas e identifique os principais clientes"
```

---

## ðŸ§ª Testes & Qualidade

### Testes dbt
```bash
# Executa todos os testes dbt
dbt test

# Executa testes para um modelo especÃ­fico
dbt test --select fct_sales

# Testa com saÃ­da detalhada
dbt test --debug
```

### Testes Python
```bash
# Executa a suÃ­te de testes pytest
pytest tests/ -v --cov

# Executa um teste especÃ­fico
pytest tests/test_extraction.py -v
```

---

## ðŸ“Š OtimizaÃ§Ã£o de Performance

### MaterializaÃ§Ãµes dbt
- **View**: Camada Staging (nÃ£o materializada)
- **Table**: Camada Intermediate (materializada)
- **Incremental**: Camada Marts (apenas anexa novas linhas)

### OtimizaÃ§Ã£o no Snowflake
- Chaves de cluster em colunas de join
- Particionamento por data
- EstatÃ­sticas para otimizaÃ§Ã£o de queries

```sql
-- Tabela Incremental com Cluster
{{ config(
    materialized='incremental',
    unique_key='sales_key',
    cluster_by=['order_date', 'customer_id']
) }}
```

---

## ðŸ” SeguranÃ§a & GovernanÃ§a

âœ… **Controle de VersÃ£o**: Todo o cÃ³digo no GitHub
âœ… **Controle de Acesso**: SeguranÃ§a a nÃ­vel de linha via dbt
âœ… **Linhagem de Dados**: dbt fornece linhagem completa
âœ… **Trilha de Auditoria**: Fivetran monitora o frescor dos dados
âœ… **Testes**: VerificaÃ§Ãµes automatizadas de qualidade de dados

---

## ðŸš€ Deployment

### Desenvolvimento Local
```bash
dbt run --target dev
```

### ProduÃ§Ã£o
```bash
dbt run --target prod
```

### CI/CD (GitHub Actions)
Push para o GitHub â†’ Teste dbt automÃ¡tico â†’ AprovaÃ§Ã£o â†’ Deploy para produÃ§Ã£o

Veja `.github/workflows/dbt_run.yml`

---

## ðŸ“š DocumentaÃ§Ã£o

- **ARCHITECTURE.md**: Design do sistema & decisÃµes
- **DBT_MODELS.md**: DocumentaÃ§Ã£o do modelo de dados
- **DATA_LINEAGE.md**: Fluxo de dados de ponta a ponta

Gere a documentaÃ§Ã£o dbt:
```bash
cd dbtproject
dbt docs generate
dbt docs serve
```

---

## ðŸ› ï¸ Comandos Comuns

```bash
# Desenvolvimento
dbt run                    # Executa todos os modelos
dbt test                   # Executa testes de qualidade de dados
dbt debug                  # Testa a conexÃ£o com o Snowflake
dbt deps                   # Instala pacotes dbt

# DocumentaÃ§Ã£o
dbt docs generate          # Gera documentaÃ§Ã£o interativa
dbt docs serve             # Visualiza a documentaÃ§Ã£o localmente

# Testes & Qualidade
dbt test --select nome_do_modelo
pytest tests/ -v --cov

# ManutenÃ§Ã£o
dbt snapshot               # Cria snapshots de dados
dbt freshness             # Verifica o frescor da fonte

# Pipeline
python scripts/loadsampledata.py   # Carrega dados de teste
bash scripts/run_pipeline.sh         # Executa o pipeline completo
```

---

## ðŸ’¡ Principais CaracterÃ­sticas

âœ… **Pronto para ProduÃ§Ã£o**: Tratamento de erros, logging
âœ… **EscalÃ¡vel**: FÃ¡cil de adicionar novas fontes
âœ… **Testado**: Testes dbt + testes Python
âœ… **Documentado**: Linhagem clara & documentaÃ§Ã£o
âœ… **CI/CD**: AutomaÃ§Ã£o com GitHub Actions
âœ… **Modular**: Staging â†’ Intermediate â†’ Marts
âœ… **Qualidade de PortfÃ³lio**: Estrutura profissional

---

## ðŸŽ“ Recursos de Aprendizagem

- [DocumentaÃ§Ã£o dbt](https://docs.getdbt.com/)
- [Snowflake University](https://university.snowflake.com/)
- [VisÃ£o Geral do Modern Data Stack](https://www.moderndatastack.xyz/)
- [Melhores PrÃ¡ticas de Engenharia de Dados](https://www.dataengineeringwiki.com/)

---

## ðŸ“ž Suporte

- Problemas: GitHub Issues
- DÃºvidas: Verifique as discussÃµes
- Melhorias: Pull requests sÃ£o bem-vindos!

---

## ðŸ“„ LicenÃ§a

LicenÃ§a MIT - Sinta-se Ã  vontade para usar para fins de portfÃ³lio.

---

## ðŸŽ¯ PrÃ³ximos Passos

1. âœ… Clonar o repositÃ³rio
2. âœ… Configurar a conexÃ£o com o Snowflake
3. âœ… Executar `dbt run` e `dbt test`
4. âœ… Conectar o dashboard do Power BI
5. âœ… Explorar a documentaÃ§Ã£o dbt
6. âœ… Criar um repositÃ³rio no GitHub para o seu portfÃ³lio
7. âœ… Compartilhar com potenciais empregadores!

**Boa engenharia de dados! ðŸš€**


