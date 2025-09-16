#!/bin/bash

# Enhanced Product Table Population Script
# BlueVelvet Music Store Database Setup
# Improved password handling and error management

set -euo pipefail
IFS=$'\n\t'

# Configuration
readonly DEFAULT_DB_NAME="bluevelvet_store"
readonly DEFAULT_MYSQL_HOST="localhost"
readonly DEFAULT_MYSQL_USER="root"
readonly DEFAULT_MYSQL_PORT="3306"
readonly LOG_FILE="product_population.log"
readonly LOCK_FILE="/tmp/bluevelvet_db_populate.lock"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Global variables
DB_NAME=""
MYSQL_HOST=""
MYSQL_USER=""
MYSQL_PORT=""
SQL_SCRIPT=""
MYSQL_PASSWORD=""

# Function to clean up on exit
cleanup() {
    local exit_code=$?
    
    # Remove lock file
    if [[ -f "$LOCK_FILE" ]]; then
        rm -f "$LOCK_FILE"
    fi
    
    # Log exit
    if [[ $exit_code -eq 0 ]]; then
        log_info "Script completed successfully"
    else
        log_error "Script failed with exit code $exit_code"
    fi
    
    exit $exit_code
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [options]

Options:
  -d, --database <name>     Database name (default: $DEFAULT_DB_NAME)
  -h, --host <host>         MySQL host (default: $DEFAULT_MYSQL_HOST)
  -u, --user <username>     MySQL username (default: $DEFAULT_MYSQL_USER)
  -p, --port <port>         MySQL port (default: $DEFAULT_MYSQL_PORT)
  -f, --file <filename>     SQL script file (default: auto-detect)
  -P, --password <password> MySQL password (alternative to environment variable)
  --help                    Display this help message

Environment variables:
  MYSQL_PASSWORD            MySQL password (recommended for security)
  MYSQL_PWD                 Alternative environment variable for password

Examples:
  $0 --database mydb --user admin --password secret
  MYSQL_PASSWORD=secret $0 --database mydb --user admin
EOF
    exit 1
}

# Function to parse command line arguments
parse_arguments() {
    local args=("$@")
    
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
            -p|--port)
                MYSQL_PORT="$2"
                shift 2
                ;;
            -f|--file)
                SQL_SCRIPT="$2"
                shift 2
                ;;
            -P|--password)
                MYSQL_PASSWORD="$2"
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
    
    # Set default values if not provided
    DB_NAME="${DB_NAME:-$DEFAULT_DB_NAME}"
    MYSQL_HOST="${MYSQL_HOST:-$DEFAULT_MYSQL_HOST}"
    MYSQL_USER="${MYSQL_USER:-$DEFAULT_MYSQL_USER}"
    MYSQL_PORT="${MYSQL_PORT:-$DEFAULT_MYSQL_PORT}"
}

# Function to get MySQL password from various sources
get_mysql_password() {
    # First, check if password was provided as argument
    if [[ -n "$MYSQL_PASSWORD" ]]; then
        log_debug "Using password from command line argument"
        return 0
    fi
    
    # Check environment variables
    if [[ -n "${MYSQL_PASSWORD:-}" ]]; then
        log_debug "Using password from MYSQL_PASSWORD environment variable"
        MYSQL_PASSWORD="${MYSQL_PASSWORD}"
        return 0
    fi
    
    if [[ -n "${MYSQL_PWD:-}" ]]; then
        log_debug "Using password from MYSQL_PWD environment variable"
        MYSQL_PASSWORD="${MYSQL_PWD}"
        return 0
    fi
    
    # Try to get password from MySQL configuration file
    if [[ -f "$HOME/.my.cnf" ]]; then
        log_debug "Trying to get password from MySQL config file"
        local config_password=$(grep -E "^\s*password\s*=" "$HOME/.my.cnf" | head -1 | awk -F= '{print $2}' | tr -d ' ')
        if [[ -n "$config_password" ]]; then
            MYSQL_PASSWORD="$config_password"
            return 0
        fi
    fi
    
    # Finally, prompt for password
    log_warning "No password found in environment variables or config files"
    read -rsp "Enter MySQL password for $MYSQL_USER: " MYSQL_PASSWORD
    echo
    if [[ -z "$MYSQL_PASSWORD" ]]; then
        log_error "No password provided"
        return 1
    fi
    
    return 0
}

