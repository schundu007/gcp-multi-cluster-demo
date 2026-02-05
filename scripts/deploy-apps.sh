#!/bin/bash
# Deploy Kubernetes applications to both clusters
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

cd "$PROJECT_ROOT/k8s"

log_info "Deploying applications to both clusters..."

# Check contexts exist
if ! kubectl config get-contexts gke-c1 &>/dev/null; then
    log_warn "Context gke-c1 not found. Run ./configure-contexts.sh first."
    exit 1
fi

if ! kubectl config get-contexts gke-c2 &>/dev/null; then
    log_warn "Context gke-c2 not found. Run ./configure-contexts.sh first."
    exit 1
fi

# Deploy to C1
log_info "=== Deploying to Cluster C1 (Frontend) ==="
kubectl --context=gke-c1 apply -f common/namespace.yaml
kubectl --context=gke-c1 apply -f c1/namespace.yaml
kubectl --context=gke-c1 apply -f common/jwt-secret.yaml
kubectl --context=gke-c1 apply -f c1/config.yaml
kubectl --context=gke-c1 apply -f c1/accounts-db.yaml

log_info "Waiting for accounts-db..."
kubectl --context=gke-c1 wait --for=condition=ready pod -l app=accounts-db -n bank-of-anthos --timeout=300s || true

# Deploy to C2
log_info "=== Deploying to Cluster C2 (Backend) ==="
kubectl --context=gke-c2 apply -f common/namespace.yaml
kubectl --context=gke-c2 apply -f c2/namespace.yaml
kubectl --context=gke-c2 apply -f common/jwt-secret.yaml
kubectl --context=gke-c2 apply -f c2/config.yaml
kubectl --context=gke-c2 apply -f c2/ledger-db.yaml

log_info "Waiting for ledger-db..."
kubectl --context=gke-c2 wait --for=condition=ready pod -l app=ledger-db -n bank-of-anthos --timeout=300s || true

# Deploy backend services to C2
log_info "Deploying backend services to C2..."
kubectl --context=gke-c2 apply -f c2/userservice.yaml
kubectl --context=gke-c2 apply -f c2/contacts.yaml
kubectl --context=gke-c2 apply -f c2/balancereader.yaml
kubectl --context=gke-c2 apply -f c2/transactionhistory.yaml
kubectl --context=gke-c2 apply -f c2/ledgerwriter.yaml
kubectl --context=gke-c2 apply -f c2/network-policy.yaml

log_info "Waiting for backend services..."
kubectl --context=gke-c2 wait --for=condition=ready pod -l tier=backend -n bank-of-anthos --timeout=300s || true

# Check ILB IPs are assigned
log_info "Checking ILB IP assignments..."
kubectl --context=gke-c2 get svc -n bank-of-anthos -o wide

# Deploy frontend to C1
log_info "Deploying frontend to C1..."
kubectl --context=gke-c1 apply -f c1/frontend.yaml
kubectl --context=gke-c1 apply -f c1/loadgenerator.yaml
kubectl --context=gke-c1 apply -f c1/network-policy.yaml

log_info "Waiting for frontend..."
kubectl --context=gke-c1 wait --for=condition=ready pod -l app=frontend -n bank-of-anthos --timeout=300s || true

# Show status
log_info "=== Deployment Complete ==="
echo ""
echo "Cluster C1 Pods:"
kubectl --context=gke-c1 get pods -n bank-of-anthos
echo ""
echo "Cluster C2 Pods:"
kubectl --context=gke-c2 get pods -n bank-of-anthos
echo ""
log_info "Access frontend:"
echo "  kubectl --context=gke-c1 port-forward svc/frontend 8080:80 -n bank-of-anthos"
echo "  Open: http://localhost:8080"
