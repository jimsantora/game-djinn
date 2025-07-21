# Game Djinn Implementation Plan

## Project Overview

**Name:** Game Djinn (play on "Game Genie")  
**Tagline:** "Your AI-powered gaming companion that knows all your games, across all your platforms"  
**Purpose:** Platform-agnostic gaming library management with AI agent integration  
**Architecture:** Microservices with standalone MCP server for universal AI compatibility  
**Target:** Self-hosted homelab application  

## Core Value Proposition

- Universal gaming library across all platforms (Steam, Xbox, GOG, PlayStation, etc.)
- AI agent accessible via MCP protocol (works with Claude Desktop, Open-WebUI, any MCP client)
- Rich metadata including ESRB ratings, Metacritic scores, and cross-platform insights
- Privacy-focused self-hosted solution

## Technology Stack

### Backend Services
- **FastAPI** - All services (consistency and async support)
- **PostgreSQL** - Primary database with JSONB for flexible platform data
- **Redis** - Caching and session management
- **Official MCP Python SDK** - Standalone MCP server
- **SQLAlchemy + asyncpg** - Async ORM
- **Pydantic** - Data validation

### AI & Integration
- **Ollama** - Local LLM (llama2 or similar 7B model)
- **LangChain** - AI agent framework with MCP client integration
- **MCP Protocol** - Universal tool interface for external AI clients

### Frontend
- **React + Vite** - Modern web interface
- **React Query** - API state management
- **WebSocket** - Real-time AI chat
- **Recharts** - Analytics visualizations

### External APIs
- **Steam Web API** ✅ - Complete integration with library access, metadata, and achievements
- **Xbox Game Pass API** 🚧 - Future integration for catalog and user data (Phase 3)
- **Metacritic API** 🚧 - Future integration for enhanced review scores (Phase 2)

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

## Implementation Phases

### Phase 0: Foundation & Development Setup ✅ COMPLETED
**Goal:** Set up development environment and basic project structure

#### 0.1 Project Setup ✅ COMPLETED
- [x] Initialize project structure and Git repository
- [x] Create `.env.example` with all required variables
- [x] Set up development docker-compose.yml
- [x] Create comprehensive README with quickstart instructions
- [x] Add `.gitignore` for Python/Node/Docker artifacts

#### 0.2 Makefile-Driven Development ✅ COMPLETED
- [x] Create comprehensive Makefile with targets:
  - `make setup` - Install all dependencies and tools
  - `make dev` - Start development environment
  - `make test` - Run all tests
  - `make lint` - Run linters (ruff, black, eslint)
  - `make build` - Build all Docker images
  - `make clean` - Clean up artifacts
  - `make db-migrate` - Run database migrations
  - `make db-seed` - Seed test data
  - `make test-backend` - Test backend API
  - `make test-frontend` - Test frontend with timeout
  - `make test-socketio` - Test real-time features
- [x] Development scripts for individual services
- [x] Claude Code-friendly command structure

#### 0.3 Database Schema & Migrations ✅ COMPLETED
- [x] Design complete database schema with platform-agnostic design
- [x] Create initial migration scripts with Alembic
- [x] Set up Alembic for schema versioning
- [x] Create comprehensive seed data for development and testing
- [x] Document database relationships and indexes
- [x] Optimize schema for homelab performance

#### 0.4 API Specifications ✅ COMPLETED
- [x] Define OpenAPI schemas for all REST endpoints
- [x] Document complete MCP tool specifications
- [x] Create example requests/responses for all APIs
- [x] Define Socket.IO event formats for real-time updates
- [x] Error code standardization across all services
- [x] Authentication and authorization patterns

#### 0.5 Development Infrastructure ✅ COMPLETED
- [x] Docker Compose for complete development environment
- [x] Health check scripts for all services
- [x] Backup/restore scripts optimized for homelab use
- [x] Environment configuration management
- [x] Service monitoring and logging setup

### Phase 1: Core Infrastructure (MVP) ✅ COMPLETED
**Goal:** Working single-platform system with comprehensive web interface and real-time features

#### 1.1 Database Setup ✅ COMPLETED
- [x] Universal game schema with platform-agnostic design
- [x] Platform registry table (steam, xbox, gog, manual, etc.) with API availability tracking
- [x] User libraries table supporting multiple platforms per user
- [x] Games table with comprehensive metadata (ESRB, Metacritic, genres, platforms, ratings)
- [x] User-game relationships with playtime tracking and progress
- [x] Database migrations with Alembic and optimized indexes
- [x] Cross-platform achievement and user data tracking

