# =============================================================================
# Reserved Internal IPs for Internal Load Balancers
# =============================================================================

# Reserved IPs for C2 backend service ILBs
resource "google_compute_address" "ilb_userservice" {
  name         = "ilb-userservice"
  project      = var.project_id
  region       = var.region_c2
  subnetwork   = google_compute_subnetwork.subnet_c2.id
  address_type = "INTERNAL"
  address      = var.ilb_ips_c2["userservice"]
  purpose      = "GCE_ENDPOINT"
}

resource "google_compute_address" "ilb_contacts" {
  name         = "ilb-contacts"
  project      = var.project_id
  region       = var.region_c2
  subnetwork   = google_compute_subnetwork.subnet_c2.id
  address_type = "INTERNAL"
  address      = var.ilb_ips_c2["contacts"]
  purpose      = "GCE_ENDPOINT"
}

resource "google_compute_address" "ilb_balancereader" {
  name         = "ilb-balancereader"
  project      = var.project_id
  region       = var.region_c2
  subnetwork   = google_compute_subnetwork.subnet_c2.id
  address_type = "INTERNAL"
  address      = var.ilb_ips_c2["balancereader"]
  purpose      = "GCE_ENDPOINT"
}

resource "google_compute_address" "ilb_transactionhistory" {
  name         = "ilb-transactionhistory"
  project      = var.project_id
  region       = var.region_c2
  subnetwork   = google_compute_subnetwork.subnet_c2.id
  address_type = "INTERNAL"
  address      = var.ilb_ips_c2["transactionhistory"]
  purpose      = "GCE_ENDPOINT"
}

resource "google_compute_address" "ilb_ledgerwriter" {
  name         = "ilb-ledgerwriter"
  project      = var.project_id
  region       = var.region_c2
  subnetwork   = google_compute_subnetwork.subnet_c2.id
  address_type = "INTERNAL"
  address      = var.ilb_ips_c2["ledgerwriter"]
  purpose      = "GCE_ENDPOINT"
}

# Reserved IP for C1 accounts-db ILB
resource "google_compute_address" "ilb_accounts_db" {
  name         = "ilb-accounts-db"
  project      = var.project_id
  region       = var.region_c1
  subnetwork   = google_compute_subnetwork.subnet_c1.id
  address_type = "INTERNAL"
  address      = var.ilb_ip_accounts_db
  purpose      = "GCE_ENDPOINT"
}
