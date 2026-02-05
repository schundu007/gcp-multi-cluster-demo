# =============================================================================
# Service Accounts
# =============================================================================

# Service account for GKE nodes in C1
resource "google_service_account" "gke_c1_sa" {
  account_id   = "gke-c1-node-sa"
  display_name = "GKE C1 Node Service Account"
  project      = var.project_id
}

# Service account for GKE nodes in C2
resource "google_service_account" "gke_c2_sa" {
  account_id   = "gke-c2-node-sa"
  display_name = "GKE C2 Node Service Account"
  project      = var.project_id
}

# =============================================================================
# IAM Roles for GKE Node Service Accounts
# =============================================================================

# Minimal permissions for GKE nodes
locals {
  gke_node_roles = [
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer",
    "roles/artifactregistry.reader",
  ]
}

# Roles for C1 service account
resource "google_project_iam_member" "gke_c1_roles" {
  for_each = toset(local.gke_node_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.gke_c1_sa.email}"
}

# Roles for C2 service account
resource "google_project_iam_member" "gke_c2_roles" {
  for_each = toset(local.gke_node_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.gke_c2_sa.email}"
}

# =============================================================================
# Workload Identity Bindings (for future use)
# =============================================================================

# Bank of Anthos namespace service account binding for C1
# This allows Kubernetes service accounts to act as the GCP service account
resource "google_service_account_iam_member" "workload_identity_c1" {
  service_account_id = google_service_account.gke_c1_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[bank-of-anthos/default]"

  depends_on = [google_container_cluster.c1]
}

# Bank of Anthos namespace service account binding for C2
resource "google_service_account_iam_member" "workload_identity_c2" {
  service_account_id = google_service_account.gke_c2_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[bank-of-anthos/default]"

  depends_on = [google_container_cluster.c2]
}