#### 1.2 Platform Integration Foundation ✅ COMPLETED
- [x] Abstract base class for platform integrations with async/await support
- [x] Comprehensive Steam Web API integration with full metadata support
- [x] Steam native metadata enhancement (cover art, screenshots, ratings, genres)
- [x] Cross-platform game matching and normalization logic
- [x] Rate limiting and error handling for external API calls
- [x] Steam content descriptors and ESRB rating integration

#### 1.3 MCP Server (Core Component) ✅ COMPLETED
- [x] Standalone MCP server using official Python SDK
- [x] Complete implementation of universal gaming tools:
  - `get_supported_platforms` - List available gaming platforms
  - `add_platform_library` - Add new platform library connections
  - `sync_platform_library` - Sync games from platform APIs with progress tracking
  - `search_games` - Universal game search with advanced filtering
  - `get_game_details` - Comprehensive game information retrieval
  - `analyze_gaming_patterns` - Gaming insights and analytics
  - `filter_by_content_rating` - ESRB-based content filtering
  - `recommend_games` - AI-powered game recommendations
- [x] Streaming support for long-running operations
- [x] Complete database integration for all MCP tools
- [x] API key authentication and comprehensive error handling
- [x] Testing framework for all MCP tools

#### 1.4 Basic Web Interface ✅ COMPLETED
- [x] FastAPI backend with comprehensive REST endpoints and Socket.IO integration
- [x] Modern React frontend with advanced library browsing and real-time updates
- [x] Complete platform configuration interface with validation
- [x] Advanced game grid/list views with search, filtering, and sorting
- [x] Comprehensive authentication and session management:
  - Optional admin authentication for homelab setup
  - JWT authentication with environment-based configuration
  - httpOnly cookie-based session storage
  - MCP server API key protection
  - Proxy-friendly auth bypass option
- [x] Real-time Socket.IO integration:
  - Live sync progress tracking with progress bars
  - Real-time notifications for sync events
  - Automatic cache invalidation for UI updates
  - Connection status monitoring
- [x] Responsive UI with complete CRUD operations:
  - Library management with statistics and search
  - Game browsing with multiple view modes
  - Detailed game pages with comprehensive metadata
  - Real-time sync status and progress indicators

### Phase 2: AI Integration 🚧 NEXT PRIORITY
**Goal:** Working AI agent with natural language queries for enhanced gaming insights

#### 2.1 AI Service (Priority: High)
- [ ] LangChain agent setup with Ollama integration (local or remote)
- [ ] MCP client integration (AI service connects to existing MCP server)
- [ ] Streaming AI responses for real-time chat experience  
- [ ] Conversation memory and context management for gaming sessions
- [ ] Error handling and fallback responses for robust user experience
- [ ] Integration with existing Socket.IO infrastructure for real-time updates

#### 2.2 Enhanced Web Features (Priority: Medium)
- [ ] AI chat widget integrated into existing web interface
- [ ] Streaming AI responses using established WebSocket connection
- [ ] Enhanced game analytics dashboard with AI-powered insights
- [ ] Cross-platform duplicate detection and consolidation
- [ ] AI-powered smart collections and advanced filtering
- [ ] Gaming habit analysis and personalized recommendations

#### 2.3 Homelab Optimization (Priority: High)
- [ ] Ollama integration optimized for homelab deployment:
  - Support for remote Ollama instances (recommended)
  - Local Ollama option for self-contained deployment
  - Resource usage monitoring and optimization
  - Model selection based on available hardware
- [ ] AI service configuration management for various homelab setups
- [ ] Performance monitoring and optimization for resource-constrained environments

### Phase 3: Multi-Platform Support
**Goal:** Support for major gaming platforms

#### 3.1 Additional Platform Integrations
- [ ] Xbox Game Pass integration
- [ ] GOG Galaxy integration
- [ ] Enhanced manual import with web scraping helpers
- [ ] Platform-specific achievement/trophy systems

#### 3.2 Advanced Features
- [ ] Cross-platform playtime aggregation
- [ ] Gaming habit insights and recommendations
- [ ] ESRB content filtering for family-friendly views
- [ ] Export capabilities (reports, backup)

