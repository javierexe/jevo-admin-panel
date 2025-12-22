#!/bin/bash
# Smoke tests for Admin UI endpoints
# Tests basic auth and endpoint availability

set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
ADMIN_USER="${ADMIN_USERNAME:-admin}"
ADMIN_PASS="${ADMIN_PASSWORD:-admin123}"

echo "=================================================="
echo "Admin UI Smoke Tests"
echo "=================================================="
echo "Backend URL: $BACKEND_URL"
echo "Admin User: $ADMIN_USER"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

test_endpoint() {
    local name="$1"
    local path="$2"
    local expected_code="$3"
    local auth="$4"
    
    echo -n "Testing $name... "
    
    if [ "$auth" = "with-auth" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" \
            -u "$ADMIN_USER:$ADMIN_PASS" \
            "$BACKEND_URL$path")
    else
        status=$(curl -s -o /dev/null -w "%{http_code}" \
            "$BACKEND_URL$path")
    fi
    
    if [ "$status" = "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} (got $status)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (expected $expected_code, got $status)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo "1. Testing authentication requirements"
echo "--------------------------------------"
test_endpoint "Clients list without auth" "/admin-ui/clients" "401" "no-auth"
test_endpoint "Fields list without auth" "/admin-ui/fields" "401" "no-auth"
test_endpoint "WhatsApp users list without auth" "/admin-ui/whatsapp-users" "401" "no-auth"

echo ""
echo "2. Testing authenticated access"
echo "--------------------------------------"
test_endpoint "Clients list with auth" "/admin-ui/clients" "200" "with-auth"
test_endpoint "Fields list with auth" "/admin-ui/fields" "200" "with-auth"
test_endpoint "WhatsApp users list with auth" "/admin-ui/whatsapp-users" "200" "with-auth"

echo ""
echo "3. Testing root redirect"
echo "--------------------------------------"
test_endpoint "Root redirects to clients" "/admin-ui" "307" "with-auth"

echo ""
echo "=================================================="
echo "Summary"
echo "=================================================="
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All smoke tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
