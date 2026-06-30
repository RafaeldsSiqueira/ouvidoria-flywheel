# 📑 Ouvidoria Event-Driven: Triagem Automática com HITL e Data Flywheel

Este repositório contém o projeto de um **Classificador Automático de Chamados de Ouvidoria** resiliente, seguro e de custo zero, projetado nativamente para o ecossistema **Google Cloud Platform (GCP)**.

O sistema utiliza uma arquitetura orientada a eventos para desacoplar as etapas e implementa uma condicional de segurança (*Human-in-the-Loop* - HITL) para isolar chamados contendo termos com risco operacional ou jurídico crítico, enviando-os para revisão humana. Para chamados comuns, a inteligência artificial categoriza e resolve o chamado automaticamente. Adicionalmente, aplica o conceito de *Data Flywheel*, coletando as decisões humanas para enriquecer a base de dados de futuros treinamentos de IA.

---

## 🎯 Objetivo do Negócio & Retorno (ROI)

### O Objetivo do Projeto:
Reduzir o gargalo operacional e o tempo de resposta na triagem de chamados de ouvidoria. O sistema foi projetado para automatizar a categorização de solicitações comuns, ao mesmo tempo em que garante **100% de segurança jurídica** ao desviar de forma determinística chamados que contêm riscos legais para a análise de especialistas humanos (*Human-in-the-Loop*).

### O Retorno Prático (Business ROI):

Abaixo apresentamos a comparação de viabilidade econômica e de infraestrutura do sistema para diferentes escalas de negócio (comparando a operação 100% manual com a nossa arquitetura serverless e IA corporativa em produção):

| Escala do Negócio | Volumetria Mensal | Equipe de Triagem Manual | Custo Operacional Manual | Custo Serverless (GCP + Vertex AI) | Economia Operacional | Vantagem de Negócio Principal |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Pequeno Porte** | **10.000 chamados** | ~1 analista (meio período) | ~R$ 1.500,00 / mês | **~R$ 4,00 / mês** *(o preço de um café)* | **99.7%** | Custo operacional fixo quase zero; escala imediata sob demanda. |
| **Grande Porte** | **1.000.000 chamados** | ~80 analistas dedicados | ~R$ 240.000,00 / mês | **~R$ 395,00 / mês** | **99.8%** | Liberação do time humano para auditoria jurídica e casos complexos. |

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

## 💡 Filosofia de Resolução: Autoatendimento vs. Contato Humano Emocional

A tomada de decisão estratégica sobre responder automaticamente ou direcionar a um humano baseia-se no nível de sensibilidade e risco do chamado:

*   **Para Chamados Sem Risco (Cenário A - Autoatendimento):** Em chamados comuns de triagem bem-sucedida, o sistema reduz o esforço do time a zero. Um gatilho no Firestore busca templates dinâmicos em uma coleção de `base_conhecimento` e envia o e-mail ou mensagem direta (WhatsApp/SMS) de resposta ao cliente de forma instantânea.
*   **Para Chamados de Risco (Cenário B - Contato Humano):** Em chamados com termos críticos (risco jurídico/operacional), a automação de resposta é **expressamente evitada**. O sistema realiza apenas o roteamento silencioso do ticket para a fila do time jurídico no CRM. A resolução é 100% conduzida por um analista humano especializado para garantir empatia, negociação e tato emocional, mitigando atritos e protegendo a relação comercial com o cliente.

---

