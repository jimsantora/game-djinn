.PHONY: help setup setup-local dev test lint build clean db-migrate db-seed db-reset stop logs ps test-mcp test-mcp-local test-mcp-tools test-mcp-install test-backend dev-backend test-api restart-backend kill-backend test-frontend dev-frontend test-socketio test-realtime

# Default target
.DEFAULT_GOAL := help

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Help target
help: ## Show this help message
	@echo '${CYAN}Game Djinn Development Commands${NC}'
	@echo ''
	@echo 'Usage:'
	@echo '  ${GREEN}make${NC} ${YELLOW}<target>${NC}'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${GREEN}%-15s${NC} %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Setup target
setup: ## Install all dependencies and tools
	@echo "${CYAN}Setting up Game Djinn development environment...${NC}"
	@echo "${YELLOW}Checking prerequisites...${NC}"
	@command -v docker >/dev/null 2>&1 || { echo "${RED}Docker is required but not installed.${NC}" >&2; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "${RED}Docker Compose is required but not installed.${NC}" >&2; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "${RED}Python 3 is required but not installed.${NC}" >&2; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "${RED}Node.js is required but not installed.${NC}" >&2; exit 1; }
	
	@echo "${YELLOW}Creating .env file if it doesn't exist...${NC}"
	@if [ ! -f .env ]; then cp .env.example .env && echo "${GREEN}.env file created from .env.example${NC}"; else echo "${GREEN}.env file already exists${NC}"; fi
	
	@echo "${YELLOW}Creating data directories...${NC}"
	@mkdir -p data/postgres data/redis data/ollama
	
	@echo "${YELLOW}Building Docker images...${NC}"
	@docker-compose build
	
	@echo "${GREEN}Setup complete! Run 'make dev' to start the development environment.${NC}"

# Local development setup
setup-local: ## Install local development dependencies
	@echo "${CYAN}Setting up local development dependencies...${NC}"
	@echo "${YELLOW}Installing backend dependencies...${NC}"
	@cd services/web/backend && pip install -r requirements.txt
	@cd services/mcp-server && pip install -r requirements.txt
	@echo "${YELLOW}Installing frontend dependencies...${NC}"
	@cd services/web/frontend && npm install
	@echo "${GREEN}Local dependencies installed!${NC}"

# Development target
dev: ## Start development environment
	@echo "${CYAN}Starting Game Djinn development environment...${NC}"
	@docker-compose up -d
	@echo "${GREEN}Services are starting up...${NC}"
	@echo ""
	@echo "Services will be available at:"
	@echo "  ${CYAN}Web UI:${NC}        http://localhost:8000"
	@echo "  ${CYAN}API Docs:${NC}      http://localhost:8000/docs"
	@echo "  ${CYAN}MCP Server:${NC}    http://localhost:8080"
	@echo "  ${CYAN}PostgreSQL:${NC}    localhost:5432"
	@echo "  ${CYAN}Redis:${NC}         localhost:6379"
	@echo ""
	@echo "Run '${GREEN}make logs${NC}' to view service logs"
	@echo "Run '${GREEN}make ps${NC}' to check service status"

# Stop services
stop: ## Stop all services
	@echo "${CYAN}Stopping Game Djinn services...${NC}"
	@docker-compose down
	@echo "${GREEN}All services stopped.${NC}"

# View logs
logs: ## View logs from all services (follow mode)
	@docker-compose logs -f

# Service status
ps: ## Show status of all services
	@docker-compose ps

# Test target
test: ## Run all tests
	@echo "${CYAN}Running tests...${NC}"
	@echo "${YELLOW}Running Python tests...${NC}"
	@docker-compose run --rm web pytest tests/ -v
	@docker-compose run --rm mcp-server pytest tests/ -v
	@docker-compose run --rm ai-service pytest tests/ -v
	@docker-compose run --rm platform-sync pytest tests/ -v
	@echo "${YELLOW}Running JavaScript tests...${NC}"
	@docker-compose run --rm web sh -c "cd /frontend && npm test"
	@echo "${GREEN}All tests completed!${NC}"

# MCP-specific test targets
test-mcp: ## Run MCP server tests
	@echo "${CYAN}Running MCP server tests...${NC}"
	@docker-compose run --rm mcp-server pytest tests/ -v --tb=short --disable-warnings
	@echo "${GREEN}MCP tests completed!${NC}"

test-mcp-local: ## Run MCP tests locally (requires local env)
	@echo "${CYAN}Running MCP server tests locally...${NC}"
	@cd services/mcp-server && python -m pytest tests/ -v --tb=short --disable-warnings
	@echo "${GREEN}MCP tests completed!${NC}"

test-mcp-tools: ## Run specific MCP tool tests
	@echo "${CYAN}Running MCP tool tests...${NC}"
	@docker-compose run --rm mcp-server pytest tests/ -v -k "$(PATTERN)" --tb=short --disable-warnings
	@echo "${GREEN}MCP tool tests completed!${NC}"

test-mcp-install: ## Install MCP test dependencies
	@echo "${CYAN}Installing MCP test dependencies...${NC}"
	@cd services/mcp-server && pip install -r requirements-test.txt
	@echo "${GREEN}MCP test dependencies installed!${NC}"

test-backend: ## Run backend API tests
	@echo "${CYAN}Running backend API tests...${NC}"
	@cd services/web/backend && DATABASE_URL="postgresql://gamedjinn:secure-password-here@localhost:5432/gamedjinn" SECRET_KEY="test-secret" MCP_API_KEY="test-mcp-key" python -m pytest tests/ -v
	@echo "${GREEN}Backend tests completed!${NC}"

