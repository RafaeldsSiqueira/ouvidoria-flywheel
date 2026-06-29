# 📑 Ouvidoria Event-Driven: Triagem Automática com HITL e Data Flywheel

Este repositório contém o projeto de um **Classificador Automático de Chamados de Ouvidoria** resiliente, seguro e de custo zero, projetado nativamente para o ecossistema **Google Cloud Platform (GCP)**.

O sistema utiliza uma arquitetura orientada a eventos para desacoplar as etapas e implementa uma condicional de segurança (*Human-in-the-Loop* - HITL) para isolar chamados contendo termos com risco operacional ou jurídico crítico, enviando-os para revisão humana. Para chamados comuns, a inteligência artificial categoriza e resolve o chamado automaticamente. Adicionalmente, aplica o conceito de *Data Flywheel*, coletando as decisões humanas para enriquecer a base de dados de futuros treinamentos de IA.

---

## 🎯 Objetivo do Negócio & Retorno (ROI)

### O Objetivo do Projeto:
Reduzir o gargalo operacional e o tempo de resposta na triagem de chamados de ouvidoria. O sistema foi projetado para automatizar a categorização de solicitações comuns, ao mesmo tempo em que garante **100% de segurança jurídica** ao desviar de forma determinística chamados que contêm riscos legais para a análise de especialistas humanos (*Human-in-the-Loop*).

### O Retorno Prático (Business ROI):
*   **Redução Drástica de Custos (FinOps):** Em cenários corporativos de grande escala (ex: **1 milhão de chamados/mês**), uma triagem 100% manual exigiria uma equipe de cerca de **80 analistas**, gerando um custo operacional de aproximadamente **R$ 240.000,00/mês** (considerando um custo médio de R$ 3.000,00 por profissional, incluindo encargos).
*   Esta arquitetura serverless processa o mesmo volume com um custo de infraestrutura de nuvem + inteligência artificial (Vertex AI / Gemini) estimado em apenas **~R$ 395,00/mês** (uma economia operacional superior a 99.8%).
*   **Mitigação de Riscos Legais:** Impede que respostas automáticas de IA gerem alucinações em casos críticos (ex: citações de PROCON ou processos), mantendo o controle total da empresa em situações sensíveis.
*   **Data Flywheel (Efeito Volante):** A intervenção do analista humano não é descartada; ela retroalimenta o banco de dados em logs estruturados, servindo como base rica para futuros retreinamentos (fine-tuning) do modelo de IA.

---

## 🏗️ Desenho da Arquitetura Lógica

```plaintext
                                   [Sistema Origem]
                                          │
                                   (1) Envia Chamado
                                          │
                                          ▼
                             [Pub/Sub: topico-chamados]
                                          │
                                          ▼
                        [Cloud Function: agente-classificador]
                                          │
                 ┌────────────────────────┴────────────────────────┐
                 │ (Cenário A: Sem Risco)                          │ (Cenário B: Risco Detectado)
                 ▼                                                 ▼
   [Firestore: chamados_resolvidos]                   [Pub/Sub: topico-auditoria]
                 │                                                 │
      ┌──────────┴──────────┐                                      ▼
      ▼                     ▼                         [Cloud Function: processa-auditoria]
[Auto-Reply / CRM]   [BigQuery / BI]                               │
(Resposta Automática)  (Dashboards)                                 ▼
                                                      [Firestore: chamados_auditoria]
                                                                   │
                                                                   ▼
                                                      [Analista Humano (Interface)]
                                                                   │
                                              ┌────────────────────┴────────────────────┐
                                              ▼                                         ▼
                                [Firestore: logs_treinamento]                 [CRM: Atualização Final]
                                  (Mecanismo Data Flywheel)                     (Resolução do Ticket)
```

---

## 🔌 Integrações Práticas e Casos de Uso (Como os resultados são consumidos)

Após o processamento dos chamados pelas Cloud Functions, o resultado final de cada cenário é integrado aos sistemas corporativos da seguinte forma:

### 🟢 Cenário A (Chamados Resolvidos Automaticamente):
1. **Automação de Resposta (Auto-Reply):** Um gatilho do Firestore (`onWrite`) monitora a coleção `chamados_resolvidos` e aciona uma Cloud Function secundária para enviar uma resposta automatizada ao cliente via e-mail (usando SendGrid/SES) ou WhatsApp (via Twilio/Zendesk API) baseada na categoria identificada pela IA.
2. **Dashboard de Métricas (BI):** Sincronização automatizada da coleção com o **Google BigQuery** para alimentar painéis executivos em tempo real no **Looker Studio** ou **PowerBI**, exibindo volumetria e sentimentos por tipo de reclamação.

### 🔴 Cenário B (Desvio de Risco & Human-in-the-Loop):
Para a auditoria especializada humana, o sistema oferece duas alternativas flexíveis de integração com o negócio:
*   **Alternativa A: Interface Customizada (Painel Próprio):** Um painel administrativo simples (construído em Streamlit ou React) consulta o Firestore buscando chamados em `AGUARDANDO_HUMANO` e os exibe para o time jurídico.
*   **Alternativa B: Integração Nativa no CRM (Sem Desenvolvimento de Frontend):** O chamado crítico é roteado via chamada de API diretamente para a fila especializada no próprio CRM da empresa (ex: Zendesk). O analista trabalha na tela nativa que já utiliza diariamente. Quando ele resolve o ticket, o CRM envia um webhook de volta à GCP para gravar os dados de fechamento.
1. **Data Flywheel:** Em ambos os casos, a decisão final do analista é salva na coleção `logs_treinamento`. Este histórico estruturado é exportado mensalmente para servir como dataset de *fine-tuning* (ajuste fino) de modelos menores e mais econômicos, ou para recalibrar o prompt do Gemini.

