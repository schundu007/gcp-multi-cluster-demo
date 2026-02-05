#!/bin/bash
# Configure kubectl contexts for both clusters
set -e

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Get project ID
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
fi

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID not set"
    exit 1
fi

log_info "Configuring kubectl for project: $PROJECT_ID"

# Get credentials
log_info "Getting credentials for cluster C1..."
gcloud container clusters get-credentials c1 --region us-central1 --project "$PROJECT_ID"

log_info "Getting credentials for cluster C2..."
gcloud container clusters get-credentials c2 --region us-east1 --project "$PROJECT_ID"

# Rename contexts
log_info "Renaming contexts..."
kubectl config rename-context "gke_${PROJECT_ID}_us-central1_c1" gke-c1 2>/dev/null || \
    log_info "Context gke-c1 already exists"
kubectl config rename-context "gke_${PROJECT_ID}_us-east1_c2" gke-c2 2>/dev/null || \
    log_info "Context gke-c2 already exists"

log_info "kubectl contexts configured!"
log_info ""
log_info "Available contexts:"
kubectl config get-contexts | grep -E "gke-c|CURRENT"

log_info ""
log_info "Usage:"
log_info "  kubectl --context=gke-c1 get pods -n bank-of-anthos"
log_info "  kubectl --context=gke-c2 get pods -n bank-of-anthos"
