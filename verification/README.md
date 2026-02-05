# GCP Multi-Cluster Verification Tool

A Python tool to verify the networking and security configuration of the GCP multi-cluster setup.

## Features

- **Connectivity Tests**: Verifies cross-cluster communication (C1→C2 and C2→C1)
- **Security Posture Checks**: Ensures no external exposure (no public IPs, no external LBs)
- **Network Policy Validation**: Confirms NetworkPolicies are correctly configured

## Prerequisites

1. Python 3.9+
2. `kubectl` configured with contexts for both clusters
3. `gcloud` CLI authenticated with appropriate permissions
4. Required Python packages (see `requirements.txt`)

## Installation

```bash
cd verification
pip install -r requirements.txt
```

## Usage

### Run all checks

```bash
python verify.py --all --project-id=your-gcp-project
```

### Run specific checks

```bash
# Connectivity tests only
python verify.py --connectivity --project-id=your-gcp-project

# Security posture tests only
python verify.py --security --project-id=your-gcp-project

# Network policy tests only
python verify.py --network-policy --project-id=your-gcp-project
```

### Verbose output

```bash
python verify.py --all --project-id=your-gcp-project --verbose
```

### Using environment variable for project ID

```bash
export PROJECT_ID=your-gcp-project
python verify.py --all
```

## Configuration

Edit `config.yaml` to customize:
- Cluster contexts and namespaces
- ILB endpoints
- Firewall rule names
- Connectivity test definitions

## Example Output

```
============================================================
  GCP Multi-Cluster Verification Tool
============================================================

=== Connectivity Tests ===

  [PASS] C1→C2: frontend -> userservice - HTTP 200 in 45ms
  [PASS] C1→C2: frontend -> contacts - HTTP 200 in 38ms
  [PASS] C1→C2: frontend -> balancereader - HTTP 200 in 52ms
  [PASS] C2→C1: userservice -> accounts-db - Connected in 5s

=== Security Posture Tests ===

  [PASS] No external LB services (c1) - All LoadBalancer services are internal
  [PASS] No external LB services (c2) - All LoadBalancer services are internal
  [PASS] No Ingress resources (c1) - No Ingress resources found
  [PASS] No Ingress resources (c2) - No Ingress resources found
  [PASS] GKE nodes have private IPs only - All GKE nodes are private
  [PASS] No external forwarding rules - No external forwarding rules found
  [PASS] Firewall rule: allow-c1-to-c2-app - Rule exists and is enabled
  [PASS] VPC peering is active - Active peerings: c1-to-c2

=== Network Policy Tests ===

  [PASS] Default-deny policy exists (c1) - Default-deny policy found
  [PASS] Default-deny policy exists (c2) - Default-deny policy found
  [PASS] NetworkPolicy: frontend-egress (c1) - Policy exists
  [PASS] NetworkPolicy: backend-ingress (c2) - Policy exists
  [PASS] Frontend egress allows C2 traffic - Egress to 10.1.0.0/16 allowed
  [PASS] Backend ingress allows C1 traffic - Ingress from 10.0.0.0/16 allowed

=== Summary ===

Total checks:    16
Passed:          16
Failed:          0

All checks passed!
```

## Troubleshooting

### "Failed to load kubeconfig"

Ensure kubectl contexts are configured:

```bash
gcloud container clusters get-credentials c1 --region us-central1
gcloud container clusters get-credentials c2 --region us-east1
kubectl config rename-context gke_PROJECT_us-central1_c1 gke-c1
kubectl config rename-context gke_PROJECT_us-east1_c2 gke-c2
```

### "Project ID required"

Either pass `--project-id` or set the `PROJECT_ID` environment variable.

### Connectivity test failures

1. Check that test pods can be created in the namespace
2. Verify ILB IPs are correct in `config.yaml`
3. Check firewall rules are in place
4. Verify VPC peering is active
