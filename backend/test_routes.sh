#!/bin/bash
echo "Testing Admin UI routes..."
echo ""
echo "1. Testing /admin-ui/clients (should require auth):"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8000/admin-ui/clients
echo ""
echo "2. Testing /admin-ui/clients with auth:"
curl -s -o /dev/null -w "Status: %{http_code}\n" -u admin:admin123 http://localhost:8000/admin-ui/clients
echo ""
echo "3. Testing /admin-ui/fields with auth:"
curl -s -o /dev/null -w "Status: %{http_code}\n" -u admin:admin123 http://localhost:8000/admin-ui/fields
echo ""
echo "4. Testing /admin-ui/whatsapp-users with auth:"
curl -s -o /dev/null -w "Status: %{http_code}\n" -u admin:admin123 http://localhost:8000/admin-ui/whatsapp-users
