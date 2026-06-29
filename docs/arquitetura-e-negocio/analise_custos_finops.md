# 📊 Análise de FinOps e ROI: Ouvidoria Event-Driven em Produção

Este documento detalha os custos de infraestrutura em nuvem e o Retorno sobre Investimento (ROI) da arquitetura de ouvidoria ao processar um volume corporativo real de **1 milhão de chamados por mês**.

---

## ☁️ 1. Detalhamento de Custos Mensais (GCP & Vertex AI)

Sem considerar a cota gratuita do *Always Free Tier*, a precificação oficial baseia-se no consumo sob demanda:

### A. Mensageria (Cloud Pub/Sub)
*   **Custo:** US$ 40,00 por Terabyte de dados transferidos.
*   **Cálculo:** 1 chamado = 1 KB. 1 milhão de chamados = 1 Gigabyte (GB) de dados.
*   **Custo:** **US$ 0,04 / mês** (desprezível).

### B. Processamento (Cloud Functions)
*   **Custo:** Invocações (US$ 0,40 / milhão) + Tempo de Computação (CPU/Memória por segundo).
*   **Cálculo:** Cloud Function configurada com 256MB de RAM rodando por 1 segundo em média.
*   **Custo:** **US$ 1,90 / mês**.

### C. Banco de Dados NoSQL (Cloud Firestore)
*   **Custo:** Leituras (US$ 0,06 por 100k) + Escritass (US$ 0,18 por 100k) + Armazenamento (US$ 0,18 por GB/mês).
*   **Cálculo:** 1 milhão de escritas (US$ 1,80) + leituras de rotina (US$ 0,50) + 2 GB de armazenamento de chamados ativos (US$ 0,36).
*   **Custo:** **US$ 2,66 / mês**.

### D. Segurança e Chaves (Secret Manager)
*   **Custo:** US$ 0,06 por versão de segredo ativa + US$ 0,03 por 10.000 requisições de API.
*   **Otimização:** A leitura da API Key do Gemini ocorre apenas no cold start (inicialização do container), e não em cada chamada, graças ao cache em variáveis globais no Python.
*   **Custo:** **US$ 0,06 / mês**.

### E. Inteligência Artificial (Vertex AI - Gemini 1.5 Flash)
*   **Custo:** US$ 0,075 por milhão de Tokens de entrada + US$ 0,30 por milhão de Tokens de saída.
*   **Cálculo:** Média de 500 tokens de input (chamado + prompt do classificador) e 100 tokens de output (resposta JSON estruturada) por chamado:
    *   *Tokens de Entrada:* 500 milhões de tokens = US$ 37,50.
    *   *Tokens de Saída:* 100 milhões de tokens = US$ 30,00.
*   **Custo:** **US$ 67,50 / mês**.

---

## 💸 2. Resumo de Gastos (Faturamento Mensal)

*   **Infraestrutura de Nuvem Serverless (GCP):** US$ 4,66 (~R$ 25,00)
*   **Inteligência Artificial (Vertex AI / Gemini):** US$ 67,50 (~R$ 370,00)
*   **Custo Total Estimado:** **~US$ 72,16 / mês (~R$ 395,00 / mês)**

---

## 📈 3. Retorno sobre Investimento (ROI) e Justificativa de Negócios

A comparação financeira entre a triagem automatizada com a intervenção humana demonstra o valor prático desta arquitetura:

1.  **Modelo Tradicional (Triagem 100% Humana):**
    *   Para processar 1 milhão de chamados mensais, uma equipe de triagem manual exigiria cerca de **80 analistas**.
    *   O custo operacional de folha de pagamento estimado é de aproximadamente **R$ 240.000,00 por mês** (considerando um custo médio por profissional de R$ 3.000,00/mês, incluindo encargos).
2.  **Modelo Proposto (Event-Driven + HITL + Gemini):**
    *   A IA resolve de forma autônoma a imensa maioria dos chamados comuns (Cenário A) sob o custo de R$ 395,00/mês.
    *   A equipe de analistas é redirecionada para focar estritamente no **Cenário B** (casos de risco que requerem auditoria especializada, representando menos de 3% do volume total).
    *   **Resultado:** Redução de custos superior a 99.8%, mantendo alta precisão e conformidade regulatória.


