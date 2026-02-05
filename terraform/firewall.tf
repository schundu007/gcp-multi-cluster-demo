# =============================================================================
# Firewall Rules - VPC C1
# =============================================================================

# Default deny all ingress for VPC C1
resource "google_compute_firewall" "c1_deny_ingress" {
  name     = "c1-deny-all-ingress"
  project  = var.project_id
  network  = google_compute_network.vpc_c1.id
  priority = 65534

  direction = "INGRESS"

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}

# Default deny all egress for VPC C1
resource "google_compute_firewall" "c1_deny_egress" {
  name     = "c1-deny-all-egress"
  project  = var.project_id
  network  = google_compute_network.vpc_c1.id
  priority = 65534

  direction = "EGRESS"

  deny {
    protocol = "all"
  }

  destination_ranges = ["0.0.0.0/0"]

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}

# Allow internal communication within VPC C1
resource "google_compute_firewall" "c1_allow_internal" {
  name     = "c1-allow-internal"
  project  = var.project_id
  network  = google_compute_network.vpc_c1.id
  priority = 1000

  direction = "INGRESS"

  allow {
    protocol = "tcp"
  }
  allow {
    protocol = "udp"
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = [var.vpc_c1_cidr, var.pods_cidr_c1, var.services_cidr_c1]
}

# Allow C1 to C2 egress (frontend -> backends on port 8085)
resource "google_compute_firewall" "c1_to_c2_app" {
  name     = "allow-c1-to-c2-app"
  project  = var.project_id
  network  = google_compute_network.vpc_c1.id
  priority = 1000

  direction = "EGRESS"

  allow {
    protocol = "tcp"
    ports    = ["8085"]
  }

  destination_ranges = [var.vpc_c2_cidr, var.pods_cidr_c2]
  target_tags        = ["gke-c1-node"]

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}

# Allow GKE health checks for C1
resource "google_compute_firewall" "c1_allow_health_checks" {
  name     = "c1-allow-health-checks"
  project  = var.project_id
  network  = google_compute_network.vpc_c1.id
  priority = 1000

  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["8085", "5432", "80", "443", "10256"]
  }

  # GCP health check ranges
  source_ranges = ["35.191.0.0/16", "130.211.0.0/22", "209.85.152.0/22", "209.85.204.0/22"]
  target_tags   = ["gke-c1-node"]
}

# Allow GKE master to nodes communication for C1
resource "google_compute_firewall" "c1_allow_master" {
  name     = "c1-allow-gke-master"
  project  = var.project_id
  network  = google_compute_network.vpc_c1.id
  priority = 1000

  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["443", "10250", "10255"]
  }

  source_ranges = [var.master_cidr_c1]
  target_tags   = ["gke-c1-node"]
}

# Allow IAP SSH for C1
resource "google_compute_firewall" "c1_allow_iap" {
  name     = "c1-allow-iap-ssh"
  project  = var.project_id
  network  = google_compute_network.vpc_c1.id
  priority = 1000

  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20"]
  target_tags   = ["gke-c1-node"]
}

# Allow C1 egress to internet (NAT for pulling images, etc.)
# Note: No target_tags so it applies to all instances including default GKE pool during init
resource "google_compute_firewall" "c1_allow_egress_internet" {
  name     = "c1-allow-egress-internet"
  project  = var.project_id
  network  = google_compute_network.vpc_c1.id
  priority = 1000

  direction = "EGRESS"

  allow {
    protocol = "tcp"
    ports    = ["443", "80"]
  }
  allow {
    protocol = "udp"
    ports    = ["53"]
  }

  destination_ranges = ["0.0.0.0/0"]
}

# Allow C1 egress to internal ranges (including master CIDR for control plane access)
# Note: No target_tags so it applies to all instances including default GKE pool during init
resource "google_compute_firewall" "c1_allow_egress_internal" {
  name     = "c1-allow-egress-internal"
  project  = var.project_id
  network  = google_compute_network.vpc_c1.id
  priority = 1000

  direction = "EGRESS"

  allow {
    protocol = "tcp"
  }
  allow {
    protocol = "udp"
  }
  allow {
    protocol = "icmp"
  }

  destination_ranges = [var.vpc_c1_cidr, var.pods_cidr_c1, var.services_cidr_c1, var.master_cidr_c1]
}

# Allow ingress from C2 to C1 accounts-db (backends -> accounts-db on port 5432)
resource "google_compute_firewall" "c2_to_c1_db" {
  name     = "allow-c2-to-c1-db"
  project  = var.project_id
  network  = google_compute_network.vpc_c1.id
  priority = 1000

  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["5432"]
  }

  source_ranges = [var.vpc_c2_cidr, var.pods_cidr_c2]
  target_tags   = ["gke-c1-node"]

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}

