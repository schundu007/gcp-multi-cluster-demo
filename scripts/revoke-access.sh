#!/bin/bash
# Revoke cross-cluster access by deleting firewall rules
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

# Revoke C1 -> C2 app traffic
revoke_c1_to_c2() {
    log_warn "Revoking C1 -> C2 application traffic..."
    log_warn "This will block frontend from reaching backend services!"

    # Delete egress rule from C1
    if gcloud compute firewall-rules describe allow-c1-to-c2-app --project="$PROJECT_ID" &>/dev/null; then
        gcloud compute firewall-rules delete allow-c1-to-c2-app \
            --project="$PROJECT_ID" \
            --quiet
        log_info "Deleted: allow-c1-to-c2-app (C1 egress)"
    else
        log_warn "Rule allow-c1-to-c2-app already deleted"
    fi

    # Delete ingress rule in C2
    if gcloud compute firewall-rules describe allow-c1-to-c2-app-ingress --project="$PROJECT_ID" &>/dev/null; then
        gcloud compute firewall-rules delete allow-c1-to-c2-app-ingress \
            --project="$PROJECT_ID" \
            --quiet
        log_info "Deleted: allow-c1-to-c2-app-ingress (C2 ingress)"
    else
        log_warn "Rule allow-c1-to-c2-app-ingress already deleted"
    fi

    log_info "C1 -> C2 application traffic has been REVOKED"
    log_warn "Frontend will now fail to reach backend services!"
}

# Revoke C2 -> C1 database traffic
revoke_c2_to_c1() {
    log_warn "Revoking C2 -> C1 database traffic..."
    log_warn "This will block userservice/contacts from reaching accounts-db!"

    # Delete ingress rule in C1
    if gcloud compute firewall-rules describe allow-c2-to-c1-db --project="$PROJECT_ID" &>/dev/null; then
        gcloud compute firewall-rules delete allow-c2-to-c1-db \
            --project="$PROJECT_ID" \
            --quiet
        log_info "Deleted: allow-c2-to-c1-db (C1 ingress)"
    else
        log_warn "Rule allow-c2-to-c1-db already deleted"
    fi

    # Delete egress rule from C2
    if gcloud compute firewall-rules describe allow-c2-to-c1-db-egress --project="$PROJECT_ID" &>/dev/null; then
        gcloud compute firewall-rules delete allow-c2-to-c1-db-egress \
            --project="$PROJECT_ID" \
            --quiet
        log_info "Deleted: allow-c2-to-c1-db-egress (C2 egress)"
    else
        log_warn "Rule allow-c2-to-c1-db-egress already deleted"
    fi

    log_info "C2 -> C1 database traffic has been REVOKED"
    log_warn "userservice and contacts will fail to authenticate users!"
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
    echo "  Access Revocation Tool"
    echo "============================================================"
    echo ""

    get_project_id
    log_info "Project: $PROJECT_ID"

    case "${1:-c1-to-c2}" in
        c1-to-c2|app)
            revoke_c1_to_c2
            ;;
        c2-to-c1|db)
            revoke_c2_to_c1
            ;;
        all)
            revoke_c1_to_c2
            echo ""
            revoke_c2_to_c1
            ;;
        status)
            show_status
            ;;
        *)
            echo "Usage: $0 {c1-to-c2|c2-to-c1|all|status}"
            echo ""
            echo "  c1-to-c2 (or app)  - Revoke frontend -> backend traffic"
            echo "  c2-to-c1 (or db)   - Revoke backend -> accounts-db traffic"
            echo "  all                - Revoke all cross-cluster traffic"
            echo "  status             - Show current firewall rule status"
            exit 1
            ;;
    esac

    echo ""
    show_status
    echo ""
    log_info "Run './restore-access.sh' to restore access"
}

main "$@"
