---
name: processa-auditoria
description: Habilidade de recebimento de chamados de risco desviados e gravação na coleção chamados_auditoria do Firestore para análise humana (HITL).
---

# 🤖 Skill: Processador de Auditoria de Ouvidoria

Esta habilidade implementa a Cloud Function responsável por:
1. Escutar mensagens de desvio publicadas no `topico-auditoria` do Pub/Sub.
2. Decodificar e validar o contrato estrito de auditoria.
3. Persistir o chamado sob o status de `AGUARDANDO_HUMANO` na coleção NoSQL `chamados_auditoria` do Firestore.

## 🛠️ Variáveis de Ambiente e Configuração
- `GCP_PROJECT_ID`: ID do projeto Google Cloud para inicialização do Firestore Client.