> [!NOTE]
> **O Padrão Adapter (Clean Architecture):** Como cada CRM (Zendesk, Salesforce, etc.) envia e espera dados em formatos JSON distintos, a arquitetura utiliza o padrão **Adapter**. O core do nosso sistema mantém contratos de dados neutros e estáveis. As camadas de infraestrutura funcionam como "tradutoras" das APIs externas, convertendo o payload de entrada de cada CRM para os nossos modelos internos e convertendo o resultado da nossa classificação para os campos customizados exigidos pelo CRM na saída. Isso permite que a empresa troque de CRM no futuro sem alterar uma única linha da lógica de triagem ou de inteligência artificial.

---

## 🛠️ Stack Tecnológica (Google Cloud Serverless)
Todos os recursos foram desenhados para se manterem 100% sob a cota do **GCP Always Free Tier**:
- **Mensageria:** Google Cloud Pub/Sub
- **Processamento:** Google Cloud Functions (Python 3.12)
- **Banco de Dados:** Google Cloud Firestore (Modo Nativo)
- **Inteligência Artificial:** API do Gemini via Google AI Studio (chave gratuita)

---

## 📂 Organização do Repositório

O projeto utiliza os padrões de **Clean Architecture** e **DDD (Domain-Driven Design)**, separando a lógica essencial de domínio de qualquer dependência externa e permitindo testes automatizados locais.

```plaintext
.
├── .agents/
│   └── AGENTS.md                  # Diretrizes globais de desenvolvimento e governança do projeto
├── docs/
│   └── plans/
│       └── 001_arquitetura_macro.md # Documentação da arquitetura lógica e custos do GCP
├── agent_workspace/
│   ├── plans/
│   │   ├── 001_setup_ambiente_free.md # Comandos gcloud CLI para criação da infraestrutura
│   │   ├── 002_agente_classificador.md# Detalhes de implementação do classificador
│   │   └── 003_processa_auditoria.md   # Detalhes de implementação do processador de auditoria
│   ├── specs/
│   │   ├── contratos_payloads_spec.md # Contratos JSON estritos de payloads e tabelas
│   │   └── testes_sandbox_spec.md     # Planejamento das fases de teste locais
│   └── skills/
│       ├── agente-classificador/      # Cloud Function 1 (Triagem)
│       │   ├── src/                   # Camadas da Clean Architecture (domain, use_cases, infrastructure)
│       │   └── tests/                 # Suíte de testes local (pytest)
│       └── processa-auditoria/        # Cloud Function 2 (Desvio de Auditoria)
│           ├── src/                   # Camadas da Clean Architecture (domain, use_cases, infrastructure)
│           └── tests/                 # Suíte de testes local (pytest)
```

---

## 🛡️ Princípios de Confiabilidade e Resiliência

Para garantir que o sistema se comporte de forma robusta e livre de custos adicionais em produção, foram incorporados os seguintes mecanismos:
1. **Idempotência no Processamento de Auditoria:** A função `processa-auditoria` consulta previamente o Firestore antes de gravar um desvio. Se o documento com o ID correspondente já existir, o processamento é ignorado. Isso impede que re-entregas do Pub/Sub sobrescrevam ações já tomadas por analistas humanos no banco de dados.
2. **Prevenção de Loops de Retry Infinitos:** Erros estruturais ou de decodificação JSON (como `KeyError` ou `JSONDecodeError`) são tratados e logados nos Handlers (`main.py`) das funções, confirmando o processamento para o Pub/Sub para que mensagens corrompidas sejam descartadas.
3. **Mecanismo de Fallback de IA:** Em caso de indisponibilidade da API do Gemini ou estouro de cota no AI Studio, a infraestrutura do classificador intercepta o erro e aplica um rótulo de fallback seguro (`DUVIDA`), garantindo que o fluxo principal nunca seja interrompido por falhas de IA.

---

## 🧪 Como Executar os Testes Locais (Sandbox)

A suíte de testes unitários e de integração utiliza o `pytest` com simulações completas de banco de dados e fila na memória, garantindo 100% de cobertura livre de custos.

### 1. Testar o Módulo 1 (agente-classificador)
```bash
# Navegar até o diretório do módulo
cd agent_workspace/skills/agente-classificador

# Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências de produção e testes
pip install -r src/requirements.txt
pip install pytest pytest-mock

# Executar a suíte de testes
pytest -v
```

### 2. Testar o Módulo 2 (processa-auditoria)
```bash
# Desativar o venv anterior se estiver ativo
deactivate

# Navegar até o diretório do módulo
cd ../processa-auditoria

# Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install -r src/requirements.txt
pip install pytest pytest-mock

# Executar os testes
pytest -v
```
