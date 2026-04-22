#!/bin/bash

# Database maintenance scripts for OldShop

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if PostgreSQL is running
check_postgres() {
    if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        print_error "PostgreSQL is not running. Please start PostgreSQL service first."
        exit 1
    fi
}

# Backup database
backup_database() {
    local db_name=$1
    local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"

    print_status "Creating backup: $backup_file"
    pg_dump -h localhost -U postgres -d "$db_name" > "$backup_file"

    if [ $? -eq 0 ]; then
        print_status "Backup completed: $backup_file"
    else
        print_error "Backup failed"
        exit 1
    fi
}

# Restore database
restore_database() {
    local db_name=$1
    local backup_file=$2

    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi

    print_warning "This will overwrite the current database. Continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Restore cancelled"
        exit 0
    fi

    print_status "Restoring from: $backup_file"
    psql -h localhost -U postgres -d "$db_name" < "$backup_file"

    if [ $? -eq 0 ]; then
        print_status "Restore completed"
    else
        print_error "Restore failed"
        exit 1
    fi
}

# Show database statistics
show_stats() {
    local db_name=$1

    print_status "Database Statistics for $db_name:"
    psql -h localhost -U postgres -d "$db_name" -c "
        SELECT
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    "
}

# Clean old logs (older than 30 days)
clean_logs() {
    local db_name=$1

    print_status "Cleaning old system logs..."
    psql -h localhost -U postgres -d "$db_name" -c "
        DELETE FROM system_log
        WHERE log_time < CURRENT_TIMESTAMP - INTERVAL '30 days';
    "
    print_status "Old logs cleaned"
}

# Main script logic
case "$1" in
    backup)
        check_postgres
        backup_database "${2:-oldshop}"
        ;;
    restore)
        check_postgres
        restore_database "${2:-oldshop}" "$3"
        ;;
    stats)
        check_postgres
        show_stats "${2:-oldshop}"
        ;;
    clean)
        check_postgres
        clean_logs "${2:-oldshop}"
        ;;
    *)
        echo "Usage: $0 {backup|restore|stats|clean} [database_name] [backup_file]"
        echo ""
        echo "Commands:"
        echo "  backup [db]     - Create database backup"
        echo "  restore [db] [file] - Restore database from backup"
        echo "  stats [db]      - Show database statistics"
        echo "  clean [db]      - Clean old logs (30+ days)"
        exit 1
        ;;
esac