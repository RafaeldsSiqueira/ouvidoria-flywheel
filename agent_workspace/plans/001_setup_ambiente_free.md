# 🚀 Plano de Ação: 001_setup_ambiente_free

## 🎯 Objetivo
Configurar toda a infraestrutura necessária no Google Cloud Platform (GCP) via terminal (`gcloud` CLI), garantindo a ativação, configuração de acessos, alertas de orçamento e validação de todos os recursos no Free Tier.

## 📋 Pré-requisitos
- Ter o `gcloud` CLI instalado e autenticado.
- Ter um ID de projeto GCP válido.

---

## 📝 Passo a Passo da Execução

### 1. Autenticação, Configuração do Projeto e Escopo
Criar um projeto dedicado no console do GCP para não misturar com outros estudos.
```bash
export PROJECT_ID="SEU_PROJECT_ID"
export REGION="southamerica-east1" # São Paulo (ou us-central1 se preferir cota US)

# Autenticar no GCP
gcloud auth login

# Definir o projeto padrão
gcloud config set project $PROJECT_ID
```

#### 1.1. Criar orçamento para o projeto definido
Para garantir que o projeto permaneça 100% gratuito, configuramos um orçamento e alerta de custo de R$ 1,00 ou R$ 5,00 no console do GCP (faturamento / Billing).
*(Nota: Alertas de orçamento geralmente são criados via Console Web do Billing ou pela API de Billing do GCP, necessitando de permissões administrativas de Billing Account).*
```bash
# Link de referência para criar alerta de orçamento no console:
# https://console.cloud.google.com/billing/budgets
```

---

### 2. Provisionamento do Pub/Sub
Criar os tópicos necessários para a comunicação assíncrona orientada a eventos.
```bash
# Habilitar a API do Pub/Sub
gcloud services enable pubsub.googleapis.com

# Criar o tópico de entrada de chamados
gcloud pubsub topics create topico-chamados

# Criar o tópico de desvio de auditoria
gcloud pubsub topics create topico-auditoria
```

#### 2.2. Criar regras do IAM para liberar acesso predefinido aos serviços
Precisamos garantir que a Cloud Function (ou o agente) tenha as permissões necessárias para ler/escrever no Pub/Sub e Firestore.
```bash
# Criar uma Service Account dedicada para os agentes do projeto
gcloud iam service-accounts create sa-ouvidoria-agente \
    --description="Service Account para o Agente Classificador e Auditoria" \
    --display-name="SA Ouvidoria Agente"

# Atribuir permissão de publicador no Pub/Sub para a Service Account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:sa-ouvidoria-agente@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher"

# Atribuir permissão de assinante (subscriber) no Pub/Sub
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:sa-ouvidoria-agente@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/pubsub.subscriber"

# Atribuir permissão de leitura/escrita no Firestore (Datastore User)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:sa-ouvidoria-agente@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/datastore.user"
```

---

### 3. Provisionamento do Firestore
Criar o banco de dados no modo nativo (Native Mode) para habilitar consultas complexas em tempo real e compatibilidade com o SDK oficial.

#### 3.1. Ativar a API respectiva
```bash
# Ativar a API do Firestore/Datastore
gcloud services enable firestore.googleapis.com

# Instanciar o banco Firestore em modo nativo
gcloud firestore databases create --location=$REGION --type=firestore-native
```

---

### 4. Configurar Secret Manager para a API Key do Gemini
Para guardar a API Key do Google AI Studio com segurança.
```bash
# Habilitar a API do Secret Manager
gcloud services enable secretmanager.googleapis.com

# Criar o secret para a API Key
gcloud secrets create gemini-api-key --replication-policy="automatic"

# Adicionar a chave de API (será solicitado o valor no terminal)
# echo -n "SUA_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=-
```

---

## 🔍 Comandos de Validação

#### 4.1. Validação em ambiente sandbox antes do teste final
Antes de testar na infraestrutura de nuvem de produção, validamos a criação dos recursos localmente ou usando listagens no ambiente do sandbox.
```bash
# Listar tópicos do Pub/Sub
gcloud pubsub topics list

# Validar se as assinaturas e permissões da SA estão corretas
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format='table(bindings.role, bindings.members)' \
    --filter="bindings.members:sa-ouvidoria-agente"

# Validar estado do banco de dados Firestore
gcloud firestore databases list
```
