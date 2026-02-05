#!/bin/bash
# Full setup automation script for GCP Multi-Cluster deployment
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Please install it first."
        exit 1
    fi

    if ! command -v terraform &> /dev/null; then
        log_error "Terraform not found. Please install it first."
        exit 1
    fi

    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install it first."
        exit 1
    fi

    # Check if logged in to gcloud
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 &> /dev/null; then
        log_error "Not logged in to gcloud. Please run 'gcloud auth login'"
        exit 1
    fi

    log_info "All prerequisites met!"
}

# Get or set project ID
get_project_id() {
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z "$PROJECT_ID" ]; then
            log_error "PROJECT_ID not set. Please set it via 'export PROJECT_ID=your-project' or 'gcloud config set project your-project'"
            exit 1
        fi
    fi
    log_info "Using GCP project: $PROJECT_ID"
    export PROJECT_ID
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."

    cd "$PROJECT_ROOT/terraform"

    # Check if terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        log_warn "terraform.tfvars not found. Creating from example..."
        cp terraform.tfvars.example terraform.tfvars

        # Replace project_id
        sed -i.bak "s/your-gcp-project-id/$PROJECT_ID/g" terraform.tfvars

        # Get current IP for master authorized networks
        MY_IP=$(curl -s ifconfig.me)
        sed -i.bak "s/YOUR_IP_ADDRESS/$MY_IP/g" terraform.tfvars
        rm -f terraform.tfvars.bak

        log_info "Created terraform.tfvars with project_id=$PROJECT_ID and your IP=$MY_IP"
        log_warn "Please review terraform.tfvars before continuing."
        read -p "Press Enter to continue or Ctrl+C to abort..."
    fi

    terraform init
    terraform plan -out=tfplan
    terraform apply tfplan

    log_info "Infrastructure deployed successfully!"
}

# Configure kubectl contexts
configure_kubectl() {
    log_info "Configuring kubectl contexts..."

    # Get cluster credentials
    gcloud container clusters get-credentials c1 --region us-central1 --project "$PROJECT_ID"
    gcloud container clusters get-credentials c2 --region us-east1 --project "$PROJECT_ID"

    # Rename contexts for convenience
    kubectl config rename-context "gke_${PROJECT_ID}_us-central1_c1" gke-c1 2>/dev/null || true
    kubectl config rename-context "gke_${PROJECT_ID}_us-east1_c2" gke-c2 2>/dev/null || true

    log_info "kubectl contexts configured: gke-c1, gke-c2"
}

# Deploy Kubernetes resources
deploy_k8s_resources() {
    log_info "Deploying Kubernetes resources..."

    cd "$PROJECT_ROOT/k8s"

    # Deploy to C1 first (frontend cluster)
    log_info "Deploying to cluster C1..."
    kubectl --context=gke-c1 apply -f common/namespace.yaml
    kubectl --context=gke-c1 apply -f c1/namespace.yaml
    kubectl --context=gke-c1 apply -f common/jwt-secret.yaml
    kubectl --context=gke-c1 apply -f c1/config.yaml
    kubectl --context=gke-c1 apply -f c1/accounts-db.yaml
    kubectl --context=gke-c1 apply -f c1/network-policy.yaml

    # Wait for accounts-db to be ready
    log_info "Waiting for accounts-db to be ready..."
    kubectl --context=gke-c1 wait --for=condition=ready pod -l app=accounts-db -n bank-of-anthos --timeout=300s || true

    # Deploy to C2 (backend cluster)
    log_info "Deploying to cluster C2..."
    kubectl --context=gke-c2 apply -f common/namespace.yaml
    kubectl --context=gke-c2 apply -f c2/namespace.yaml
    kubectl --context=gke-c2 apply -f common/jwt-secret.yaml
    kubectl --context=gke-c2 apply -f c2/config.yaml
    kubectl --context=gke-c2 apply -f c2/ledger-db.yaml

    # Wait for ledger-db to be ready
    log_info "Waiting for ledger-db to be ready..."
    kubectl --context=gke-c2 wait --for=condition=ready pod -l app=ledger-db -n bank-of-anthos --timeout=300s || true

    # Deploy backend services
    kubectl --context=gke-c2 apply -f c2/userservice.yaml
    kubectl --context=gke-c2 apply -f c2/contacts.yaml
    kubectl --context=gke-c2 apply -f c2/balancereader.yaml
    kubectl --context=gke-c2 apply -f c2/transactionhistory.yaml
    kubectl --context=gke-c2 apply -f c2/ledgerwriter.yaml
    kubectl --context=gke-c2 apply -f c2/network-policy.yaml

    # Wait for backend services
    log_info "Waiting for backend services to be ready..."
    kubectl --context=gke-c2 wait --for=condition=ready pod -l tier=backend -n bank-of-anthos --timeout=300s || true

    # Now deploy frontend (depends on backend ILBs being ready)
    log_info "Deploying frontend to C1..."
    kubectl --context=gke-c1 apply -f c1/frontend.yaml
    kubectl --context=gke-c1 apply -f c1/loadgenerator.yaml

    log_info "Kubernetes resources deployed successfully!"
}

