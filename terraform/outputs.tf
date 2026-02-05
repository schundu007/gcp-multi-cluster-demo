# =============================================================================
# Cluster Outputs
# =============================================================================

output "cluster_c1_name" {
  description = "Name of GKE cluster C1"
  value       = google_container_cluster.c1.name
}

output "cluster_c1_endpoint" {
  description = "Endpoint for GKE cluster C1"
  value       = google_container_cluster.c1.endpoint
  sensitive   = true
}

output "cluster_c1_location" {
  description = "Location of GKE cluster C1"
  value       = google_container_cluster.c1.location
}

output "cluster_c2_name" {
  description = "Name of GKE cluster C2"
  value       = google_container_cluster.c2.name
}

output "cluster_c2_endpoint" {
  description = "Endpoint for GKE cluster C2"
  value       = google_container_cluster.c2.endpoint
  sensitive   = true
}

output "cluster_c2_location" {
  description = "Location of GKE cluster C2"
  value       = google_container_cluster.c2.location
}

# =============================================================================
# VPC Outputs
# =============================================================================

output "vpc_c1_name" {
  description = "Name of VPC C1"
  value       = google_compute_network.vpc_c1.name
}

output "vpc_c1_id" {
  description = "ID of VPC C1"
  value       = google_compute_network.vpc_c1.id
}

output "vpc_c2_name" {
  description = "Name of VPC C2"
  value       = google_compute_network.vpc_c2.name
}

output "vpc_c2_id" {
  description = "ID of VPC C2"
  value       = google_compute_network.vpc_c2.id
}

output "subnet_c1_cidr" {
  description = "CIDR of subnet C1"
  value       = google_compute_subnetwork.subnet_c1.ip_cidr_range
}

output "subnet_c2_cidr" {
  description = "CIDR of subnet C2"
  value       = google_compute_subnetwork.subnet_c2.ip_cidr_range
}

# =============================================================================
# ILB IP Outputs
# =============================================================================

output "ilb_userservice_ip" {
  description = "Internal IP for userservice ILB"
  value       = google_compute_address.ilb_userservice.address
}

output "ilb_contacts_ip" {
  description = "Internal IP for contacts ILB"
  value       = google_compute_address.ilb_contacts.address
}

output "ilb_balancereader_ip" {
  description = "Internal IP for balancereader ILB"
  value       = google_compute_address.ilb_balancereader.address
}

output "ilb_transactionhistory_ip" {
  description = "Internal IP for transactionhistory ILB"
  value       = google_compute_address.ilb_transactionhistory.address
}

output "ilb_ledgerwriter_ip" {
  description = "Internal IP for ledgerwriter ILB"
  value       = google_compute_address.ilb_ledgerwriter.address
}

output "ilb_accounts_db_ip" {
  description = "Internal IP for accounts-db ILB"
  value       = google_compute_address.ilb_accounts_db.address
}

# =============================================================================
# Service Account Outputs
# =============================================================================

output "gke_c1_service_account" {
  description = "Service account email for GKE C1 nodes"
  value       = google_service_account.gke_c1_sa.email
}

output "gke_c2_service_account" {
  description = "Service account email for GKE C2 nodes"
  value       = google_service_account.gke_c2_sa.email
}

# =============================================================================
# Kubeconfig Commands
# =============================================================================

output "kubeconfig_c1_command" {
  description = "Command to configure kubectl for cluster C1"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.c1.name} --region ${google_container_cluster.c1.location} --project ${var.project_id}"
}

output "kubeconfig_c2_command" {
  description = "Command to configure kubectl for cluster C2"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.c2.name} --region ${google_container_cluster.c2.location} --project ${var.project_id}"
}

# =============================================================================
# Firewall Rule Names (for revocation demo)
# =============================================================================

output "firewall_c1_to_c2_app" {
  description = "Name of firewall rule allowing C1 to C2 app traffic (for revocation demo)"
  value       = google_compute_firewall.c1_to_c2_app.name
}

output "firewall_c1_to_c2_app_ingress" {
  description = "Name of firewall rule allowing C1 to C2 app ingress (for revocation demo)"
  value       = google_compute_firewall.c1_to_c2_app_ingress.name
}

output "firewall_c2_to_c1_db" {
  description = "Name of firewall rule allowing C2 to C1 db traffic (for revocation demo)"
  value       = google_compute_firewall.c2_to_c1_db.name
}

output "firewall_c2_to_c1_db_egress" {
  description = "Name of firewall rule allowing C2 to C1 db egress (for revocation demo)"
  value       = google_compute_firewall.c2_to_c1_db_egress.name
}

# =============================================================================
# Summary Output
# =============================================================================

output "summary" {
  description = "Summary of deployed infrastructure"
  value = <<-EOT

    ============================================================
    GCP Multi-Cluster Infrastructure Deployed Successfully
    ============================================================

    CLUSTERS:
      C1 (Frontend + accounts-db): ${google_container_cluster.c1.name}
         Region: ${google_container_cluster.c1.location}
         Zones: ${join(", ", var.zones_c1)}

      C2 (Backends + ledger-db): ${google_container_cluster.c2.name}
         Region: ${google_container_cluster.c2.location}
         Zones: ${join(", ", var.zones_c2)}

    VPC PEERING:
      ${google_compute_network.vpc_c1.name} <-> ${google_compute_network.vpc_c2.name}

    ILB IPs (for Kubernetes service configuration):
      C2 Backend Services:
        userservice:        ${google_compute_address.ilb_userservice.address}
        contacts:           ${google_compute_address.ilb_contacts.address}
        balancereader:      ${google_compute_address.ilb_balancereader.address}
        transactionhistory: ${google_compute_address.ilb_transactionhistory.address}
        ledgerwriter:       ${google_compute_address.ilb_ledgerwriter.address}

      C1 Database:
        accounts-db:        ${google_compute_address.ilb_accounts_db.address}

    NEXT STEPS:
      1. Configure kubectl:
         gcloud container clusters get-credentials c1 --region ${var.region_c1} --project ${var.project_id}
         gcloud container clusters get-credentials c2 --region ${var.region_c2} --project ${var.project_id}

      2. Rename contexts:
         kubectl config rename-context gke_${var.project_id}_${var.region_c1}_c1 gke-c1
         kubectl config rename-context gke_${var.project_id}_${var.region_c2}_c2 gke-c2

      3. Deploy Kubernetes resources:
         ./scripts/deploy-apps.sh

    ============================================================
  EOT
}
