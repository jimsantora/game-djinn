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
- **Steam Web API** - Full library access
- **Xbox Game Pass API** - Catalog and user data
- **RAWG API** - 500k+ games database with ESRB ratings
- **IGDB API** - Additional game metadata
- **Metacritic API** - Review scores

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

### Phase 1: Core Infrastructure (MVP)
**Goal:** Working single-platform system with AI chat

#### 1.1 Database Setup
- [ ] Universal game schema with platform-agnostic design
- [ ] Platform registry table (steam, xbox, gog, manual, etc.)
- [ ] User libraries table (multiple platforms per user)
- [ ] Games table with rich metadata (ESRB, Metacritic, genres)
- [ ] User-game relationships with playtime tracking
- [ ] Database migrations and indexes

#### 1.2 Platform Integration Foundation
- [ ] Abstract base class for platform integrations
- [ ] Steam integration with full Web API support
- [ ] Manual import integration (CSV/JSON upload)
- [ ] Game data enrichment service (RAWG + IGDB APIs)
- [ ] Cross-platform game matching logic

#### 1.3 MCP Server (Core Component)
- [ ] Standalone MCP server using official Python SDK
- [ ] Universal gaming tools:
  - `get_supported_platforms`
  - `add_platform_library`
  - `sync_platform_library`
  - `search_games`
  - `get_game_details`
  - `analyze_gaming_patterns`
  - `filter_by_content_rating`
  - `recommend_games`
- [ ] Streaming support for long operations
- [ ] Database integration for all MCP tools

#### 1.4 Basic Web Interface
- [ ] FastAPI backend with REST endpoints
- [ ] React frontend with library browsing
- [ ] Platform configuration interface
- [ ] Basic game grid/list views
- [ ] Authentication and session management

### Phase 2: AI Integration
**Goal:** Working AI agent with natural language queries

#### 2.1 AI Service
- [ ] LangChain agent setup with Ollama integration
- [ ] MCP client integration (AI service connects to MCP server)
- [ ] WebSocket chat interface for real-time responses
- [ ] Conversation memory and context management
- [ ] Error handling and fallback responses

#### 2.2 Enhanced Web Features
- [ ] AI chat widget in web interface
- [ ] Streaming AI responses
- [ ] Game analytics dashboard
- [ ] Cross-platform duplicate detection
- [ ] Smart collections and filtering

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

### Required API Keys
- **Steam Web API Key** (free) - https://steamcommunity.com/dev/apikey
- **RAWG API Key** (free) - https://rawg.io/apidocs
- **IGDB Client ID & Access Token** (free) - https://api.igdb.com/
- **Xbox Live API** (OAuth) - https://docs.microsoft.com/en-us/gaming/

### Optional Enhancements
- **Metacritic API** - For additional review scores
- **HowLongToBeat API** - For game completion time estimates

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
      - RAWG_API_KEY=${RAWG_API_KEY}
  
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

## Success Criteria

### MVP Success (Phase 1)
- [ ] Steam library sync working end-to-end
- [ ] MCP server functional with core tools
- [ ] Basic web interface for library browsing
- [ ] Manual game import working
- [ ] Game metadata enrichment from RAWG/IGDB

### AI Integration Success (Phase 2)
- [ ] AI agent responds to natural language gaming queries
- [ ] Claude Desktop can connect and use gaming tools
- [ ] Streaming responses for long operations
- [ ] Basic gaming insights and recommendations

### Multi-Platform Success (Phase 3)
- [ ] At least 3 platforms supported (Steam, Xbox, Manual)
- [ ] Cross-platform duplicate detection
- [ ] ESRB content filtering working
- [ ] Export/backup functionality

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

---

This implementation plan provides a clear roadmap for building Game Djinn as a robust, platform-agnostic gaming library management system with universal AI integration capabilities.
