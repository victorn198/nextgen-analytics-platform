# Zed Reopen Checklist

Guia rapido para retomar o projeto no Zed sem perder contexto.

Data: 2026-02-17

Atualizacao: 2026-02-18

## 1) O que ja esta pronto

- Auditoria automatica de qualidade no Snowflake:
  - `scripts/setup_data_quality_audit.sql`
- Alerta automatico encadeado apos auditoria:
  - `scripts/setup_data_quality_alerting.sql`
- Carga RAW em modo incremental operacional:
  - `scripts/loadsampledata.py`
  - `fivetran_simulator/extract_customers.py`
  - `fivetran_simulator/extract_products.py`
  - `fivetran_simulator/extract_orders.py`
- Views operacionais para Power BI:
  - `scripts/setup_operational_monitoring_views.sql`
- Guia de dashboard operacional:
  - `power_bi/README.md`
- Guia MCP para Power BI (PBIXRay + MCPBI):
  - `docs/MCP_POWERBI_AGENT_SETUP.md`
- Launcher estavel do PBIXRay MCP:
  - `scripts/run_pbixray_mcp.ps1`

## 2) Configurar MCP PBIXRay no Zed

No `settings.json` do Zed:

```json
{
  "context_servers": {
    "pbixray": {
      "command": "powershell",
      "args": [
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "D:\\projects\\data-pipeline-portfolio\\scripts\\run_pbixray_mcp.ps1",
        "-MaxRows",
        "100",
        "-PageSize",
        "10"
      ],
      "env": {}
    }
  }
}
```

## 3) Ao reabrir o Zed

1. Abrir a pasta do projeto: `D:\projects\data-pipeline-portfolio`
2. Reiniciar o Agent no Zed.
3. Confirmar que `pbixray` aparece conectado.
4. Abrir o `.pbix` no Power BI Desktop.
5. Continuar criacao de medidas de forma governada:
   - registrar medidas em `docs/MEASURE_DICTIONARY.md` (criar se nao existir)
   - registrar sessao em `docs/POWER_BI_BUILD_LOG.md` (criar se nao existir)

## 4) Comando de validacao rapida (pipeline)

```powershell
.\venv\Scripts\python.exe scripts/loadsampledata.py --mode incremental
```

## 5) Prompt de retomada recomendado

```text
Leia docs/ZED_REOPEN_CHECKLIST.md, PROGRESS_LOG.md e docs/MCP_POWERBI_AGENT_SETUP.md e continue a implementacao do dashboard com medidas organizadas via MCP.
```

## 6) Nota de versionamento (temporaria)

- Durante a montagem final do dashboard, `power_bi/` foi mantido fora do Git por regra temporaria no `.gitignore`.
- Ao fechar o dashboard, revisar `.gitignore` e decidir o que entra no commit final de BI.
