#!/usr/bin/env bash

# Comprehensive URL Content Analysis Script
HOST="localhost"
PORTS=(5000 8001)
OUTPUT_FILE="URL_CONTENT_ANALYSIS.txt"
TIMEOUT=5

echo "=== COMPREHENSIVE URL CONTENT ANALYSIS ===" > $OUTPUT_FILE
echo "Date: $(date)" >> $OUTPUT_FILE
echo "Analyzing all 66 routes discovered in URL_URL-ALL.txt" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Extract all accessible URLs from the original file
grep "✅ ACCESSIBLE" URL_URL-ALL.txt | grep -o "http://[^)]*" > accessible_urls.tmp

echo "=== ACCESSIBLE ROUTES SUMMARY ===" >> $OUTPUT_FILE
echo "Total accessible routes: $(wc -l < accessible_urls.tmp)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Function to analyze content type and extract key information
analyze_content() {
    local url="$1"
    local port="$2"
    local route="$3"
    
    echo "--- Analyzing: $route on port $port ---" >> $OUTPUT_FILE
    echo "URL: $url" >> $OUTPUT_FILE
    
    # Get HTTP headers
    headers=$(curl -sSL -I --max-time $TIMEOUT "$url" 2>/dev/null)
    content_type=$(echo "$headers" | grep -i "content-type" | cut -d: -f2 | xargs)
    
    echo "Content-Type: $content_type" >> $OUTPUT_FILE
    
    # Get content and analyze
    content=$(curl -sSL --max-time $TIMEOUT "$url" 2>/dev/null)
    content_length=${#content}
    
    echo "Content Length: $content_length characters" >> $OUTPUT_FILE
    
    # Determine content type and extract relevant information
    if [[ "$content_type" == *"json"* ]]; then
        echo "Type: JSON API Response" >> $OUTPUT_FILE
        echo "JSON Preview:" >> $OUTPUT_FILE
        echo "$content" | head -c 500 | jq '.' 2>/dev/null || echo "$content" | head -c 500 >> $OUTPUT_FILE
    elif [[ "$content_type" == *"html"* ]]; then
        echo "Type: HTML Page" >> $OUTPUT_FILE
        
        # Extract title
        title=$(echo "$content" | grep -o "<title>[^<]*</title>" | head -1)
        if [[ -n "$title" ]]; then
            echo "Page Title: $title" >> $OUTPUT_FILE
        fi
        
        # Check if it's FastAPI docs
        if echo "$content" | grep -q "swagger-ui\|openapi"; then
            echo "Subtype: FastAPI Documentation (Swagger UI)" >> $OUTPUT_FILE
        # Check if it's ReDoc
        elif echo "$content" | grep -q "redoc"; then
            echo "Subtype: FastAPI Documentation (ReDoc)" >> $OUTPUT_FILE
        # Check if it's a Jinja2 template
        elif echo "$content" | grep -q "{% \|{{ "; then
            echo "Subtype: Jinja2 Template" >> $OUTPUT_FILE
            echo "Template blocks found:" >> $OUTPUT_FILE
            echo "$content" | grep -o "{% [^%]*%}" | head -3 >> $OUTPUT_FILE
        else
            echo "Subtype: Regular HTML" >> $OUTPUT_FILE
        fi
        
        # Extract first few lines of body content
        echo "HTML Preview (first 200 chars):" >> $OUTPUT_FILE
        echo "$content" | head -c 200 >> $OUTPUT_FILE
    else
        echo "Type: Other/Unknown" >> $OUTPUT_FILE
        echo "Content Preview (first 200 chars):" >> $OUTPUT_FILE
        echo "$content" | head -c 200 >> $OUTPUT_FILE
    fi
    
    echo "" >> $OUTPUT_FILE
}

# Analyze each accessible URL
echo "=== DETAILED CONTENT ANALYSIS ===" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

while read -r url; do
    # Extract port and route from URL
    port=$(echo "$url" | grep -o ':[0-9]*' | cut -d: -f2)
    route=$(echo "$url" | sed "s|http://localhost:$port||")
    
    analyze_content "$url" "$port" "$route"
done < accessible_urls.tmp

# Compare similar routes between ports
echo "=== CROSS-PORT ROUTE COMPARISON ===" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Find routes that exist on both ports
for route in "/" "/devices" "/automation" "/operations" "/chat" "/settings" "/docs" "/openapi.json" "/redoc"; do
    echo "--- Comparing route: $route ---" >> $OUTPUT_FILE
    
    # Check if exists on both ports
    url_5000="http://localhost:5000$route"
    url_8001="http://localhost:8001$route"
    
    if grep -q "$url_5000" accessible_urls.tmp && grep -q "$url_8001" accessible_urls.tmp; then
        echo "Available on both ports - comparing content..." >> $OUTPUT_FILE
        
        content_5000=$(curl -sSL --max-time $TIMEOUT "$url_5000" 2>/dev/null | head -c 1000)
        content_8001=$(curl -sSL --max-time $TIMEOUT "$url_8001" 2>/dev/null | head -c 1000)
        
        if [[ "$content_5000" == "$content_8001" ]]; then
            echo "✅ IDENTICAL CONTENT" >> $OUTPUT_FILE
        else
            echo "❌ DIFFERENT CONTENT" >> $OUTPUT_FILE
            echo "Port 5000 sample: ${content_5000:0:100}..." >> $OUTPUT_FILE
            echo "Port 8001 sample: ${content_8001:0:100}..." >> $OUTPUT_FILE
        fi
    else
        echo "Not available on both ports" >> $OUTPUT_FILE
    fi
    echo "" >> $OUTPUT_FILE
done

# API endpoint analysis
echo "=== API ENDPOINTS ANALYSIS ===" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Analyze API endpoints specifically
grep "✅ ACCESSIBLE" URL_URL-ALL.txt | grep "/api/" | grep -o "http://[^)]*" > api_urls.tmp

echo "API Endpoints Found: $(wc -l < api_urls.tmp)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

while read -r url; do
    route=$(echo "$url" | sed 's|http://localhost:[0-9]*||')
    echo "API: $route" >> $OUTPUT_FILE
    
    content=$(curl -sSL --max-time $TIMEOUT "$url" 2>/dev/null)
    
    # Check if it's JSON
    if echo "$content" | jq '.' >/dev/null 2>&1; then
        echo "  Type: Valid JSON" >> $OUTPUT_FILE
        echo "  Sample: $(echo "$content" | head -c 100)..." >> $OUTPUT_FILE
    else
        echo "  Type: Non-JSON or Error" >> $OUTPUT_FILE
        echo "  Content: $(echo "$content" | head -c 100)..." >> $OUTPUT_FILE
    fi
    echo "" >> $OUTPUT_FILE
done < api_urls.tmp

# Statistics
echo "=== CONTENT STATISTICS ===" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

total_urls=$(wc -l < accessible_urls.tmp)
json_endpoints=$(while read url; do curl -sSL --max-time $TIMEOUT "$url" 2>/dev/null | head -c 10; done < accessible_urls.tmp | grep -c "{")
html_endpoints=$(while read url; do curl -sSL --max-time $TIMEOUT "$url" 2>/dev/null | head -c 50; done < accessible_urls.tmp | grep -c "<!DOCTYPE\|<html")

echo "Total accessible URLs: $total_urls" >> $OUTPUT_FILE
echo "JSON endpoints: $json_endpoints" >> $OUTPUT_FILE
echo "HTML endpoints: $html_endpoints" >> $OUTPUT_FILE
echo "Other/Mixed: $((total_urls - json_endpoints - html_endpoints))" >> $OUTPUT_FILE

# Clean up temp files
rm -f accessible_urls.tmp api_urls.tmp

echo "" >> $OUTPUT_FILE
echo "Analysis complete! Results saved to: $OUTPUT_FILE" >> $OUTPUT_FILE

echo "Analysis complete! Results saved to: $OUTPUT_FILE"
