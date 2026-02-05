#!/bin/bash
# Restore cross-cluster access by recreating firewall rules
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

# Get project ID
get_project_id() {
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z "$PROJECT_ID" ]; then
            log_error "PROJECT_ID not set"
            exit 1
        fi
    fi
    export PROJECT_ID
}

# Restore C1 -> C2 app traffic
restore_c1_to_c2() {
    log_info "Restoring C1 -> C2 application traffic..."

    # Restore egress rule from C1
    if ! gcloud compute firewall-rules describe allow-c1-to-c2-app --project="$PROJECT_ID" &>/dev/null; then
        gcloud compute firewall-rules create allow-c1-to-c2-app \
            --project="$PROJECT_ID" \
            --network=vpc-c1 \
            --direction=EGRESS \
            --priority=1000 \
            --destination-ranges=10.1.0.0/16,10.1.16.0/20 \
            --rules=tcp:8080 \
            --target-tags=gke-c1-node \
            --enable-logging
        log_info "Created: allow-c1-to-c2-app (C1 egress)"
    else
        log_warn "Rule allow-c1-to-c2-app already exists"
    fi

    # Restore ingress rule in C2
    if ! gcloud compute firewall-rules describe allow-c1-to-c2-app-ingress --project="$PROJECT_ID" &>/dev/null; then
        gcloud compute firewall-rules create allow-c1-to-c2-app-ingress \
            --project="$PROJECT_ID" \
            --network=vpc-c2 \
            --direction=INGRESS \
            --priority=1000 \
            --source-ranges=10.0.0.0/16,10.0.16.0/20 \
            --rules=tcp:8080 \
            --target-tags=gke-c2-node \
            --enable-logging
        log_info "Created: allow-c1-to-c2-app-ingress (C2 ingress)"
    else
        log_warn "Rule allow-c1-to-c2-app-ingress already exists"
    fi

    log_info "C1 -> C2 application traffic has been RESTORED"
}

# Restore C2 -> C1 database traffic
restore_c2_to_c1() {
    log_info "Restoring C2 -> C1 database traffic..."

    # Restore ingress rule in C1
    if ! gcloud compute firewall-rules describe allow-c2-to-c1-db --project="$PROJECT_ID" &>/dev/null; then
        gcloud compute firewall-rules create allow-c2-to-c1-db \
            --project="$PROJECT_ID" \
            --network=vpc-c1 \
            --direction=INGRESS \
            --priority=1000 \
            --source-ranges=10.1.0.0/16,10.1.16.0/20 \
            --rules=tcp:5432 \
            --target-tags=gke-c1-node \
            --enable-logging
        log_info "Created: allow-c2-to-c1-db (C1 ingress)"
    else
        log_warn "Rule allow-c2-to-c1-db already exists"
    fi

    # Restore egress rule from C2
    if ! gcloud compute firewall-rules describe allow-c2-to-c1-db-egress --project="$PROJECT_ID" &>/dev/null; then
        gcloud compute firewall-rules create allow-c2-to-c1-db-egress \
            --project="$PROJECT_ID" \
            --network=vpc-c2 \
            --direction=EGRESS \
            --priority=1000 \
            --destination-ranges=10.0.0.0/16,10.0.16.0/20 \
            --rules=tcp:5432 \
            --target-tags=gke-c2-node \
            --enable-logging
        log_info "Created: allow-c2-to-c1-db-egress (C2 egress)"
    else
        log_warn "Rule allow-c2-to-c1-db-egress already exists"
    fi

    log_info "C2 -> C1 database traffic has been RESTORED"
}

# Show current status
show_status() {
    echo ""
    log_info "Current firewall rules:"
    gcloud compute firewall-rules list \
        --project="$PROJECT_ID" \
        --filter="name~allow-c1-to-c2 OR name~allow-c2-to-c1" \
        --format="table(name,network,direction,allowed[].map().firewall_rule().list():label=ALLOW)"
}

# Main
main() {
    echo "============================================================"
    echo "  Access Restoration Tool"
    echo "============================================================"
    echo ""

    get_project_id
    log_info "Project: $PROJECT_ID"

    case "${1:-all}" in
        c1-to-c2|app)
            restore_c1_to_c2
            ;;
        c2-to-c1|db)
            restore_c2_to_c1
            ;;
        all)
            restore_c1_to_c2
            echo ""
            restore_c2_to_c1
            ;;
        status)
            show_status
            ;;
        *)
            echo "Usage: $0 {c1-to-c2|c2-to-c1|all|status}"
            echo ""
            echo "  c1-to-c2 (or app)  - Restore frontend -> backend traffic"
            echo "  c2-to-c1 (or db)   - Restore backend -> accounts-db traffic"
            echo "  all                - Restore all cross-cluster traffic"
            echo "  status             - Show current firewall rule status"
            exit 1
            ;;
    esac

    echo ""
    show_status
    echo ""
    log_info "Cross-cluster access restored!"
}

main "$@"
