#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration - Updated ports to avoid conflicts
GATEWAY_URL="${GATEWAY_URL:-http://localhost:8005}"
TIMEOUT=10
LOG_FILE="./logs/health-check.log"

# Ensure log directory exists
mkdir -p ./logs

# Services to check - Updated ports to avoid conflicts
SERVICES=(
    "gateway:$GATEWAY_URL"
    "chat:http://localhost:3001"
    "tools:http://localhost:8001"
    "research:http://localhost:8002"
    "mcp:http://localhost:8003"
    "rtpi:http://localhost:8004"
)

# External services to check
EXTERNAL_SERVICES=(
    "cloudflare:https://api.cloudflare.com/client/v4/user/tokens/verify"
)

echo -e "${BLUE}🏥 C3S-ATTCK Service Health Check${NC}"
echo -e "${BLUE}=================================${NC}"
echo -e "${CYAN}Timestamp: $(date)${NC}"
echo -e "${CYAN}Gateway URL: $GATEWAY_URL${NC}"
echo -e "${CYAN}Log File: $LOG_FILE${NC}"
echo ""

# Function to log messages
log_message() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" >> "$LOG_FILE"
}

# Function to check service health
check_service() {
    local name=$1
    local url=$2
    local health_endpoint="${url}/health"
    
    echo -n "Checking $name service... "
    log_message "Checking $name service at $health_endpoint"
    
    # Test basic connectivity first
    if ! curl -f -s --max-time $TIMEOUT --connect-timeout 5 "$health_endpoint" > /dev/null 2>&1; then
        echo -e "${RED}❌ Unreachable${NC}"
        log_message "ERROR: $name service unreachable at $health_endpoint"
        return 1
    fi
    
    # Get detailed health info
    local response=$(curl -f -s --max-time $TIMEOUT "$health_endpoint" 2>/dev/null)
    if [ $? -eq 0 ]; then
        # Try to parse response as JSON
        if command -v jq >/dev/null 2>&1; then
            local status=$(echo "$response" | jq -r '.status // "unknown"' 2>/dev/null)
            local version=$(echo "$response" | jq -r '.version // "unknown"' 2>/dev/null)
            echo -e "${GREEN}✅ Healthy${NC} (status: $status, version: $version)"
            log_message "SUCCESS: $name service healthy - status: $status, version: $version"
        else
            echo -e "${GREEN}✅ Healthy${NC} (response received)"
            log_message "SUCCESS: $name service healthy"
        fi
        return 0
    else
        echo -e "${RED}❌ Unhealthy${NC}"
        log_message "ERROR: $name service returned unhealthy status"
        return 1
    fi
}

# Function to check external service
check_external_service() {
    local name=$1
    local url=$2
    
    echo -n "Checking external $name... "
    log_message "Checking external $name at $url"
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" 2>/dev/null)
    
    if [ "$response_code" = "200" ]; then
        echo -e "${GREEN}✅ Accessible${NC}"
        log_message "SUCCESS: External $name accessible"
        return 0
    else
        echo -e "${YELLOW}⚠️  Response: $response_code${NC}"
        log_message "WARNING: External $name returned $response_code"
        return 1
    fi
}

# Function to check existing services (don't interfere)
check_existing_services() {
    echo -e "\n${YELLOW}📊 Existing System Services:${NC}"
    log_message "Checking existing system services"
    
    # Check if existing services are running
    echo -n "Checking existing postgres (port 5432)... "
    if netstat -tln 2>/dev/null | grep -q ":5432 " || ss -tln 2>/dev/null | grep -q ":5432 "; then
        echo -e "${GREEN}✅ Running${NC}"
        log_message "SUCCESS: Existing PostgreSQL running on port 5432"
    else
        echo -e "${RED}❌ Not running${NC}"
        log_message "WARNING: Existing PostgreSQL not running on port 5432"
    fi
    
    echo -n "Checking existing redis (port 6379)... "
    if netstat -tln 2>/dev/null | grep -q ":6379 " || ss -tln 2>/dev/null | grep -q ":6379 "; then
        echo -e "${GREEN}✅ Running${NC}"
        log_message "SUCCESS: Existing Redis running on port 6379"
    else
        echo -e "${RED}❌ Not running${NC}"
        log_message "WARNING: Existing Redis not running on port 6379"
    fi
    
    echo -n "Checking kasa_db (port 8000)... "
    if netstat -tln 2>/dev/null | grep -q ":8000 " || ss -tln 2>/dev/null | grep -q ":8000 "; then
        echo -e "${GREEN}✅ Running${NC}"
        log_message "SUCCESS: kasa_db running on port 8000"
    else
        echo -e "${YELLOW}⚠️  Not running${NC}"
        log_message "INFO: kasa_db not running on port 8000"
    fi
}

