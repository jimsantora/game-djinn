# Game Djinn MCP Tools Specification

## Overview

Game Djinn exposes gaming library management capabilities through the Model Context Protocol (MCP). These tools enable AI assistants to interact with gaming libraries, perform searches, sync data, and provide insights.

## Authentication

- **API Key**: Required in `X-API-Key` header
- **Environment Variable**: `MCP_API_KEY`
- **Security**: API key should be generated with high entropy

## Base URL

- **Development**: `http://localhost:8080`
- **Production**: `http://mcp-server:8080` (internal)

## Tool Categories

### Platform Management

#### `get_supported_platforms`

List all supported gaming platforms.

**Parameters**: None

**Returns**:
```json
{
  "platforms": [
    {
      "platform_code": "steam",
      "platform_name": "Steam",
      "api_available": true,
      "setup_required": false
    },
    {
      "platform_code": "xbox",
      "platform_name": "Xbox Game Pass",
      "api_available": true,
      "setup_required": true
    }
  ]
}
```

**Usage Examples**:
- "What platforms does Game Djinn support?"
- "List available gaming platforms"
- "Which platforms have API integration?"

---

#### `add_platform_library`

Add a new user library for a platform.

**Parameters**:
- `platform_code` (string, required): Platform identifier (steam, xbox, gog, etc.)
- `user_identifier` (string, required): Platform-specific user ID
- `display_name` (string, required): Friendly name for the library
- `credentials` (object, optional): Platform-specific authentication data

**Returns**:
```json
{
  "library_id": "123e4567-e89b-12d3-a456-426614174000",
  "platform_code": "steam",
  "display_name": "My Steam Library",
  "sync_status": "pending",
  "created_at": "2024-07-20T12:00:00Z"
}
```

**Usage Examples**:
- "Add my Steam library with ID 76561198000000000"
- "Connect my Xbox Game Pass account"
- "Set up GOG library for user GamerTag123"

---

#### `sync_platform_library`

Trigger synchronization for a platform library.

**Parameters**:
- `library_id` (string, required): UUID of the library to sync
- `force` (boolean, optional): Force sync even if recently synced
- `sync_type` (string, optional): full_sync, incremental_sync (default: incremental_sync)

**Returns**:
```json
{
  "operation_id": "456e7890-e89b-12d3-a456-426614174001",
  "library_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "started",
  "operation_type": "incremental_sync",
  "estimated_duration_minutes": 5
}
```

**Usage Examples**:
- "Sync my Steam library"
- "Update games from Xbox Game Pass"
- "Force a full sync of all libraries"

---

### Game Discovery

#### `search_games`

Search for games across all platforms and libraries.

**Parameters**:
- `query` (string, required): Search terms
- `platform_filter` (array, optional): Filter by platform codes
- `status_filter` (array, optional): Filter by game status (unplayed, playing, completed, etc.)
- `rating_filter` (object, optional): Filter by ratings (min/max metacritic, user rating)
- `genre_filter` (array, optional): Filter by genres
- `owned_only` (boolean, optional): Show only owned games (default: false)
- `limit` (integer, optional): Max results (default: 20, max: 100)

**Returns**:
```json
{
  "games": [
    {
      "game_id": "789e0123-e89b-12d3-a456-426614174002",
      "title": "The Witcher 3: Wild Hunt",
      "developer": "CD Projekt Red",
      "release_date": "2015-05-19",
      "genres": ["RPG", "Open World"],
      "esrb_rating": "M",
      "metacritic_score": 93,
      "cover_image_url": "https://example.com/cover.jpg",
      "owned_platforms": ["steam", "gog"],
      "user_status": "completed",
      "user_rating": 5,
      "total_playtime_hours": 127
    }
  ],
  "total_results": 1,
  "search_time_ms": 42
}
```

**Usage Examples**:
- "Find RPG games I haven't played yet"
- "Search for 'witcher' in my Steam library"
- "Show me highly rated games from 2023"

---

#### `get_game_details`

Get comprehensive information about a specific game.

**Parameters**:
- `game_id` (string, required): UUID of the game
- `library_id` (string, optional): Include user-specific data from this library

**Returns**:
```json
{
  "game_id": "789e0123-e89b-12d3-a456-426614174002",
  "title": "The Witcher 3: Wild Hunt",
  "description": "As war rages on throughout the Northern Realms...",
  "developer": "CD Projekt Red",
  "publisher": "CD Projekt",
  "release_date": "2015-05-19",
  "genres": ["RPG", "Open World", "Fantasy"],
  "tags": ["Singleplayer", "Story Rich", "Choices Matter"],
  "esrb_rating": "M",
  "esrb_descriptors": ["Blood and Gore", "Intense Violence", "Nudity"],
  "metacritic_score": 93,
  "steam_score": 96,
  "playtime_main_hours": 51,
  "playtime_completionist_hours": 173,
  "platforms_available": ["steam", "gog", "xbox", "playstation"],
  "external_ids": {
    "steam_appid": 292030
  },
  "media": {
    "cover_image_url": "https://example.com/cover.jpg",
    "screenshots": ["https://example.com/screen1.jpg"],
    "videos": [{"type": "trailer", "url": "https://example.com/trailer.mp4"}]
  },
  "user_data": {
    "owned": true,
    "total_playtime_minutes": 7620,
    "last_played_at": "2024-01-15T14:30:00Z",
    "game_status": "completed",
    "user_rating": 5,
    "is_favorite": true,
    "user_notes": "Amazing story and side quests!"
  }
}
```

