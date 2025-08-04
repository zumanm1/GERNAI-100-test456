#!/usr/bin/env bash

# Simple route discovery and testing script
HOST="localhost"
PORTS=(5000 8001)

# Define all known routes
FRONTEND_ROUTES=(
    "/"
    "/devices"
    "/genai"
    "/dashboard"
    "/automation"
    "/device-management"
    "/chat"
    "/operations"
    "/settings"
)

BACKEND_ROUTES=(
    "/"
    "/login"
    "/devices"
    "/automation"
    "/operations"
    "/settings"
    "/chat"
    "/genai-settings"
    "/health"
    "/api/stats"
    "/api/v1/devices/"
    "/api/v1/operations/"
    "/api/v1/auth/login"
    "/api/v1/auth/register"
    "/api/v1/auth/verify"
    "/api/v1/auth/me"
    "/api/v1/dashboard/stats"
    "/api/v1/dashboard/device-status-chart"
    "/api/v1/dashboard/operations-timeline"
    "/api/v1/dashboard/recent-operations"
    "/api/v1/genai-settings/genai/llm"
    "/api/v1/genai-settings/genai/rag"
    "/api/v1/genai-settings/genai/agentic"
    "/api/v1/settings/"
    "/api/v1/chat/conversations"
    "/api/v1/automation/playbooks"
    "/api/v1/users/"
    "/api/v1/actions/"
    "/api/v1/genai/"
    "/api/device-status-chart"
    "/api/operations-timeline"
    "/api/network-operations/status"
    "/api/chat/status"
)

echo "=== COMPREHENSIVE URL TESTING FOR NETWORK AUTOMATION APP ===" > URL_URL-ALL.txt
echo "Date: $(date)" >> URL_URL-ALL.txt
echo "" >> URL_URL-ALL.txt

test_route() {
    local url="$1"
    local port="$2"
    local route="$3"
    
    http_code=$(curl -sSL -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        if [[ "$http_code" =~ ^2|3 ]]; then
            status="✅ ACCESSIBLE (HTTP $http_code)"
        else
            status="❌ INACCESSIBLE (HTTP $http_code)"
        fi
    else
        status="⚠️ ERROR/TIMEOUT"
    fi
    
    echo "Route: $route -> URL: $url -> $status"
    echo "Route: $route -> URL: $url -> $status" >> URL_URL-ALL.txt
    
    # Get content preview for successful routes
    if [[ "$http_code" =~ ^2 ]]; then
        content=$(curl -sSL --max-time 3 "$url" 2>/dev/null | head -c 500)
        if [[ -n "$content" ]]; then
            echo "  Content Preview: ${content:0:100}..." >> URL_URL-ALL.txt
        fi
    fi
}

echo "Testing Frontend Routes (Port 8001)..."
echo "" >> URL_URL-ALL.txt
echo "=== FRONTEND ROUTES (Port 8001) ===" >> URL_URL-ALL.txt
for route in "${FRONTEND_ROUTES[@]}"; do
    url="http://$HOST:8001$route"
    test_route "$url" "8001" "$route"
done

echo ""
echo "Testing Backend Routes (Port 5000)..."
echo "" >> URL_URL-ALL.txt
echo "=== BACKEND ROUTES (Port 5000) ===" >> URL_URL-ALL.txt
for route in "${BACKEND_ROUTES[@]}"; do
    url="http://$HOST:5000$route"
    test_route "$url" "5000" "$route"
done

# Test some additional common API endpoints
echo ""
echo "Testing additional API endpoints..."
echo "" >> URL_URL-ALL.txt
echo "=== ADDITIONAL API ENDPOINTS ===" >> URL_URL-ALL.txt

ADDITIONAL_ENDPOINTS=(
    "/docs"
    "/openapi.json"
    "/redoc"
    "/api/docs"
    "/swagger"
    "/api"
    "/api/v1"
    "/api/v2"
    "/status"
    "/ping"
    "/version"
    "/info"
)

for port in "${PORTS[@]}"; do
    echo "Port $port additional endpoints:" >> URL_URL-ALL.txt
    for endpoint in "${ADDITIONAL_ENDPOINTS[@]}"; do
        url="http://$HOST:$port$endpoint"
        test_route "$url" "$port" "$endpoint"
    done
    echo "" >> URL_URL-ALL.txt
done

echo ""
echo "=== SUMMARY ===" >> URL_URL-ALL.txt
echo "Total routes tested: $((${#FRONTEND_ROUTES[@]} + ${#BACKEND_ROUTES[@]} + ${#ADDITIONAL_ENDPOINTS[@]} * 2))" >> URL_URL-ALL.txt
echo "Results saved to: URL_URL-ALL.txt"
echo "Route outputs directory created for detailed responses"

echo ""
echo "Done! Results saved to URL_URL-ALL.txt"