## 🛠️ Stack Tecnológica (Google Cloud Serverless)
Todos os recursos foram desenhados para se manterem 100% sob a cota do **GCP Always Free Tier**:
- **Mensageria:** Google Cloud Pub/Sub
- **Processamento:** Google Cloud Functions (Python 3.12)
- **Banco de Dados:** Google Cloud Firestore (Modo Nativo)
- **Inteligência Artificial:** Google AI Studio API ou Vertex AI API (Gemini via SDK modular - configurável com chave do Secret Manager para sandboxes de desenvolvimento ou IAM nativo para produção corporativa)

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
│       ├── processa-auditoria/        # Cloud Function 2 (Desvio de Auditoria)
│       │   ├── src/                   # Camadas da Clean Architecture (domain, use_cases, infrastructure)
│       │   └── tests/                 # Suíte de testes local (pytest)
│       └── finaliza-auditoria/        # Cloud Function 3 (Webhook de Resolução / HITL)
│           ├── src/                   # Camadas da Clean Architecture (domain, use_cases, infrastructure)
│           └── tests/                 # Suíte de testes local (pytest)
```

---

## 🛡️ Princípios de Confiabilidade e Resiliência

Para garantir que o sistema se comporte de forma robusta e livre de custos adicionais em produção, foram incorporados os seguintes mecanismos:
1. **Idempotência no Processamento de Auditoria:** A função `processa-auditoria` consulta previamente o Firestore antes de gravar um desvio. Se o documento com o ID correspondente já existir, o processamento é ignorado. Isso impede que re-entregas do Pub/Sub sobrescrevam ações já tomadas por analistas humanos no banco de dados.
2. **Prevenção de Loops de Retry Infinitos:** Erros estruturais ou de decodificação JSON (como `KeyError` ou `JSONDecodeError`) são tratados e logados nos Handlers (`main.py`) das funções, confirmando o processamento para o Pub/Sub para que mensagens corrompidas sejam descartadas.
3. **Mecanismo de Fallback de IA:** Em caso de indisponibilidade da API do Gemini ou falhas de comunicação com o provedor (AI Studio ou Vertex AI), a infraestrutura do classificador intercepta o erro e aplica um rótulo de fallback seguro (`DUVIDA`), garantindo que o fluxo principal nunca seja interrompido por falhas de IA.

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

### 3. Testar o Módulo 3 (finaliza-auditoria)
```bash
# Desativar o venv anterior se estiver ativo
deactivate

# Navegar até o diretório do módulo
cd ../finaliza-auditoria

# Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências de produção e testes
pip install -r src/requirements.txt
pip install pytest pytest-mock flask

# Executar os testes
pytest -v
```

---

## 🧪 Como Executar o Teste Funcional na Nuvem Real (GCP)

Após realizar o deploy das Cloud Functions na sua conta do Google Cloud, você pode conduzir um teste funcional completo utilizando a linha de comando para validar a lógica em produção e coletar evidências de funcionamento.

### 🟢 Cenário A: Chamado Comum (Sucesso e Classificação por IA)

Neste cenário, enviaremos um chamado padrão sem termos de risco para provar que a IA o categoriza automaticamente.

#### 1. Enviar o Chamado (Terminal 1):
Execute o comando para publicar um chamado de dúvida no tópico de entrada:
```bash
gcloud pubsub topics publish topico-chamados \
  --message='{"chamado_id": "11111111-1111-1111-1111-111111111111", "cliente_id": "cliente-123", "data_criacao": "2026-06-29T18:18:18Z", "assunto": "Dúvida sobre entrega", "mensagem": "Olá, meu produto ainda não chegou. Poderiam me passar o código de rastreamento do envio?"}'
```

#### 2. Evidências Técnicas a Coletar:
*   **Logs do Cloud Logging (Terminal 2 ou Console GCP):** Os logs da Cloud Function `agente-classificador` mostrarão:
    1.  `Iniciando processamento do chamado 11111111-...`
    2.  `Nenhum termo de risco detectado.`
    3.  `Chamando API do Gemini (Tempo de resposta: X.Xs)...`
    4.  `Classificação gerada: DUVIDA. Salvando na coleção chamados_resolvidos.`
*   **Firestore (Banco de Dados):** Acesse a coleção `chamados_resolvidos` no console do Firestore. Você verá um novo documento com o campo `status_final: RESOLVIDO_AUTO` e a resposta estruturada.

---

### 🔴 Cenário B: Chamado de Risco (Bloqueio determinístico e Desvio)

Neste cenário, enviaremos um chamado contendo termos jurídicos críticos para provar que o sistema barra a IA e joga o fluxo para auditoria humana de forma determinística.

#### 1. Enviar o Chamado (Terminal 1):
Publique um chamado contendo o termo "PROCON" e "processar":
```bash
gcloud pubsub topics publish topico-chamados \
  --message='{"chamado_id": "22222222-2222-2222-2222-222222222222", "cliente_id": "cliente-999", "data_criacao": "2026-06-29T18:18:18Z", "assunto": "Reclamação Urgente", "mensagem": "Se meu estorno não cair até amanhã, vou abrir reclamação no PROCON e processar vocês na justiça!"}'
