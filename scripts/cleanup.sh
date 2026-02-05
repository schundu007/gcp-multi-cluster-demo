#!/bin/bash
# Cleanup script - destroys all resources
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get project ID
get_project_id() {
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z "$PROJECT_ID" ]; then
            log_error "PROJECT_ID not set"
            exit 1
        fi
    fi
    export PROJECT_ID
}

# Delete Kubernetes resources
delete_k8s_resources() {
    log_info "Deleting Kubernetes resources..."

    # Delete from C1
    if kubectl config get-contexts gke-c1 &>/dev/null; then
        log_info "Deleting resources from C1..."
        kubectl --context=gke-c1 delete namespace bank-of-anthos --ignore-not-found=true || true
        kubectl --context=gke-c1 delete namespace monitoring --ignore-not-found=true || true
    else
        log_warn "Context gke-c1 not found, skipping"
    fi

    # Delete from C2
    if kubectl config get-contexts gke-c2 &>/dev/null; then
        log_info "Deleting resources from C2..."
        kubectl --context=gke-c2 delete namespace bank-of-anthos --ignore-not-found=true || true
    else
        log_warn "Context gke-c2 not found, skipping"
    fi

    log_info "Kubernetes resources deleted"
}

# Destroy Terraform resources
destroy_terraform() {
    log_info "Destroying Terraform resources..."

    cd "$PROJECT_ROOT/terraform"

    if [ -f "terraform.tfstate" ] || [ -d ".terraform" ]; then
        terraform destroy -auto-approve
        log_info "Terraform resources destroyed"
    else
        log_warn "No Terraform state found, skipping"
    fi
}

# Clean up kubectl contexts
cleanup_kubectl_contexts() {
    log_info "Cleaning up kubectl contexts..."

    kubectl config delete-context gke-c1 2>/dev/null || true
    kubectl config delete-context gke-c2 2>/dev/null || true
    kubectl config delete-context "gke_${PROJECT_ID}_us-central1_c1" 2>/dev/null || true
    kubectl config delete-context "gke_${PROJECT_ID}_us-east1_c2" 2>/dev/null || true

    log_info "kubectl contexts cleaned up"
}

# Main
main() {
    echo "============================================================"
    echo "  GCP Multi-Cluster Cleanup"
    echo "============================================================"
    echo ""

    get_project_id
    log_info "Project: $PROJECT_ID"

    log_warn "This will DESTROY all resources!"
    log_warn "  - GKE Clusters (c1, c2)"
    log_warn "  - VPC Networks (vpc-c1, vpc-c2)"
    log_warn "  - Firewall Rules"
    log_warn "  - All Kubernetes resources"
    echo ""

    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_info "Cleanup cancelled"
        exit 0
    fi

    case "${1:-all}" in
        k8s)
            delete_k8s_resources
            ;;
        infra)
            destroy_terraform
            ;;
        contexts)
            cleanup_kubectl_contexts
            ;;
        all)
            delete_k8s_resources
            destroy_terraform
            cleanup_kubectl_contexts
            ;;
        *)
            echo "Usage: $0 {k8s|infra|contexts|all}"
            echo ""
            echo "  k8s       - Delete only Kubernetes resources"
            echo "  infra     - Destroy only Terraform resources"
            echo "  contexts  - Clean up kubectl contexts"
            echo "  all       - Full cleanup (default)"
            exit 1
            ;;
    esac

    log_info "Cleanup complete!"
}

main "$@"
