# Projeto de Modelagem de Dados dbt + Snowflake

Projeto focado na transformação e modelagem de dados (ELT) utilizando dbt (Data Build Tool) sobre dados brutos pré-carregados no Snowflake. O escopo abrange desde o staging dos dados até a criação das tabelas de consumo analítico (Marts).

## Arquitetura de Transformação

Este projeto implementa uma arquitetura de modelagem em três camadas (Staging, Intermediate e Marts) diretamente no Snowflake, gerida e orquestrada pelo dbt.

```
SNOWFLAKE (RAW)
  |
dbt (STAGING / INTERMEDIATE)
  |
dbt (MARTS - Consumo Analítico)
```

## Fonte de Dados (RAW Layer)

Os dados de origem já estão persistidos no schema `ANALYTICS.RAW` do Snowflake.

| Tabela | Registros | Descricao |
|--------|-----------|-----------|
| orders_raw | 1.000 | Pedidos com cliente/produto |
| customers_raw | 500 | Clientes brasileiros |
| products_raw | 100 | Produtos categorizados |

## Tecnologias

- **Snowflake**: Data Warehouse central (Camadas RAW, ANALYTICS)
- **dbt (Data Build Tool)**: Engenharia de Transformação (ELT), Testes e Documentação
- **GitHub Actions**: Pipeline de Integração Contínua/Entrega Contínua (CI/CD)

## Principais Features

- **Modelagem 3-Camadas**: Implementação da arquitetura Staging → Intermediate → Marts.
- **Modelos Otimizados**: 7 modelos dbt desenvolvidos para performance e manutenibilidade.
- **Qualidade de Dados**: Cobertura robusta de testes de integridade e validação de dados (`dbt test`).
- **Governança de Dados**: Geração automática de documentação técnica e linhagem de dados (`dbt docs`).
- **Automação**: Configuração de pipeline CI/CD via GitHub Actions para deploy de modelos.

## Como Começar

Siga estes passos para configurar e executar o projeto localmente.

### Pré-requisitos

-   Python 3.8+
-   `pip` (gerenciador de pacotes Python)
-   dbt CLI (instalado via pip, adaptador `dbt-snowflake`)
-   Conta Snowflake com as permissões necessárias

### 1. Clone o repositório

```bash
git clone https://github.com/your-username/data-pipeline-portfolio.git
cd data-pipeline-portfolio
```

### 2. Configure o ambiente Python e instale as dependências

É recomendado usar um ambiente virtual.

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure as Credenciais do Snowflake

#### Para o script `loadsampledata.py`:

Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`. Este arquivo armazenará os detalhes de conexão do Snowflake para o script Python que carrega os dados de exemplo.

```
SNOWFLAKE_ACCOUNT=sua_conta_snowflake
SNOWFLAKE_USER=seu_usuario_snowflake
SNOWFLAKE_PASSWORD=sua_senha_snowflake
SNOWFLAKE_WAREHOUSE=seu_warehouse_snowflake
SNOWFLAKE_DATABASE=seu_database_snowflake
SNOWFLAKE_SCHEMA=seu_schema_snowflake
```

**Nota:** O arquivo `.env` não deve ser commitado no controle de versão.

#### Para o dbt:

Configure seu arquivo `profiles.yml` do dbt. Por padrão, este projeto procura um perfil chamado `data_pipeline`. Seu `profiles.yml` deve estar localizado em `~/.dbt/profiles.yml` (no Linux/macOS) ou `%userprofile%\.dbt\profiles.yml` (no Windows).

Exemplo de entrada em `profiles.yml`:

```yaml
data_pipeline:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}" # Usar variável de ambiente
      user: "{{ env_var('SNOWFLAKE_USER') }}"       # Usar variável de ambiente
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}" # Usar variável de ambiente
      role: seu_snowflake_role
      warehouse: "{{ env_var('SNOWFLAKE_WAREHOUSE') }}" # Usar variável de ambiente
      database: "{{ env_var('SNOWFLAKE_DATABASE') }}" # Usar variável de ambiente
      schema: "{{ env_var('SNOWFLAKE_SCHEMA') }}" # Usar variável de ambiente
      threads: 4
      client_session_keep_alive: False
```

É altamente recomendado usar variáveis de ambiente também para as credenciais do dbt, configurando-as no seu shell ou carregando-as do arquivo `.env` se o seu ambiente de execução dbt suportar (ex: via um script wrapper).

### 4. Carregar Dados de Exemplo

Execute o script Python para popular seu schema `RAW` no Snowflake com dados de exemplo.

```bash
python scripts/loadsampledata.py
```

### 5. Executar transformações dbt

Navegue até o diretório `dbtproject` e execute seus modelos dbt.

```bash
cd dbtproject
dbt deps
dbt seed # Se você tiver arquivos seed (atualmente não neste projeto, mas boa prática)
dbt run
dbt test
dbt docs generate
dbt docs serve # Para visualizar a documentação gerada
```

## Skills Demonstrados

- Design de Data Warehouse e arquitetura 3-camadas.
- Melhores práticas de ELT e modelagem dimensional com dbt.
- Desenvolvimento e automação de testes de qualidade de dados.
- Implementação de governança de dados através de documentação automatizada.
- Controle de versão Git e pipeline CI/CD.

---
Victor Nogueira | Data Engineer | Sao Paulo, BR