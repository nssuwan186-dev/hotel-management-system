#!/bin/bash
# VIPAT Hotel ERP v2.0 - Deployment Script (Integrated)

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

case "${1:-help}" in
    upgrade)
        echo "Updating Database Schema..."
        python3 database/models/upgrade_to_erp_v2.py
        ;;
    test)
        echo "Running Integrated System Test..."
        python3 scripts/maintenance/master_system_test.py
        ;;
    *)
        echo "Usage: $0 [upgrade|test]"
        ;;
esac