## Directory Structure

```
game-djinn/
├── docker-compose.yml
├── .env.example
├── README.md
├── services/
│   ├── web/                    # React frontend + FastAPI backend
│   │   ├── backend/
│   │   │   ├── app/
│   │   │   │   ├── main.py
│   │   │   │   ├── api/
│   │   │   │   ├── models/
│   │   │   │   └── database/
│   │   │   └── requirements.txt
│   │   ├── frontend/
│   │   │   ├── src/
│   │   │   ├── package.json
│   │   │   └── vite.config.js
│   │   └── Dockerfile
│   ├── mcp-server/            # Standalone MCP server
│   │   ├── src/
│   │   │   ├── main.py
│   │   │   ├── tools/
│   │   │   ├── platforms/
│   │   │   └── database/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── ai-service/            # AI agent with LangChain
│   │   ├── src/
│   │   │   ├── main.py
│   │   │   ├── agents/
│   │   │   └── mcp_client/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── platform-sync/         # Background sync services
│       ├── src/
│       │   ├── main.py
│       │   ├── integrations/
│       │   └── enrichment/
│       ├── requirements.txt
│       └── Dockerfile
├── database/
│   ├── migrations/
│   └── init.sql
└── docs/
    ├── api.md
    ├── mcp-tools.md
    └── platform-setup.md
```

## Key Database Tables

### Core Tables
```sql
-- Platform registry
platforms (platform_id, platform_code, platform_name, api_available)

-- User libraries across platforms  
user_libraries (library_id, platform_id, user_identifier, display_name, api_credentials)

-- Universal games with rich metadata
games (game_id, title, normalized_title, platform_ids, esrb_rating, metacritic_score, genres, etc.)

-- User-specific game data
user_games (user_game_id, library_id, game_id, total_playtime_minutes, game_status, user_rating)

-- Cross-platform achievements
game_achievements (achievement_id, game_id, platform_id, title, description)
user_achievements (user_achievement_id, user_game_id, achievement_id, unlocked_at)
```

## MCP Tools Specification

### Core Tools
- **get_supported_platforms()** → List available gaming platforms
- **add_platform_library(platform_code, credentials, display_name)** → Add new library
- **sync_platform_library(library_id)** → Sync games from platform API
- **search_games(query, platform_filter, status_filter, rating_filter)** → Universal game search
- **get_game_details(game_id, library_id)** → Comprehensive game information
- **analyze_gaming_patterns(library_id, time_period)** → Gaming insights and analytics
- **filter_by_content_rating(esrb_rating)** → ESRB-based content filtering
- **recommend_games(criteria, limit, genre_preference)** → AI-powered recommendations

### Advanced Tools
- **get_cross_platform_games()** → Find games owned on multiple platforms
- **export_library_data(format, filters)** → Export user data
- **create_smart_collection(name, rules)** → Auto-updating game collections

## External API Requirements

### Required API Keys (Phase 1) ✅
- **Steam Web API Key** ✅ (free) - https://steamcommunity.com/dev/apikey
  - Fully integrated with comprehensive metadata support
  - Rate limiting and error handling implemented
  - Cover art, screenshots, ratings, and achievement data

### Future Platform APIs (Phase 3)
- **Xbox Live API** (OAuth) - https://docs.microsoft.com/en-us/gaming/
- **GOG Galaxy API** - For DRM-free game libraries
- **Epic Games Store API** - For Epic launcher integration

### Optional Enhancements (Phase 2+)
- **Metacritic API** - For additional review scores and critic ratings
- **HowLongToBeat API** - For game completion time estimates
- **IGDB API** - For enhanced game metadata and cross-platform matching

## Platform API Rate Limits

### Rate Limits by Service
- **Steam Web API**: 100 requests per 5 minutes, 100k daily
- **Xbox API**: 300 requests per minute, 3k hourly

### Rate Limit Strategy
- Implement rate limiter with sliding window
- Automatic retry with exponential backoff
- Manual retry option in UI for failed syncs
- Save sync position for resumable operations

## Docker Compose Configuration

