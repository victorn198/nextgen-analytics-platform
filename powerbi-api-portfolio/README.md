# Power BI API Portfolio

Projeto simples de BI com dados públicos da GitHub API.

## Arquitetura

```text
GitHub API -> Python -> PostgreSQL -> view SQL -> Power BI
```

## Objetivo

Demonstrar um fluxo completo e reproduzível de ingestão, tratamento SQL e
consumo analítico no Power BI.

## Escopo inicial

- coletar repositórios públicos de um usuário ou organização;
- armazenar os dados brutos no PostgreSQL;
- preparar uma view analítica para o Power BI;
- acompanhar repositórios, issues, pull requests e atividade mensal;
- validar os indicadores com queries SQL simples.

## Estrutura

```text
powerbi-api-portfolio/
├── data/
├── powerbi/
├── sql/
│   ├── 001_schema.sql
│   └── 002_powerbi_view.sql
├── src/
│   └── ingest_github.py
├── .env.example
└── README.md
```

## Próximos passos

1. configurar PostgreSQL;
2. executar a ingestão;
3. criar a view analítica;
4. conectar o Power BI à view;
5. adicionar screenshots e medidas DAX.
