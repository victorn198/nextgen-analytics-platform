# Runbook do Projeto de Pipeline de Dados

Este documento serve como um guia rápido para executar e interagir com este projeto.

## Estado Atual do Projeto

O projeto está em um estado funcional e completo:

1.  **Dados Brutos:** As tabelas `RAW` no Snowflake (`ANALYTICS.RAW`) estão populadas com 1000 pedidos de exemplo.
2.  **Dados Transformados:** Os modelos dbt foram executados com sucesso. As tabelas de dimensão (`dim_customer`, `dim_product`) e a tabela de fatos (`fct_sales`) estão criadas e prontas para análise na schema `STAGING_MARTS`.
3.  **Servidor da API:** Um servidor FastAPI (`mcp_server_fastapi.py`) está configurado para permitir que o agente Gemini interaja com o banco de dados.

## Como Colocar Tudo para Funcionar

Siga estes passos para reativar o ambiente de trabalho.

### Pré-requisito: Ambiente Virtual

Todos os comandos devem ser executados usando o Python e as ferramentas do ambiente virtual (`venv`) da pasta do projeto.

### Passo 1: (Opcional) Recarregar os Dados Brutos

Se você quiser resetar os dados brutos no Snowflake para o estado original, execute o script de carregamento. **Atenção:** Isso irá apagar os dados das tabelas `RAW` e inserir um novo conjunto de 1000 pedidos.

```bash
# No seu terminal, na raiz do projeto
D:\projects\data-pipeline-portfolio\venv\Scripts\python.exe D:\projects\data-pipeline-portfolio\scripts\loadsampledata.py
```

### Passo 2: Executar os modelos dbt

Para re-executar os modelos dbt e transformar os dados brutos, execute o seguinte comando:

```bash
# No seu terminal, na pasta dbtproject
..\venv\Scripts\dbt.exe run
```

### Passo 3: Iniciar o servidor da API

Para iniciar o servidor da API, execute o seguinte comando:

```bash
# No seu terminal, na raiz do projeto
D:\projects\data-pipeline-portfolio\venv\Scripts\python.exe -m uvicorn mcp_server_fastapi:app --reload
```

## Próximos Passos

*   **Análise de Dados:** Você pode agora usar um cliente SQL ou uma ferramenta de BI para se conectar ao Snowflake e analisar os dados nas tabelas de `STAGING_MARTS`.
*   **Interagir com a API:** Você pode interagir com a API FastAPI para consultar os dados do Snowflake. A documentação da API está disponível em `http://localhost:8000/docs`.
*   **Desenvolver novos modelos dbt:** Você pode desenvolver novos modelos dbt para criar novas visões e análises dos dados.