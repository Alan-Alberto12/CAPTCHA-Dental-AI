#!/bin/bash
# Database migration helper script for Alembic

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in Docker
if [ -f /.dockerenv ]; then
    DOCKER_CMD=""
    print_info "Running inside Docker container"
else
    DOCKER_CMD="docker exec captcha-dental-backend"
    print_info "Running on host, will execute commands in Docker container"
fi

# Main command logic
case "${1:-help}" in
    create)
        if [ -z "$2" ]; then
            print_error "Migration message required. Usage: ./migrate.sh create \"your message\""
            exit 1
        fi
        print_info "Creating new migration: $2"
        $DOCKER_CMD alembic revision --autogenerate -m "$2"
        print_info "Migration created successfully!"
        print_warning "Please review the generated migration file before applying it"
        ;;

    upgrade)
        print_info "Applying all pending migrations..."
        $DOCKER_CMD alembic upgrade head
        print_info "Migrations applied successfully!"
        ;;

    downgrade)
        if [ -z "$2" ]; then
            print_info "Downgrading by 1 version..."
            $DOCKER_CMD alembic downgrade -1
        else
            print_info "Downgrading to revision: $2"
            $DOCKER_CMD alembic downgrade "$2"
        fi
        print_info "Downgrade completed!"
        ;;

    current)
        print_info "Current database revision:"
        $DOCKER_CMD alembic current
        ;;

    history)
        print_info "Migration history:"
        $DOCKER_CMD alembic history --verbose
        ;;

    stamp)
        if [ -z "$2" ]; then
            print_error "Revision required. Usage: ./migrate.sh stamp <revision>"
            exit 1
        fi
        print_info "Stamping database with revision: $2"
        $DOCKER_CMD alembic stamp "$2"
        print_info "Database stamped successfully!"
        ;;

    help|*)
        echo "Database Migration Helper Script"
        echo ""
        echo "Usage: ./migrate.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  create <message>    - Create a new migration with autogenerate"
        echo "  upgrade            - Apply all pending migrations"
        echo "  downgrade [rev]    - Downgrade by 1 version (or to specific revision)"
        echo "  current            - Show current database revision"
        echo "  history            - Show migration history"
        echo "  stamp <revision>   - Stamp database with specific revision (without running migrations)"
        echo "  help               - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./migrate.sh create \"Add user email verification\""
        echo "  ./migrate.sh upgrade"
        echo "  ./migrate.sh downgrade"
        echo "  ./migrate.sh downgrade abc123"
        echo "  ./migrate.sh current"
        echo "  ./migrate.sh history"
        echo "  ./migrate.sh stamp head"
        ;;
esac
