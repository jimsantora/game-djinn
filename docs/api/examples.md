# API Examples

This document provides practical examples of using the Game Djinn APIs, including both the Web Service REST API and MCP Tools.

## Authentication

### Web Service Login

**Request:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@gamedjinn.local",
    "password": "your-password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### MCP Authentication

All MCP requests require an API key in the header:

```bash
curl -H "X-API-Key: your-mcp-api-key" \
  http://localhost:8080/tools/get_supported_platforms
```

## Platform Management

### List Supported Platforms

**Web API:**
```bash
curl http://localhost:8000/platforms
```

**MCP Tool:**
```bash
curl -H "X-API-Key: your-mcp-api-key" \
  -X POST http://localhost:8080/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_supported_platforms",
    "arguments": {}
  }'
```

**Response:**
```json
{
  "platforms": [
    {
      "platform_id": "550e8400-e29b-41d4-a716-446655440000",
      "platform_code": "steam",
      "platform_name": "Steam",
      "api_available": true,
      "icon_url": "https://steamcdn-a.akamaihd.net/steam/apps/APPID/header.jpg",
      "created_at": "2024-07-20T10:00:00Z"
    },
    {
      "platform_id": "550e8400-e29b-41d4-a716-446655440001",
      "platform_code": "xbox",
      "platform_name": "Xbox Game Pass",
      "api_available": true,
      "icon_url": null,
      "created_at": "2024-07-20T10:00:00Z"
    }
  ]
}
```

### Add Steam Library

**Web API:**
```bash
curl -X POST http://localhost:8000/platforms/550e8400-e29b-41d4-a716-446655440000/libraries \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "user_identifier": "76561198000000000",
    "display_name": "My Steam Library",
    "api_credentials": {
      "steam_api_key": "ABCDEF1234567890"
    }
  }'
```

**MCP Tool:**
```bash
curl -H "X-API-Key: your-mcp-api-key" \
  -X POST http://localhost:8080/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "add_platform_library",
    "arguments": {
      "platform_code": "steam",
      "user_identifier": "76561198000000000",
      "display_name": "My Steam Library",
      "credentials": {
        "steam_api_key": "ABCDEF1234567890"
      }
    }
  }'
```

**Response:**
```json
{
  "library_id": "123e4567-e89b-12d3-a456-426614174000",
  "platform": {
    "platform_code": "steam",
    "platform_name": "Steam"
  },
  "display_name": "My Steam Library",
  "sync_enabled": true,
  "sync_status": "pending",
  "games_count": 0,
  "created_at": "2024-07-20T12:00:00Z"
}
```

## Library Synchronization

### Trigger Library Sync

**Web API:**
```bash
curl -X POST http://localhost:8000/libraries/123e4567-e89b-12d3-a456-426614174000/sync \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

**MCP Tool:**
```bash
curl -H "X-API-Key: your-mcp-api-key" \
  -X POST http://localhost:8080/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sync_platform_library",
    "arguments": {
      "library_id": "123e4567-e89b-12d3-a456-426614174000",
      "force": false,
      "sync_type": "incremental_sync"
    }
  }'
```

**Response:**
```json
{
  "operation_id": "456e7890-e89b-12d3-a456-426614174001",
  "library_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "started",
  "operation_type": "incremental_sync",
  "started_at": "2024-07-20T12:05:00Z",
  "estimated_duration_minutes": 5,
  "games_processed": 0,
  "games_added": 0,
  "games_updated": 0
}
```

## Game Search and Discovery

### Search Games

**Web API with Filters:**
```bash
curl "http://localhost:8000/games/search?q=witcher&esrb_rating=M&limit=5" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**MCP Tool:**
```bash
curl -H "X-API-Key: your-mcp-api-key" \
  -X POST http://localhost:8080/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "search_games",
    "arguments": {
      "query": "witcher",
      "rating_filter": {
        "min_metacritic": 80
      },
      "genre_filter": ["RPG"],
      "owned_only": false,
      "limit": 5
    }
  }'
```

