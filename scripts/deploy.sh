#!/bin/bash

# C3S-ATTCK Service Deployment Script
# Comprehensive deployment automation for the entire service ecosystem

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
LOG_FILE="$PROJECT_ROOT/logs/deployment.log"
ENV_FILE="$PROJECT_ROOT/.env"

# Deployment settings
DEPLOYMENT_MODE="${DEPLOYMENT_MODE:-production}"
SKIP_DEPENDENCIES="${SKIP_DEPENDENCIES:-false}"
SKIP_TOKENS="${SKIP_TOKENS:-false}"
SKIP_TERRAFORM="${SKIP_TERRAFORM:-false}"
FORCE_REBUILD="${FORCE_REBUILD:-false}"

# Ensure logs directory exists
mkdir -p "$PROJECT_ROOT/logs"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Print step with styling
print_step() {
    local step_num="$1"
    local step_desc="$2"
    echo -e "\n${BLUE}=== Step $step_num: $step_desc ===${NC}"
    log "INFO" "Step $step_num: $step_desc"
}

# Print success message
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS" "$1"
}

# Print warning message
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING" "$1"
}

# Print error message
print_error() {
    echo -e "${RED}❌ $1${NC}"
    log "ERROR" "$1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
check_dependencies() {
    print_step "1" "Checking System Dependencies"
    
    local missing_deps=()
    local required_commands=("docker" "curl" "jq" "python3")
    
    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            missing_deps+=("$cmd")
        else
            print_success "$cmd is available"
        fi
    done
    
    # Check for Docker Compose (V2 or V1)
    if docker compose version >/dev/null 2>&1; then
        print_success "docker compose is available (V2)"
    elif command_exists "docker-compose"; then
        print_success "docker-compose is available (V1)"
    else
        missing_deps+=("docker-compose")
    fi
    
    # Check optional commands
    local optional_commands=("terraform" "go" "netstat" "ss")
    for cmd in "${optional_commands[@]}"; do
        if command_exists "$cmd"; then
            print_success "$cmd is available (optional)"
        else
            print_warning "$cmd is not available (optional)"
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        echo -e "\nPlease install missing dependencies:"
        for dep in "${missing_deps[@]}"; do
            case "$dep" in
                docker)
                    echo "  - Docker: https://docs.docker.com/get-docker/"
                    ;;
                docker-compose)
                    echo "  - Docker Compose: https://docs.docker.com/compose/install/"
                    ;;
                jq)
                    echo "  - jq: sudo apt-get install jq (Ubuntu/Debian) or brew install jq (macOS)"
                    ;;
                python3)
                    echo "  - Python 3: https://www.python.org/downloads/"
                    ;;
                *)
                    echo "  - $dep: Please install using your package manager"
                    ;;
            esac
        done
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    
    print_success "All required dependencies are available"
}

