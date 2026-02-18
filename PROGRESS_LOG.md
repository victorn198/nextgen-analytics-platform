# PROGRESS_LOG.md

Checkpoint oficial para retomar o projeto sem perda de contexto.
Data de referencia: 2026-02-16.

## Estado atual (confirmado)

- Carga RAW com API real + amplificacao executada com sucesso:
  - `RAW.CUSTOMERS_RAW`: 10000
  - `RAW.PRODUCTS_RAW`: 2000
  - `RAW.ORDERS_RAW`: 100000
- Pipeline dbt validado:
  - `dbt run --full-refresh`: PASS
  - `dbt test`: PASS (39 testes)
- Qualidade validada no Snowflake:
  - Chaves nulas criticas: 0
  - Duplicidades por chave de negocio: 0
  - Orfaos na fato: 0
  - Pedido com data futura: 0
  - Divergencia de `total_amount` vs `quantity * unit_price`: 0

## O que foi implementado nesta fase

1. Integracao real com API (Fake Store) no lugar do simulador local:
- `fivetran_simulator/extract_customers.py`
- `fivetran_simulator/extract_products.py`
- `fivetran_simulator/extract_orders.py`
- `scripts/loadsampledata.py`

2. Escala de volume "empresa" com parametros:
- `FAKESTORE_TARGET_CUSTOMERS` (default 10000)
- `FAKESTORE_TARGET_PRODUCTS` (default 2000)
- `FAKESTORE_TARGET_ORDER_LINES` (default 100000)
- `FAKESTORE_INSERT_BATCH_SIZE` (default 5000)
- `FAKESTORE_RANDOM_SEED` (default 42)

3. Tratamento profissional em staging:
- `dbtproject/models/staging/stg_customers.sql`
- `dbtproject/models/staging/stg_products.sql`
- `dbtproject/models/staging/stg_orders.sql`

4. Testes adicionais de qualidade:
- `dbtproject/tests/assert_no_future_orders.sql`
- `dbtproject/tests/assert_order_amount_consistency.sql`
- `dbtproject/tests/assert_valid_customer_email.sql`

5. Snapshot nativo no Snowflake (SCD2) para clientes:
- Tabela: `ANALYTICS.SNAPSHOTS.CUSTOMERS_SCD2`
- Procedure: `ANALYTICS.SNAPSHOTS.SP_REFRESH_CUSTOMERS_SCD2()`
- Task diaria: `ANALYTICS.SNAPSHOTS.TASK_REFRESH_CUSTOMERS_SCD2_DAILY`
  - Schedule: `USING CRON 55 23 * * * America/Sao_Paulo`
  - Estado: `started`
- Views:
  - `ANALYTICS.SNAPSHOTS.VW_CUSTOMERS_SCD2_CURRENT`
  - `ANALYTICS.SNAPSHOTS.VW_CUSTOMERS_SCD2_HISTORY`

6. Integracao do snapshot nativo ao dbt:
- Source adicionada em `dbtproject/models/schema/schema.yml` (`snapshots_native`)
- Model de staging criado:
  - `dbtproject/models/staging/stg_customers_snapshot_current.sql`

7. Snapshot antigo do dbt desativado para evitar duplicidade de estrategia:
- `dbtproject/snapshots/customers_snapshot.sql` com `enabled=False`

8. Pipeline shell atualizado para nao chamar `dbt snapshot`:
- `scripts/run_pipeline.sh`

9. Aviso deprecado do dbt resolvido:
- Removido `config.send_anonymous_usage_stats` de `dbtproject/profiles.yml`
- Adicionado em `dbtproject/dbt_project.yml`:
  - `flags.send_anonymous_usage_stats: false`

## Como validar rapidamente (comandos)

Na raiz do repo:

```bash
python scripts/loadsampledata.py
```

No diretorio `dbtproject`:

```bash
..\venv\Scripts\dbt.exe run --full-refresh --no-partial-parse
..\venv\Scripts\dbt.exe test --no-partial-parse
```

## Consultas uteis no Snowflake

