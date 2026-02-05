# Architecture Design Document

## Overview

This document describes the architecture design for the GCP Multi-Cluster Networking & Security implementation, using Bank of Anthos as the demonstration application.

## Design Goals

1. **Private-by-default**: All services internal; no external exposure
2. **Clear traffic paths**: Easily traceable for verification and demonstration
3. **Defense in depth**: Multiple security layers (VPC, firewall, NetworkPolicy)
4. **Demo-focused**: Clear C1→C2 communication path for access revocation demonstration

## Architecture Decision: Private Connectivity Approach

**Selected: Internal Load Balancer with Global Access + VPC Peering**

### Why This Approach

| Criteria | Score | Notes |
|----------|-------|-------|
| Simplicity | High | Straightforward to implement and debug |
| Visibility | High | Clear traffic paths, easy to trace |
| Native GCP | Yes | No additional products required |
| Cost | Low | Minimal additional charges |
| Verifiable | High | Clear firewall rules and network paths |

### Alternatives Considered

| Approach | Why Not Chosen |
|----------|----------------|
| Cloud SQL | Additional cost, less control for demo |
| Private Service Connect | More complex setup, overkill for demo scope |
| Shared VPC | Complex IAM, doesn't demonstrate cross-VPC |
| Anthos Service Mesh | Significant complexity, time constraints |

## Network Architecture

### VPC Design

```
vpc-c1 (us-central1)          vpc-c2 (us-east1)
├── 10.0.0.0/16               ├── 10.1.0.0/16
│                             │
├── Subnet: 10.0.0.0/20       ├── Subnet: 10.1.0.0/20
├── Pods:   10.0.16.0/20      ├── Pods:   10.1.16.0/20
├── Svcs:   10.0.32.0/20      ├── Svcs:   10.1.32.0/20
└── Master: 10.0.48.0/28      └── Master: 10.1.48.0/28
```

### VPC Peering

- Bidirectional peering between vpc-c1 and vpc-c2
- Custom routes exported/imported for full connectivity
- No overlapping CIDR blocks

### Firewall Rules Strategy

**Default Deny (Priority 65534)**
- `c1-deny-all-ingress`: Block all ingress to vpc-c1
- `c1-deny-all-egress`: Block all egress from vpc-c1
- `c2-deny-all-ingress`: Block all ingress to vpc-c2
- `c2-deny-all-egress`: Block all egress from vpc-c2

**Explicit Allows (Priority 1000)**
- `allow-c1-to-c2-app`: C1 egress → C2 TCP:8080
- `allow-c1-to-c2-app-ingress`: C2 ingress ← C1 TCP:8080
- `allow-c2-to-c1-db`: C1 ingress ← C2 TCP:5432
- `allow-c2-to-c1-db-egress`: C2 egress → C1 TCP:5432
- `*-allow-internal`: Intra-VPC communication
- `*-allow-health-checks`: GCP health check ranges
- `*-allow-gke-master`: Control plane to nodes
- `*-allow-iap-ssh`: IAP tunnel for admin access

## Application Architecture

### Service Distribution

**Cluster C1 (us-central1) - Frontend + User Data**

| Service | Type | Purpose |
|---------|------|---------|
| frontend | Python | Web UI, calls backend services |
| loadgenerator | Python | Traffic simulation |
| accounts-db | PostgreSQL | User account data |

**Cluster C2 (us-east1) - Backend Services + Ledger Data**

| Service | Type | Purpose |
|---------|------|---------|
| userservice | Python | User authentication |
| contacts | Python | Contact management |
| balancereader | Java | Balance queries |
| transactionhistory | Java | Transaction history |
| ledgerwriter | Java | Transaction processing |
| ledger-db | PostgreSQL | Transaction data |

### Why This Distribution

1. **Frontend in C1**: Demonstrates client-side of cross-cluster communication
2. **All backends in C2**: Creates clear C1→C2 dependency for access revocation demo
3. **accounts-db in C1**: Enables bidirectional traffic (C2 backends → C1 database)
4. **ledger-db in C2**: Co-located with services that use it heavily

### Cross-Cluster Communication

```
Direction 1: C1 → C2 (Frontend to Backends)
┌────────────────────────────────────────────────────────────────┐
│ frontend (C1) → userservice-ilb:8080     (10.1.100.10)        │
│              → contacts-ilb:8080         (10.1.100.11)        │
│              → balancereader-ilb:8080    (10.1.100.12)        │
│              → transactionhistory-ilb:8080 (10.1.100.13)      │
│              → ledgerwriter-ilb:8080     (10.1.100.14)        │
└────────────────────────────────────────────────────────────────┘

Direction 2: C2 → C1 (Backends to User Database)
┌────────────────────────────────────────────────────────────────┐
│ userservice (C2)  ─┐                                           │
│ contacts (C2)     ─┴→ accounts-db-ilb:5432 (10.0.100.50)       │
└────────────────────────────────────────────────────────────────┘
```

