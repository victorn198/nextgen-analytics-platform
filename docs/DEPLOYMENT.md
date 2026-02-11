# Guia de Deployment

Este documento descreve os passos para fazer o deploy deste projeto em um ambiente de produção.

## Visão Geral

O deployment deste projeto consiste em duas partes principais:
1.  **Deployment do Pipeline dbt**: Garantir que os modelos dbt sejam executados de forma agendada e automatizada.
2.  **Deployment do Servidor de API (Opcional)**: Publicar o servidor FastAPI para que ele possa ser acessado pela internet.

---

## 1. Deployment do Pipeline dbt com GitHub Actions

O método de deployment principal para o pipeline dbt já está configurado através do GitHub Actions.

### Pré-requisitos
- Um repositório no GitHub com o código do projeto.
- Uma conta no Snowflake com as devidas permissões.

### Passos de Configuração

1.  **Configurar os GitHub Secrets**:
    *   No seu repositório do GitHub, vá para `Settings` -> `Secrets and variables` -> `Actions`.
    *   Crie os seguintes "Repository secrets" com os valores da sua conta Snowflake (os mesmos do seu arquivo `.env`):
        *   `SNOWFLAKE_ACCOUNT`
        *   `SNOWFLAKE_USER`
        *   `SNOWFLAKE_PASSWORD`
        *   `SNOWFLAKE_WAREHOUSE`
        *   `SNOWFLAKE_DATABASE`
        *   `SNOWFLAKE_SCHEMA`

2.  **Ativar o Workflow**:
    *   O workflow definido em `.github/workflows/dbt_run.yml` será executado automaticamente em cada `push` ou `pull_request` para a branch `main`.
    *   Você pode modificar o gatilho (trigger) no arquivo `.yml` para rodar em um agendamento (`schedule`), por exemplo, diariamente.

    ```yaml
    # Exemplo para rodar todo dia à 1h da manhã UTC
    on:
      schedule:
        - cron: '0 1 * * *'
    ```

### Monitoramento
- O status de cada execução pode ser acompanhado na aba **Actions** do seu repositório no GitHub.

---

## 2. Deployment do Servidor de API (FastAPI)

Para expor a API na internet, você pode usar diversas plataformas de nuvem. Aqui está um exemplo usando o **Render**, que possui um plano gratuito.

### Pré-requisitos
- Conta no Render (ou outra plataforma como Heroku, Vercel, etc.).
- O código do projeto no seu repositório GitHub.

### Passos de Deployment com o Render

1.  **Crie um "New Web Service"** no dashboard do Render.
2.  **Conecte seu repositório GitHub** e selecione o repositório do projeto.
3.  **Configure o serviço**:
    *   **Name**: Dê um nome para o seu serviço (e.g., `data-pipeline-api`).
    *   **Root Directory**: Deixe em branco se o `requirements.txt` está na raiz.
    *   **Runtime**: `Python 3`.
    *   **Build Command**: `pip install -r requirements.txt`.
    *   **Start Command**: `uvicorn mcp_tools.mcp_server_fastapi:app --host 0.0.0.0 --port $PORT`.
4.  **Adicione as Variáveis de Ambiente**:
    *   Na seção `Environment`, adicione as mesmas credenciais do Snowflake que você adicionou como GitHub Secrets. O Render as injetará como variáveis de ambiente no seu servidor.
5.  **Clique em "Create Web Service"**.

O Render irá fazer o deploy do seu servidor e fornecer uma URL pública (e.g., `https://data-pipeline-api.onrender.com`).
