# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Game Djinn** - AI-powered gaming library management system
- Microservices architecture with standalone MCP server
- Platform-agnostic (Steam, Xbox, GOG, PlayStation, etc.)
- Self-hosted homelab application

## Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │   AI Service    │    │   MCP Server    │
│  React + API    │◄──►│ LangChain +     │◄──►│ Game Library    │
│                 │    │ Ollama          │    │ Tools           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ PostgreSQL      │    │ Redis           │    │ Platform Sync   │
│ Universal       │    │ Cache +         │    │ Background      │
│ Game Schema     │    │ Sessions        │    │ Services        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

- **Backend**: FastAPI (all services), PostgreSQL, Redis
- **Frontend**: React + Vite, React Query, WebSocket
- **AI/MCP**: Official MCP Python SDK, Ollama, LangChain
- **External APIs**: Steam, Xbox, RAWG, IGDB

## Development Commands

### Backend Services (FastAPI)
```bash
cd services/<service-name>
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest tests/ -v
ruff check . && black . --check && mypy app/
```

### Frontend (React)
```bash
cd services/web/frontend
npm install && npm run dev
npm test && npm run build
npm run lint && npm run format:check
```

### Docker & Kubernetes
```bash
# Docker
docker-compose up -d
docker-compose logs -f <service>

# Kubernetes
helm install game-djinn ./helm/game-djinn -n game-djinn
kubectl port-forward -n game-djinn svc/game-djinn-web 8000:8000
```

## Git Workflow

### Commit Format
`<type>: <description>` or `<type>(<scope>): <description>`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Branch Naming
`<type>/<description>` (e.g., `feature/steam-integration`)

## Directory Structure

```
game-djinn/
├── services/
│   ├── web/          # React + FastAPI
│   ├── mcp-server/   # MCP tools
│   ├── ai-service/   # LangChain agent
│   └── platform-sync/# Background jobs
├── helm/             # Kubernetes charts
├── database/         # Schema & migrations
├── scripts/          # Utility scripts
└── docs/             # Documentation
```

## MCP Tools

Core tools available in MCP server:
- `get_supported_platforms` - List platforms
- `sync_platform_library` - Sync games
- `search_games` - Universal search
- `get_game_details` - Game info
- `analyze_gaming_patterns` - Analytics
- `recommend_games` - AI recommendations

## Key Database Tables

- `platforms` - Platform registry
- `user_libraries` - User platform connections
- `games` - Universal game catalog
- `user_games` - User-specific data

## Where to Find Details

- **Implementation Details**: See `Game_Djinn_Implementation_Plan.md`
- **API Documentation**: `docs/api.md`
- **MCP Tools Spec**: `docs/mcp-tools.md`
- **Deployment Guide**: `docs/deployment.md`

## Important Patterns

1. All services use FastAPI with async/await
2. Database access via SQLAlchemy + asyncpg
3. Rate limiting implemented per platform
4. JWT auth for web, API keys for MCP
5. Health checks at `/health` for all services

## Environment Configuration

Create `.env` from `.env.example` with required API keys:
- Steam, RAWG, IGDB API keys (required)
- Database and Redis URLs
- Secret keys for auth

## Testing & Linting

- Unit tests with pytest
- Linting: ruff, black, mypy (Python); ESLint (JS)
- Run tests before committing
- All services have health check endpoints