```

#### 2. Evidências Técnicas a Coletar:
*   **Logs do Cloud Logging:** Os logs mostrarão a atuação das duas Cloud Functions sequencialmente:
    *   `agente-classificador`: *`Risco detectado! Gatilhos encontrados: ['procon', 'processar', 'justiça']. Pulando IA. Publicando no topico-auditoria.`*
    *   `processa-auditoria`: *`Recebido desvio de auditoria. Salvando chamado na fila humana.`*
*   **Firestore (Banco de Dados):**
    *   Na coleção `chamados_resolvidos`: Estará vazia para este ID (provando que o fluxo seguro funcionou e não chamou a IA).
    *   Na coleção `chamados_auditoria`: Haverá um novo documento com `status_revisao: AGUARDANDO_HUMANO` e `motivo_desvio: RISCO_JURIDICO_DETECTADO`.

---

### 📈 Como Coletar Métricas Reais no GCP (FinOps e Confiabilidade)

Depois de rodar estes testes, você terá dados suficientes para extrair métricas de desempenho para o seu portfólio:

1.  **Tempo de Execução (Latência):**
    *   No console do GCP, acesse **Cloud Functions > agente-classificador > Monitoramento**.
    *   Você verá o gráfico **Execution Times**. O Cenário B (sem IA) executa na faixa de **50ms** (apenas checagem regex), enquanto o Cenário A (com Gemini) leva entre **800ms e 1.5s** (dependendo da resposta do Gemini). Isso demonstra como o desvio de segurança economiza tempo e cota de computação.
2.  **Métricas de Volume de Escrita (Firestore):**
    *   No painel do Firestore, você verá a telemetria mostrando exatamente 1 escrita para o Cenário A e 1 escrita para o Cenário B.
3.  **Logs de Sucesso da Execução:**
    *   No Log Explorer, você pode exportar a sequência lógica das mensagens transitando pelo Pub/Sub até a gravação no banco de dados.

---

## 🔮 Evolução Futura: Arquitetura RAG + Fila de Incerteza (HITL)

Como próximo marco evolutivo de produto, o sistema está preparado para suportar a transição de uma triagem simples para uma **geração automatizada de respostas contextuais** utilizando **RAG (Retrieval-Augmented Generation)**:

1. **Base de Conhecimento Vetorial (Vertex AI Search):** Upload de manuais internos, regras de negócio e FAQs da empresa no Google Cloud Storage (GCS) e indexação no banco de dados vetorial do GCP.
2. **Geração de Resposta Aterrada (Grounded Response):** Ao processar um chamado comum (Cenário A), o classificador busca as regras e FAQs mais relevantes no banco vetorial e as injeta como contexto para o Gemini. A IA gera uma resposta personalizada baseando-se estritamente nas políticas da empresa, mitigando alucinações.
3. **Fila de Incerteza (Confidence Routing):** O Gemini retorna no JSON estruturado a resposta e o score de confiabilidade (`confianca_resposta`):
   *   **Confiança Alta (>= 0.80):** O chamado é respondido de forma 100% automática ao cliente (Auto-Reply).
   *   **Confiança Baixa (< 0.80):** O chamado é enviado para a fila humana (`chamados_auditoria`) com a tag `INSUFICIENTE_CONFIANCA` contendo o rascunho gerado pela IA. O analista apenas revisa e ajusta o texto pré-escrito, economizando tempo de digitação e garantindo a qualidade final.
