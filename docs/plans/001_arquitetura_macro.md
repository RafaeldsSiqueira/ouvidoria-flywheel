# 📑 Plano Macro: Sistema de Triagem de Ouvidoria com HITL e Data Flywheel

## 🎯 Visão Geral e Objetivo do Negócio
Este projeto consiste em um **Classificador Automático de Chamados de Ouvidoria** resiliente e seguro, projetado nativamente no ecossistema **Google Cloud (GCloud)**. O sistema utiliza uma arquitetura orientada a eventos para desacoplar o recebimento de mensagens e implementa uma condicional de segurança (*Human-in-the-Loop* - HITL) para isolar automaticamente chamados com alto risco operacional ou jurídico (Ex: menções a processos, PROCON, justiça, advogados). Esses chamados de risco são enviados para auditoria humana sem interromper o fluxo principal. 

Adicionalmente, o sistema aplica o conceito de *Data Flywheel*, coletando as correções e decisões humanas para retroalimentar futuros treinamentos de IA.

---

## 🏗️ Desenho da Arquitetura (Visão Lógica)

```
[Sistema Origem] ──(1) Envia Chamado──> [Pub/Sub: topico-chamados]
                                                │
                                                ▼
                                    [Cloud Function: agente-classificador]
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 │ (Cenário A: Sem Risco)                                      │ (Cenário B: Risco Detectado)
                 ▼                                                             ▼
   [Firestore: chamados_resolvidos]                             [Pub/Sub: topico-auditoria]
                                                                               │
                                                                               ▼
                                                                  [Cloud Function: processa-auditoria]
                                                                               │
                                                                               ▼
                                                                  [Firestore: chamados_auditoria]
                                                                               │
                                                                               ▼
                                                                   [Analista Humano (Interface)]
                                                                               │
                                                                               ▼
                                                                  [Firestore: logs_treinamento]
                                                                     (Mecanismo Data Flywheel)
```

---

## 🛠️ Stack Tecnológica (Google Cloud Serverless no Free Tier)

Para garantir custo zero durante o desenvolvimento e demonstração no portfólio, utilizaremos o **GCP Always Free Tier**:

1. **Mensageria:** Google Cloud Pub/Sub
   - *Cota Gratuita:* Até 10 GB de dados por mês.
2. **Processamento (Compute):** Google Cloud Functions (Python)
   - *Cota Gratuita:* Até 2 milhões de execuções mensais (respeitando limites de CPU/Memória por segundo).
3. **Banco de Dados:** Google Cloud Firestore (Modo Nativo/NoSQL)
   - *Cota Gratuita:* 1 GB de armazenamento + 50.000 leituras e 20.000 escritas por dia.
4. **Inteligência Artificial (Classificador):** API do Gemini via **Google AI Studio**
   - *Cota Gratuita:* Chave de API gratuita (limite por minuto/dia), eliminando cobranças no Vertex AI.

---

## 📐 Diretrizes de Design (Clean Architecture & DDD)

Para demonstrar maturidade de desenvolvimento de nível intermediário/sênior, aplicaremos:
- **DDD (Domain-Driven Design):** Isolamento das entidades de domínio e regras de negócio essenciais (como detecção de palavras de risco e categorização do chamado) de infraestruturas externas (Pub/Sub, Firestore).
- **Clean Architecture:** Organização modular do código dentro das Cloud Functions, onde:
  - `domain/` define as regras puras de negócios.
  - `use_cases/` coordena as ações da aplicação (ex: receber chamado e classificar).
  - `infrastructure/` implementa adaptadores de comunicação externa (SDK do Firestore, SDK do Pub/Sub, Cliente do Gemini).
  - `main.py` serve como entrypoint configurador da Cloud Function.

---

## 🛡️ Princípios de Confiabilidade e Resiliência

Para garantir que o sistema se comporte de forma robusta em um ambiente de nuvem de produção, foram incorporados os seguintes mecanismos:
1. **Idempotência no Processamento de Auditoria:** Como a entrega do Pub/Sub é do tipo *pelo menos uma vez*, a função `processa-auditoria` consulta previamente o Firestore antes de gravar um desvio. Se o documento já existir, o processamento é ignorado. Isso impede que re-entregas de mensagens sobrescrevam e reiniciem status de chamados já corrigidos ou resolvidos pelo analista humano.
2. **Prevenção de Loops de Retry por Payloads Corrompidos:** Erros de formato de dados no JSON de entrada são explicitamente tratados (captura de `KeyError` e `JSONDecodeError`), logados e descartados (enviando ACK ao Pub/Sub) para evitar que o GCP tente reprocessar eternamente mensagens inválidas, estourando a cota gratuita.
3. **Mecanismo de Fallback de IA:** Caso a API do Gemini atinja limites de quota no Free Tier ou apresente falhas temporárias, a infraestrutura do classificador intercepta a exceção e aplica um fallback de classificação segura (`DUVIDA`), garantindo a resiliência operacional do fluxo do chamado.
