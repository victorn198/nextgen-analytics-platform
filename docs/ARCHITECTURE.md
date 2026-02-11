# Arquitetura do Projeto de Pipeline de Dados

Este documento descreve a arquitetura do pipeline de dados, desde a extração até a camada de apresentação.

## Visão Geral

A arquitetura segue o padrão **Modern Data Stack**, utilizando ferramentas baseadas em nuvem e de código aberto para criar um pipeline robusto, escalável e de fácil manutenção.

![Arquitetura](https://i.imgur.com/example.png)  <!-- Você pode gerar um diagrama e substituir o link -->

## Componentes

1.  **Fonte de Dados (Simulada)**
    *   **Descrição**: Os dados brutos são gerados por um script Python (`scripts/loadsampledata.py`) que simula um conector Fivetran, inserindo dados de pedidos, clientes e produtos.
    *   **Tecnologia**: Python, Snowflake Connector.

2.  **Data Warehouse**
    *   **Descrição**: O Snowflake serve como nosso Data Warehouse centralizado, armazenando os dados brutos, intermediários e transformados.
    *   **Tecnologia**: Snowflake.
    *   **Estrutura**:
        *   `ANALYTICS.RAW`: Schema de landing zone para os dados brutos.
        *   `ANALYTICS.STAGING`: Views de limpeza e padronização.
        *   `ANALYTICS.INTERMEDIATE`: Modelos intermediários com lógicas de negócio.
        *   `ANALYTICS.MARTS`: Tabelas de fatos e dimensões prontas para consumo.

3.  **Transformação**
    *   **Descrição**: O dbt (Data Build Tool) é usado para transformar os dados brutos em modelos de dados limpos, testados e prontos para análise. A lógica de transformação segue o padrão de modelagem dimensional.
    *   **Tecnologia**: dbt Core.

4.  **Orquestração e CI/CD**
    *   **Descrição**: O GitHub Actions é utilizado para automação de CI/CD. O workflow (`.github/workflows/dbt_run.yml`) executa os modelos e testes do dbt automaticamente a cada push na branch `main`.
    *   **Tecnologia**: GitHub Actions.

5.  **Camada de Apresentação (Business Intelligence)**
    *   **Descrição**: A camada final onde os dados são consumidos e visualizados. O projeto está preparado para usar o Power BI.
    *   **Tecnologia**: Power BI Desktop.
    *   **Conexão**: O Power BI se conecta diretamente ao schema `MARTS` no Snowflake.

6.  **Integração com IA (MCP)**
    *   **Descrição**: Um servidor FastAPI (`mcp_tools/mcp_server_fastapi.py`) permite a interação de agentes de IA (como o Gemini CLI) com os dados do projeto, possibilitando análises e consultas em linguagem natural.
    *   **Tecnologia**: FastAPI, Python.