**Response:**
```json
{
  "games": [
    {
      "game_id": "789e0123-e89b-12d3-a456-426614174002",
      "title": "The Witcher 3: Wild Hunt",
      "developer": "CD Projekt Red",
      "publisher": "CD Projekt",
      "release_date": "2015-05-19",
      "genres": ["RPG", "Open World", "Fantasy"],
      "esrb_rating": "M",
      "metacritic_score": 93,
      "cover_image_url": "https://cdn.akamai.steamstatic.com/steam/apps/292030/header.jpg",
      "owned_platforms": ["steam"],
      "user_status": "completed",
      "user_rating": 5,
      "total_playtime_hours": 127.5
    }
  ],
  "total_results": 1,
  "search_time_ms": 42
}
```

### Get Game Details

**Web API:**
```bash
curl http://localhost:8000/games/789e0123-e89b-12d3-a456-426614174002 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**MCP Tool:**
```bash
curl -H "X-API-Key: your-mcp-api-key" \
  -X POST http://localhost:8080/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_game_details",
    "arguments": {
      "game_id": "789e0123-e89b-12d3-a456-426614174002",
      "library_id": "123e4567-e89b-12d3-a456-426614174000"
    }
  }'
```

**Response:**
```json
{
  "game_id": "789e0123-e89b-12d3-a456-426614174002",
  "title": "The Witcher 3: Wild Hunt",
  "description": "As war rages on throughout the Northern Realms, you take on the greatest contract of your life — tracking down the Child of Prophecy.",
  "short_description": "An open-world RPG masterpiece with rich storytelling.",
  "developer": "CD Projekt Red",
  "publisher": "CD Projekt",
  "release_date": "2015-05-19",
  "genres": ["RPG", "Open World", "Fantasy"],
  "tags": ["Singleplayer", "Story Rich", "Choices Matter", "Medieval"],
  "esrb_rating": "M",
  "esrb_descriptors": ["Blood and Gore", "Intense Violence", "Nudity", "Strong Language"],
  "metacritic_score": 93,
  "steam_score": 96,
  "playtime_main_hours": 51,
  "playtime_completionist_hours": 173,
  "platforms_available": ["steam", "gog", "xbox", "playstation"],
  "external_ids": {
    "steam_appid": 292030,
    "igdb_id": 1942
  },
  "media": {
    "cover_image_url": "https://cdn.akamai.steamstatic.com/steam/apps/292030/header.jpg",
    "background_image_url": "https://cdn.akamai.steamstatic.com/steam/apps/292030/page_bg_generated_v6b.jpg",
    "screenshots": [
      "https://cdn.akamai.steamstatic.com/steam/apps/292030/ss_1.jpg",
      "https://cdn.akamai.steamstatic.com/steam/apps/292030/ss_2.jpg"
    ]
  },
  "user_data": {
    "owned": true,
    "total_playtime_minutes": 7650,
    "last_played_at": "2024-01-15T14:30:00Z",
    "first_played_at": "2023-12-01T19:00:00Z",
    "game_status": "completed",
    "user_rating": 5,
    "is_favorite": true,
    "user_notes": "One of the best RPGs ever made!"
  }
}
```

## User Game Management

### Update Game Status and Rating

**Web API:**
```bash
curl -X PATCH http://localhost:8000/user-games/abc12345-e89b-12d3-a456-426614174003 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "game_status": "completed",
    "user_rating": 4,
    "is_favorite": true,
    "user_notes": "Great game but a bit long"
  }'
