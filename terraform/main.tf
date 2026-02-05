terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  # Uncomment to use remote state
  # backend "gcs" {
  #   bucket = "your-terraform-state-bucket"
  #   prefix = "ciroos/state"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region_c1
}

provider "google-beta" {
  project = var.project_id
  region  = var.region_c1
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "servicenetworking.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# Wait for APIs to be enabled
resource "time_sleep" "api_enablement" {
  depends_on      = [google_project_service.apis]
  create_duration = "30s"
}
