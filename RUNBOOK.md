# RUNBOOK.md

Guia rapido de operacao do pipeline.

## 1) Executar carga RAW (API real + escala)

Na raiz do projeto:

```bash
python scripts/loadsampledata.py
```

Modo padrao: `incremental` (nao recria RAW e insere apenas IDs novos ate o target).

Forcar full refresh operacional:

```bash
python scripts/loadsampledata.py --mode full_refresh
```

Resultado esperado (aprox.):
- Customers: 10000
- Products: 2000
- Orders: 100000

Variavel opcional de ambiente:
- `PIPELINE_LOAD_MODE=incremental|full_refresh`

## 2) Executar transformacoes e testes dbt

No diretorio `dbtproject`:

```bash
..\venv\Scripts\dbt.exe run --full-refresh --no-partial-parse
..\venv\Scripts\dbt.exe test --no-partial-parse
```

## 3) Snapshot de clientes (agora nativo no Snowflake)

O snapshot nao depende mais de `dbt snapshot`.

Objetos ativos:
- Tabela SCD2: `ANALYTICS.SNAPSHOTS.CUSTOMERS_SCD2`
- Procedure: `ANALYTICS.SNAPSHOTS.SP_REFRESH_CUSTOMERS_SCD2()`
- Task diaria: `ANALYTICS.SNAPSHOTS.TASK_REFRESH_CUSTOMERS_SCD2_DAILY`
  - `USING CRON 55 23 * * * America/Sao_Paulo`

Views de consulta:
- `ANALYTICS.SNAPSHOTS.VW_CUSTOMERS_SCD2_CURRENT`
- `ANALYTICS.SNAPSHOTS.VW_CUSTOMERS_SCD2_HISTORY`

## 4) Queries operacionais uteis

```sql
show tasks like 'TASK_REFRESH_CUSTOMERS_SCD2_DAILY' in schema ANALYTICS.SNAPSHOTS;

select count(*) as scd2_total
from ANALYTICS.SNAPSHOTS.CUSTOMERS_SCD2;

select count(*) as scd2_current
from ANALYTICS.SNAPSHOTS.VW_CUSTOMERS_SCD2_CURRENT;

select count(*) as scd2_historical
from ANALYTICS.SNAPSHOTS.VW_CUSTOMERS_SCD2_HISTORY
where snapshot_state = 'historical';
```

## 5) Modelos e testes de qualidade adicionados

Staging tratado:
- `dbtproject/models/staging/stg_customers.sql`
- `dbtproject/models/staging/stg_products.sql`
- `dbtproject/models/staging/stg_orders.sql`

Testes singulares:
- `dbtproject/tests/assert_no_future_orders.sql`
- `dbtproject/tests/assert_order_amount_consistency.sql`
- `dbtproject/tests/assert_valid_customer_email.sql`
- `dbtproject/tests/assert_positive_total_amount.sql`

## 6) Observacoes importantes

- Snapshot antigo do dbt foi desativado em:
  - `dbtproject/snapshots/customers_snapshot.sql` (`enabled=False`)
- Pipeline shell nao roda mais `dbt snapshot`:
  - `scripts/run_pipeline.sh`
- O warning de config deprecada foi corrigido:
  - `dbtproject/dbt_project.yml` com `flags.send_anonymous_usage_stats: false`

## 7) Proxima etapa recomendada

Implementar auditoria e alerta de qualidade no Snowflake:
- tabela `DATA_QUALITY_AUDIT`
- procedure de validacao
- task de monitoramento

## 8) Auditoria automatica de qualidade (implementado)

Provisionamento dos objetos:

```bash
snowsql -f scripts/setup_data_quality_audit.sql
```

Objetos criados:
- Tabela: `ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT`
- Procedure: `ANALYTICS.DATA_QUALITY.SP_RUN_DATA_QUALITY_AUDIT()`
- View (ultimo status por regra): `ANALYTICS.DATA_QUALITY.VW_DATA_QUALITY_AUDIT_LATEST`
- Task horaria: `ANALYTICS.DATA_QUALITY.TASK_RUN_DATA_QUALITY_AUDIT_HOURLY`
  - `USING CRON 5 * * * * America/Sao_Paulo`

Execucao manual:

```sql
call ANALYTICS.DATA_QUALITY.SP_RUN_DATA_QUALITY_AUDIT();
```

Consultas de operacao:

```sql
show tasks like 'TASK_RUN_DATA_QUALITY_AUDIT_HOURLY' in schema ANALYTICS.DATA_QUALITY;

select *
from ANALYTICS.DATA_QUALITY.VW_DATA_QUALITY_AUDIT_LATEST
order by rule_name;

select *
from ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT
order by checked_at desc, audit_id desc
limit 100;
```

## 9) Alerta automatico para falhas de qualidade (implementado)

Provisionamento dos objetos:

```bash
snowsql -f scripts/setup_data_quality_alerting.sql
```

Objetos criados:
- Tabela de incidentes: `ANALYTICS.DATA_QUALITY.DATA_QUALITY_ALERTS`
- Procedure de deteccao: `ANALYTICS.DATA_QUALITY.SP_PROCESS_DATA_QUALITY_ALERTS()`
- View de alertas abertos: `ANALYTICS.DATA_QUALITY.VW_OPEN_DATA_QUALITY_ALERTS`
- Task encadeada: `ANALYTICS.DATA_QUALITY.TASK_PROCESS_DATA_QUALITY_ALERTS`
  - Executa automaticamente apos `TASK_RUN_DATA_QUALITY_AUDIT_HOURLY`

Regra de alerta:
- Cria alerta somente quando houver `STATUS='FAIL'` com `SEVERITY='ERROR'` no run mais recente.
- Evita duplicidade com `RUN_ID` unico na tabela de alertas.

Consultas operacionais:

```sql
show tasks like 'TASK_PROCESS_DATA_QUALITY_ALERTS' in schema ANALYTICS.DATA_QUALITY;

select *
from ANALYTICS.DATA_QUALITY.VW_OPEN_DATA_QUALITY_ALERTS
order by alert_created_at desc;

select run_id, rule_name, status, severity, error_count, checked_at
from ANALYTICS.DATA_QUALITY.DATA_QUALITY_AUDIT
order by checked_at desc, audit_id desc;
```

## 10) Dataset operacional para Power BI (implementado)

Provisionamento das views operacionais:

```bash
snowsql -f scripts/setup_operational_monitoring_views.sql
```

Objetos criados em `ANALYTICS.MONITORING`:
- `VW_PIPELINE_OPERATIONAL_KPIS`
- `VW_RAW_TABLE_COUNTS`
- `VW_SCD2_SNAPSHOT_STATUS`
- `VW_DATA_QUALITY_LATEST`
- `VW_DATA_QUALITY_RUNS`
- `VW_OPEN_DATA_QUALITY_ALERTS`

Validacao rapida:

```sql
select * from ANALYTICS.MONITORING.VW_PIPELINE_OPERATIONAL_KPIS;
select * from ANALYTICS.MONITORING.VW_RAW_TABLE_COUNTS order by table_name;
select * from ANALYTICS.MONITORING.VW_DATA_QUALITY_LATEST order by rule_name;
select * from ANALYTICS.MONITORING.VW_OPEN_DATA_QUALITY_ALERTS order by alert_created_at desc;
```

Guia de publicacao:
- `power_bi/README.md`
