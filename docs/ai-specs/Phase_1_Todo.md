# Phase 1: Core Infrastructure (MVP)

**Goal:** Working single-platform system with AI chat

## Progress Tracker

### 1.1 Database Setup
- [ ] Set up PostgreSQL database with designed schema
- [ ] Configure Alembic for production migrations
- [ ] Implement database connection pooling
- [ ] Create initial data seeding scripts
- [ ] Set up database health checks
- [ ] Configure database indexes for optimal performance

### 1.2 Platform Integration Foundation
- [ ] **PRIORITY**: Remove RAWG references from all documentation and code
- [ ] Create abstract base class for platform integrations
- [ ] Implement comprehensive Steam Web API integration
  - [ ] User authentication flow
  - [ ] Game library fetching with detailed metadata
  - [ ] Achievement data retrieval
  - [ ] User profile information
  - [ ] Playtime tracking and statistics
  - [ ] Steam ratings and review summaries
  - [ ] Content descriptors and maturity ratings
- [ ] Create game data enrichment service (IGDB primary)
  - [ ] IGDB API integration for comprehensive metadata
  - [ ] Cover art and screenshot handling
  - [ ] Genre, theme, and rating information
  - [ ] Release date and platform information
- [ ] Implement game matching logic for Steam + IGDB
  - [ ] Steam ID to IGDB ID mapping
  - [ ] Fuzzy title matching for missing mappings
  - [ ] Developer/publisher correlation
  - [ ] Manual override capability

### 1.3 MCP Server (Core Component)
- [ ] Set up standalone MCP server using official Python SDK
- [ ] Implement core MCP tools:
  - [ ] `get_supported_platforms` - List available gaming platforms
  - [ ] `add_platform_library` - Add new platform library
  - [ ] `sync_platform_library` - Sync games from platform API
  - [ ] `search_games` - Universal game search with filters
  - [ ] `get_game_details` - Comprehensive game information
  - [ ] `analyze_gaming_patterns` - Gaming insights and analytics
  - [ ] `filter_by_content_rating` - ESRB-based content filtering
  - [ ] `recommend_games` - AI-powered game recommendations
- [ ] Implement streaming support for long operations
- [ ] Set up database integration for all MCP tools
- [ ] Configure API key authentication
- [ ] Add comprehensive error handling and logging
- [ ] Create MCP tool testing framework

### 1.4 Basic Web Interface
- [ ] Set up FastAPI backend with REST endpoints
  - [ ] User authentication endpoints
  - [ ] Library management endpoints
  - [ ] Game browsing and search endpoints
  - [ ] Platform configuration endpoints
  - [ ] Sync operation endpoints
- [ ] Create React frontend with basic functionality
  - [ ] User login and session management
  - [ ] Library browsing interface (grid/list views)
  - [ ] Game detail pages
  - [ ] Platform configuration interface
  - [ ] Sync status and progress tracking
- [ ] Implement authentication and session management
  - [ ] Single admin user setup for homelab
  - [ ] JWT token generation and validation
  - [ ] Redis-based session storage
  - [ ] MCP server API key protection
  - [ ] Session timeout and refresh logic
- [ ] Add WebSocket integration for real-time updates
  - [ ] Sync progress streaming
  - [ ] Real-time notifications
  - [ ] Connection management
- [ ] Create responsive UI components
  - [ ] Game cards with cover art
  - [ ] Search and filter interface
  - [ ] Platform status indicators
  - [ ] Progress bars and loading states

## Key Technical Decisions

### Authentication Strategy
- **Web Interface**: JWT-based authentication with environment-configurable admin user
- **MCP Server**: API key authentication for external clients
- **Session Storage**: Redis for scalability and persistence
- **Admin Configuration**: Username/password via environment variables

### Database Design
- **Primary Database**: PostgreSQL with JSONB for flexible platform data
- **Connection Pooling**: SQLAlchemy with asyncpg for async operations
- **Migration Management**: Alembic for schema versioning

