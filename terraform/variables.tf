variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region_c1" {
  description = "Region for Cluster 1"
  type        = string
  default     = "us-central1"
}

variable "region_c2" {
  description = "Region for Cluster 2"
  type        = string
  default     = "us-east1"
}

variable "zones_c1" {
  description = "Zones for Cluster 1"
  type        = list(string)
  default     = ["us-central1-a", "us-central1-b"]
}

variable "zones_c2" {
  description = "Zones for Cluster 2"
  type        = list(string)
  default     = ["us-east1-b", "us-east1-c"]
}

# VPC CIDR blocks
variable "vpc_c1_cidr" {
  description = "CIDR block for VPC C1"
  type        = string
  default     = "10.0.0.0/16"
}

variable "vpc_c2_cidr" {
  description = "CIDR block for VPC C2"
  type        = string
  default     = "10.1.0.0/16"
}

# Subnet CIDR blocks
variable "subnet_c1_cidr" {
  description = "CIDR block for subnet in C1"
  type        = string
  default     = "10.0.0.0/20"
}

variable "subnet_c2_cidr" {
  description = "CIDR block for subnet in C2"
  type        = string
  default     = "10.1.0.0/20"
}

# GKE Pod CIDR ranges (secondary ranges)
variable "pods_cidr_c1" {
  description = "CIDR block for pods in C1"
  type        = string
  default     = "10.0.16.0/20"
}

variable "pods_cidr_c2" {
  description = "CIDR block for pods in C2"
  type        = string
  default     = "10.1.16.0/20"
}

# GKE Service CIDR ranges (secondary ranges)
variable "services_cidr_c1" {
  description = "CIDR block for services in C1"
  type        = string
  default     = "10.0.32.0/20"
}

variable "services_cidr_c2" {
  description = "CIDR block for services in C2"
  type        = string
  default     = "10.1.32.0/20"
}

# GKE Master CIDR ranges
variable "master_cidr_c1" {
  description = "CIDR block for GKE master in C1"
  type        = string
  default     = "10.0.48.0/28"
}

variable "master_cidr_c2" {
  description = "CIDR block for GKE master in C2"
  type        = string
  default     = "10.1.48.0/28"
}

# GKE Node configuration
variable "node_machine_type" {
  description = "Machine type for GKE nodes"
  type        = string
  default     = "e2-standard-4"
}

variable "node_count_per_zone" {
  description = "Number of nodes per zone"
  type        = number
  default     = 1
}

variable "node_disk_size_gb" {
  description = "Disk size for GKE nodes in GB"
  type        = number
  default     = 50
}

# Master authorized networks
variable "master_authorized_networks" {
  description = "List of CIDR blocks authorized to access GKE master"
  type = list(object({
    cidr_block   = string
    display_name = string
  }))
  default = []
}

# ILB Reserved IPs
variable "ilb_ips_c2" {
  description = "Reserved IPs for backend ILBs in C2 (must be within 10.1.0.0/20)"
  type        = map(string)
  default = {
    userservice        = "10.1.10.10"
    contacts           = "10.1.10.11"
    balancereader      = "10.1.10.12"
    transactionhistory = "10.1.10.13"
    ledgerwriter       = "10.1.10.14"
  }
}

variable "ilb_ip_accounts_db" {
  description = "Reserved IP for accounts-db ILB in C1 (must be within 10.0.0.0/20)"
  type        = string
  default     = "10.0.10.50"
}

# Environment labels
variable "environment" {
  description = "Environment label"
  type        = string
  default     = "demo"
}
