#!/usr/bin/env bash

# ---------- CONFIG ----------
HOST="localhost"
PORTS=(5000 8001)
INITIAL_ROUTES=("/" "/login" "/chat" "/dashboard" "/operations" "/devices" "/automation" "/settings" "/genai" "/genai-settings" "/device-management" "/health")
# Heuristic API roots to probe for discovering further endpoints
API_ROOTS=("/api" "/api/v1" "/api/v2" "/api/stats" "/api/device-status-chart" "/api/operations-timeline" "/api/network-operations/status" "/api/chat/status")
TIMEOUT=5  # seconds
OUTPUT_DIR="./route_outputs"
MAX_CRAWL_PER_PORT=100    # cap total distinct routes per port to avoid runaway
MAX_DEPTH=2               # how deep to follow internal links
# ----------------------------

# Colors for visibility (optional)
RED=$(tput setaf 1 2>/dev/null || echo "")
GREEN=$(tput setaf 2 2>/dev/null || echo "")
YELLOW=$(tput setaf 3 2>/dev/null || echo "")
BLUE=$(tput setaf 4 2>/dev/null || echo "")
RESET=$(tput sgr0 2>/dev/null || echo "")

mkdir -p "$OUTPUT_DIR"

normalize_route() {
  local r="$1"
  # ensure starts with /
  [[ "$r" != /* ]] && r="/$r"
  # strip query/fragments for dedup key
  r="${r%%\?*}"
  r="${r%%\#*}"
  echo "$r"
}

fetch_and_save() {
  local url="$1"
  local port="$2"
  local route="$3"

  safe_route=$(echo "$route" | tr "/" "_" | sed 's/^_//')
  out_file="${OUTPUT_DIR}/${port}${safe_route}.txt"

  # accessibility/status
  http_code=$(curl -sSL -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url")
  if [[ "$?" -ne 0 ]]; then
    echo -e "Route: ${route} -> URL: ${url} ... ${YELLOW}ERROR (no response or timeout)${RESET}"
    return 1
  fi

  if [[ "$http_code" =~ ^2|3 ]]; then
    echo -e "Route: ${route} -> URL: ${url} ... ${GREEN}Accessible (HTTP ${http_code})${RESET}"
  else
    echo -e "Route: ${route} -> URL: ${url} ... ${RED}Inaccessible (HTTP ${http_code})${RESET}"
  fi

  # fetch body (limited)
  curl -sSL --max-time "$TIMEOUT" "$url" | head -c 512000 > "$out_file"

  echo "  → Saved body to ${out_file}, first 20 lines:"
  echo "-----"
  head -n 20 "$out_file"
  echo "-----"
  echo
  return 0
}

# Simple crawler per port: BFS up to depth
crawl_port() {
  local port=$1
  declare -A seen=()
  declare -a queue=()

  # start with initial + API roots
  for r in "${INITIAL_ROUTES[@]}" "${API_ROOTS[@]}"; do
    nr=$(normalize_route "$r")
    seen["$nr"]=0  # depth 0
    queue+=("$nr")
  done

  echo "${BLUE}== Port ${port} ==${RESET}"
  idx=0
  while [[ $idx -lt ${#queue[@]} ]]; do
    route=${queue[$idx]}
    depth=${seen["$route"]}
    ((idx++))

    # stop if too many
    if [[ "${#seen[@]}" -gt $MAX_CRAWL_PER_PORT ]]; then
      echo "${YELLOW}Reached max distinct routes (${MAX_CRAWL_PER_PORT}) on port ${port}, stopping further discovery.${RESET}"
      break
    fi

    url="http://${HOST}:${port}${route}"
    fetch_and_save "$url" "$port" "$route"

    # only crawl for HTML or JSON containing embedded URLs
    content=$(curl -sSL --max-time "$TIMEOUT" "$url")
    # extract same-host internal links from HTML href/src
    if [[ $depth -lt $MAX_DEPTH ]]; then
      # find href/src values
      # crude parsing: look for href="...", src="..."
      while IFS= read -r link; do
        # strip quotes
        link="${link%\"}"
        link="${link#\"}"
        # if absolute with host, extract path; if relative, take as is
        if [[ "$link" =~ ^https?:// ]]; then
          # only keep if host matches
          hostpart=$(echo "$link" | awk -F/ '{print $3}')
          if [[ "$hostpart" != "${HOST}:${port}" && "$hostpart" != "${HOST}" ]]; then
            continue
          fi
          # extract path + query
          path="/$(echo "$link" | cut -d/ -f4-)"
          path="/${path#"${path%%[!/]}" }"  # normalize multiple slashes
        else
          # relative
          if [[ "$link" == /* ]]; then
            path="$link"
          else
            # append to current route's directory
            base=$(dirname "$route")
            path="$base/$link"
          fi
        fi
        norm=$(normalize_route "$path")
        if [[ -z "${seen[$norm]}" ]]; then
          seen["$norm"]=$((depth + 1))
          queue+=("$norm")
        fi
      done < <(echo "$content" | grep -oiE 'href="[^"]+"|src="[^"]+"' | sed -E 's/^(href|src)=//' )
      # also if JSON-looking, try to extract embedded same-host URLs
      if echo "$content" | grep -qiE '"https?://'; then
        while IFS= read -r jlink; do
          # extract URL
          urlfound=$(echo "$jlink" | grep -oE 'https?://[^","]+' | head -1)
          if [[ -z "$urlfound" ]]; then continue; fi
          if [[ "$urlfound" =~ ^https?:// ]]; then
            # only same host/port
            if echo "$urlfound" | grep -q "${HOST}:${port}"; then
              path="${urlfound#*${HOST}:${port}}"
              norm=$(normalize_route "$path")
              if [[ -z "${seen[$norm]}" ]]; then
                seen["$norm"]=$((depth + 1))
                queue+=("$norm")
              fi
            fi
          fi
        done < <(echo "$content")
      fi
    fi
  done
}

echo "Starting route + API discovery checks on ports: ${PORTS[*]}"
echo

for port in "${PORTS[@]}"; do
  crawl_port "$port"
done

echo "Done. Full bodies saved under ${OUTPUT_DIR}/"