# Deploy observability stack
deploy_observability() {
    log_info "Deploying observability stack..."

    cd "$PROJECT_ROOT/observability"

    kubectl --context=gke-c1 apply -f prometheus/prometheus-rbac.yaml
    kubectl --context=gke-c1 apply -f prometheus/prometheus-config.yaml
    kubectl --context=gke-c1 apply -f prometheus/prometheus-deploy.yaml
    kubectl --context=gke-c1 apply -f grafana/grafana-datasource.yaml
    kubectl --context=gke-c1 apply -f grafana/grafana-dashboards-cm.yaml
    kubectl --context=gke-c1 apply -f grafana/grafana-deploy.yaml

    log_info "Observability stack deployed!"
}

# Show status
show_status() {
    log_info "Deployment Status:"
    echo ""
    echo "=== Cluster C1 (Frontend) ==="
    kubectl --context=gke-c1 get pods -n bank-of-anthos
    echo ""
    echo "=== Cluster C1 Services ==="
    kubectl --context=gke-c1 get svc -n bank-of-anthos
    echo ""
    echo "=== Cluster C2 (Backend) ==="
    kubectl --context=gke-c2 get pods -n bank-of-anthos
    echo ""
    echo "=== Cluster C2 Services ==="
    kubectl --context=gke-c2 get svc -n bank-of-anthos
    echo ""
    echo "=== Monitoring ==="
    kubectl --context=gke-c1 get pods -n monitoring
    echo ""
    log_info "To access the frontend:"
    echo "  kubectl --context=gke-c1 port-forward svc/frontend 8080:80 -n bank-of-anthos"
    echo "  Open: http://localhost:8080"
    echo ""
    log_info "To access Grafana:"
    echo "  kubectl --context=gke-c1 port-forward svc/grafana 3000:3000 -n monitoring"
    echo "  Open: http://localhost:3000 (admin/admin)"
}

# Main execution
main() {
    echo "============================================================"
    echo "  GCP Multi-Cluster Setup"
    echo "============================================================"
    echo ""

    check_prerequisites
    get_project_id

    case "${1:-all}" in
        infra)
            deploy_infrastructure
            configure_kubectl
            ;;
        k8s)
            deploy_k8s_resources
            ;;
        observability)
            deploy_observability
            ;;
        status)
            show_status
            ;;
        all)
            deploy_infrastructure
            configure_kubectl
            deploy_k8s_resources
            deploy_observability
            show_status
            ;;
        *)
            echo "Usage: $0 {infra|k8s|observability|status|all}"
            exit 1
            ;;
    esac

    log_info "Setup complete!"
}

main "$@"
