# GCP Multi-Cluster Security Demo UI

A web-based UI for demonstrating the GCP Multi-Cluster Networking & Security setup.

## Features

1. **Connectivity Testing**
   - Test C1 → C2 connectivity (Frontend → Backend services)
   - Test C2 → C1 connectivity (Backend → Database)
   - Real-time status indicators

2. **Access Control**
   - Revoke access with one click (deletes firewall rule)
   - Restore access with one click (creates firewall rule)
   - Visual status indicator

3. **Security Verification**
   - Check for external LoadBalancer IPs
   - Verify no Ingress resources
   - Confirm GKE nodes are private
   - Validate VPC peering status
   - Verify NetworkPolicies exist

4. **Observability**
   - Links to Grafana dashboards
   - Embedded dashboard preview
   - Cross-Cluster Metrics, Loki Logs, Errors & Failures

## Quick Start

### Option 1: Run with script (recommended)

```bash
cd demo-ui
./run-demo.sh
```

This will:
- Set up port-forwarding for Grafana, Prometheus, and Loki
- Launch the Streamlit demo UI
- Open the demo at http://localhost:8501

### Option 2: Manual start

1. Start port-forwarding:
```bash
kubectl --context gke-c1 port-forward svc/grafana 3001:3000 -n monitoring &
kubectl --context gke-c1 port-forward svc/prometheus 9090:9090 -n monitoring &
kubectl --context gke-c1 port-forward svc/loki 3100:3100 -n monitoring &
```

2. Install dependencies:
```bash
pip install streamlit
```

3. Run the app:
```bash
streamlit run app.py --server.port 8501
```

4. Open http://localhost:8501 in your browser

## Demo Flow

### 1. Show Successful Connectivity
- Go to **Connectivity** tab
- Click "Test C1 → C2 Connectivity"
- All 5 services should show ✅ Connected

### 2. Show Security Verification
- Go to **Verification** tab
- Click "Run Security Verification"
- All checks should pass ✅

### 3. Revoke Access
- Go to **Access Control** tab
- Click "REVOKE ACCESS"
- Status changes to 🔴 REVOKED

### 4. Verify Blocked Access
- Go to **Connectivity** tab
- Click "Test C1 → C2 Connectivity"
- All 5 services should show ❌ BLOCKED

### 5. Show Observability
- Go to **Observability** tab
- View embedded Grafana dashboards
- Show Errors & Failures dashboard

### 6. Restore Access
- Go to **Access Control** tab
- Click "RESTORE ACCESS"
- Status changes to 🟢 ENABLED

## URLs

| Service | URL |
|---------|-----|
| Demo UI | http://localhost:8501 |
| Grafana | http://localhost:3001 |
| Prometheus | http://localhost:9090 |
| Cross-Cluster Dashboard | http://localhost:3001/d/cross-cluster-boa/ |
| Loki Logs Dashboard | http://localhost:3001/d/loki-logs-boa/ |
| Errors Dashboard | http://localhost:3001/d/errors-failures/ |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Demo UI (Streamlit)                     │
│                    http://localhost:8501                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Connectivity│  │   Access    │  │ Verification│        │
│  │   Testing   │  │   Control   │  │   Checks    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              kubectl / gcloud commands               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    GKE Clusters                             │
├──────────────────────────┬──────────────────────────────────┤
│     C1 (us-central1)     │        C2 (us-east1)            │
│  ┌──────────────────┐    │    ┌──────────────────┐         │
│  │ frontend         │────┼───▶│ userservice      │         │
│  │ loadgenerator    │    │    │ contacts         │         │
│  │ accounts-db      │◀───┼────│ balancereader    │         │
│  │ monitoring stack │    │    │ ledgerwriter     │         │
│  └──────────────────┘    │    │ ledger-db        │         │
│                          │    └──────────────────┘         │
└──────────────────────────┴──────────────────────────────────┘
```
