#!/bin/bash

# Health check script for OldShop database

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-oldshop}
DB_USER=${DB_USER:-oldshop_user}
DB_PASSWORD=${DB_PASSWORD:-oldshop_password}

# Function to check database connection
check_connection() {
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Database connection: OK"
        return 0
    else
        echo -e "${RED}✗${NC} Database connection: FAILED"
        return 1
    fi
}

# Function to check table counts
check_table_counts() {
    local result
    result=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT
            'users: ' || COUNT(*) FROM \"user\" UNION ALL
        SELECT 'products: ' || COUNT(*) FROM product WHERE is_deleted = FALSE UNION ALL
        SELECT 'orders: ' || COUNT(*) FROM \"order\" WHERE is_deleted = FALSE UNION ALL
        SELECT 'categories: ' || COUNT(*) FROM category WHERE is_deleted = FALSE;
    ")

    echo "Table counts:"
    echo "$result"
}

# Function to check recent activity
check_recent_activity() {
    local result
    result=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT
            'Recent orders: ' || COUNT(*) FROM \"order\"
            WHERE order_date >= CURRENT_TIMESTAMP - INTERVAL '24 hours' UNION ALL
        SELECT 'Recent logins: ' || COUNT(*) FROM \"user\"
            WHERE last_login >= CURRENT_TIMESTAMP - INTERVAL '24 hours';
    ")

    echo "Recent activity (24h):"
    echo "$result"
}

# Function to check disk usage
check_disk_usage() {
    local result
    result=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT
            schemaname || '.' || tablename || ': ' || pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        LIMIT 5;
    ")

    echo "Largest tables:"
    echo "$result"
}

# Main health check
main() {
    echo "=== OldShop Database Health Check ==="
    echo "Time: $(date)"
    echo

    local status=0

    check_connection || status=1
    echo

    if [ $status -eq 0 ]; then
        check_table_counts
        echo
        check_recent_activity
        echo
        check_disk_usage
    fi

    echo
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Health check completed successfully"
    else
        echo -e "${RED}✗${NC} Health check failed"
    fi

    return $status
}

# Run main function
main "$@"