# 🏗️ Fluxos da Arquitetura, Data Flywheel e Pitch de Portfólio

Este documento detalha os dois caminhos de execução do sistema, a aplicação prática dos resultados e o pitch conceitual ideal para postagens no LinkedIn ou apresentações de portfólio.

---

## 🟢 1. Caminho A: Chamados Resolvidos Automaticamente (`chamados_resolvidos`)

Representa o fluxo automatizado de baixo custo (sem intervenção humana). O resultado (JSON com a classificação da IA salvo no Firestore) é usado para:

### A. Automação de Resposta ao Cliente (Auto-Reply)
*   Uma Cloud Function secundária é disparada por gatilhos do Firestore (`onWrite`) ao detectar novos registros na coleção `chamados_resolvidos`.
*   Ela envia automaticamente um e-mail de resposta personalizado para o cliente com base na categoria definida pelo Gemini.
*   *Exemplo:* Se classificado como `DUVIDA` sobre cadastros, envia os links do passo a passo do FAQ. Se for `ELOGIO`, envia uma mensagem de agradecimento.

### B. Dashboard de Analytics e Business Intelligence (BI)
*   Os dados da coleção `chamados_resolvidos` são sincronizados com o **Google BigQuery** (utilizando a extensão oficial Firestore-to-BigQuery).
*   Esses dados históricos servem de fonte para painéis dinâmicos no **Looker Studio**, onde gestores podem acompanhar a volumetria de reclamações ou dúvidas por categoria em tempo real.

---

## 🔴 2. Caminho B: Desvio de Risco e Human-in-the-Loop (`chamados_auditoria` e `logs_treinamento`)

Este caminho protege a corporação contra crises financeiras ou jurídicas. Os resultados (chamados com status `AGUARDANDO_HUMANO` e o log de treinamento final do Flywheel) são consumidos da seguinte forma:

### A. Painel do Analista (Interface Administrativa)
*   Uma interface web simples (construída em Streamlit, React ou Angular) consome a coleção NoSQL `chamados_auditoria` trazendo documentos com status `AGUARDANDO_HUMANO`.
*   O analista especializado do time jurídico ou de ouvidoria de 2º nível revisa os dados na tela, que exibe o chamado e o termo crítico encontrado (ex: *"Vou no PROCON"*).
*   Após o tratamento humano, o analista atualiza o status do chamado para `RESOLVIDO`.

### B. Mecanismo de Aprendizado Contínuo (Data Flywheel)
*   Quando o analista submete a decisão, os dados do desvio e a correção humana final (a classe correta) são gravados na coleção `logs_treinamento`.
*   Esse histórico estruturado é usado periodicamente para:
    *   **Ajuste Fino (Fine-Tuning):** Treinar ou calibrar modelos de IA locais menores na GCP, economizando custos futuros de API do Gemini.
    *   **Engenharia de Prompt:** Ajustar o prompt de sistema do classificador principal inserindo exemplos das correções humanas como novos contextos (*Few-Shot Learning*).

---

## 💡 3. Pitch para LinkedIn e Portfólio (Copywriting)

Abaixo está o roteiro e pitch conceitual perfeito para você utilizar ao divulgar o projeto no LinkedIn:

> 🚀 **Como processar 1 milhão de chamados por mês gastando menos de R$ 400,00 e com Custo Zero de Infraestrutura Ociosa?**
>
> Desenvolvi um **Classificador Automático de Ouvidoria Event-Driven** integrado à nuvem do **Google Cloud (GCP)** e ao **Gemini (Google AI Studio)**.
>
> ### 💡 Os destaques de engenharia do projeto:
>
> 1. **Serverless de Custo Zero (GCP Free Tier):** A arquitetura utiliza Cloud Functions, Pub/Sub e Firestore. Se não houver chamados, a conta do GCP é exatamente R$ 0,00.
> 2. **Segurança com Human-in-the-Loop (HITL):** O sistema identifica deterministicamente termos críticos de risco jurídico (como *"PROCON"* ou *"processo"*) e desvia o chamado automaticamente para uma fila de auditoria humana, eliminando qualquer risco de a IA alucinar respostas legais sensíveis.
> 3. **Mecanismo Data Flywheel:** A tomada de decisão dos analistas humanos é coletada e persistida em logs estruturados. Esse dataset serve para retroalimentar e retreinar a inteligência artificial de forma contínua.
>
> ### 📐 Padrões de Design Aplicados:
> * Clean Architecture e DDD (Domain-Driven Design) em Python.
> * Idempotência robusta contra reprocessamento do Pub/Sub.
> * Mocks em memória (pytest) para testes locais rápidos e gratuitos.
>
> 🔗 *Confira o repositório completo e documentado no meu GitHub!*

---

## 📐 Por que isso chama a atenção dos Recrutadores?
*   Demonstra que você não é apenas um "codificador de prompts", mas sabe desenhar uma **solução de nível corporativo (Enterprise)** focada em confiabilidade.
*   Mostra conhecimento prático de **FinOps**, que é a cultura de otimização de custos em nuvem (altamente valorizada por gerentes de engenharia).
