#!/bin/bash
# Port forwarding startup script for GCP Multi-Cluster demo

# Source user environment
export HOME=/Users/chundu
export USER=chundu
export KUBECONFIG=/Users/chundu/.kube/config
export CLOUDSDK_CONFIG=/Users/chundu/.config/gcloud
export PATH=/usr/local/bin:/opt/homebrew/bin:/Users/chundu/google-cloud-sdk/bin:$PATH

# Source bash profile if it exists (for gcloud auth)
[ -f /Users/chundu/.bash_profile ] && source /Users/chundu/.bash_profile 2>/dev/null
[ -f /Users/chundu/.zshrc ] && source /Users/chundu/.zshrc 2>/dev/null

# Kill any existing port-forward processes
pkill -f "port-forward" 2>/dev/null || true
sleep 1

# Find kubectl binary
KUBECTL=""
if [ -x "/usr/local/bin/kubectl" ]; then
    KUBECTL="/usr/local/bin/kubectl"
elif [ -x "/opt/homebrew/bin/kubectl" ]; then
    KUBECTL="/opt/homebrew/bin/kubectl"
elif command -v kubectl &> /dev/null; then
    KUBECTL=$(command -v kubectl)
fi

if [ -z "$KUBECTL" ]; then
    echo "kubectl not found"
    exit 1
fi

# Start port forwards in background
nohup $KUBECTL --context gke-c1 port-forward --address 127.0.0.1 svc/grafana 3002:3000 -n monitoring >/dev/null 2>&1 &
sleep 0.5
nohup $KUBECTL --context gke-c1 port-forward --address 127.0.0.1 svc/prometheus 9090:9090 -n monitoring >/dev/null 2>&1 &
sleep 0.5
nohup $KUBECTL --context gke-c1 port-forward --address 127.0.0.1 svc/loki 3100:3100 -n monitoring >/dev/null 2>&1 &
sleep 0.5
nohup $KUBECTL --context gke-c1 port-forward --address 127.0.0.1 svc/frontend 8085:80 -n bank-of-anthos >/dev/null 2>&1 &

sleep 3
echo "done"
