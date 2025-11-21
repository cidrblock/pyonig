#!/usr/bin/env bash
# Deployment Script - Production Infrastructure
# Purpose: Deploy application to Kubernetes cluster with zero downtime

set -euo pipefail

# Configuration
readonly CLUSTER_NAME="production-us-east-1"
readonly NAMESPACE="production"
readonly APP_NAME="web-api"
readonly IMAGE_TAG="${1:-latest}"
readonly REPLICAS="${REPLICAS:-3}"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    for cmd in kubectl docker helm; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "Required command not found: $cmd"
            exit 1
        fi
    done
    
    log_success "All prerequisites satisfied"
}

# Verify cluster connectivity
verify_cluster() {
    log_info "Verifying cluster connectivity..."
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    local current_context
    current_context=$(kubectl config current-context)
    log_info "Connected to cluster: $current_context"
}

# Build and push Docker image
build_image() {
    local image_name="$1"
    log_info "Building Docker image: $image_name"
    
    docker build -t "$image_name" . || {
        log_error "Failed to build Docker image"
        return 1
    }
    
    log_info "Pushing image to registry..."
    docker push "$image_name" || {
        log_error "Failed to push Docker image"
        return 1
    }
    
    log_success "Image built and pushed: $image_name"
}

# Deploy application
deploy_app() {
    log_info "Deploying $APP_NAME to $NAMESPACE namespace..."
    
    # Update deployment with new image
    kubectl set image "deployment/$APP_NAME" \
        "$APP_NAME=registry.example.com/$APP_NAME:$IMAGE_TAG" \
        --namespace="$NAMESPACE" \
        --record
    
    # Wait for rollout to complete
    log_info "Waiting for rollout to complete..."
    if kubectl rollout status "deployment/$APP_NAME" \
        --namespace="$NAMESPACE" \
        --timeout=5m; then
        log_success "Deployment successful!"
    else
        log_error "Deployment failed!"
        log_warning "Rolling back..."
        kubectl rollout undo "deployment/$APP_NAME" --namespace="$NAMESPACE"
        exit 1
    fi
}

# Health check
health_check() {
    log_info "Running health checks..."
    
    local endpoint="https://api.example.com/health"
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$endpoint" > /dev/null; then
            log_success "Health check passed!"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Main deployment flow
main() {
    log_info "Starting deployment process for $APP_NAME:$IMAGE_TAG"
    
    check_prerequisites
    verify_cluster
    
    local image_name="registry.example.com/$APP_NAME:$IMAGE_TAG"
    build_image "$image_name"
    
    deploy_app
    health_check
    
    log_success "Deployment completed successfully! 🚀"
}

# Run main function
main "$@"