```yaml
version: '3.8'
services:
  web:
    build: ./services/web
    ports: ["8000:8000"]
    depends_on: [db, redis, mcp-server]
  
  mcp-server:
    build: ./services/mcp-server
    ports: ["8080:8080"]  # Exposed for external MCP clients
    depends_on: [db]
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/gamedjinn
      - STEAM_API_KEY=${STEAM_API_KEY}
  
  ai-service:
    build: ./services/ai-service
    depends_on: [mcp-server, ollama]
    environment:
      - MCP_SERVER_URL=http://mcp-server:8080
  
  ollama:
    image: ollama/ollama
    volumes: ["ollama_models:/root/.ollama"]
    environment:
      - OLLAMA_MODELS=llama2:7b
  
  db:
    image: postgres:15
    volumes: ["postgres_data:/var/lib/postgresql/data"]
    environment:
      - POSTGRES_DB=gamedjinn
      - POSTGRES_USER=gamedjinn
      - POSTGRES_PASSWORD=${DB_PASSWORD}
  
  redis:
    image: redis:7
    volumes: ["redis_data:/data"]

volumes:
  postgres_data:
  redis_data:
  ollama_models:
```

## Data Persistence & Backup

### Volume Management
```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/postgres
  redis_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/redis
  ollama_models:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/ollama
```

### Backup Strategy
- PostgreSQL: Daily automated backups with pg_dump
- Redis: BGSAVE snapshots
- Ollama models: Weekly tar archives
- Scripts provided in `/scripts` directory

## Configuration Management

### Environment Variables (.env.example)
```bash
# Database
DB_PASSWORD=secure-password-here
DATABASE_URL=postgresql://gamedjinn:${DB_PASSWORD}@db:5432/gamedjinn

# Authentication
SECRET_KEY=generate-with-openssl-rand-hex-32
MCP_API_KEY=generate-a-secure-api-key
ADMIN_EMAIL=admin@gamedjinn.local
ADMIN_PASSWORD=changeme

# External APIs (Required)
STEAM_API_KEY=your-steam-api-key

# Service URLs
MCP_SERVER_URL=http://mcp-server:8080
OLLAMA_URL=http://ollama:11434

# Ports
WEB_PORT=8000
MCP_PORT=8080
```

## Success Criteria

### ✅ MVP Success (Phase 1) - ACHIEVED!
- [x] **Steam library sync working end-to-end** - Complete with real-time progress tracking
- [x] **MCP server functional with core tools** - All 8 core tools implemented and tested
- [x] **Comprehensive web interface for library management** - Modern React app with full CRUD operations
- [x] **Steam metadata enhancement working** - Rich game data with cover art, ratings, and genres
- [x] **Real-time updates and notifications** - Socket.IO integration with live sync progress
- [x] **Authentication and security** - Optional JWT auth with environment-based configuration
- [x] **Homelab-optimized deployment** - Docker Compose with persistence and backup scripts

### 🎯 AI Integration Success (Phase 2) - NEXT MILESTONE
- [ ] AI agent responds to natural language gaming queries through existing MCP server
- [ ] Claude Desktop and other MCP clients can connect and use gaming tools
- [ ] Streaming AI responses integrated with existing Socket.IO infrastructure
- [ ] Enhanced gaming insights and AI-powered recommendations
- [ ] Homelab-optimized Ollama integration (local and remote options)

### 🚀 Multi-Platform Success (Phase 3) - FUTURE EXPANSION
- [ ] At least 3 platforms supported (Steam ✅, Xbox, Manual import)
- [ ] Cross-platform duplicate detection and game consolidation
- [ ] ESRB content filtering and family-friendly views
- [ ] Export/backup functionality for data portability
- [ ] Enhanced analytics across multiple gaming platforms

## Testing Strategy

### Unit Tests
- Platform integration modules
- MCP tool functions
- Database models and queries
- Game matching algorithms

### Integration Tests
- End-to-end platform sync flows
- MCP server tool responses
- AI agent conversation flows
- Web API endpoints

### Manual Testing
- External MCP client connections (Claude Desktop)
- Multi-platform library management
- Gaming analytics accuracy
- Performance with large libraries (1000+ games)

## Error Recovery & Monitoring

### Sync Failure Handling
- Save sync state and position for resume capability
- Automatic retry with exponential backoff for rate limits
- Manual retry triggers via API and UI
- Detailed error logging per platform

### Health Monitoring
- `/health` endpoints on all services
- Docker healthchecks with auto-restart
- Centralized logging in `/var/log/game-djinn/`
- Service status dashboard in web UI