```

**Response:**
```json
{
  "user_game_id": "abc12345-e89b-12d3-a456-426614174003",
  "game": {
    "game_id": "789e0123-e89b-12d3-a456-426614174002",
    "title": "Cyberpunk 2077",
    "cover_image_url": "https://cdn.akamai.steamstatic.com/steam/apps/1091500/header.jpg"
  },
  "owned": true,
  "total_playtime_minutes": 1440,
  "last_played_at": "2024-07-18T20:15:00Z",
  "game_status": "completed",
  "user_rating": 4,
  "is_favorite": true,
  "user_notes": "Great game but a bit long"
}
```

## Analytics and Insights

### Gaming Pattern Analysis

**MCP Tool:**
```bash
curl -H "X-API-Key: your-mcp-api-key" \
  -X POST http://localhost:8080/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "analyze_gaming_patterns",
    "arguments": {
      "library_id": "123e4567-e89b-12d3-a456-426614174000",
      "time_period": "month",
      "include_predictions": true
    }
  }'
```

**Response:**
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
    },
    {
      "type": "backlog",
      "game_title": "Hollow Knight",
      "reason": "Short sessions, high rating, matches trending genres",
      "confidence": 0.78
    }
  ],
  "achievements": {
    "unlocked_this_period": 15,
    "completion_percentage": 23.4,
    "rarest_achievement": "Master Difficulty Completion"
  }
}
```

### Game Recommendations

**MCP Tool:**
```bash
curl -H "X-API-Key: your-mcp-api-key" \
  -X POST http://localhost:8080/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "recommend_games",
    "arguments": {
      "library_id": "123e4567-e89b-12d3-a456-426614174000",
      "criteria": {
        "genres": ["RPG", "Indie"],
        "max_playtime_hours": 30,
        "min_rating": 85,
        "platforms": ["steam", "gog"]
      },
      "limit": 3,
      "include_owned": false
    }
  }'
```

**Response:**
```json
{
  "recommendations": [
    {
      "game_id": "def45678-e89b-12d3-a456-426614174004",
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
        "available_platforms": ["steam", "gog"],
        "cover_image_url": "https://cdn.akamai.steamstatic.com/steam/apps/632470/header.jpg"
      }
    }
  ],
  "recommendation_basis": "Based on your completed RPGs and preferred story-rich games",
  "total_candidates_analyzed": 1547
}
```

## Content Filtering

### Family-Friendly Game Filter

**MCP Tool:**
```bash
curl -H "X-API-Key: your-mcp-api-key" \
  -X POST http://localhost:8080/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "filter_by_content_rating",
    "arguments": {
      "max_rating": "E10+",
      "library_id": "123e4567-e89b-12d3-a456-426614174000",
      "exclude_descriptors": ["Violence", "Blood"],
      "include_unrated": false
    }
  }'
```

**Response:**
```json
{
  "filtered_games": [
    {
      "game_id": "ghi78901-e89b-12d3-a456-426614174005",
      "title": "Among Us",
      "esrb_rating": "E10+",
      "esrb_descriptors": ["Fantasy Violence", "Mild Blood"],
      "safe_for_rating": "E10+",
      "genres": ["Party", "Multiplayer"],
      "user_owned": true,
      "total_playtime_minutes": 180
    }
  ],
  "filter_criteria": {
    "max_rating": "E10+",
    "excluded_descriptors": ["Violence", "Blood"],
    "total_games_filtered": 156,
    "games_passed_filter": 23
  },
  "content_warnings": [
    "Some games may have user-generated content not covered by ESRB ratings"
  ]
}
```

## Collections Management

### Create Smart Collection

**Web API:**
```bash
curl -X POST http://localhost:8000/libraries/123e4567-e89b-12d3-a456-426614174000/collections \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Unfinished RPGs",
    "description": "RPG games I still need to complete",
    "color": "#8b5cf6",
    "icon": "sword",
    "is_smart": true,
    "rules": {
      "genres": ["RPG"],
      "status": ["unplayed", "playing"],
      "rating_range": {
        "min_metacritic": 75
      }
    }
  }'
```

**MCP Tool:**
```bash
curl -H "X-API-Key: your-mcp-api-key" \
  -X POST http://localhost:8080/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "create_smart_collection",
    "arguments": {
      "library_id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Unfinished RPGs",
      "rules": {
        "genres": ["RPG"],
        "status": ["unplayed", "playing"],
        "rating_range": {
          "min": 75
        }
      }
    }
  }'
```