### Platform Integration
- **Steam First**: Start with Steam Web API as primary platform
- **Steam Integration Depth**: Include playtime, achievements, ratings, and maturity data
- **Data Enrichment**: IGDB API as primary metadata source (RAWG removed)
- **Future Platforms**: Architecture supports easy addition of other platforms

### API Architecture
- **Backend**: FastAPI with async/await throughout
- **Frontend**: React with Vite for modern development experience
- **Real-time**: WebSocket for sync progress and notifications
- **Documentation**: Auto-generated OpenAPI specs

## Success Criteria

Phase 1 will be considered successful when:

- [ ] **Steam Library Sync**: Complete end-to-end Steam library synchronization
- [ ] **MCP Server Functional**: All core tools working with external MCP clients
- [ ] **Web Interface**: Basic library browsing and platform management
- [ ] **Game Metadata**: Enrichment from IGDB API functional with comprehensive data
- [ ] **Authentication**: Secure admin access to web interface
- [ ] **Real-time Updates**: WebSocket sync progress working

## Testing Strategy

**Testing Scope**: Basic unit tests for core functionality with automated MCP tool testing

### Unit Tests
- [ ] Database model tests
- [ ] Steam integration tests
- [ ] IGDB integration tests
- [ ] MCP tool function tests
- [ ] API endpoint tests
- [ ] Authentication flow tests

### Integration Tests
- [ ] End-to-end Steam sync flow
- [ ] MCP server tool responses
- [ ] Web interface user flows
- [ ] Database migration tests
- [ ] External API integration tests

### Manual Testing
- [ ] Steam API connection and comprehensive data fetching
- [ ] MCP client connection (Claude Desktop)
- [ ] Web interface usability and data presentation
- [ ] IGDB metadata enrichment accuracy
- [ ] Error handling and recovery

## Development Workflow

### Environment Setup
```bash
# Initial setup
make setup

# Start development environment
make dev

# Run tests
make test

# Database operations
make db-migrate
make db-seed
```

### Service Development Order
1. **RAWG Cleanup** - Remove all RAWG references from existing code/docs
2. **Database Setup** - Get PostgreSQL running with schema
3. **MCP Server** - Core functionality for AI integration
4. **Steam Integration** - Comprehensive Steam API integration
5. **IGDB Integration** - Primary metadata enrichment service
6. **Web Backend** - FastAPI with environment-based authentication
7. **Web Frontend** - React interface (functional but architecturally sound)
8. **Integration** - Connect all services together

## Notes

### Phase 1 Focus
- **Steam Only**: Focus entirely on Steam platform (defer other platforms)
- **Comprehensive Steam Data**: Include all available data (games, playtime, achievements, ratings)
- **IGDB Metadata**: Rich game metadata from IGDB API
- **Functional UI**: Basic but well-architected interface for future polish
- **Local Development**: All services running locally via Docker Compose
- **Environment-Based Auth**: Configurable admin credentials

### External Dependencies
- **Steam Web API Key**: Required for Steam integration
- **IGDB Client ID & Access Token**: Required for game metadata enrichment
- **Environment Variables**: Admin credentials configurable via .env

### Performance Considerations
- **Rate Limiting**: Implement for all external API calls
- **Caching**: Redis for session data and API response caching
- **Database Indexes**: Optimize for search and filtering operations
- **Connection Pooling**: Proper database connection management

### Security Considerations
- **API Keys**: Secure storage and rotation capability
- **JWT Secrets**: Strong secret key generation
- **Input Validation**: All user inputs properly validated
- **SQL Injection**: Use parameterized queries throughout
- **CORS**: Proper configuration for web interface

## Next Steps After Phase 1

Once Phase 1 is complete, Phase 2 will focus on:
1. **AI Service Integration** - LangChain agent with Ollama
2. **Enhanced Web Features** - AI chat interface and analytics
3. **Advanced MCP Tools** - Smarter recommendations and insights
4. **Performance Optimization** - Caching, background jobs, optimizations

This phase establishes the foundational infrastructure needed for all future development and proves the core concept with a working single-platform system.