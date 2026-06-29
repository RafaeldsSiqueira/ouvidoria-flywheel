#!/usr/bin/env bash

# ==============================================================================
# 🚀 script_setup_gcp_infra.sh
# script para provisionamento automatizado dos recursos no GCP Free Tier
# ==============================================================================

set -euo pipefail

# --- CONFIGURAÇÕES DE ENTRADA ---
PROJECT_ID="${1:-}"
REGION="${2:-southamerica-east1}" # Região de São Paulo (ou altere para us-central1)

if [[ -z "$PROJECT_ID" ]]; then
    echo "❌ ERRO: O ID do projeto GCP deve ser passado como primeiro argumento."
    echo "Uso: ./setup_gcp_infra.sh <PROJECT_ID> [REGION]"
    exit 1
fi

echo "=================================================================="
echo "🎯 Iniciando Setup de Infraestrutura GCP para Ouvidoria Event-Driven"
echo "   Projeto: $PROJECT_ID"
echo "   Região:  $REGION"
echo "=================================================================="

# 1. Configurar escopo do projeto padrão
echo "⚙️ 1. Definindo projeto padrão no gcloud CLI..."
gcloud config set project "$PROJECT_ID"

# 2. Habilitação de APIs
echo "🔌 2. Habilitando APIs necessárias..."
gcloud services enable \
    pubsub.googleapis.com \
    firestore.googleapis.com \
    secretmanager.googleapis.com

# 3. Provisionamento do Pub/Sub
echo "📨 3. Criando tópicos do Pub/Sub..."
if gcloud pubsub topics describe topico-chamados &>/dev/null; then
    echo "   - Tópico 'topico-chamados' já existe. Ignorando."
else
    gcloud pubsub topics create topico-chamados
    echo "   - Tópico 'topico-chamados' criado com sucesso."
fi

if gcloud pubsub topics describe topico-auditoria &>/dev/null; then
    echo "   - Tópico 'topico-auditoria' já existe. Ignorando."
else
    gcloud pubsub topics create topico-auditoria
    echo "   - Tópico 'topico-auditoria' criado com sucesso."
fi

# 4. Provisionamento da Service Account e regras IAM
echo "🔑 4. Configurando Service Account e permissões IAM..."
SA_NAME="sa-ouvidoria-agente"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if gcloud iam service-accounts describe "$SA_EMAIL" &>/dev/null; then
    echo "   - Service Account '$SA_EMAIL' já existe. Ignorando."
else
    gcloud iam service-accounts create "$SA_NAME" \
        --description="Service Account para o Agente Classificador e Auditoria" \
        --display-name="SA Ouvidoria Agente"
    echo "   - Service Account '$SA_EMAIL' criada com sucesso."
fi

# Atribuição de permissões IAM
echo "   - Atribuindo role 'roles/pubsub.publisher'..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/pubsub.publisher" &>/dev/null

echo "   - Atribuindo role 'roles/pubsub.subscriber'..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/pubsub.subscriber" &>/dev/null

echo "   - Atribuindo role 'roles/datastore.user' (Firestore)..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/datastore.user" &>/dev/null

# 5. Provisionamento do Firestore (Native Mode)
echo "💾 5. Criando banco de dados Firestore..."
# Verifica se o banco padrão (default) já existe. Se não, cria-o.
if gcloud firestore databases describe &>/dev/null; then
    echo "   - Instância Firestore '(default)' já existe."
else
    gcloud firestore databases create --location="$REGION" --type=firestore-native
    echo "   - Instância Firestore criada no modo Native na região $REGION."
fi

# 6. Configuração do Secret Manager
echo "🔒 6. Criando Secret para API Key do Gemini..."
if gcloud secrets describe gemini-api-key &>/dev/null; then
    echo "   - Secret 'gemini-api-key' já existe. Ignorando."
else
    gcloud secrets create gemini-api-key --replication-policy="automatic"
    echo "   - Secret 'gemini-api-key' criado."
    echo "   📌 IMPORTANTE: Adicione o valor da chave usando:"
    echo "     echo -n \"SUA_API_KEY\" | gcloud secrets versions add gemini-api-key --data-file=-"
fi

echo "=================================================================="
echo "✅ Setup concluído com sucesso!"
echo "   Próximo passo: deploy das Cloud Functions com gcloud deploy"
echo "=================================================================="
