#!/bin/bash

# Enhanced database population script with error handling and best practices
set -euo pipefail

# Configuration
DEFAULT_DB_NAME="user_management_db"
DEFAULT_MYSQL_HOST="localhost"
DEFAULT_MYSQL_USER="root"
LOG_FILE="database_population.log"
SQL_SCRIPT=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to display usage
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -d, --database <name>     Database name (default: $DEFAULT_DB_NAME)"
    echo "  -h, --host <host>         MySQL host (default: $DEFAULT_MYSQL_HOST)"
    echo "  -u, --user <username>     MySQL username (default: $DEFAULT_MYSQL_USER)"
    echo "  -f, --file <filename>     SQL script file (default: auto-detect)"
    echo "  --help                    Display this help message"
    exit 1
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--database)
                DB_NAME="$2"
                shift 2
                ;;
            -h|--host)
                MYSQL_HOST="$2"
                shift 2
                ;;
            -u|--user)
                MYSQL_USER="$2"
                shift 2
                ;;
            -f|--file)
                SQL_SCRIPT="$2"
                shift 2
                ;;
            --help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done
}

# Function to validate environment
validate_environment() {
    # Check if MYSQL_PASSWORD is set
    if [ -z "${MYSQL_PASSWORD:-}" ]; then
        log_error "MYSQL_PASSWORD environment variable is not set."
        log_error "Please set it using: export MYSQL_PASSWORD='your_password'"
        exit 1
    fi
    
    # Set default values if not provided
    DB_NAME="${DB_NAME:-$DEFAULT_DB_NAME}"
    MYSQL_HOST="${MYSQL_HOST:-$DEFAULT_MYSQL_HOST}"
    MYSQL_USER="${MYSQL_USER:-$DEFAULT_MYSQL_USER}"
    
    # Find SQL script if not specified
    if [ -z "$SQL_SCRIPT" ]; then
        find_sql_script
    fi
    
    # Validate SQL script exists
    if [ ! -f "$SQL_SCRIPT" ]; then
        log_error "SQL script file '$SQL_SCRIPT' not found."
        exit 1
    fi
}

# Function to find SQL script with case-insensitive search
find_sql_script() {
    local patterns=(
        "Populate_MySQL_database.sql"
        "Populate_MySQL_database.SQL"
        "populate_mysql_database.sql"
        "database_population.sql"
    )
    
    for pattern in "${patterns[@]}"; do
        if [ -f "$pattern" ]; then
            SQL_SCRIPT="$pattern"
            log_info "Using SQL script: $SQL_SCRIPT"
            return
        fi
    done
    
    log_error "No SQL script found. Please specify with -f option."
    exit 1
}

# Function to test MySQL connection
test_mysql_connection() {
    log_info "Testing MySQL connection..."
    if ! mysql --host="$MYSQL_HOST" --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" --execute="SELECT 1;" --silent --skip-column-names 2>/dev/null; then
        log_error "Cannot connect to MySQL server. Please check your credentials and try again."
        exit 1
    fi
    log_info "MySQL connection successful."
}

# Function to check if database exists
check_database_exists() {
    local db_exists=$(mysql --host="$MYSQL_HOST" --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" \
        --execute="SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = '$DB_NAME';" --silent --skip-column-names 2>/dev/null)
    
    if [ "$db_exists" -eq 0 ]; then
        log_warning "Database '$DB_NAME' does not exist. It will be created by the script."
        return 1
    else
        log_info "Database '$DB_NAME' exists."
        return 0
    fi
}

# Function to execute SQL script
execute_sql_script() {
    log_info "Executing SQL script: $SQL_SCRIPT"
    
    # Capture output and errors
    if mysql --host="$MYSQL_HOST" --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" < "$SQL_SCRIPT" 2>&1 | tee -a "$LOG_FILE"; then
        log_info "SQL script executed successfully."
        return 0
    else
        log_error "Failed to execute SQL script."
        return 1
    fi
}

# Function to verify data insertion
verify_data_insertion() {
    log_info "Verifying data insertion..."
    
    local verification_query="
        SELECT 'USER table' AS table_name, COUNT(*) AS row_count FROM USER
        UNION ALL
        SELECT 'ROLE table', COUNT(*) FROM ROLE
        UNION ALL
        SELECT 'ROLE_USER table', COUNT(*) FROM ROLE_USER;
    "
    
    mysql --host="$MYSQL_HOST" --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" "$DB_NAME" \
        --execute="$verification_query" --silent --skip-column-names 2>> "$LOG_FILE" | while read -r line; do
        log_info "$line"
    done
}

# Function to display sample data
display_sample_data() {
    log_info "Displaying sample data..."
    
    local sample_query="
        SELECT 'Last 5 users:' AS '';
        SELECT user_id, email, first_name, last_name, enabled FROM USER ORDER BY user_id DESC LIMIT 5;
        
        SELECT 'All roles:' AS '';
        SELECT role_id, name, description FROM ROLE;
        
        SELECT 'Sample user roles:' AS '';
        SELECT u.email, r.name as role_name 
        FROM USER u
        JOIN ROLE_USER ru ON u.user_id = ru.user_id
        JOIN ROLE r ON ru.role_id = r.role_id
        LIMIT 10;
    "
    
    mysql --host="$MYSQL_HOST" --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" "$DB_NAME" \
        --execute="$sample_query" 2>> "$LOG_FILE" || log_warning "Could not display sample data"
}

# Main function
main() {
    log_info "Starting database population process"
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Validate environment
    validate_environment
    
    # Test MySQL connection
    test_mysql_connection
    
    # Check if database exists
    check_database_exists || true
    
    # Execute SQL script
    if execute_sql_script; then
        # Verify data insertion
        verify_data_insertion
        
        # Display sample data
        display_sample_data
        
        log_info "Database population completed successfully!"
    else
        log_error "Database population failed. Check $LOG_FILE for details."
        exit 1
    fi
}

# Trap to handle script interruption
trap 'log_error "Script interrupted by user"; exit 1' INT TERM

# Run main function with all arguments
main "$@"
