# Data Pipeline Portfolio

![Social preview](./assets/social-preview.png)

Projeto de analytics engineering ponta a ponta construido com `Python`,
`PostgreSQL`, `dbt`, `FastAPI`, `Power BI` e dashboard analitico em formato
`desktop-first`.

Este repositorio foi organizado como estudo de caso de portfolio. A ideia nao
e mostrar apenas um dashboard final, mas a cadeia completa: ingestao,
warehouse, qualidade, semantica, API e camada de produto analitico.

## O que o projeto demonstra

- `100.000+` linhas de pedidos simuladas
- `10.000` clientes
- `2.000` produtos
- `8` modelos dbt
- `1` snapshot dbt
- `4+` testes SQL
- `19` testes de API e camada semantica passando hoje
- experiencia analitica em desktop com:
  - `Sales Overview`
  - `Revenue Trends`
  - `Predictive Outlook`
  - `Customer Segmentation`
  - `Retention Cohorts`
  - `Product Performance`
  - `Order Flow Operations`

## Galeria

<img src="./assets/gallery/desktop-home.png" alt="Desktop analytics shell" width="900">

<img src="./assets/gallery/desktop-sales-predictive.png" alt="Sales Overview no dashboard desktop" width="900">

<img src="./assets/gallery/desktop-products-retention.png" alt="Customer Segmentation e Retention Cohorts no dashboard desktop" width="900">

## Arquitetura

<img src="./assets/diagrams/architecture-overview.png" alt="Arquitetura analitica do projeto" width="900">

## Camadas de warehouse e banco

<img src="./assets/diagrams/warehouse-model.png" alt="Modelo de warehouse e camadas de banco derivadas do repositorio" width="900">

Observacao: a imagem acima representa a estrutura do warehouse a partir do
repositorio. Nao e screenshot de uma GUI de banco em tempo real. Mantive assim
para mostrar o desenho tecnico mesmo quando o banco local nao esta rodando.

## Analises presentes no dashboard

- comparacao entre periodos com tratamento correto de borda parcial
- Pareto e classificacao `ABC`
- segmentacao `RFM`
- cohorts de retencao
- deteccao de anomalias e mudanca estrutural
- cenarios preditivos (`Base`, `Conservative`, `Upside`)
- drilldown para membros subjacentes
- Spotlight windows com filtros locais e contexto congelado

## Funcionalidades de produto

- shell desktop com janelas e taskbar
- `Spotlight` para investigacao focada
- `Compare` para recortes lado a lado
- `Bookmarks` para restaurar layouts
- `Recent` e `Action Board`
- exportacao CSV
- temas visuais dentro do desktop

## Transparencia sobre uso de IA

Eu usei assistente de IA no projeto e nao escondo isso.

Usei IA para:

- acelerar implementacao
- explorar alternativas de UI
- refatorar e limpar codigo
- ampliar testes
- redigir documentacao
- fazer review de seguranca

Nao deleguei o que realmente importa: direcao do produto, framing de negocio,
validacao das mudancas, rejeicao de solucoes ruins e revisao final. Na pratica,
usei IA como acelerador profissional, nao como substituto de criterio.

Mais detalhe: [AI Collaboration Disclosure](./docs/AI_COLLABORATION_DISCLOSURE.md)

## Inicio rapido

```bash
docker compose up -d
cp .env.example .env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/loadsampledata.py --mode full_refresh
cd dbtproject
dbt deps
dbt run --full-refresh
dbt snapshot
dbt test
cd ..
uvicorn nextgen_dashboard.backend.main:app --reload --port 8601
```

Acesse `http://127.0.0.1:8601`

## Qualidade e seguranca

```bash
pytest tests/test_nextgen_dashboard_api.py
python scripts/benchmark_dashboard.py --threshold-seconds 1.50
```

Hardening aplicado:

- CORS explicito
- mutacoes do agente desligadas por padrao
- token para mutacoes quando habilitadas
- allowlist de assets estaticos
- escrita atomica no estado local do agente

## Mapa rapido do repositorio

- `fivetran_simulator/`: simulacao de ingestao
- `dbtproject/models/`: transformacoes dbt
- `scripts/setup_*.sql`: monitoramento e qualidade
- `scripts/benchmark_dashboard.py`: benchmark do dashboard
- `nextgen_dashboard/`: backend FastAPI + frontend desktop
- `assets/gallery/`: screenshots reais do projeto
- `assets/diagrams/`: visuais tecnicos gerados
- `assets/social-preview.png`: imagem recomendada para social preview no GitHub

## Documentacao util

- [GitHub Repository Setup](./docs/GITHUB_REPOSITORY_SETUP.md)

- [Architecture](./docs/ARCHITECTURE.md)
- [Data Lineage](./docs/DATA_LINEAGE.md)
- [Measure Dictionary](./docs/MEASURE_DICTIONARY.md)
- [Predictive Outlook Method](./docs/PREDICTIVE_OUTLOOK_METHOD.md)
- [Statistical Analytics Stack](./docs/STATISTICAL_ANALYTICS_STACK.md)
- [Project Interview Narrative](./docs/PROJECT_INTERVIEW_NARRATIVE.md)
- [Portfolio Action Plan](./docs/PORTFOLIO_ACTION_PLAN.md)
