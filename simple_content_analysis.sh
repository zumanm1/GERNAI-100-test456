#!/usr/bin/env bash

OUTPUT_FILE="URL_CONTENT_ANALYSIS.txt"
TIMEOUT=5

echo "=== COMPREHENSIVE URL CONTENT ANALYSIS ===" > $OUTPUT_FILE
echo "Date: $(date)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Extract accessible URLs manually from our known results
declare -a ACCESSIBLE_URLS=(
    # Frontend URLs (8001)
    "http://localhost:8001/"
    "http://localhost:8001/devices"
    "http://localhost:8001/genai"
    "http://localhost:8001/dashboard"
    "http://localhost:8001/automation"
    "http://localhost:8001/device-management"
    "http://localhost:8001/chat"
    "http://localhost:8001/operations"
    "http://localhost:8001/settings"
    "http://localhost:8001/docs"
    "http://localhost:8001/openapi.json"
    "http://localhost:8001/redoc"
    
    # Backend URLs (5000)
    "http://localhost:5000/"
    "http://localhost:5000/login"
    "http://localhost:5000/devices"
    "http://localhost:5000/automation"
    "http://localhost:5000/operations"
    "http://localhost:5000/settings"
    "http://localhost:5000/chat"
    "http://localhost:5000/genai-settings"
    "http://localhost:5000/health"
    "http://localhost:5000/api/stats"
    "http://localhost:5000/api/v1/devices/"
    "http://localhost:5000/api/v1/operations/"
    "http://localhost:5000/api/v1/genai-settings/genai/llm"
    "http://localhost:5000/api/v1/genai-settings/genai/rag"
    "http://localhost:5000/api/v1/genai-settings/genai/agentic"
    "http://localhost:5000/api/v1/settings/"
    "http://localhost:5000/api/device-status-chart"
    "http://localhost:5000/api/operations-timeline"
    "http://localhost:5000/api/network-operations/status"
    "http://localhost:5000/api/chat/status"
    "http://localhost:5000/docs"
    "http://localhost:5000/openapi.json"
    "http://localhost:5000/redoc"
)

echo "Total accessible URLs to analyze: ${#ACCESSIBLE_URLS[@]}" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Function to get content type
get_content_type() {
    local url="$1"
    curl -sSL -I --max-time $TIMEOUT "$url" 2>/dev/null | grep -i "content-type" | cut -d: -f2 | xargs
}