```sql
select count(*) from ANALYTICS.SNAPSHOTS.CUSTOMERS_SCD2;
select count(*) from ANALYTICS.SNAPSHOTS.VW_CUSTOMERS_SCD2_CURRENT;
select count(*) from ANALYTICS.SNAPSHOTS.VW_CUSTOMERS_SCD2_HISTORY where snapshot_state='historical';
show tasks like 'TASK_REFRESH_CUSTOMERS_SCD2_DAILY' in schema ANALYTICS.SNAPSHOTS;
```

## Proximos passos planejados (ainda nao executados)

- [x] Criar auditoria automatica de qualidade no Snowflake (`DATA_QUALITY_AUDIT`).
  - Script: `scripts/setup_data_quality_audit.sql`
  - Objetos: tabela de auditoria, procedure de validacao, view de ultimo status e task horaria
- [x] Criar alerta operacional para falhas de qualidade.
  - Script: `scripts/setup_data_quality_alerting.sql`
  - Objetos: tabela de alertas, procedure de deteccao, view de alertas abertos e task encadeada
- [x] Ajustar carga para modo incremental operacional (sem recriar RAW toda execucao).
  - `scripts/loadsampledata.py` com modos `incremental` (padrao) e `full_refresh`
  - `fivetran_simulator/extract_customers.py` incremental por `CUSTOMER_ID`
  - `fivetran_simulator/extract_products.py` incremental por `PRODUCT_ID`
  - `fivetran_simulator/extract_orders.py` incremental por `ORDER_ID`
- [x] Publicar base operacional para dashboard (Power BI) com metricas de carga, SCD2 e qualidade.
  - Script: `scripts/setup_operational_monitoring_views.sql`
  - Schema de consumo: `ANALYTICS.MONITORING`
  - Guia de publicacao: `power_bi/README.md`
- [x] Documentar setup MCP para desenvolvimento de medidas no Power BI.
  - Guia: `docs/MCP_POWERBI_AGENT_SETUP.md`
  - Estrategia: `pbixray` (metadata local) + `mcpbi` (validacao DAX em modelo vivo)

## Nota de retomada

Na proxima sessao, pedir:
"Leia `PROGRESS_LOG.md` e continue pelos proximos passos planejados."

Checklist de retomada no Zed:
- `docs/ZED_REOPEN_CHECKLIST.md`

---

## Checkpoint extra (2026-02-18) - Power BI em andamento

### O que foi feito hoje

- Sessao MCP `pbixray` foi recarregada e validada.
- Estrutura do modelo operacional foi confirmada:
  - Tabelas principais: `kpi_ops`, `dq_latest`, `dq_runs`, `dq_alerts`, `fct_sales`.
  - Relacionamentos essenciais da fato com dimensoes validados.
- Medidas operacionais e de vendas foram definidas e organizadas no Desktop/Tabular em uma tabela de medidas dedicada:
  - Pastas: `01 Ops KPIs`, `02 Data Quality`, `03 Sales`.
- Pagina `Pipeline Operations` montada com:
  - Cards operacionais (volumes RAW e status DQ).
  - Tabela de qualidade por regra.
  - Tabela de alertas.
  - Serie temporal de runs DQ.
- Estado atual dos dados operacionais observado no dashboard:
  - `Open Alerts Count = 0`.
  - Regras de qualidade no recorte atual sem falhas (valores `FAILED_* = 0` nos runs exibidos).

### Decisao de versionamento (importante)

- Conteudo de `power_bi/` foi mantido fora do Git temporariamente para evitar commit parcial durante a construcao do dashboard.
- Regras adicionadas no `.gitignore` para ignorar artefatos de Power BI ate fechamento da fase.

### Proxima retomada (ordem sugerida)

1. Finalizar as paginas restantes do dashboard:
   - `Sales Overview`
   - `Revenue Trends`
   - `Customer Segmentation`
   - `Product Performance`
2. Revisar padrao visual e navegacao entre paginas.
3. Validar medidas finais com casos de filtro reais.
4. Somente apos fechamento visual/funcional:
   - remover excecao temporaria de `power_bi/` no `.gitignore` (se desejar versionar o conteudo),
   - commitar pacote final do BI.

### Prompt de retomada recomendado

```text
Leia PROGRESS_LOG.md e continue do checkpoint 2026-02-18, finalizando as 4 paginas restantes do dashboard Power BI.
```