# =============================================================================
# Firewall Rules - VPC C2
# =============================================================================

# Default deny all ingress for VPC C2
resource "google_compute_firewall" "c2_deny_ingress" {
  name     = "c2-deny-all-ingress"
  project  = var.project_id
  network  = google_compute_network.vpc_c2.id
  priority = 65534

  direction = "INGRESS"

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}

# Default deny all egress for VPC C2
resource "google_compute_firewall" "c2_deny_egress" {
  name     = "c2-deny-all-egress"
  project  = var.project_id
  network  = google_compute_network.vpc_c2.id
  priority = 65534

  direction = "EGRESS"

  deny {
    protocol = "all"
  }

  destination_ranges = ["0.0.0.0/0"]

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}

# Allow internal communication within VPC C2
resource "google_compute_firewall" "c2_allow_internal" {
  name     = "c2-allow-internal"
  project  = var.project_id
  network  = google_compute_network.vpc_c2.id
  priority = 1000

  direction = "INGRESS"

  allow {
    protocol = "tcp"
  }
  allow {
    protocol = "udp"
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = [var.vpc_c2_cidr, var.pods_cidr_c2, var.services_cidr_c2]
}

# Allow C1 to C2 ingress (frontend -> backends on port 8085)
resource "google_compute_firewall" "c1_to_c2_app_ingress" {
  name     = "allow-c1-to-c2-app-ingress"
  project  = var.project_id
  network  = google_compute_network.vpc_c2.id
  priority = 1000

  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["8085"]
  }

  source_ranges = [var.vpc_c1_cidr, var.pods_cidr_c1]
  target_tags   = ["gke-c2-node"]

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}

# Allow GKE health checks for C2
resource "google_compute_firewall" "c2_allow_health_checks" {
  name     = "c2-allow-health-checks"
  project  = var.project_id
  network  = google_compute_network.vpc_c2.id
  priority = 1000

  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["8085", "5432", "80", "443", "10256"]
  }

  # GCP health check ranges
  source_ranges = ["35.191.0.0/16", "130.211.0.0/22", "209.85.152.0/22", "209.85.204.0/22"]
  target_tags   = ["gke-c2-node"]
}

# Allow GKE master to nodes communication for C2
resource "google_compute_firewall" "c2_allow_master" {
  name     = "c2-allow-gke-master"
  project  = var.project_id
  network  = google_compute_network.vpc_c2.id
  priority = 1000

  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["443", "10250", "10255"]
  }

  source_ranges = [var.master_cidr_c2]
  target_tags   = ["gke-c2-node"]
}

# Allow IAP SSH for C2
resource "google_compute_firewall" "c2_allow_iap" {
  name     = "c2-allow-iap-ssh"
  project  = var.project_id
  network  = google_compute_network.vpc_c2.id
  priority = 1000

  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20"]
  target_tags   = ["gke-c2-node"]
}

# Allow C2 egress to internet (NAT for pulling images, etc.)
# Note: No target_tags so it applies to all instances including default GKE pool during init
resource "google_compute_firewall" "c2_allow_egress_internet" {
  name     = "c2-allow-egress-internet"
  project  = var.project_id
  network  = google_compute_network.vpc_c2.id
  priority = 1000

  direction = "EGRESS"

  allow {
    protocol = "tcp"
    ports    = ["443", "80"]
  }
  allow {
    protocol = "udp"
    ports    = ["53"]
  }

  destination_ranges = ["0.0.0.0/0"]
}

# Allow C2 egress to internal ranges (including master CIDR for control plane access)
# Note: No target_tags so it applies to all instances including default GKE pool during init
resource "google_compute_firewall" "c2_allow_egress_internal" {
  name     = "c2-allow-egress-internal"
  project  = var.project_id
  network  = google_compute_network.vpc_c2.id
  priority = 1000

  direction = "EGRESS"

  allow {
    protocol = "tcp"
  }
  allow {
    protocol = "udp"
  }
  allow {
    protocol = "icmp"
  }

  destination_ranges = [var.vpc_c2_cidr, var.pods_cidr_c2, var.services_cidr_c2, var.master_cidr_c2]
}

# Allow C2 egress to C1 (backends -> accounts-db on port 5432)
resource "google_compute_firewall" "c2_to_c1_db_egress" {
  name     = "allow-c2-to-c1-db-egress"
  project  = var.project_id
  network  = google_compute_network.vpc_c2.id
  priority = 1000

  direction = "EGRESS"

  allow {
    protocol = "tcp"
    ports    = ["5432"]
  }

  destination_ranges = [var.vpc_c1_cidr, var.pods_cidr_c1]
  target_tags        = ["gke-c2-node"]

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}
