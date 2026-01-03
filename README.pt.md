# Portfolio Data Pipeline

Projeto end-to-end de data engineering production-ready com Snowflake, dbt, Python ETL.

## Arquitetura

```
RAW <- Python ETL (1.600 registros)
  |
STAGING <- dbt models (views limpas)
  |
MARTS <- Tabelas Fato/Dimensao
```

## Dados Carregados

| Tabela | Registros | Descricao |
|--------|-----------|-----------|
| orders_raw | 1.000 | Pedidos com cliente/produto |
| customers_raw | 500 | Clientes brasileiros |
| products_raw | 100 | Produtos categorizados |

## Tecnologias

- **Snowflake**: Data Warehouse (ANALYTICS.RAW)
- **Python**: Automacao ETL (loadsampledata.py)
- **dbt**: Transformacoes (STAGING/MARTS)
- **GitHub Actions**: Pipeline CICD

## Principais Features

- ETL production-ready com tratamento de erros
- 7 modelos dbt de transformacao
- Testes de qualidade de dados e validacao
- Arquitetura modular (Staging → Intermediate → Marts)
- Escalavel para APIs reais e cargas de producao

## Skills Demonstrados

- Design de Data Warehouse com arquitetura 3-camadas
- Desenvolvimento e automacao de Python ETL
- Melhores praticas de dbt ELT e modelagem
- Controle de versao Git e pipeline CICD
- Testes de qualidade de dados e validacao

---

Victor Nogueira | Data Engineer | Sao Paulo, BR