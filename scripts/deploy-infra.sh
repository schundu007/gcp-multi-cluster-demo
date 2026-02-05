#!/bin/bash
# Deploy only the infrastructure (Terraform)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

cd "$PROJECT_ROOT/terraform"

# Check project ID
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
fi

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID not set"
    exit 1
fi

log_info "Deploying infrastructure for project: $PROJECT_ID"

# Create tfvars if needed
if [ ! -f "terraform.tfvars" ]; then
    log_info "Creating terraform.tfvars..."
    cp terraform.tfvars.example terraform.tfvars
    sed -i.bak "s/your-gcp-project-id/$PROJECT_ID/g" terraform.tfvars
    MY_IP=$(curl -s ifconfig.me)
    sed -i.bak "s/YOUR_IP_ADDRESS/$MY_IP/g" terraform.tfvars
    rm -f terraform.tfvars.bak
fi

terraform init
terraform plan -out=tfplan
terraform apply tfplan

log_info "Infrastructure deployed!"
log_info "Run './configure-contexts.sh' to set up kubectl"