# Check port availability
check_port_availability() {
    print_step "2" "Checking Port Availability"
    
    local conflicting_ports=()
    local our_ports=(8005 3001 8001 8002 8003 8004)
    
    for port in "${our_ports[@]}"; do
        if netstat -tln 2>/dev/null | grep -q ":$port " || ss -tln 2>/dev/null | grep -q ":$port "; then
            # Check if it's already one of our services
            local container_name=$(docker ps --format "table {{.Names}}\t{{.Ports}}" 2>/dev/null | grep ":$port->" | awk '{print $1}' | head -1)
            if [[ "$container_name" =~ (chat-attck|tools-attck|researcher-c3s|mcp-c3s|service-gateway|rtpi-pen) ]]; then
                print_warning "Port $port is used by our service ($container_name)"
            else
                conflicting_ports+=("$port")
                print_warning "Port $port is occupied by external service"
            fi
        else
            print_success "Port $port is available"
        fi
    done
    
    if [ ${#conflicting_ports[@]} -ne 0 ]; then
        print_warning "Port conflicts detected: ${conflicting_ports[*]}"
        echo "These ports are already in use. Continue anyway? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_error "Deployment cancelled due to port conflicts"
            exit 1
        fi
    fi
    
    print_success "Port availability checked"
}

# Setup environment configuration
setup_environment() {
    print_step "3" "Setting Up Environment Configuration"
    
    # Create .env from .env.example if it doesn't exist
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$PROJECT_ROOT/offsec-team/.env.example" ]; then
            cp "$PROJECT_ROOT/offsec-team/.env.example" "$ENV_FILE"
            print_success "Created .env from .env.example"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
    
    # Set proper permissions
    chmod 600 "$ENV_FILE"
    
    # Load environment variables
    set -a  # Automatically export variables
    source "$ENV_FILE"
    set +a
    
    # Verify critical environment variables
    local required_vars=(
        "CLOUDFLARE_ACCOUNT_ID"
        "CLOUDFLARE_API_TOKEN" 
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "POSTGRES_DB"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_warning "Missing environment variables: ${missing_vars[*]}"
        print_warning "Please update $ENV_FILE with proper values"
    else
        print_success "All required environment variables are set"
    fi
    
    # Create necessary directories
    local dirs=("logs" "offsec-team/configs" "traefik")
    for dir in "${dirs[@]}"; do
        mkdir -p "$PROJECT_ROOT/$dir"
        print_success "Created directory: $dir"
    done
}

# Generate service tokens
generate_service_tokens() {
    if [ "$SKIP_TOKENS" = "true" ]; then
        print_warning "Skipping token generation (SKIP_TOKENS=true)"
        return 0
    fi
    
    print_step "4" "Generating Service Authentication Tokens"
    
    cd "$PROJECT_ROOT/offsec-team/scripts"
    
    # Check if tokens already exist
    if [ -f "../configs/service-tokens.json" ]; then
        print_warning "Service tokens already exist. Regenerate? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_success "Using existing service tokens"
            return 0
        fi
    fi
    
    # Generate tokens
    if python3 generate-tokens.py --terraform; then
        print_success "Service tokens generated successfully"
        
        # Reload environment to get new tokens
        set -a
        source "$ENV_FILE"
        set +a
    else
        print_error "Failed to generate service tokens"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
}

# Build Docker images
build_docker_images() {
    print_step "5" "Building Docker Images"
    
    local build_args=""
    if [ "$FORCE_REBUILD" = "true" ]; then
        build_args="--no-cache"
    fi
    
    # Build images in parallel where possible
    echo -e "${CYAN}Building service images...${NC}"
    
    # Use docker compose (V2) or fallback to docker-compose (V1)
    if docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    if $COMPOSE_CMD build $build_args; then
        print_success "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
}

# Deploy Terraform infrastructure
deploy_terraform() {
    if [ "$SKIP_TERRAFORM" = "true" ]; then
        print_warning "Skipping Terraform deployment (SKIP_TERRAFORM=true)"
        return 0
    fi
    
    print_step "6" "Deploying Cloudflare Infrastructure"
    
    if ! command_exists terraform; then
        print_warning "Terraform not found. Skipping infrastructure deployment."
        print_warning "Install Terraform to deploy Cloudflare Access configuration."
        return 0
    fi
    
    cd "$PROJECT_ROOT/offsec-team/infrastructure"
    
    # Initialize Terraform
    if terraform init; then
        print_success "Terraform initialized"
    else
        print_error "Failed to initialize Terraform"
        exit 1
    fi
    
    # Validate configuration
    if terraform validate; then
        print_success "Terraform configuration is valid"
    else
        print_error "Terraform configuration is invalid"
        exit 1
    fi
    
    # Plan deployment
    echo -e "${CYAN}Planning Terraform deployment...${NC}"
    if terraform plan -out=deployment.tfplan; then
        print_success "Terraform plan created"
        
        # Apply if approved
        echo "Apply Terraform plan? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            if terraform apply deployment.tfplan; then
                print_success "Terraform infrastructure deployed"
            else
                print_error "Failed to deploy Terraform infrastructure"
                exit 1
            fi
        else
            print_warning "Terraform deployment skipped"
        fi
    else
        print_error "Failed to create Terraform plan"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
}

# Start services
start_services() {
    print_step "7" "Starting Services"
    
    # Use docker compose (V2) or fallback to docker-compose (V1)
    if docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    # Stop existing services if running
    echo -e "${CYAN}Stopping existing services...${NC}"
    $COMPOSE_CMD down --remove-orphans || true
    
    # Start services
    echo -e "${CYAN}Starting services in background...${NC}"
    if $COMPOSE_CMD up -d; then
        print_success "Services started successfully"
    else
        print_error "Failed to start services"
        exit 1
    fi
    
    # Wait for services to be ready
    echo -e "${CYAN}Waiting for services to be ready...${NC}"
    sleep 30
    
    # Check service health
    local max_attempts=12
    local attempt=1
    local healthy_services=0
    local total_services=6
    
    while [ $attempt -le $max_attempts ]; do
        echo "Health check attempt $attempt/$max_attempts..."
        
        if "$PROJECT_ROOT/offsec-team/scripts/health-check.sh" --quiet; then
            healthy_services=$total_services
            break
        fi
        
        sleep 15
        ((attempt++))
    done
    
    if [ $healthy_services -eq $total_services ]; then
        print_success "All services are healthy"
    else
        print_warning "Some services may not be fully ready yet"
        print_warning "Run './offsec-team/scripts/health-check.sh' to check status"
    fi
}

# Verify deployment
verify_deployment() {
    print_step "8" "Verifying Deployment"
    
    echo -e "${CYAN}Running comprehensive health checks...${NC}"
    
    if "$PROJECT_ROOT/offsec-team/scripts/health-check.sh"; then
        print_success "All health checks passed"
    else
        print_warning "Some health checks failed. Check logs for details."
    fi
    
    # Test key endpoints
    echo -e "\n${CYAN}Testing key endpoints:${NC}"
    
    local endpoints=(
        "Gateway:http://localhost:8005/health"
        "Chat Service:http://localhost:3001/health"
        "Tools Service:http://localhost:8001/health"
        "Research Service:http://localhost:8002/health"
        "MCP Service:http://localhost:8003/health"
        "RTPI Service:http://localhost:8004/health"
    )
    
    local successful_tests=0
    for endpoint in "${endpoints[@]}"; do
        IFS=':' read -r name url <<< "$endpoint"
        echo -n "Testing $name... "
        
        if curl -f -s --max-time 10 "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ OK${NC}"
            ((successful_tests++))
        else
            echo -e "${RED}❌ Failed${NC}"
        fi
    done
    
    echo -e "\nEndpoint tests: $successful_tests/${#endpoints[@]} passed"
    
    # Display service URLs
    echo -e "\n${BLUE}🌐 Service URLs:${NC}"
    echo "  - Gateway:          http://localhost:8005"
    echo "  - Chat (OpenWebUI): http://localhost:3001"
    echo "  - Tools:            http://localhost:8001"
    echo "  - Research:         http://localhost:8002"
    echo "  - MCP:              http://localhost:8003"  
    echo "  - RTPI:             http://localhost:8004"
    echo "  - Traefik:          http://localhost:8091"
    echo "  - Prometheus:       http://localhost:9090"
    
    if [ -n "${CLOUDFLARE_API_TOKEN:-}" ] && [ "$SKIP_TERRAFORM" != "true" ]; then
        echo -e "\n${BLUE}🌍 Production URLs (after DNS propagation):${NC}"
        echo "  - Chat:      https://chat.attck.nexus"
        echo "  - Tools:     https://tools.attck.nexus"
        echo "  - Research:  https://researcher.c3s.nexus"
        echo "  - MCP:       https://mcp.c3s.nexus"
        echo "  - RTPI:      https://rtpi.attck.nexus"
    fi
}

# Cleanup function
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        print_error "Deployment failed with exit code $exit_code"
        echo -e "\n${YELLOW}Troubleshooting:${NC}"
        echo "1. Check logs: $LOG_FILE"
        echo "2. Check service logs: docker-compose logs"
        echo "3. Verify environment: cat $ENV_FILE"
        echo "4. Check health: ./offsec-team/scripts/health-check.sh"
        echo "5. Manual cleanup: docker-compose down --remove-orphans"
    fi
}

# Main deployment function
main() {
    trap cleanup EXIT
    
    echo -e "${BLUE}"
    echo "  ______  _____ _____        _   _______ _______  _____ _  __ "
    echo " / ____ \\|__   |__   | _   _ |  \\__   __|__   __ |__   | ||_/ "
    echo "| |    | |  |  |  |  |_| |_| |   | |     |  |  | |  |  | / /  "
    echo "| |____| |  |  |  |         |   | |     |  |  | |  |  |   \\  "
    echo " \\______/|___|__|___|       |___|____|  |__|__|__|___|__|_|\\_\\ "
    echo ""
    echo "Service Deployment Script v1.0"
    echo "Comprehensive deployment automation for C3S-ATTCK services"
    echo -e "${NC}"
    
    log "INFO" "=== Deployment started ==="
    log "INFO" "Mode: $DEPLOYMENT_MODE"
    log "INFO" "Skip dependencies: $SKIP_DEPENDENCIES"
    log "INFO" "Skip tokens: $SKIP_TOKENS"
    log "INFO" "Skip terraform: $SKIP_TERRAFORM"
    log "INFO" "Force rebuild: $FORCE_REBUILD"
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Run deployment steps
    if [ "$SKIP_DEPENDENCIES" != "true" ]; then
        check_dependencies
        check_port_availability
    fi
    
    setup_environment
    generate_service_tokens
    build_docker_images
    deploy_terraform
    start_services
    verify_deployment
    
    # Success message
    echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "\n${BLUE}📋 Next Steps:${NC}"
    echo "1. Configure OpenWebUI to use: http://localhost:8001/openapi.json"
    echo "2. Access chat interface: http://localhost:3001"
    echo "3. Monitor services: docker-compose ps"
    echo "4. Check logs: docker-compose logs [service-name]"
    echo "5. Health monitoring: ./offsec-team/scripts/health-check.sh"
    
    if [ "$SKIP_TERRAFORM" != "true" ] && command_exists terraform; then
        echo "6. DNS propagation may take 5-15 minutes for production URLs"
        echo "7. Configure Cloudflare Access policies as needed"
    fi
    
    log "INFO" "=== Deployment completed successfully ==="
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "C3S-ATTCK Deployment Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help                 Show this help message"
        echo "  --skip-deps           Skip dependency checks"
        echo "  --skip-tokens         Skip token generation"
        echo "  --skip-terraform      Skip Terraform deployment"
        echo "  --force-rebuild       Force rebuild of Docker images"
        echo "  --production          Production deployment mode (default)"
        echo "  --development         Development deployment mode"
        echo ""
        echo "Environment Variables:"
        echo "  SKIP_DEPENDENCIES     Skip dependency checks (true/false)"
        echo "  SKIP_TOKENS          Skip token generation (true/false)"  
        echo "  SKIP_TERRAFORM       Skip Terraform deployment (true/false)"
        echo "  FORCE_REBUILD        Force rebuild of images (true/false)"
        echo "  DEPLOYMENT_MODE      Deployment mode (production/development)"
        echo ""
        exit 0
        ;;
    --skip-deps)
        SKIP_DEPENDENCIES="true"
        ;;
    --skip-tokens)
        SKIP_TOKENS="true"
        ;;
    --skip-terraform)
        SKIP_TERRAFORM="true"
        ;;
    --force-rebuild)
        FORCE_REBUILD="true"
        ;;
    --production)
        DEPLOYMENT_MODE="production"
        ;;
    --development)
        DEPLOYMENT_MODE="development"
        ;;
esac

# Run main deployment
main "$@"
