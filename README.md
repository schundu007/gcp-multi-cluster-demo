# GCP Multi-Cluster Network Security Demo

A production-grade demonstration of secure, private, multi-region GCP Kubernetes infrastructure with instant access revocation capabilities and SRE observability.

## Overview

This project demonstrates how to build a zero-trust, private multi-cluster architecture on GCP:

- **Private GKE Clusters** across two regions (us-central1, us-east1)
  <img width="1597" height="854" alt="image" src="https://github.com/user-attachments/assets/4a55647b-9077-42d2-8137-de2e4341ca1a" />

- **VPC Peering** for secure cross-cluster communication
- **Internal Load Balancers** with global access (no public IPs)
- **Firewall Rules** for network-level access control
- **NetworkPolicies** for pod-level segmentation
- **Instant Access Revocation** via firewall rule deletion
- **SRE Observability** with Prometheus, Grafana, and Loki

## Architecture
<img width="1206" height="1118" alt="image" src="https://github.com/user-attachments/assets/1473d01b-27c6-4adb-970e-9c69df3a6108" />


```
┌────────────────────────────────────────────────────────────────────────────┐
│                              GCP Project                                   │
├───────────────────────────────────┬────────────────────────────────────────┤
│       us-central1 (C1)            │           us-east1 (C2)                │
│  ┌─────────────────────────────┐  │  ┌─────────────────────────────────┐   │
│  │     VPC: vpc-c1             │  │  │      VPC: vpc-c2                │   │
│  │     10.0.0.0/16             │◄─┼──┼─►    10.1.0.0/16                │   │
│  │                             │  │  │      VPC Peering                │   │
│  │  ┌───────────────────────┐  │  │  │  ┌───────────────────────────┐  │   │
│  │  │  GKE Cluster C1       │  │  │  │  │  GKE Cluster C2           │  │   │
│  │  │  (Private Nodes)      │  │  │  │  │  (Private Nodes)          │  │   │
│  │  │                       │  │  │  │  │                           │  │   │
│  │  │  • frontend           │──┼──┼──┼──┼─► userservice (ILB)       │  │   │
│  │  │  • loadgenerator      │  │  │  │  │  • contacts (ILB)         │  │   │
│  │  │  • accounts-db (ILB)◄─┼──┼──┼──┼──┼─ • balancereader (ILB)    │  │   │
│  │  │                       │  │  │  │  │  • transactionhistory     │  │   │
│  │  │                       │  │  │  │  │  • ledgerwriter (ILB)     │  │   │
│  │  │                       │  │  │  │  │  • ledger-db              │  │   │
│  │  └───────────────────────┘  │  │  │  └───────────────────────────┘  │   │
│  └─────────────────────────────┘  │  └─────────────────────────────────┘   │
└───────────────────────────────────┴────────────────────────────────────────┘

Traffic Flows:
  C1 → C2: frontend → [userservice, contacts, balancereader, txnhistory, ledgerwriter]
  C2 → C1: [userservice, contacts] → accounts-db
```

## Demo UI Features

### 4-Page Interactive Demo
1. **Overview** - Problem statement, approach, production roadmap
2. **Architecture** - Visual cluster diagram, design decisions
3. **Workflow** - Step-by-step demo flow
4. **Live Demo** - Real-time connectivity testing and access control

### SRE Alert System
When access is revoked, the demo displays:
- Critical incident banner with SEV-1 indicator
- Scrolling error ticker
- Live error stream with timestamps
- Service status with shake animations

### SRE Metrics Dashboard
- **SLO Availability**: 99.95% → 94.2% (when blocked)
- **Error Budget**: 43% → 0% (when blocked)
- **P99 Latency**: 245ms → 892ms (when blocked)
- **Error Rate**: 0.02% → 12.4% (when blocked)
- **MTTR**: 4.2 minutes
- **MTTI**: 1.8 minutes
- **MTTA**: 2.4 minutes

### Embedded Grafana Dashboards
- Cross-Cluster Metrics
- Errors & Failures
- Loki Logs

## Prerequisites

- GCP Project with billing enabled
- `gcloud` CLI configured and authenticated
- `kubectl` installed
- `terraform` >= 1.0
- Python 3.9+ with `streamlit`

## Quick Start

### 1. Deploy Infrastructure

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project ID

terraform init
terraform plan
terraform apply
```

### 2. Configure kubectl Contexts

```bash
gcloud container clusters get-credentials c1 --region us-central1
gcloud container clusters get-credentials c2 --region us-east1

kubectl config rename-context gke_${PROJECT_ID}_us-central1_c1 gke-c1
kubectl config rename-context gke_${PROJECT_ID}_us-east1_c2 gke-c2
```

### 3. Deploy Application

```bash
# Deploy to C2 first (backend services)
kubectl --context gke-c2 apply -f k8s/c2/

# Deploy to C1 (frontend + accounts-db)
kubectl --context gke-c1 apply -f k8s/c1/

