# ==============================================================================
# 🚀 main.tf - Ouvidoria Event-Driven & IaC (Terraform)
# Provisionamento de infraestrutura serverless elegível para Always Free Tier
# ==============================================================================

# 1. Habilitação de APIs
resource "google_project_service" "gcp_services" {
  for_each = toset([
    "pubsub.googleapis.com",
    "firestore.googleapis.com",
    "secretmanager.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudresourcemanager.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# 2. Provisionamento do Pub/Sub
resource "google_pubsub_topic" "topico_chamados" {
  name       = "topico-chamados"
  depends_on = [google_project_service.gcp_services]
}

resource "google_pubsub_topic" "topico_auditoria" {
  name       = "topico-auditoria"
  depends_on = [google_project_service.gcp_services]
}

# 3. Criação da Service Account do Agente
resource "google_service_account" "sa_ouvidoria" {
  account_id   = "sa-ouvidoria-agente"
  display_name = "SA Ouvidoria Agente"
  depends_on   = [google_project_service.gcp_services]
}

# 4. Atribuição de permissões IAM do projeto para a Service Account (SOLID Least Privilege)
resource "google_project_iam_member" "sa_roles" {
  for_each = toset([
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/datastore.user",
    "roles/aiplatform.user"
  ])
  project    = var.project_id
  role       = each.key
  member     = "serviceAccount:${google_service_account.sa_ouvidoria.email}"
  depends_on = [google_service_account.sa_ouvidoria]
}

# 5. Provisionamento da Instância Firestore (Modo Nativo)
resource "google_firestore_database" "firestore_db" {
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
  depends_on  = [google_project_service.gcp_services]
}

# 6. Configuração do Secret Manager para a chave do Gemini
resource "google_secret_manager_secret" "gemini_key" {
  secret_id = "gemini-api-key"
  replication {
    auto {}
  }
  depends_on = [google_project_service.gcp_services]
}

# Atribuição de permissão para a Service Account ler o Segredo no Secret Manager
resource "google_secret_manager_secret_iam_member" "sa_secret_access" {
  secret_id  = google_secret_manager_secret.gemini_key.secret_id
  role       = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:${google_service_account.sa_ouvidoria.email}"
  depends_on = [google_secret_manager_secret.gemini_key, google_service_account.sa_ouvidoria]
}
