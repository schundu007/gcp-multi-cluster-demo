# =============================================================================
# GKE Cluster 1 (us-central1) - Frontend + accounts-db
# =============================================================================

resource "google_container_cluster" "c1" {
  provider = google-beta

  name     = "c1"
  project  = var.project_id
  location = var.region_c1

  # Disable deletion protection for easier cleanup during demo
  deletion_protection = false

  # Multi-zone deployment
  node_locations = var.zones_c1

  # Use separately managed node pool
  remove_default_node_pool = true
  initial_node_count       = 1

  # Network configuration
  network    = google_compute_network.vpc_c1.id
  subnetwork = google_compute_subnetwork.subnet_c1.id

  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false # Allow kubectl from authorized networks
    master_ipv4_cidr_block  = var.master_cidr_c1
  }

  # IP allocation policy for VPC-native cluster
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods-c1"
    services_secondary_range_name = "services-c1"
  }

  # Master authorized networks
  master_authorized_networks_config {
    dynamic "cidr_blocks" {
      for_each = var.master_authorized_networks
      content {
        cidr_block   = cidr_blocks.value.cidr_block
        display_name = cidr_blocks.value.display_name
      }
    }
    # Allow access from VPC C1 (for internal tools)
    cidr_blocks {
      cidr_block   = var.vpc_c1_cidr
      display_name = "VPC C1"
    }
  }

  # Enable Dataplane V2 for better NetworkPolicy support
  # Note: Dataplane V2 includes native NetworkPolicy enforcement, no need for Calico
  datapath_provider = "ADVANCED_DATAPATH"

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    dns_cache_config {
      enabled = true
    }
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  # Logging and monitoring
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
    managed_prometheus {
      enabled = true
    }
  }

  # Release channel
  release_channel {
    channel = "REGULAR"
  }

  # Resource labels
  resource_labels = {
    environment = var.environment
    cluster     = "c1"
    region      = var.region_c1
  }

  # Workload Identity (recommended for production)
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  depends_on = [
    google_compute_subnetwork.subnet_c1,
    google_compute_network_peering.c1_to_c2,
    google_compute_network_peering.c2_to_c1,
  ]
}

# Node pool for Cluster 1
resource "google_container_node_pool" "c1_nodes" {
  provider = google-beta

  name     = "c1-node-pool"
  project  = var.project_id
  location = var.region_c1
  cluster  = google_container_cluster.c1.name

  node_count = var.node_count_per_zone

  node_config {
    machine_type = var.node_machine_type
    disk_size_gb = var.node_disk_size_gb
    disk_type    = "pd-standard"

    # Use Container-Optimized OS
    image_type = "COS_CONTAINERD"

    # OAuth scopes
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    # Labels
    labels = {
      environment = var.environment
      cluster     = "c1"
    }

    # Tags for firewall rules
    tags = ["gke-c1-node"]

    # Shielded instance config
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    # Workload metadata config for Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  # Node management
  management {
    auto_repair  = true
    auto_upgrade = true
  }

  # Upgrade settings
  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# =============================================================================
# GKE Cluster 2 (us-east1) - Backend services + ledger-db
# =============================================================================

resource "google_container_cluster" "c2" {
  provider = google-beta

  name     = "c2"
  project  = var.project_id
  location = var.region_c2

  # Disable deletion protection for easier cleanup during demo
  deletion_protection = false

  # Multi-zone deployment
  node_locations = var.zones_c2

  # Use separately managed node pool
  remove_default_node_pool = true
  initial_node_count       = 1

  # Network configuration
  network    = google_compute_network.vpc_c2.id
  subnetwork = google_compute_subnetwork.subnet_c2.id

  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false # Allow kubectl from authorized networks
    master_ipv4_cidr_block  = var.master_cidr_c2
  }

  # IP allocation policy for VPC-native cluster
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods-c2"
    services_secondary_range_name = "services-c2"
  }

  # Master authorized networks
  master_authorized_networks_config {
    dynamic "cidr_blocks" {
      for_each = var.master_authorized_networks
      content {
        cidr_block   = cidr_blocks.value.cidr_block
        display_name = cidr_blocks.value.display_name
      }
    }
    # Allow access from VPC C2 (for internal tools)
    cidr_blocks {
      cidr_block   = var.vpc_c2_cidr
      display_name = "VPC C2"
    }
  }

  # Enable Dataplane V2 for better NetworkPolicy support
  # Note: Dataplane V2 includes native NetworkPolicy enforcement, no need for Calico
  datapath_provider = "ADVANCED_DATAPATH"

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    dns_cache_config {
      enabled = true
    }
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  # Logging and monitoring
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
    managed_prometheus {
      enabled = true
    }
  }

  # Release channel
  release_channel {
    channel = "REGULAR"
  }

  # Resource labels
  resource_labels = {
    environment = var.environment
    cluster     = "c2"
    region      = var.region_c2
  }

  # Workload Identity (recommended for production)
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  depends_on = [
    google_compute_subnetwork.subnet_c2,
    google_compute_network_peering.c1_to_c2,
    google_compute_network_peering.c2_to_c1,
  ]
}

# Node pool for Cluster 2
resource "google_container_node_pool" "c2_nodes" {
  provider = google-beta

  name     = "c2-node-pool"
  project  = var.project_id
  location = var.region_c2
  cluster  = google_container_cluster.c2.name

  node_count = var.node_count_per_zone

  node_config {
    machine_type = var.node_machine_type
    disk_size_gb = var.node_disk_size_gb
    disk_type    = "pd-standard"

    # Use Container-Optimized OS
    image_type = "COS_CONTAINERD"

    # OAuth scopes
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    # Labels
    labels = {
      environment = var.environment
      cluster     = "c2"
    }

    # Tags for firewall rules
    tags = ["gke-c2-node"]

    # Shielded instance config
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    # Workload metadata config for Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  # Node management
  management {
    auto_repair  = true
    auto_upgrade = true
  }

  # Upgrade settings
  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}
