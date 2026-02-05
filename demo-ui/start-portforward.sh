#!/bin/bash
export HOME=/Users/chundu
export KUBECONFIG=/Users/chundu/.kube/config

pkill -f "port-forward" 2>/dev/null || true
sleep 1

nohup /usr/local/bin/kubectl --context gke-c1 port-forward svc/grafana 3001:3000 -n monitoring >/dev/null 2>&1 &
nohup /usr/local/bin/kubectl --context gke-c1 port-forward svc/prometheus 9090:9090 -n monitoring >/dev/null 2>&1 &
nohup /usr/local/bin/kubectl --context gke-c1 port-forward svc/loki 3100:3100 -n monitoring >/dev/null 2>&1 &
nohup /usr/local/bin/kubectl --context gke-c1 port-forward svc/frontend 8085:80 -n bank-of-anthos >/dev/null 2>&1 &

sleep 3
echo "done"
