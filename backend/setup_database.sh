#!/bin/bash
# Complete database setup script for new team members

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  CAPTCHA Dental AI - Database Setup   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# Step 1: Check if Docker is running
echo -e "${YELLOW}[1/4]${NC} Checking Docker..."
if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker is running\n"

# Step 2: Start containers
echo -e "${YELLOW}[2/4]${NC} Starting Docker containers..."
docker-compose up -d
echo -e "${GREEN}✓${NC} Containers started\n"

# Wait for database to be ready
echo -e "${YELLOW}     ${NC} Waiting for database to be ready..."
sleep 5
echo -e "${GREEN}✓${NC} Database ready\n"

# Step 3: Run migrations
echo -e "${YELLOW}[3/4]${NC} Applying database migrations..."
./migrate.sh upgrade
echo -e "${GREEN}✓${NC} Migrations applied\n"

# Step 4: Seed database
echo -e "${YELLOW}[4/4]${NC} Seeding database with initial data..."
docker exec captcha-dental-backend python seed_data.py
echo -e "${GREEN}✓${NC} Database seeded\n"

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Database Setup Complete! 🎉        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}\n"

echo "Your database is ready to use!"
echo ""
echo "Login credentials:"
echo "  Admin: admin@captcha.local / admin123"
echo "  Test:  test@captcha.local / test123"
echo ""
echo "Next steps:"
echo "  - Upload images via admin panel"
echo "  - Start annotating!"
