#!/bin/sh
# Verify mk-pm backend is running on FreeBSD (or locally)

BASE_URL="${1:-http://127.0.0.1:8000}"
NGINX_URL="${2:-}"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

pass() { printf "${GREEN}PASS${NC} %s\n" "$1"; }
fail() { printf "${RED}FAIL${NC} %s\n" "$1"; FAILED=1; }

FAILED=0

echo "Checking API at $BASE_URL ..."

if curl -sf "$BASE_URL/health" > /tmp/mkpm_health.json 2>/dev/null; then
    pass "Health endpoint ($BASE_URL/health)"
    cat /tmp/mkpm_health.json
    echo ""
else
    fail "Health endpoint ($BASE_URL/health)"
fi

TOKEN=$(curl -sf -X POST "$BASE_URL/api/auth/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123" | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

if [ -n "$TOKEN" ]; then
    pass "Login (admin/admin123)"
else
    fail "Login (admin/admin123)"
fi

if [ -n "$TOKEN" ]; then
    if curl -sf -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/projects/" > /dev/null; then
        pass "Authenticated projects API"
    else
        fail "Authenticated projects API"
    fi
fi

if [ -n "$NGINX_URL" ]; then
    echo ""
    echo "Checking nginx proxy at $NGINX_URL ..."
    if curl -sf "$NGINX_URL/health" > /dev/null; then
        pass "Nginx health proxy"
    else
        fail "Nginx health proxy"
    fi
    if curl -sf "$NGINX_URL/api/projects/" > /dev/null 2>&1; then
        warn_status="expected 401/403 without token"
        pass "Nginx /api/ route reachable ($warn_status)"
    else
        fail "Nginx /api/ route"
    fi
fi

echo ""
if [ "$FAILED" -eq 0 ]; then
    echo "All checks passed."
    exit 0
fi

echo "Some checks failed. Inspect logs:"
echo "  sudo tail -f /var/log/karyaradhane.err.log"
echo "  sudo supervisorctl status"
exit 1
