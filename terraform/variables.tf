variable "project_id" {
  type        = string
  description = "O ID do projeto do Google Cloud Platform (GCP)."
}

variable "region" {
  type        = string
  default     = "us-central1" # Usamos us-central1 (Iowa) para garantir elegibilidade no Firestore Always Free Tier
  description = "A região onde os recursos do GCP serão provisionados."
}