**Usage Examples**:
- "Tell me about The Witcher 3"
- "Show details for this game including my playtime"
- "What's the ESRB rating and why?"

---

### Analytics & Insights

#### `analyze_gaming_patterns`

Analyze gaming patterns and provide insights.

**Parameters**:
- `library_id` (string, optional): Analyze specific library (default: all libraries)
- `time_period` (string, optional): week, month, quarter, year, all (default: month)
- `include_predictions` (boolean, optional): Include ML-based predictions (default: true)

**Returns**:
```json
{
  "period": "month",
  "total_playtime_hours": 45.5,
  "games_played": 12,
  "new_games_started": 3,
  "games_completed": 2,
  "avg_session_duration_minutes": 85,
  "most_played_genre": "RPG",
  "completion_rate_percent": 67,
  "favorite_play_times": ["evening", "weekend"],
  "patterns": {
    "trending_up": ["indie_games", "roguelike"],
    "trending_down": ["fps", "sports"]
  },
  "recommendations": [
    {
      "type": "new_game",
      "game_title": "Disco Elysium",
      "reason": "Based on your love for story-rich RPGs",
      "confidence": 0.85
    }
  ],
  "achievements": {
    "unlocked_this_period": 15,
    "completion_percentage": 23.4
  }
}
```

**Usage Examples**:
- "Analyze my gaming patterns this month"
- "What are my gaming trends?"
- "Show me insights about my playtime"

---

#### `recommend_games`

Get personalized game recommendations.

**Parameters**:
- `library_id` (string, optional): Base recommendations on specific library
- `criteria` (object, optional): Recommendation criteria
  - `genres` (array): Preferred genres
  - `max_playtime_hours` (integer): Maximum game length
  - `min_rating` (integer): Minimum metacritic score
  - `platforms` (array): Available platforms
- `limit` (integer, optional): Number of recommendations (default: 10)
- `include_owned` (boolean, optional): Include already owned games (default: false)

**Returns**:
```json
{
  "recommendations": [
    {
      "game_id": "abc12345-e89b-12d3-a456-426614174003",
      "title": "Disco Elysium",
      "recommendation_score": 0.92,
      "reasons": [
        "Story-rich RPG matching your preferences",
        "Highly rated by users with similar taste",
        "Perfect length for your typical gaming sessions"
      ],
      "match_factors": {
        "genre_match": 0.95,
        "rating_match": 0.88,
        "playtime_match": 0.90
      },
      "game_info": {
        "developer": "ZA/UM",
        "genres": ["RPG", "Indie"],
        "metacritic_score": 91,
        "estimated_playtime_hours": 25,
        "available_platforms": ["steam", "gog"]
      }
    }
  ],
  "recommendation_basis": "Based on your completed RPGs and preferred story-rich games",
  "total_candidates_analyzed": 1547
}
```

**Usage Examples**:
- "Recommend some new games for me"
- "Find RPG games similar to what I've enjoyed"
- "Suggest games I can finish in under 20 hours"

---

### Content Filtering

#### `filter_by_content_rating`

Filter games by ESRB content ratings for family-friendly viewing.

**Parameters**:
- `max_rating` (string, required): Maximum ESRB rating (E, E10+, T, M)
- `library_id` (string, optional): Filter specific library
- `exclude_descriptors` (array, optional): Exclude games with specific content descriptors
- `include_unrated` (boolean, optional): Include unrated games (default: true)

**Returns**:
```json
{
  "filtered_games": [
    {
      "game_id": "def45678-e89b-12d3-a456-426614174004",
      "title": "Among Us",
      "esrb_rating": "E10+",
      "esrb_descriptors": ["Fantasy Violence", "Mild Blood"],
      "safe_for_rating": "E10+",
      "genres": ["Party", "Multiplayer"],
      "user_owned": true
    }
  ],
  "filter_criteria": {
    "max_rating": "E10+",
    "excluded_descriptors": [],
    "total_games_filtered": 156,
    "games_passed_filter": 23
  },
  "content_warnings": []
}
```

**Usage Examples**:
- "Show me games appropriate for teenagers"
- "Filter my library for E-rated games only"
- "What games can kids play from my collection?"

---

### Advanced Features

#### `get_cross_platform_games`

