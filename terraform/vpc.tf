# =============================================================================
# VPC Networks
# =============================================================================

# VPC for Cluster 1 (us-central1)
resource "google_compute_network" "vpc_c1" {
  name                    = "vpc-c1"
  project                 = var.project_id
  auto_create_subnetworks = false
  routing_mode            = "GLOBAL"

  depends_on = [time_sleep.api_enablement]
}

# VPC for Cluster 2 (us-east1)
resource "google_compute_network" "vpc_c2" {
  name                    = "vpc-c2"
  project                 = var.project_id
  auto_create_subnetworks = false
  routing_mode            = "GLOBAL"

  depends_on = [time_sleep.api_enablement]
}

# =============================================================================
# Subnets
# =============================================================================

# Subnet for Cluster 1
resource "google_compute_subnetwork" "subnet_c1" {
  name                     = "subnet-c1"
  project                  = var.project_id
  region                   = var.region_c1
  network                  = google_compute_network.vpc_c1.id
  ip_cidr_range            = var.subnet_c1_cidr
  private_ip_google_access = true

  # Secondary ranges for GKE pods and services
  secondary_ip_range {
    range_name    = "pods-c1"
    ip_cidr_range = var.pods_cidr_c1
  }

  secondary_ip_range {
    range_name    = "services-c1"
    ip_cidr_range = var.services_cidr_c1
  }

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# Subnet for Cluster 2
resource "google_compute_subnetwork" "subnet_c2" {
  name                     = "subnet-c2"
  project                  = var.project_id
  region                   = var.region_c2
  network                  = google_compute_network.vpc_c2.id
  ip_cidr_range            = var.subnet_c2_cidr
  private_ip_google_access = true

  # Secondary ranges for GKE pods and services
  secondary_ip_range {
    range_name    = "pods-c2"
    ip_cidr_range = var.pods_cidr_c2
  }

  secondary_ip_range {
    range_name    = "services-c2"
    ip_cidr_range = var.services_cidr_c2
  }

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# =============================================================================
# VPC Peering (Bidirectional)
# =============================================================================

# Peering from VPC C1 to VPC C2
resource "google_compute_network_peering" "c1_to_c2" {
  name                 = "c1-to-c2"
  network              = google_compute_network.vpc_c1.self_link
  peer_network         = google_compute_network.vpc_c2.self_link
  export_custom_routes = true
  import_custom_routes = true
}

# Peering from VPC C2 to VPC C1
resource "google_compute_network_peering" "c2_to_c1" {
  name                 = "c2-to-c1"
  network              = google_compute_network.vpc_c2.self_link
  peer_network         = google_compute_network.vpc_c1.self_link
  export_custom_routes = true
  import_custom_routes = true

  depends_on = [google_compute_network_peering.c1_to_c2]
}

# =============================================================================
# Cloud Router (for NAT - needed for private nodes to access internet)
# =============================================================================

# Cloud Router for C1
resource "google_compute_router" "router_c1" {
  name    = "router-c1"
  project = var.project_id
  region  = var.region_c1
  network = google_compute_network.vpc_c1.id
}

# Cloud Router for C2
resource "google_compute_router" "router_c2" {
  name    = "router-c2"
  project = var.project_id
  region  = var.region_c2
  network = google_compute_network.vpc_c2.id
}

# Cloud NAT for C1 (allows private nodes to pull images, etc.)
resource "google_compute_router_nat" "nat_c1" {
  name                               = "nat-c1"
  project                            = var.project_id
  router                             = google_compute_router.router_c1.name
  region                             = var.region_c1
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Cloud NAT for C2 (allows private nodes to pull images, etc.)
resource "google_compute_router_nat" "nat_c2" {
  name                               = "nat-c2"
  project                            = var.project_id
  router                             = google_compute_router.router_c2.name
  region                             = var.region_c2
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}
