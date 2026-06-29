---
name: agente-classificador
description: Habilidade de classificação automática de chamados de ouvidoria com detecção de risco (HITL) e integração com Gemini (AI Studio).
---

# 🤖 Skill: Agente Classificador de Ouvidoria

Esta habilidade implementa a Cloud Function responsável por:
1. Receber chamados via Pub/Sub.
2. Analisar o conteúdo para identificar riscos jurídicos e operacionais (termos como "processo", "PROCON", etc.).
3. Se houver risco (Cenário B): Desviar o fluxo publicando no `topico-auditoria` com status `AGUARDANDO_HUMANO`.
4. Se for seguro (Cenário A): Categorizar usando a API do Gemini via Google AI Studio e salvar na coleção `chamados_resolvidos` do Firestore.

## 🛠️ Variáveis de Ambiente e Configuração
- `GEMINI_API_KEY`: Chave de API obtida no Google AI Studio (necessária em produção).
- `GCP_PROJECT_ID`: ID do projeto Google Cloud.
