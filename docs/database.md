# Game Djinn Database Documentation

## Overview

Game Djinn uses PostgreSQL with JSONB for flexible platform data storage. The database is designed to handle multiple gaming platforms while maintaining data consistency and enabling cross-platform game matching.

## Architecture Principles

- **Platform Agnostic**: Schema supports any gaming platform
- **Flexible Metadata**: JSONB columns for platform-specific data
- **Search Optimized**: Full-text search with tsvector
- **Audit Trail**: Created/updated timestamps on all tables
- **Performance**: Strategic indexing for common queries

## Core Tables

### `platforms`
Registry of supported gaming platforms.

**Key Fields:**
- `platform_code`: Unique identifier (steam, xbox, gog, etc.)
- `api_available`: Whether platform has programmatic API access
- `base_url`: Platform's website URL

### `user_libraries`
User accounts on different platforms.

**Key Relationships:**
- Belongs to one `platform`
- Has many `user_games`
- Has many `game_collections`

**Sync Management:**
- `sync_status`: Current sync state
- `sync_position`: Resumable sync checkpoint
- `last_sync_at`: Last successful sync timestamp

### `games`
Universal game catalog with rich metadata.

**Content Ratings:**
- `esrb_rating`: E, E10+, T, M, AO, RP
- `pegi_rating`: 3, 7, 12, 16, 18

**External IDs:**
- `steam_appid`: Steam application ID
- `igdb_id`: Internet Game Database ID

**Search Features:**
- `search_vector`: Full-text search index
- `normalized_title`: Cleaned title for matching

### `user_games`
User-specific game data and preferences.

**Status Values:**
- `unplayed`: Owned but never played
- `playing`: Currently being played
- `completed`: Finished the main story
- `abandoned`: Started but stopped playing
- `wishlist`: Desired but not owned

**Platform Integration:**
- `platform_game_id`: Platform's internal game identifier
- `platform_data`: JSONB for platform-specific fields

## Relationship Diagram

```
platforms (1) ──────── (*) user_libraries
                            │
                            │ (1)
                            │
                            ▼ (*)
                       user_games ────── (*) games (1)
                            │
                            │ (1)
                            │
                            ▼ (*)
                    user_achievements ──── (*) game_achievements (1)
                                                │
                                                │ (*)
                                                │
                                                ▼ (1)
                                              games

user_libraries (1) ──── (*) game_collections ──── (*) collection_games ──── (*) games

games (1) ──── (*) game_matches ──── (*) games (1)
```

## Key Features

### Cross-Platform Game Matching

Games can be matched across platforms using:
- **Exact Title Match**: Identical normalized titles
- **Fuzzy Title Match**: Similar titles with confidence score
- **External ID Match**: Shared IGDB identifiers
- **Manual Match**: User-verified matches

The `game_matches` table tracks these relationships with confidence scores.

### Smart Collections

Collections can be:
- **Static**: Manually curated game lists
- **Smart**: Auto-updating based on JSON rules

Smart collection rules support:
- Genre filtering
- Rating thresholds
- Playtime ranges
- Platform restrictions
- Release date ranges

### Full-Text Search

Games are searchable by:
- Title (weight A - highest)
- Developer/Publisher (weight B)
- Description (weight C - lowest)

Search vector is automatically maintained via triggers.

### Sync Management

Platform sync operations are tracked with:
- Operation type (full, incremental, manual)
- Progress metrics (processed, added, updated)
- Error handling and retry logic
- Resumable positions for large syncs

## Performance Considerations

### Indexes

Critical indexes for performance:
- `games.normalized_title` - Game matching
- `games.search_vector` (GIN) - Full-text search
- `user_games.library_id` - User data queries
- `user_games.game_status` - Status filtering
- Platform-specific ID indexes - External lookups

### Query Patterns

Common queries optimized:
- User library browsing
- Cross-platform game lookup
- Search with filters
- Sync status monitoring
- Collection management

### Data Types

- **UUIDs**: All primary keys for distributed scaling
- **JSONB**: Flexible platform data with indexing
- **Enums**: Consistent status values
- **tsvector**: Optimized full-text search

## Security Considerations

### Sensitive Data

- `api_credentials`: Should be encrypted at application level
- User identifiers: Platform-specific, not personal data
- Game preferences: User-controlled visibility

### Access Patterns

- Single admin user for homelab deployment
- Platform credentials stored per library
- MCP server API key protection

## Migration Strategy

### Alembic Integration

- Version-controlled schema changes
- Automatic migration on deployment
- Rollback capability for safety
- Environment variable configuration

### Data Migration

When adding new platforms:
1. Insert platform definition
2. Add platform-specific columns if needed
3. Update enum types if necessary
4. Migrate existing data if applicable

## Backup Strategy

### Regular Backups

- Daily PostgreSQL dumps
- Schema and data included
- Compressed storage
- Retention policy (30 days)

### Point-in-Time Recovery

- WAL archiving for PITR
- Testing restore procedures
- Documentation for recovery

## Development Guidelines

### Adding New Platforms

1. Insert platform record
2. Update API integration
3. Add platform-specific fields to JSONB
4. Update sync logic
5. Test cross-platform matching

### Schema Changes

1. Create Alembic migration
2. Test on sample data
3. Document breaking changes
4. Plan deployment strategy
5. Communicate to users

### Performance Monitoring

- Query execution plans
- Index usage statistics
- Table size monitoring
- Slow query identification