# Deploy observability stack
kubectl --context gke-c1 apply -f observability/
```

### 4. Run Demo UI

```bash
cd demo-ui
pip install streamlit
./run-demo.sh
```

Open http://localhost:8501

### 5. Start Port Forwarding

```bash
kubectl --context gke-c1 port-forward svc/grafana 3002:3000 -n monitoring &
kubectl --context gke-c1 port-forward svc/prometheus 9090:9090 -n monitoring &
kubectl --context gke-c1 port-forward svc/frontend 8085:80 -n bank-of-anthos &
```

## Demo Flow

### 1. Show Successful Connectivity
- Navigate to **Demo** → **Command Center**
- Click **TEST CONNECTIVITY**
- All 5 services show **ONLINE**

### 2. Revoke Access
- Click **REVOKE ACCESS**
- Watch the SRE alerts activate:
  - Critical incident banner appears
  - Scrolling error ticker starts
  - Live error stream shows failures
  - SLO metrics degrade

### 3. Observe Impact
- Go to **Observability** → **SRE Metrics**
- See degraded metrics in real-time
- Check Grafana dashboards for error spikes

### 4. Restore Access
- Click **RESTORE ACCESS**
- Metrics recover automatically
- Services return to **ONLINE**

  <img width="819" height="1174" alt="image" src="https://github.com/user-attachments/assets/2e04b132-3a01-45ae-96f4-1a4048156bac" />


## Project Structure

```
gcp-multi-cluster-demo/
├── README.md
├── terraform/                 # Infrastructure as Code
│   ├── main.tf
│   ├── vpc.tf                # VPCs, subnets, peering
│   ├── gke.tf                # Private GKE clusters
│   ├── firewall.tf           # Firewall rules
│   └── outputs.tf
├── k8s/
│   ├── c1/                   # Cluster C1 manifests
│   │   ├── frontend.yaml
│   │   ├── accounts-db.yaml
│   │   └── network-policy.yaml
│   ├── c2/                   # Cluster C2 manifests
│   │   ├── userservice.yaml
│   │   ├── contacts.yaml
│   │   ├── balancereader.yaml
│   │   └── network-policy.yaml
│   └── common/
│       └── default-deny.yaml
├── observability/
│   ├── prometheus/
│   ├── grafana/
│   └── loki/
├── demo-ui/
│   ├── app.py                # Streamlit demo application
│   ├── run-demo.sh
│   ├── requirements.txt
│   └── assets/               # Architecture diagrams
└── verification/
    └── verify.py             # Connectivity verification tool
```

## What's Implemented vs Production

| Implemented | Production Enhancement |
|-------------|----------------------|
| Private GKE Clusters | Service Mesh (Istio) for mTLS |
| VPC Peering | API Gateway for rate limiting |
| Internal Load Balancers | Redis/Memcached caching |
| Firewall Rules | Database sharding |
| NetworkPolicies | Cloud Armor WAF |
| Prometheus + Grafana | Secret Manager integration |
| Loki Logging | CI/CD with ArgoCD |
| Instant Access Revocation | Velero backup & DR |

## Internet Exposure Options

For production deployment:

| Option | Best For | Features |
|--------|----------|----------|
| **GKE Gateway** | Production | Global L7 LB, managed TLS, Cloud Armor |
| **Identity-Aware Proxy** | Internal Tools | Zero-trust, Google identity |
| **Anthos Ingress** | Multi-cloud | Global anycast, traffic splitting |

## Firewall Rules

| Rule | Source | Destination | Ports | Purpose |
|------|--------|-------------|-------|---------|
| allow-c1-to-c2-app | 10.0.0.0/16 | 10.1.0.0/16 | TCP:8085 | Frontend → Backends |
| allow-c2-to-c1-db | 10.1.0.0/16 | 10.0.0.0/16 | TCP:5432 | Backends → accounts-db |
| allow-internal-c1 | 10.0.0.0/16 | 10.0.0.0/16 | all | C1 internal |
| allow-internal-c2 | 10.1.0.0/16 | 10.1.0.0/16 | all | C2 internal |

## URLs (Local Development)

| Service | URL |
|---------|-----|
| Demo UI | http://localhost:8501 |
| Grafana | http://localhost:3002 |
| Prometheus | http://localhost:9090 |
| Bank of Anthos | http://localhost:8085 |

## Troubleshooting

### Port Forwarding
```bash
# Start all port forwards
kubectl --context gke-c1 port-forward svc/grafana 3002:3000 -n monitoring &
kubectl --context gke-c1 port-forward svc/prometheus 9090:9090 -n monitoring &
kubectl --context gke-c1 port-forward svc/frontend 8085:80 -n bank-of-anthos &
```

### Check Firewall Rule
```bash
gcloud compute firewall-rules describe allow-c1-to-c2-app
```

### Verify Connectivity
```bash
kubectl --context gke-c1 exec -n bank-of-anthos deploy/frontend -- \
  curl -s http://10.1.10.10:8085/ready
```

### Grafana Not Loading in Iframe
```bash
# Enable embedding in Grafana
kubectl --context gke-c1 set env deployment/grafana -n monitoring \
  GF_SECURITY_ALLOW_EMBEDDING=true
```

## Security Controls

| Layer | Control | Purpose |
|-------|---------|---------|
| Network | VPC Peering | Private cross-cluster communication |
| Network | Firewall Rules | Explicit allow for specific traffic |
| K8s | NetworkPolicies | Pod-level ingress/egress control |
| K8s | Private Clusters | No public IPs on nodes |
| K8s | Internal LBs | No external service exposure |

## Cleanup

```bash
cd terraform
terraform destroy
```

## License

MIT

## Author

Built for GCP Multi-Cluster Security Demo
