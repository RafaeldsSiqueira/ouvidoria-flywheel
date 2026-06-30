#!/usr/bin/env bash

# ==============================================================================
# 🚀 deploy_functions.sh
# Script para deploy automatizado das Cloud Functions no GCP Free Tier
# ==============================================================================

set -euo pipefail

PROJECT_ID="project-647ad0dc-ac55-4368-859"
REGION="us-central1"
SA_EMAIL="sa-ouvidoria-agente@$PROJECT_ID.iam.gserviceaccount.com"

echo "=================================================================="
echo "🚀 Iniciando deploy das Cloud Functions na GCP..."
echo "   Projeto: $PROJECT_ID"
echo "   Região:  $REGION"
echo "=================================================================="

# 1. Deploy da Cloud Function 1: agente-classificador
echo "🧠 1. Realizando deploy de 'agente-classificador'..."
gcloud functions deploy agente-classificador \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --runtime=python312 \
    --trigger-topic=topico-chamados \
    --entry-point=classificar_chamado \
    --service-account="$SA_EMAIL" \
    --source=agent_workspace/skills/agente-classificador/src \
    --set-secrets="GEMINI_API_KEY=gemini-api-key:latest" \
    --allow-unauthenticated

# 2. Deploy da Cloud Function 2: processa-auditoria
echo "🛡️ 2. Realizando deploy de 'processa-auditoria'..."
gcloud functions deploy processa-auditoria \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --runtime=python312 \
    --trigger-topic=topico-auditoria \
    --entry-point=processar_auditoria \
    --service-account="$SA_EMAIL" \
    --source=agent_workspace/skills/processa-auditoria/src \
    --allow-unauthenticated

# 3. Deploy da Cloud Function 3: finaliza-auditoria
echo "📥 3. Realizando deploy de 'finaliza-auditoria' (Webhook HTTP)..."
gcloud functions deploy finaliza-auditoria \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --runtime=python312 \
    --trigger-http \
    --entry-point=webhook_resolucao \
    --service-account="$SA_EMAIL" \
    --source=agent_workspace/skills/finaliza-auditoria/src \
    --allow-unauthenticated

echo "=================================================================="
echo "✅ Deploy de todas as Cloud Functions concluído com sucesso!"
echo "=================================================================="