# Lint target
lint: ## Run linters (ruff, black, eslint)
	@echo "${CYAN}Running linters...${NC}"
	@echo "${YELLOW}Running Python linters...${NC}"
	@docker-compose run --rm web sh -c "ruff check . && black . --check && mypy app/"
	@docker-compose run --rm mcp-server sh -c "ruff check . && black . --check && mypy ."
	@docker-compose run --rm ai-service sh -c "ruff check . && black . --check && mypy ."
	@docker-compose run --rm platform-sync sh -c "ruff check . && black . --check && mypy ."
	@echo "${YELLOW}Running JavaScript linters...${NC}"
	@docker-compose run --rm web sh -c "cd /frontend && npm run lint"
	@echo "${GREEN}All linting checks passed!${NC}"

# Build target
build: ## Build all Docker images
	@echo "${CYAN}Building Docker images...${NC}"
	@docker-compose build --no-cache
	@echo "${GREEN}All images built successfully!${NC}"

# Clean target
clean: ## Clean up artifacts
	@echo "${CYAN}Cleaning up artifacts...${NC}"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "${GREEN}Cleanup complete!${NC}"

# Database migration
db-migrate: ## Run database migrations
	@echo "${CYAN}Running database migrations...${NC}"
	@docker-compose run --rm web alembic upgrade head
	@echo "${GREEN}Migrations complete!${NC}"

# Database seed
db-seed: ## Seed test data
	@echo "${CYAN}Seeding database with test data...${NC}"
	@docker-compose run --rm web python -m scripts.seed_data
	@echo "${GREEN}Database seeded!${NC}"

# Database reset
db-reset: ## Reset database (WARNING: destroys all data)
	@echo "${RED}WARNING: This will delete all data in the database!${NC}"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	@echo "${CYAN}Resetting database...${NC}"
	@docker-compose down -v
	@docker-compose up -d db
	@sleep 5
	@docker-compose run --rm web alembic upgrade head
	@echo "${GREEN}Database reset complete!${NC}"

# Service-specific commands
web-shell: ## Open shell in web service
	@docker-compose exec web /bin/sh

mcp-shell: ## Open shell in MCP server
	@docker-compose exec mcp-server /bin/sh

db-shell: ## Open PostgreSQL shell
	@docker-compose exec db psql -U gamedjinn -d gamedjinn

redis-cli: ## Open Redis CLI
	@docker-compose exec redis redis-cli

# Development helpers
format: ## Auto-format code
	@echo "${CYAN}Auto-formatting code...${NC}"
	@docker-compose run --rm web black .
	@docker-compose run --rm mcp-server black .
	@docker-compose run --rm ai-service black .
	@docker-compose run --rm platform-sync black .
	@docker-compose run --rm web sh -c "cd /frontend && npm run format"
	@echo "${GREEN}Code formatted!${NC}"

type-check: ## Run type checking
	@echo "${CYAN}Running type checks...${NC}"
	@docker-compose run --rm web mypy app/
	@docker-compose run --rm mcp-server mypy .
	@docker-compose run --rm ai-service mypy .
	@docker-compose run --rm platform-sync mypy .
	@echo "${GREEN}Type checking complete!${NC}"

# Local development commands
dev-backend: ## Start backend locally for development
	@echo "${CYAN}Starting backend development server...${NC}"
	@cd services/web/backend && ./scripts/start_dev.sh

test-api: ## Test backend API endpoints
	@echo "${CYAN}Testing backend API...${NC}"
	@cd services/web/backend && ./scripts/test_api.sh

restart-backend: ## Clean restart of backend server
	@echo "${CYAN}Restarting backend server...${NC}"
	@cd services/web/backend && ./scripts/kill_server.sh && sleep 2 && ./scripts/start_dev.sh

kill-backend: ## Stop backend development server
	@echo "${CYAN}Stopping backend server...${NC}"
	@cd services/web/backend && ./scripts/kill_server.sh

test-frontend: ## Test frontend with automatic timeout
	@echo "${CYAN}Testing frontend...${NC}"
	@cd services/web/frontend && ./scripts/test-frontend.sh

dev-frontend: ## Start frontend development server
	@echo "${CYAN}Starting frontend development server...${NC}"
	@cd services/web/frontend && npm run dev

test-socketio: ## Test Socket.IO integration
	@echo "${CYAN}Testing Socket.IO integration...${NC}"
	@echo "${YELLOW}Starting backend server for Socket.IO testing...${NC}"
	@cd services/web/backend && ./scripts/start_dev.sh &
	@sleep 3
	@echo "${YELLOW}Testing Socket.IO connection...${NC}"
	@cd services/web/frontend && npm run dev -- --host 0.0.0.0 --port 3000 &
	@sleep 5
	@echo "${GREEN}Socket.IO test servers started!${NC}"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend WebSocket: ws://localhost:8000"
	@echo "Press Ctrl+C to stop servers"

test-realtime: ## Test real-time features end-to-end
	@echo "${CYAN}Testing real-time features...${NC}"
	@echo "${YELLOW}Ensure both backend and frontend are running${NC}"
	@echo "1. Backend should be running at http://localhost:8000"
	@echo "2. Frontend should be running at http://localhost:3000" 
	@echo "3. Test sync progress by triggering a library sync"
	@echo "4. Verify real-time updates in library table"
	@echo "${GREEN}Manual real-time testing guide displayed${NC}"