# Function to check port conflicts
check_port_conflicts() {
    echo -e "\n${YELLOW}🚨 Port Conflict Analysis:${NC}"
    log_message "Checking for port conflicts"
    
    # Check our planned ports
    local our_ports=(8005 3001 8001 8002 8003 8004)
    local conflicts=()
    
    for port in "${our_ports[@]}"; do
        if netstat -tln 2>/dev/null | grep -q ":$port " || ss -tln 2>/dev/null | grep -q ":$port "; then
            # Check if it's one of our services
            local service_name=$(get_service_name_by_port $port)
            if [ -n "$service_name" ]; then
                echo -e "Port $port: ${GREEN}✅ Our service ($service_name)${NC}"
                log_message "INFO: Port $port occupied by our service: $service_name"
            else
                conflicts+=("$port")
                echo -e "Port $port: ${RED}⚠️  Conflict detected${NC}"
                log_message "WARNING: Port conflict detected on port $port"
            fi
        else
            echo -e "Port $port: ${CYAN}🆓 Available${NC}"
            log_message "INFO: Port $port is available"
        fi
    done
    
    if [ ${#conflicts[@]} -eq 0 ]; then
        echo -e "\n${GREEN}✅ No port conflicts detected${NC}"
        log_message "SUCCESS: No port conflicts detected"
    else
        echo -e "\n${RED}⚠️  Port conflicts detected: ${conflicts[*]}${NC}"
        echo "Consider stopping conflicting services or changing ports in docker-compose.yml"
        log_message "ERROR: Port conflicts detected on ports: ${conflicts[*]}"
    fi
}

# Function to get service name by port
get_service_name_by_port() {
    local port=$1
    case $port in
        8005) echo "gateway" ;;
        3001) echo "chat" ;;
        8001) echo "tools" ;;
        8002) echo "research" ;;
        8003) echo "mcp" ;;
        8004) echo "rtpi" ;;
        *) echo "" ;;
    esac
}

# Function to check Docker status
check_docker_status() {
    echo -e "\n${YELLOW}🐳 Docker Container Status:${NC}"
    log_message "Checking Docker container status"
    
    if command -v docker >/dev/null 2>&1; then
        local our_containers=$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | grep -E "(chat-attck|tools-attck|researcher-c3s|mcp-c3s|service-gateway|rtpi-pen)" | head -10)
        
        if [ -n "$our_containers" ]; then
            echo "$our_containers"
            log_message "Docker containers found and listed"
        else
            echo -e "${YELLOW}⚠️  No C3S-ATTCK containers found${NC}"
            log_message "WARNING: No C3S-ATTCK containers found"
        fi
    else
        echo -e "${RED}❌ Docker not available${NC}"
        log_message "ERROR: Docker command not available"
    fi
}

# Function to check network connectivity
check_network_connectivity() {
    echo -e "\n${YELLOW}🌐 Network Connectivity Check:${NC}"
    log_message "Checking network connectivity"
    
    local our_service_ports=(8005 3001 8001 8002 8003 8004)
    local healthy_services=0
    
    for port in "${our_service_ports[@]}"; do
        local service_name=$(get_service_name_by_port $port)
        echo -n "Port $port ($service_name)... "
        
        if netstat -tln 2>/dev/null | grep -q ":$port " || ss -tln 2>/dev/null | grep -q ":$port "; then
            # Test if we can actually connect
            if timeout 3 bash -c "</dev/tcp/localhost/$port" 2>/dev/null; then
                echo -e "${GREEN}✅ Listening & Responsive${NC}"
                log_message "SUCCESS: Port $port ($service_name) listening and responsive"
                ((healthy_services++))
            else
                echo -e "${YELLOW}⚠️  Listening but not responsive${NC}"
                log_message "WARNING: Port $port ($service_name) listening but not responsive"
            fi
        else
            echo -e "${RED}❌ Not listening${NC}"
            log_message "ERROR: Port $port ($service_name) not listening"
        fi
    done
    
    echo -e "\nNetwork Health: $healthy_services/${#our_service_ports[@]} services responsive"
    log_message "Network health summary: $healthy_services/${#our_service_ports[@]} services responsive"
}

