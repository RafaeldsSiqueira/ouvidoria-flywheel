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

Abaixo está o comparativo de viabilidade econômica do sistema para diferentes escalas de negócio, confrontando a triagem manual tradicional com a nossa arquitetura serverless automatizada:

### Tabela Comparativa de Custos

| Escala do Negócio | Volumetria Mensal | Equipe de Triagem Manual | Custo Operacional Manual | Custo Serverless (GCP + Vertex AI) | Economia Operacional | Vantagem de Negócio Principal |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Pequeno Porte** | **10.000 chamados** | ~1 analista (meio período) | ~R$ 1.500,00 / mês | **~R$ 4,00 / mês** *(o preço de um café)* | **99.7%** | Custo operacional fixo quase zero; escala imediata sob demanda. |
| **Grande Porte** | **1.000.000 chamados** | ~80 analistas dedicados | ~R$ 240.000,00 / mês | **~R$ 395,00 / mês** | **99.8%** | Liberação do time humano para auditoria jurídica e casos complexos. |

### Detalhamento para Pequeno Porte (10.000 chamados/mês)
Em pequenas operações, o sistema atua quase de graça porque os limites do **GCP Always Free Tier** não são ultrapassados:
1.  **GCP (Pub/Sub + Functions + Firestore):** R$ 0,00 (100% coberto pelo Free Tier).
2.  **Secret Manager (Cofre de Chaves):** ~R$ 0,33/mês (custo fixo de 1 versão de segredo ativa).
3.  **Vertex AI (Gemini 1.5 Flash):** ~R$ 3,70/mês (calculado para 5M tokens de entrada e 1M de saída).
    *   *Nota:* Se a empresa optar por usar a chave gratuita do Google AI Studio em vez da Vertex AI corporativa, o custo de IA cai para R$ 0,00, resultando em um custo total de **R$ 0,33/mês**.