# Function to validate environment
validate_environment() {
    # Check if lock file exists (prevent concurrent execution)
    if [[ -f "$LOCK_FILE" ]]; then
        log_error "Script is already running (lock file exists: $LOCK_FILE)"
        exit 1
    fi
    
    # Create lock file
    touch "$LOCK_FILE"
    
    # Check if MySQL client is available
    if ! command -v mysql &> /dev/null; then
        log_error "MySQL client is not installed or not in PATH"
        exit 1
    fi
    
    # Get MySQL password
    if ! get_mysql_password; then
        log_error "Failed to get MySQL password"
        exit 1
    fi
    
    # Find SQL script if not specified
    if [[ -z "$SQL_SCRIPT" ]]; then
        find_sql_script
    fi
    
    # Validate SQL script exists
    if [[ ! -f "$SQL_SCRIPT" ]]; then
        log_error "SQL script file '$SQL_SCRIPT' not found."
        exit 1
    fi
    
    # Validate SQL script is readable
    if [[ ! -r "$SQL_SCRIPT" ]]; then
        log_error "SQL script file '$SQL_SCRIPT' is not readable."
        exit 1
    fi
}

# Function to find SQL script with case-insensitive search
find_sql_script() {
    local patterns=(
        "Create_Product_Table.sql"
        "create_product_table.sql"
        "product_table.sql"
        "Populate_Products.sql"
        "populate_products.sql"
    )
    
    for pattern in "${patterns[@]}"; do
        if [[ -f "$pattern" ]]; then
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
    log_info "Testing MySQL connection to $MYSQL_HOST:$MYSQL_PORT..."
    
    # Use a temporary config file to avoid password in command line
    local temp_config=$(mktemp)
    cat > "$temp_config" << EOF
[client]
host = $MYSQL_HOST
port = $MYSQL_PORT
user = $MYSQL_USER
password = $MYSQL_PASSWORD
EOF
    
    local connection_test
    connection_test=$(mysql --defaults-file="$temp_config" --execute="SELECT 1;" --silent --skip-column-names 2>&1)
    local exit_code=$?
    
    # Clean up temp config file
    rm -f "$temp_config"
    
    if [[ $exit_code -ne 0 ]]; then
        log_error "Cannot connect to MySQL server: $connection_test"
        log_error "Please check your credentials and try again."
        exit 1
    fi
    
    log_info "MySQL connection successful."
}

# Function to execute SQL script
execute_sql_script() {
    log_info "Executing SQL script: $SQL_SCRIPT"
    
    # Use a temporary config file to avoid password in command line
    local temp_config=$(mktemp)
    cat > "$temp_config" << EOF
[client]
host = $MYSQL_HOST
port = $MYSQL_PORT
user = $MYSQL_USER
password = $MYSQL_PASSWORD
EOF
    
    # Capture output and errors
    local start_time
    start_time=$(date +%s)
    
    if mysql --defaults-file="$temp_config" --verbose < "$SQL_SCRIPT" 2>&1 | tee -a "$LOG_FILE"; then
        local end_time
        end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log_info "SQL script executed successfully in $duration seconds."
        
        # Clean up temp config file
        rm -f "$temp_config"
        return 0
    else
        log_error "Failed to execute SQL script."
        
        # Clean up temp config file
        rm -f "$temp_config"
        return 1
    fi
}

# Function to verify data insertion
verify_data_insertion() {
    log_info "Verifying data insertion..."
    
    # Use a temporary config file to avoid password in command line
    local temp_config=$(mktemp)
    cat > "$temp_config" << EOF
[client]
host = $MYSQL_HOST
port = $MYSQL_PORT
user = $MYSQL_USER
password = $MYSQL_PASSWORD
EOF
    
    local verification_query="
        USE $DB_NAME;
        SELECT 'PRODUCT table' AS table_name, COUNT(*) AS row_count FROM Product;
        SELECT category, COUNT(*) as product_count FROM Product GROUP BY category ORDER BY product_count DESC;
    "
    
    mysql --defaults-file="$temp_config" --execute="$verification_query" 2>> "$LOG_FILE" | tee -a "$LOG_FILE"
    
    # Clean up temp config file
    rm -f "$temp_config"
}

# Main function
main() {
    log_info "Starting product table population process for BlueVelvet Music Store"
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Validate environment
    validate_environment
    
    # Test MySQL connection
    test_mysql_connection
    
    # Execute SQL script
    if execute_sql_script; then
        # Verify data insertion
        verify_data_insertion
        
        log_info "Product table population completed successfully!"
        log_info "Log file: $LOG_FILE"
        return 0
    else
        log_error "Product table population failed. Check $LOG_FILE for details."
        return 1
    fi
}

# Run main function with all arguments
if main "$@"; then
    exit 0
else
    exit 1
fi