# Function to analyze each URL
analyze_url() {
    local url="$1"
    local port route content content_type
    
    # Extract port and route
    if [[ $url == *":5000"* ]]; then
        port="5000"
        route=${url#*:5000}
    else
        port="8001"
        route=${url#*:8001}
    fi
    
    echo "--- $route (Port $port) ---" >> $OUTPUT_FILE
    echo "URL: $url" >> $OUTPUT_FILE
    
    # Get content type
    content_type=$(get_content_type "$url")
    echo "Content-Type: $content_type" >> $OUTPUT_FILE
    
    # Get content
    content=$(curl -sSL --max-time $TIMEOUT "$url" 2>/dev/null)
    echo "Content Length: ${#content} characters" >> $OUTPUT_FILE
    
    # Analyze content
    if [[ $content_type == *"json"* ]]; then
        echo "Type: JSON API Response" >> $OUTPUT_FILE
        echo "Content: ${content:0:200}..." >> $OUTPUT_FILE
    elif [[ $content_type == *"html"* ]]; then
        echo "Type: HTML Page" >> $OUTPUT_FILE
        
        # Check for specific patterns
        if echo "$content" | grep -q "swagger-ui"; then
            echo "Subtype: Swagger UI Documentation" >> $OUTPUT_FILE
        elif echo "$content" | grep -q "redoc"; then
            echo "Subtype: ReDoc Documentation" >> $OUTPUT_FILE
        elif echo "$content" | grep -q "{% \|{{"; then
            echo "Subtype: Jinja2 Template" >> $OUTPUT_FILE
        else
            echo "Subtype: Standard HTML" >> $OUTPUT_FILE
        fi
        
        # Extract title
        title=$(echo "$content" | grep -o "<title>[^<]*</title>" | head -1)
        if [[ -n $title ]]; then
            echo "Title: $title" >> $OUTPUT_FILE
        fi
        
        echo "Content Preview: ${content:0:150}..." >> $OUTPUT_FILE
    else
        echo "Type: Other" >> $OUTPUT_FILE
        echo "Content Preview: ${content:0:150}..." >> $OUTPUT_FILE
    fi
    
    echo "" >> $OUTPUT_FILE
}

echo "=== DETAILED CONTENT ANALYSIS ===" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Analyze each URL
for url in "${ACCESSIBLE_URLS[@]}"; do
    analyze_url "$url"
done

# Compare identical routes between ports
echo "=== CROSS-PORT COMPARISON ===" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

declare -a COMMON_ROUTES=("/" "/devices" "/automation" "/operations" "/chat" "/settings" "/docs" "/openapi.json" "/redoc")

for route in "${COMMON_ROUTES[@]}"; do
    echo "--- Comparing: $route ---" >> $OUTPUT_FILE
    
    url_5000="http://localhost:5000$route"
    url_8001="http://localhost:8001$route"
    
    content_5000=$(curl -sSL --max-time $TIMEOUT "$url_5000" 2>/dev/null | head -c 500)
    content_8001=$(curl -sSL --max-time $TIMEOUT "$url_8001" 2>/dev/null | head -c 500)
    
    if [[ "$content_5000" == "$content_8001" ]]; then
        echo "✅ IDENTICAL CONTENT" >> $OUTPUT_FILE
    else
        echo "❌ DIFFERENT CONTENT" >> $OUTPUT_FILE
        echo "Port 5000: ${content_5000:0:100}..." >> $OUTPUT_FILE
        echo "Port 8001: ${content_8001:0:100}..." >> $OUTPUT_FILE
    fi
    echo "" >> $OUTPUT_FILE
done

# API Endpoint specific analysis
echo "=== API ENDPOINTS SUMMARY ===" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

declare -a API_ENDPOINTS=(
    "http://localhost:5000/health"
    "http://localhost:5000/api/stats"
    "http://localhost:5000/api/v1/devices/"
    "http://localhost:5000/api/v1/operations/"
    "http://localhost:5000/api/v1/genai-settings/genai/llm"
    "http://localhost:5000/api/v1/genai-settings/genai/rag"
    "http://localhost:5000/api/v1/genai-settings/genai/agentic"
    "http://localhost:5000/api/v1/settings/"
    "http://localhost:5000/api/device-status-chart"
    "http://localhost:5000/api/operations-timeline"
    "http://localhost:5000/api/network-operations/status"
    "http://localhost:5000/api/chat/status"
)

echo "API Endpoints: ${#API_ENDPOINTS[@]}" >> $OUTPUT_FILE
for api_url in "${API_ENDPOINTS[@]}"; do
    route=${api_url#*:5000}
    content=$(curl -sSL --max-time $TIMEOUT "$api_url" 2>/dev/null)
    
    echo "$route: ${content:0:100}..." >> $OUTPUT_FILE
done

echo "" >> $OUTPUT_FILE
echo "=== SUMMARY STATISTICS ===" >> $OUTPUT_FILE
echo "Total URLs analyzed: ${#ACCESSIBLE_URLS[@]}" >> $OUTPUT_FILE
echo "API endpoints: ${#API_ENDPOINTS[@]}" >> $OUTPUT_FILE
echo "Frontend pages (8001): 12" >> $OUTPUT_FILE  
echo "Backend pages/APIs (5000): $((${#ACCESSIBLE_URLS[@]} - 12))" >> $OUTPUT_FILE

echo "Analysis complete! Check URL_CONTENT_ANALYSIS.txt for full results."
