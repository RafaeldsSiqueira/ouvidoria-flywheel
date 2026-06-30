---
name: finaliza-auditoria
description: Habilidade de recebimento de atualizações da decisão de auditoria humana (webhook HTTP) e salvamento no Firestore (logs_treinamento) fechando o Data Flywheel.
---

# 🤖 Skill: Finalizador de Auditoria de Ouvidoria (Webhook HTTP)

Esta habilidade implementa a Cloud Function responsável por:
1. Servir como Webhook HTTP que recebe o sinal de resolução humana (CRM ou painel administrativo).
2. Validar a ação resolutiva e a categoria final aplicada pelo analista.
3. Atualizar o status da auditoria correspondente para `RESOLVIDO` na coleção `chamados_auditoria` do Firestore.
4. Gravar os dados de correção e categorização final na coleção `logs_treinamento` (Fechando o ciclo do **Data Flywheel**).

## 🛠️ Variáveis de Ambiente e Configuração
- `GCP_PROJECT_ID`: ID do projeto Google Cloud para inicialização do Firestore Client.