**Response:**
```json
{
  "collection_id": "jkl90123-e89b-12d3-a456-426614174006",
  "name": "Unfinished RPGs",
  "description": "RPG games I still need to complete",
  "color": "#8b5cf6",
  "icon": "sword",
  "is_smart": true,
  "rules": {
    "genres": ["RPG"],
    "status": ["unplayed", "playing"],
    "rating_range": {
      "min_metacritic": 75
    }
  },
  "current_games_count": 15,
  "auto_update": true,
  "created_at": "2024-07-20T12:30:00Z"
}
```

## Error Handling Examples

### Invalid Library ID

**Request:**
```bash
curl -H "X-API-Key: your-mcp-api-key" \
  -X POST http://localhost:8080/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sync_platform_library",
    "arguments": {
      "library_id": "invalid-library-id"
    }
  }'
```

**Error Response:**
```json
{
  "error": {
    "code": "LIBRARY_NOT_FOUND",
    "message": "Library with ID 'invalid-library-id' not found",
    "details": {
      "library_id": "invalid-library-id",
      "valid_libraries": ["123e4567-e89b-12d3-a456-426614174000"]
    },
    "timestamp": "2024-07-20T12:00:00Z"
  }
}
```

### Rate Limit Exceeded

**Error Response:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED", 
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "details": {
      "limit": 100,
      "window_seconds": 60,
      "retry_after": 60
    },
    "timestamp": "2024-07-20T12:00:00Z"
  }
}
```

### Sync Already in Progress

**Error Response:**
```json
{
  "error": {
    "code": "SYNC_IN_PROGRESS",
    "message": "Library sync is already in progress",
    "details": {
      "library_id": "123e4567-e89b-12d3-a456-426614174000",
      "current_operation_id": "456e7890-e89b-12d3-a456-426614174001",
      "started_at": "2024-07-20T11:55:00Z",
      "estimated_completion": "2024-07-20T12:00:00Z"
    },
    "timestamp": "2024-07-20T12:00:00Z"
  }
}
```

## WebSocket Events

### Connect to WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to Game Djinn WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Sync Progress Update

```json
{
  "type": "sync_progress",
  "data": {
    "operation_id": "456e7890-e89b-12d3-a456-426614174001",
    "library_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "in_progress", 
    "progress_percentage": 45,
    "games_processed": 89,
    "games_total": 198,
    "current_game": "The Witcher 3: Wild Hunt",
    "estimated_completion": "2024-07-20T12:03:00Z"
  }
}
```

## Bulk Operations

### Export Library Data

**MCP Tool:**
```bash
curl -H "X-API-Key: your-mcp-api-key" \
  -X POST http://localhost:8080/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "export_library_data",
    "arguments": {
      "library_id": "123e4567-e89b-12d3-a456-426614174000",
      "format": "csv",
      "include_fields": ["title", "developer", "genres", "playtime", "rating"],
      "filters": {
        "status": ["completed", "playing"],
        "min_playtime_minutes": 60
      }
    }
  }'
```

**Response:**
```json
{
  "export_id": "export_1721462400",
  "format": "csv", 
  "download_url": "/downloads/export_1721462400.csv",
  "file_size_bytes": 45672,
  "games_exported": 87,
  "expires_at": "2024-07-21T12:00:00Z",
  "export_summary": {
    "total_games": 87,
    "total_playtime_hours": 432.5,
    "libraries_included": ["My Steam Library"],
    "export_date": "2024-07-20T12:00:00Z",
    "filters_applied": {
      "status": ["completed", "playing"],
      "min_playtime_minutes": 60
    }
  }
}
```

These examples demonstrate the comprehensive API functionality available in Game Djinn, supporting both direct web API access and MCP tool integration for AI assistants.