Find games owned on multiple platforms.

**Parameters**: None

**Returns**:
```json
{
  "cross_platform_games": [
    {
      "game_id": "789e0123-e89b-12d3-a456-426614174002",
      "title": "The Witcher 3: Wild Hunt",
      "owned_platforms": [
        {
          "platform_code": "steam",
          "library_name": "Main Steam Library",
          "playtime_minutes": 7620,
          "achievements_unlocked": 45
        },
        {
          "platform_code": "gog",
          "library_name": "GOG Collection",
          "playtime_minutes": 0,
          "achievements_unlocked": 0
        }
      ],
      "total_playtime_minutes": 7620,
      "preferred_platform": "steam"
    }
  ],
  "summary": {
    "total_cross_platform_games": 12,
    "most_common_duplicate": "steam_gog",
    "potential_savings": "$127.45"
  }
}
```

**Usage Examples**:
- "Which games do I own on multiple platforms?"
- "Show my duplicate game purchases"
- "Find games I have on both Steam and GOG"

---

#### `export_library_data`

Export user library data in various formats.

**Parameters**:
- `library_id` (string, optional): Export specific library (default: all)
- `format` (string, required): json, csv, xlsx
- `include_fields` (array, optional): Specific fields to include
- `filters` (object, optional): Filter criteria for export

**Returns**:
```json
{
  "export_id": "export_123456789",
  "format": "csv",
  "download_url": "/downloads/export_123456789.csv",
  "file_size_bytes": 45672,
  "games_exported": 234,
  "expires_at": "2024-07-21T12:00:00Z",
  "export_summary": {
    "total_games": 234,
    "total_playtime_hours": 1547.5,
    "libraries_included": ["Steam", "Xbox Game Pass"],
    "export_date": "2024-07-20T12:00:00Z"
  }
}
```

**Usage Examples**:
- "Export my Steam library to CSV"
- "Create a backup of all my game data"
- "Generate an Excel report of my gaming stats"

---

#### `create_smart_collection`

Create auto-updating game collections based on rules.

**Parameters**:
- `library_id` (string, required): Library to create collection in
- `name` (string, required): Collection name
- `rules` (object, required): Collection rules
  - `genres` (array, optional): Include games with these genres
  - `rating_range` (object, optional): Min/max rating filters
  - `playtime_range` (object, optional): Min/max playtime filters
  - `status` (array, optional): Include games with these statuses
  - `platforms` (array, optional): Include games from these platforms
  - `release_date_range` (object, optional): Date range filters

**Returns**:
```json
{
  "collection_id": "collection_123456",
  "name": "Unfinished RPGs",
  "is_smart": true,
  "rules": {
    "genres": ["RPG"],
    "status": ["unplayed", "playing"],
    "rating_range": {"min": 80}
  },
  "current_games_count": 15,
  "auto_update": true,
  "created_at": "2024-07-20T12:00:00Z"
}
```

**Usage Examples**:
- "Create a collection of unfinished RPG games"
- "Make a smart collection for highly rated indie games"
- "Auto-collect games I should play next"

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "LIBRARY_NOT_FOUND",
    "message": "Library with ID 'invalid-id' not found",
    "details": {
      "library_id": "invalid-id",
      "valid_libraries": ["lib1", "lib2"]
    },
    "timestamp": "2024-07-20T12:00:00Z"
  }
}
```

### Common Error Codes

- `INVALID_API_KEY`: Authentication failed
- `LIBRARY_NOT_FOUND`: Specified library doesn't exist
- `GAME_NOT_FOUND`: Specified game doesn't exist
- `SYNC_IN_PROGRESS`: Cannot start sync, operation already running
- `RATE_LIMIT_EXCEEDED`: Too many requests, try again later
- `PLATFORM_API_ERROR`: External platform API error
- `INVALID_PARAMETERS`: Missing or invalid parameters
- `INTERNAL_ERROR`: Server-side error

## Rate Limiting

- **Per IP**: 100 requests per minute
- **Per API Key**: 1000 requests per minute
- **Sync Operations**: 1 per library per 5 minutes
- **Export Operations**: 5 per hour

## Webhooks (Future Enhancement)

Game Djinn will support webhooks for real-time updates:

- `sync.completed`: Library sync finished
- `game.added`: New game added to library
- `achievement.unlocked`: Achievement unlocked
- `recommendation.available`: New recommendations ready

## Integration Examples

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "game-djinn": {
      "command": "node",
      "args": ["path/to/mcp-client.js"],
      "env": {
        "MCP_SERVER_URL": "http://localhost:8080",
        "MCP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Common Use Cases

1. **Library Management**: "Sync my Steam library and show me new games"
2. **Game Discovery**: "Find unplayed RPGs with high ratings"
3. **Analytics**: "How much did I play this month?"
4. **Family Features**: "Show games safe for kids"
5. **Collection Management**: "Create a collection of short games"