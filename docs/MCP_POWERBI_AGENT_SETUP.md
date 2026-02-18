# MCP + Power BI + Zed (Setup Profissional)

Guia para usar MCP com Power BI de forma organizada para criacao/validacao de medidas.

Data de referencia: 2026-02-17.

## Objetivo

Usar dois servidores MCP em paralelo:
- `pbixray` para contexto estrutural de arquivo `.pbix` (metadata/modelo/local).
- `mcpbi` para contexto de modelo vivo no Power BI Desktop (DAX query/validacao).

## Quando usar cada um

### `pbixray` (arquivo local)
- Ler tabelas, relacionamentos, medidas ja existentes e Power Query.
- Bom para documentacao e engenharia reversa do `.pbix`.
- Nao e a melhor opcao para "executar" DAX no modelo vivo.

### `mcpbi` (modelo vivo no Desktop)
- Rodar/validar DAX no modelo aberto no Power BI Desktop.
- Melhor para ciclo profissional de criacao de medidas com teste.

## Custos

- `pbixray-mcp-server`: open source (sem custo de licenca).
- `mcpbi`: open source (sem custo de licenca).
- Custo de IA depende do agente/modelo usado no Zed (Codex/Claude/etc).
- Se usar APIs externas (ex.: Azure/Power BI remoto), pode haver custo separado.

## Pre-requisitos

1. Power BI Desktop aberto com o `.pbix` do projeto.
2. Python 3.10+ (para `pbixray`).
3. .NET 8 Runtime (para `mcpbi`).
4. Zed com Agent habilitado.

## Setup 1: PBIXRay MCP (local)

### Instalar

```powershell
.\venv\Scripts\python.exe -m pip install pbixray-mcp-server
```

### Configurar no Zed (`settings.json`)

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

Observacao:
- O executavel `pbixray-mcp-server.exe` pode falhar por bug de entrypoint.
- Use o launcher local `scripts/run_pbixray_mcp.ps1`, que chama `python -m src.pbixray_server`.

## Setup 2: MCPBI (modelo vivo do Power BI Desktop)

Referencia: `jonaolden/mcpbi`.

### Passos

1. Baixar release do `mcpbi`.
2. Com Power BI Desktop aberto, descobrir porta da instancia local.
3. Configurar o servidor no Zed apontando para `mcpbi.exe` e porta descoberta.

### Exemplo no Zed (`settings.json`)

```json
{
  "context_servers": {
    "mcpbi": {
      "command": "C:\\tools\\mcpbi\\mcpbi.exe",
      "args": [
        "--port",
        "63717"
      ],
      "env": {}
    }
  }
}
```

## Fluxo recomendado para medidas (governanca)

1. Definir medida no formato:
- Nome tecnico
- Definicao de negocio (1 frase)
- Granularidade
- Filtros esperados
- Regra de validacao manual

2. Pedir ao agente (com `mcpbi`) para:
- sugerir DAX
- validar sintaxe
- rodar query de validacao

3. Aprovar medida e registrar em `docs/MEASURE_DICTIONARY.md`.

4. Atualizar dashboard e registrar no `docs/POWER_BI_BUILD_LOG.md`.

## Prompt padrao para o agente

```text
Crie a medida [NOME] na pasta [DISPLAY_FOLDER].
Definicao de negocio: [DEFINICAO].
Tabela base: [TABELA].
Comportamento de filtro: [REGRAS].
Inclua protecao para divisao por zero quando aplicavel.
Depois valide com consulta DAX e retorne:
1) formula final
2) resultado da validacao
3) checklist de testes manuais no visual.
```

## Risco comum e mitigacao

- Risco: agente criar medida correta em sintaxe, mas errada no negocio.
- Mitigacao: toda medida precisa de regra de validacao manual com numero esperado.
