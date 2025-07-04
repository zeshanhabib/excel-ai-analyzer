#!/bin/bash

# Excel AI Analyzer - Docker Deployment Script

set -e

echo "🐳 Excel AI Analyzer - Docker Deployment"
echo "========================================"

# Function to check if Docker is running
check_docker() {
    if ! docker info &>/dev/null; then
        echo "❌ Docker is not running. Please start Docker first."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to create directories
create_directories() {
    echo "📁 Creating directories..."
    mkdir -p data logs
    echo "✅ Directories created"
}

# Function to build and start services
start_services() {
    echo "🔨 Building and starting services..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "⚠️  .env file not found. Copying from .env.docker template..."
        cp .env.docker .env
        echo "📝 Please edit .env file with your API keys before running again"
        echo "   At minimum, set your OPENAI_API_KEY"
        exit 1
    fi
    
    # Build and start the main service
    docker-compose up --build -d excel-ai-analyzer
    
    echo "✅ Services started successfully!"
}

# Function to start with reverse proxy
start_with_proxy() {
    echo "🔨 Building and starting services with reverse proxy..."
    docker-compose --profile proxy up --build -d
    echo "✅ Services with proxy started successfully!"
}

# Function to show status
show_status() {
    echo "📊 Service Status:"
    docker-compose ps
    
    echo ""
    echo "🌐 Access URLs:"
    echo "  📊 Excel AI Analyzer: http://localhost:8501"
    
    if docker-compose ps | grep -q traefik; then
        echo "  🔄 Traefik Dashboard: http://localhost:8080"
        echo "  🌍 Custom Domain: http://excel-ai.localhost (if configured)"
    fi
}

# Function to show logs
show_logs() {
    echo "📋 Application Logs:"
    docker-compose logs -f excel-ai-analyzer
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    docker-compose down
    echo "✅ Services stopped"
}

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    docker-compose down --volumes --remove-orphans
    docker system prune -f
    echo "✅ Cleanup complete"
}

# Function to backup data
backup_data() {
    echo "💾 Creating backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    tar -czf "backup_${timestamp}.tar.gz" data logs .env
    echo "✅ Backup created: backup_${timestamp}.tar.gz"
}

# Function to show help
show_help() {
    echo "Excel AI Analyzer - Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start          Start the application (default)"
    echo "  start-proxy    Start with reverse proxy (Traefik)"
    echo "  stop           Stop all services"
    echo "  restart        Restart all services"
    echo "  status         Show service status"
    echo "  logs           Show application logs"
    echo "  backup         Create backup of data and configuration"
    echo "  cleanup        Stop services and clean up Docker resources"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Start the application"
    echo "  $0 start-proxy     # Start with reverse proxy"
    echo "  $0 logs           # View logs"
    echo "  $0 backup         # Create backup"
}

# Main script logic
main() {
    local command="${1:-start}"
    
    case "$command" in
        "start")
            check_docker
            create_directories
            start_services
            show_status
            ;;
        "start-proxy")
            check_docker
            create_directories
            start_with_proxy
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_services
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "backup")
            backup_data
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo "❌ Unknown command: $command"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