### Log Management
```bash
# Docker logs
docker-compose logs -f <service>

# Kubernetes logs
kubectl logs -n game-djinn deployment/<service> -f

# Log locations
/var/log/game-djinn/
├── web/
├── mcp-server/
├── ai-service/
└── platform-sync/
```

## Kubernetes Deployment (Helm)

### Helm Chart Structure
```
game-djinn/
├── helm/
│   └── game-djinn/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── templates/
│       │   ├── configmap.yaml
│       │   ├── secret.yaml
│       │   ├── pvc.yaml
│       │   ├── deployment-web.yaml
│       │   ├── deployment-mcp.yaml
│       │   ├── deployment-ai.yaml
│       │   ├── deployment-sync.yaml
│       │   ├── service-web.yaml
│       │   ├── service-mcp.yaml
│       │   ├── statefulset-postgres.yaml
│       │   ├── statefulset-redis.yaml
│       │   ├── statefulset-ollama.yaml
│       │   └── ingress.yaml
│       └── values-homelab.yaml
```

### Deployment Strategy
- **StatefulSets** for PostgreSQL, Redis, and Ollama (persistent data)
- **Deployments** for stateless services (web, mcp, ai, sync)
- **PersistentVolumeClaims** for data persistence
- **ConfigMaps** and **Secrets** for configuration
- **Services** for internal networking
- **Optional Ingress** for external access

### Resource Requirements (Homelab)
```yaml
resources:
  web:
    requests: { memory: "256Mi", cpu: "100m" }
    limits: { memory: "512Mi", cpu: "500m" }
  mcp:
    requests: { memory: "128Mi", cpu: "100m" }
  ai:
    requests: { memory: "512Mi", cpu: "200m" }
  ollama:
    requests: { memory: "4Gi", cpu: "1000m" }  # 7B model
  postgres:
    requests: { memory: "256Mi", cpu: "100m" }
```

### Helm Commands
```bash
# Create namespace
kubectl create namespace game-djinn

# Install
helm install game-djinn ./helm/game-djinn \
  -f ./helm/game-djinn/values-homelab.yaml \
  -n game-djinn

# Upgrade
helm upgrade game-djinn ./helm/game-djinn \
  -f ./helm/game-djinn/values-homelab.yaml \
  -n game-djinn

# Port forwarding for local access
kubectl port-forward -n game-djinn svc/game-djinn-web 8000:8000
kubectl port-forward -n game-djinn svc/game-djinn-mcp 8080:8080
```

## Future Expansion Ideas

### Platform Support
- PlayStation Network (web scraping)
- Epic Games Store
- Nintendo Switch (manual import)
- Retro platforms (emulation libraries)

### Advanced Features
- Social features (share libraries, recommendations)
- Integration with streaming platforms (Twitch, YouTube)
- Gaming goal tracking and achievements
- Price tracking and deal alerts
- VR/AR game filtering

### AI Enhancements
- Voice interface integration
- Personalized gaming schedule suggestions
- Mood-based game recommendations
- Integration with calendar for gaming time planning

## Implementation Details

### Authentication Implementation

#### JWT Authentication (FastAPI)
```python
# services/web/backend/app/auth.py
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy

# Single admin user for homelab
DEFAULT_ADMIN_EMAIL = "admin@gamedjinn.local"
DEFAULT_ADMIN_PASSWORD = "changeme"  # Change on first login

# JWT settings
SECRET_KEY = "your-secret-key-here"  # Generate with: openssl rand -hex 32
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

#### MCP Server API Key Protection
```python
# services/mcp-server/src/auth.py
MCP_API_KEY = os.getenv("MCP_API_KEY", "generate-a-secure-key")

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path.startswith("/health"):
        return await call_next(request)
    
    api_key = request.headers.get("X-API-Key")
    if api_key != MCP_API_KEY:
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    
    return await call_next(request)
```

#### Redis Session Storage
```python
# services/web/backend/app/sessions.py
from redis import asyncio as aioredis

redis = await aioredis.from_url("redis://redis:6379")
session_ttl = 3600  # 1 hour

# Store session
await redis.setex(f"session:{session_id}", session_ttl, user_data)

# Retrieve session
session_data = await redis.get(f"session:{session_id}")
```

### Rate Limiting Implementation

#### Rate Limiter Class
```python
# services/platform-sync/src/rate_limiter.py
from asyncio import sleep
import time