## Security Architecture

### Defense in Depth Layers

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: VPC Peering                                            │
│   - Must be active for any cross-cluster traffic                │
│   - Foundation for all connectivity                             │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2: GCP Firewall Rules                                     │
│   - Network-level protocol/port filtering                       │
│   - Default-deny with explicit allows                           │
│   - Logged for audit trail                                      │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3: Kubernetes NetworkPolicies                             │
│   - Pod-level ingress/egress control                            │
│   - Namespace isolation                                         │
│   - Selector-based targeting                                    │
├─────────────────────────────────────────────────────────────────┤
│ Layer 4: (Not Implemented) Service Mesh mTLS                    │
│   - Would provide service-to-service encryption                 │
│   - Fine-grained authorization                                  │
└─────────────────────────────────────────────────────────────────┘
```

### NetworkPolicy Design

**C1 Policies:**
- `default-deny-all`: Block all traffic by default
- `frontend-egress`: Allow egress to C2:8080 only
- `frontend-ingress`: Allow from loadgenerator
- `accounts-db-ingress`: Allow from C2:5432 + health checks

**C2 Policies:**
- `default-deny-all`: Block all traffic by default
- `backend-ingress`: Allow from C1:8080 + health checks
- `backend-egress`: Allow to C1:5432 + local ledger-db
- `ledger-db-ingress`: Allow from local backends only

### Security Control Impact Analysis

| Control Removed | Application Effect |
|-----------------|-------------------|
| Firewall `allow-c1-to-c2-app` | Frontend cannot reach backends; app unusable |
| Firewall `allow-c2-to-c1-db` | userservice/contacts cannot authenticate; login fails |
| NetworkPolicy `frontend-egress` | Frontend could probe other services |
| NetworkPolicy `accounts-db-ingress` | Any C2 pod could access user data |
| VPC Peering | Total app failure |

## Access Revocation Mechanism

### Primary Method: Firewall Rule Deletion

**Why firewall rules (not NetworkPolicy):**
- Faster to demonstrate (single gcloud command)
- More visible in GCP Console
- Deterministic failure mode (connection timeout)
- Easy to restore
- Provides audit log

### Demo Flow

```
1. Baseline (all working)
   ✓ frontend → userservice
   ✓ frontend → balancereader
   ✓ userservice → accounts-db

2. Revoke (delete allow-c1-to-c2-app)
   ✗ frontend → userservice (TIMEOUT)
   ✗ frontend → balancereader (TIMEOUT)
   ✓ userservice → accounts-db (still works)

3. Restore (recreate firewall rule)
   ✓ All connections restored
```

### Revocation Commands

```bash
# Revoke frontend → backends
gcloud compute firewall-rules delete allow-c1-to-c2-app --quiet
gcloud compute firewall-rules delete allow-c1-to-c2-app-ingress --quiet

# Restore
gcloud compute firewall-rules create allow-c1-to-c2-app \
  --network=vpc-c1 --direction=EGRESS --priority=1000 \
  --destination-ranges=10.1.0.0/16 --rules=tcp:8080 \
  --target-tags=gke-c1-node
```

## Observability Architecture

### Components

- **Prometheus**: Metrics collection and storage
- **Grafana**: Dashboards and visualization

### Key Metrics

| Metric | Purpose |
|--------|---------|
| Request rate | Traffic volume monitoring |
| Error rate | Service health indication |
| Latency (p95, p99) | Performance monitoring |
| Pod CPU/Memory | Resource utilization |

### Dashboard Design

The cross-cluster dashboard shows:
1. Backend request rate by service
2. Error rate (5xx responses)
3. Service health status (UP/DOWN)
4. Resource utilization

This enables clear before/after visualization during access revocation demos.

## Scope Limitations

### Implemented
- Core infrastructure (VPCs, GKE, peering, firewall)
- Bank of Anthos deployment across clusters
- NetworkPolicies for egress/ingress control
- Python verification tool
- Basic Prometheus + Grafana
- Firewall-based access revocation

### Not Implemented (Production Would Include)
- **mTLS**: Would use Anthos Service Mesh
- **Pod Security Standards**: Restricted PSS profile
- **Workload Identity**: Instead of node service account
- **Secret Management**: GCP Secret Manager + External Secrets
- **HA Observability**: Multi-replica Prometheus/Grafana
- **Backup/DR**: Velero, database backups
- **Binary Authorization**: Image signing enforcement
- **VPC Service Controls**: Additional perimeter defense

## Future Enhancements

1. **Add Ingress for Anthos**: Global load balancing with external access
2. **Implement mTLS**: Via Anthos Service Mesh or Istio
3. **Add Cloud Armor**: WAF protection for external endpoints
4. **Multi-project setup**: Demonstrate cross-project connectivity
5. **GitOps**: ArgoCD or Flux for deployment automation