# Function to check service dependencies
check_service_dependencies() {
    echo -e "\n${YELLOW}🔗 Service Dependencies:${NC}"
    log_message "Checking service dependencies"
    
    # Check if required environment variables are set
    local required_vars=(
        "CLOUDFLARE_ACCOUNT_ID"
        "CLOUDFLARE_API_TOKEN"
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "REDIS_HOST"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All required environment variables are set${NC}"
        log_message "SUCCESS: All required environment variables are set"
    else
        echo -e "${YELLOW}⚠️  Missing environment variables: ${missing_vars[*]}${NC}"
        log_message "WARNING: Missing environment variables: ${missing_vars[*]}"
    fi
    
    # Check .env file
    if [ -f ".env" ]; then
        echo -e "${GREEN}✅ .env file exists${NC}"
        log_message "SUCCESS: .env file exists"
    else
        echo -e "${YELLOW}⚠️  .env file not found (using .env.example)${NC}"
        log_message "WARNING: .env file not found"
    fi
}

# Function to test API endpoints
test_api_endpoints() {
    echo -e "\n${YELLOW}🔌 API Endpoint Testing:${NC}"
    log_message "Testing API endpoints"
    
    # Test gateway discovery endpoint
    echo -n "Gateway discovery endpoint... "
    if curl -f -s --max-time $TIMEOUT "$GATEWAY_URL/discover" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Responsive${NC}"
        log_message "SUCCESS: Gateway discovery endpoint responsive"
    else
        echo -e "${RED}❌ Not responsive${NC}"
        log_message "ERROR: Gateway discovery endpoint not responsive"
    fi
    
    # Test OpenAPI endpoints
    local openapi_services=("chat:3001" "tools:8001")
    for service_port in "${openapi_services[@]}"; do
        IFS=':' read -r service port <<< "$service_port"
        echo -n "$service OpenAPI endpoint... "
        if curl -f -s --max-time $TIMEOUT "http://localhost:$port/openapi.json" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Available${NC}"
            log_message "SUCCESS: $service OpenAPI endpoint available"
        else
            echo -e "${YELLOW}⚠️  Not available${NC}"
            log_message "WARNING: $service OpenAPI endpoint not available"
        fi
    done
}

# Function to generate health report
generate_health_report() {
    local healthy_count=$1
    local total_count=$2
    
    echo -e "\n${BLUE}📋 Health Summary Report:${NC}"
    echo "================================"
    echo "Timestamp: $(date)"
    echo "Services Healthy: $healthy_count/$total_count"
    
    local health_percentage=$((healthy_count * 100 / total_count))
    
    if [ $health_percentage -ge 80 ]; then
        echo -e "Overall Status: ${GREEN}✅ HEALTHY${NC} ($health_percentage%)"
        log_message "SUMMARY: Overall system status HEALTHY ($health_percentage%)"
    elif [ $health_percentage -ge 50 ]; then
        echo -e "Overall Status: ${YELLOW}⚠️  DEGRADED${NC} ($health_percentage%)"
        log_message "SUMMARY: Overall system status DEGRADED ($health_percentage%)"
    else
        echo -e "Overall Status: ${RED}❌ CRITICAL${NC} ($health_percentage%)"
        log_message "SUMMARY: Overall system status CRITICAL ($health_percentage%)"
    fi
    
    echo ""
    echo "Recommendations:"
    if [ $healthy_count -lt $total_count ]; then
        echo "- Check unhealthy services logs: docker-compose logs [service-name]"
        echo "- Restart unhealthy services: docker-compose restart [service-name]"
        echo "- Verify environment configuration in .env file"
    fi
    echo "- View detailed logs: $LOG_FILE"
    echo "- Monitor services: docker-compose ps"
}

# Main health check execution
main() {
    log_message "=== Health check started ==="
    
    HEALTHY_COUNT=0
    TOTAL_COUNT=${#SERVICES[@]}

    echo -e "${BLUE}Service Health Status:${NC}"
    echo ""

    # Check our services
    for service in "${SERVICES[@]}"; do
        IFS=':' read -r name url <<< "$service"
        if check_service "$name" "$url"; then
            ((HEALTHY_COUNT++))
        fi
    done

    # Additional checks
    check_existing_services
    check_port_conflicts
    check_docker_status
    check_network_connectivity
    check_service_dependencies
    test_api_endpoints
    
    # Check external services if API token is available
    if [ -n "$CLOUDFLARE_API_TOKEN" ]; then
        echo -e "\n${YELLOW}🌍 External Services:${NC}"
        for service in "${EXTERNAL_SERVICES[@]}"; do
            IFS=':' read -r name url <<< "$service"
            check_external_service "$name" "$url"
        done
    fi

    # Generate final report
    generate_health_report $HEALTHY_COUNT $TOTAL_COUNT
    
    log_message "=== Health check completed ==="
    
    # Exit with appropriate code
    if [ $HEALTHY_COUNT -eq $TOTAL_COUNT ]; then
        exit 0
    else
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--help] [--quiet] [--verbose]"
        echo "  --help     Show this help message"
        echo "  --quiet    Minimal output"
        echo "  --verbose  Detailed output"
        exit 0
        ;;
    --quiet|-q)
        # Redirect stdout to log file for quiet mode
        exec 1>>"$LOG_FILE"
        ;;
    --verbose|-v)
        # Enable debug mode
        set -x
        ;;
esac

# Run main function
main "$@"
