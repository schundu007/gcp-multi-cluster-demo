# Claude Code Guidance for CIROOS Project

## Project Overview

This is a GCP Multi-Cluster Networking & Security implementation demonstrating cross-cluster Kubernetes communication with Bank of Anthos.

## Key Components

- **terraform/**: Infrastructure as Code for GCP resources
- **k8s/**: Kubernetes manifests for both clusters
- **verification/**: Python tool for validating connectivity and security
- **observability/**: Prometheus + Grafana monitoring stack
- **scripts/**: Automation scripts for setup, demo, and cleanup

## Architecture Summary

- **Cluster C1 (us-central1)**: Frontend + accounts-db
- **Cluster C2 (us-east1)**: Backend services + ledger-db
- **Communication**: Via Internal Load Balancers with global access over VPC peering

## Common Tasks

### Deploy Infrastructure
```bash
export PROJECT_ID=your-project
./scripts/setup.sh
```

### Test Connectivity
```bash
cd verification
python verify.py --all --project-id=$PROJECT_ID
```

### Demo Access Revocation
```bash
./scripts/revoke-access.sh c1-to-c2
./scripts/restore-access.sh all
```

### Port Forwarding (IMPORTANT: Use port 8085 for Frontend)
```bash
# Frontend - MUST use port 8085
kubectl --context gke-c1 port-forward svc/frontend 8085:80 -n bank-of-anthos &

# Grafana
kubectl --context gke-c1 port-forward svc/grafana 3001:3000 -n monitoring &

# Prometheus
kubectl --context gke-c1 port-forward svc/prometheus 9090:9090 -n monitoring &

# Loki
kubectl --context gke-c1 port-forward svc/loki 3100:3100 -n monitoring &
```

### Access URLs
| Service | URL |
|---------|-----|
| Demo UI | http://localhost:8501 |
| Frontend (Bank of Anthos) | http://localhost:8085 |
| Grafana | http://localhost:3001 |
| Prometheus | http://localhost:9090 |

## Important IPs (Internal Load Balancers)

| Service | IP | Port | Cluster |
|---------|-----|------|---------|
| userservice | 10.1.10.10 | 8085 | C2 |
| contacts | 10.1.10.11 | 8085 | C2 |
| balancereader | 10.1.10.12 | 8085 | C2 |
| transactionhistory | 10.1.10.13 | 8085 | C2 |
| ledgerwriter | 10.1.10.14 | 8085 | C2 |
| accounts-db | 10.0.10.50 | 5432 | C1 |

## Firewall Rules for Demo

- `allow-c1-to-c2-app`: Frontend → Backend (revocation target)
- `allow-c2-to-c1-db`: Backend → accounts-db

## Testing Approach

1. Run verification tool before changes
2. Make infrastructure changes
3. Run verification tool to confirm impact
4. Restore and verify recovery