PLATFORM_LIMITS = {
    "steam": {
        "requests_per_window": 100,
        "window_seconds": 300,  # 5 minutes
        "daily_limit": 100000,
        "retry_after": 60
    },
    "rawg": {
        "requests_per_window": 20,
        "window_seconds": 1,  # Per second on free tier
        "monthly_limit": 20000,
        "retry_after": 2
    },
    "xbox": {
        "requests_per_window": 300,
        "window_seconds": 60,
        "hourly_limit": 3000,
        "retry_after": 30
    }
}

class RateLimiter:
    def __init__(self, platform: str):
        self.limits = PLATFORM_LIMITS[platform]
        self.requests = []
    
    async def acquire(self):
        now = time.time()
        window_start = now - self.limits["window_seconds"]
        
        # Clean old requests
        self.requests = [r for r in self.requests if r > window_start]
        
        # Check if at limit
        if len(self.requests) >= self.limits["requests_per_window"]:
            wait_time = self.requests[0] + self.limits["window_seconds"] - now
            await sleep(wait_time)
            return await self.acquire()
        
        self.requests.append(now)

# Usage
limiter = RateLimiter("steam")
async def sync_steam_library(library_id):
    await limiter.acquire()
    # Make API call
```

#### Manual Retry UI Component
```typescript
// services/web/frontend/src/components/SyncStatus.tsx
const SyncStatus = ({ library }) => {
  const [retryIn, setRetryIn] = useState(null);
  
  if (library.lastSyncError?.includes("rate limit")) {
    return (
      <Alert severity="warning">
        Rate limit reached. 
        {retryIn ? (
          <span>Auto-retry in {retryIn}s</span>
        ) : (
          <Button onClick={() => manualSync(library.id)}>
            Retry Now
          </Button>
        )}
      </Alert>
    );
  }
};
```

### Error Recovery Implementation

#### Sync Failure Handling
```python
# services/platform-sync/src/sync_manager.py

class SyncManager:
    async def sync_library(self, library_id: str):
        try:
            # Save sync state
            await self.db.update_sync_status(library_id, "in_progress")
            
            # Get last successful position
            last_position = await self.db.get_sync_position(library_id)
            
            # Resume from last position
            async for game in self.platform.get_games(start=last_position):
                await self.process_game(game)
                await self.db.update_sync_position(library_id, game.id)
                
        except RateLimitError as e:
            await self.db.update_sync_status(
                library_id, 
                "rate_limited",
                error=str(e),
                retry_after=e.retry_after
            )
        except Exception as e:
            await self.db.update_sync_status(
                library_id,
                "failed", 
                error=str(e)
            )
            raise
```

#### Manual Re-sync API
```python
# services/web/backend/app/api/sync.py

@router.post("/libraries/{library_id}/sync")
async def trigger_sync(library_id: str, force: bool = False):
    """Manually trigger library sync"""
    
    # Check if already syncing
    status = await db.get_sync_status(library_id)
    if status == "in_progress" and not force:
        raise HTTPException(400, "Sync already in progress")
    
    # Queue sync job
    await queue.send("sync_library", {
        "library_id": library_id,
        "force": force,
        "requested_by": "manual"
    })
    
    return {"status": "queued", "library_id": library_id}
```

### Backup & Persistence Scripts

#### Backup Script
```bash
#!/bin/bash
# scripts/backup.sh

# PostgreSQL backup
docker-compose exec -T db pg_dump -U gamedjinn gamedjinn > backups/gamedjinn_$(date +%Y%m%d_%H%M%S).sql

# Redis backup
docker-compose exec -T redis redis-cli BGSAVE
docker cp game-djinn_redis_1:/data/dump.rdb backups/redis_$(date +%Y%m%d_%H%M%S).rdb

# Ollama models backup (large files)
tar -czf backups/ollama_models_$(date +%Y%m%d).tar.gz data/ollama/
```

#### Database Reset Script
```bash
#!/bin/bash
# scripts/reset-database.sh

echo "WARNING: This will delete all data. Continue? (y/N)"
read -r response
if [[ "$response" != "y" ]]; then
    exit 1
fi

# Stop services
docker-compose down

# Remove volumes
docker volume rm game-djinn_postgres_data game-djinn_redis_data

