#!/bin/bash
#
# GCP Multi-Cluster Security Demo Runner
# This script sets up port-forwarding and launches the demo UI
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "  GCP Multi-Cluster Security Demo"
echo "=============================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl."
    exit 1
fi

if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud not found. Please install Google Cloud SDK."
    exit 1
fi

if ! command -v streamlit &> /dev/null; then
    echo "📦 Installing Streamlit..."
    pip3 install streamlit --quiet
fi

echo "✅ Prerequisites OK"
echo ""

# Kill any existing port-forwards
echo "Cleaning up existing port-forwards..."
pkill -f "port-forward.*grafana" 2>/dev/null || true
pkill -f "port-forward.*prometheus" 2>/dev/null || true
pkill -f "port-forward.*loki" 2>/dev/null || true
sleep 2

# Start port-forwarding in background
echo "Starting port-forwarding..."

echo "  → Grafana (localhost:3001)"
kubectl --context gke-c1 port-forward svc/grafana 3001:3000 -n monitoring &>/dev/null &
GRAFANA_PID=$!

echo "  → Prometheus (localhost:9090)"
kubectl --context gke-c1 port-forward svc/prometheus 9090:9090 -n monitoring &>/dev/null &
PROMETHEUS_PID=$!

echo "  → Loki (localhost:3100)"
kubectl --context gke-c1 port-forward svc/loki 3100:3100 -n monitoring &>/dev/null &
LOKI_PID=$!

sleep 3

# Check if port-forwards are running
if ! kill -0 $GRAFANA_PID 2>/dev/null; then
    echo "⚠️  Warning: Grafana port-forward may have failed"
fi

echo "✅ Port-forwarding started"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $GRAFANA_PID 2>/dev/null || true
    kill $PROMETHEUS_PID 2>/dev/null || true
    kill $LOKI_PID 2>/dev/null || true
    echo "Done."
}

trap cleanup EXIT

# Launch the demo UI
echo "=============================================="
echo "  Launching Demo UI"
echo "=============================================="
echo ""
echo "Access the demo at: http://localhost:8501"
echo ""
echo "Grafana dashboards available at:"
echo "  - Cross-Cluster Metrics: http://localhost:3001/d/cross-cluster-boa/"
echo "  - Loki Logs: http://localhost:3001/d/loki-logs-boa/"
echo "  - Errors & Failures: http://localhost:3001/d/errors-failures/"
echo ""
echo "Press Ctrl+C to stop the demo"
echo "=============================================="
echo ""

streamlit run app.py --server.port 8501 --server.headless true