# Recreate and initialize
docker-compose up -d db
sleep 5
docker-compose exec -T db psql -U gamedjinn -d gamedjinn < database/init.sql
```

### Health Monitoring Implementation

#### Health Check Endpoint
```python
# All services implement /health endpoint
@app.get("/health")
async def health_check():
    checks = {
        "status": "healthy",
        "database": await check_database(),
        "redis": await check_redis(),
        "external_apis": await check_apis()
    }
    
    # Return 503 if any check fails
    if not all(checks.values()):
        return JSONResponse(
            status_code=503,
            content=checks
        )
    
    return checks

# Docker healthcheck
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Complete Environment Configuration

#### .env.example
```bash
# Database
DB_PASSWORD=secure-password-here
DATABASE_URL=postgresql://gamedjinn:${DB_PASSWORD}@db:5432/gamedjinn

# Redis
REDIS_URL=redis://redis:6379

# Authentication
SECRET_KEY=generate-with-openssl-rand-hex-32
MCP_API_KEY=generate-a-secure-api-key
ADMIN_EMAIL=admin@gamedjinn.local
ADMIN_PASSWORD=changeme

# External APIs (Required)
STEAM_API_KEY=your-steam-api-key

# External APIs (Optional)
XBOX_CLIENT_ID=
XBOX_CLIENT_SECRET=
METACRITIC_API_KEY=
HOWLONGTOBEAT_API_KEY=

# Service URLs (internal Docker/K8s networking)
MCP_SERVER_URL=http://mcp-server:8080
OLLAMA_URL=http://ollama:11434
WEB_API_URL=http://web:8000

# Ollama Model
OLLAMA_MODEL=llama2:7b

# Ports (for external access)
WEB_PORT=8000
MCP_PORT=8080

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance
WORKERS=2
MAX_CONNECTIONS=100
CACHE_TTL=3600
```

#### External Access Configuration (nginx)
```nginx
# nginx.conf for reverse proxy
server {
    listen 80;
    server_name game-djinn.local;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /mcp/ {
        proxy_pass http://localhost:8080/;
        proxy_set_header X-API-Key $http_x_api_key;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Homelab-Specific Optimizations ✅ IMPLEMENTED

### Resource Efficiency
- **Docker Compose** deployment optimized for single-host homelab scenarios
- **Optional authentication** that can be disabled for reverse proxy scenarios
- **Persistent volumes** with bind mounts for easy backup and data management
- **Health checks** and auto-restart policies for reliability
- **Resource-conscious** container configurations

### Security & Privacy
- **Self-hosted architecture** - All data stays within your homelab
- **API key management** via environment variables
- **Optional authentication** that can be bypassed for trusted networks
- **No external analytics** or telemetry - completely private
- **Secure defaults** with environment-based configuration

### Backup & Maintenance
- **Simple backup scripts** for PostgreSQL, Redis, and Ollama models
- **Volume management** optimized for homelab storage
- **Database seeding** for easy development and testing
- **Environment configuration** examples for various homelab setups
- **Makefile-driven operations** for easy management

### Deployment Options
1. **Docker Compose** (Recommended) - Single host deployment with all services
2. **Kubernetes/Helm** - For advanced homelab setups with orchestration
3. **Manual deployment** - For custom homelab configurations

### Integration Friendly
- **MCP server** can be accessed by external AI clients (Claude Desktop, Open-WebUI)
- **REST API** for integration with home automation systems
- **WebSocket events** for real-time integration with other homelab services
- **Health endpoints** for monitoring integration

### Phase 2 Homelab Considerations
- **Remote Ollama support** - AI service can connect to existing Ollama instances
- **Local Ollama option** - For completely self-contained deployment
- **Resource monitoring** - Track AI service resource usage
- **Model selection** - Choose AI models based on available hardware

---

This implementation plan provides a comprehensive roadmap for building Game Djinn as a robust, platform-agnostic gaming library management system optimized for homelab deployment with universal AI integration capabilities.

## 🎉 Current Status: Phase 1 MVP Complete!

Game Djinn now provides a fully functional gaming library management system with:
- ✅ Complete Steam integration with rich metadata
- ✅ Modern web interface with real-time updates
- ✅ Comprehensive MCP server for AI integration
- ✅ Homelab-optimized deployment and backup solutions
- ✅ Ready foundation for Phase 2 AI integration

The system is production-ready for homelab deployment and ready for Phase 2 AI service integration when desired.
