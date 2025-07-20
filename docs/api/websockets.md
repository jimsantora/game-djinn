# WebSocket Event Specifications

Game Djinn uses WebSockets for real-time communication between the web interface and backend services, enabling live updates for sync operations, AI chat, and system notifications.

## Connection

### Endpoint
```
ws://localhost:8000/ws
wss://game-djinn.local/ws
```

### Authentication
WebSocket connections require JWT authentication via query parameter:
```
ws://localhost:8000/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Connection Flow
1. Client connects with JWT token
2. Server validates token and establishes connection
3. Server sends `connection_established` event
4. Client can send commands and receive events

## Message Format

All WebSocket messages follow this structure:

```json
{
  "type": "event_type",
  "data": {},
  "timestamp": "2024-07-20T12:00:00Z",
  "id": "optional-message-id"
}
```

## Client-to-Server Events

### Subscribe to Events

Subscribe to specific event types:

```json
{
  "type": "subscribe",
  "data": {
    "events": ["sync_progress", "ai_chat", "notifications"],
    "filters": {
      "library_id": "123e4567-e89b-12d3-a456-426614174000"
    }
  }
}
```

### Unsubscribe from Events

```json
{
  "type": "unsubscribe", 
  "data": {
    "events": ["sync_progress"]
  }
}
```

### AI Chat Message

Send a message to the AI assistant:

```json
{
  "type": "ai_chat_message",
  "data": {
    "message": "Show me my unplayed RPG games",
    "context": {
      "library_id": "123e4567-e89b-12d3-a456-426614174000",
      "conversation_id": "conv_456789"
    }
  },
  "id": "msg_123456"
}
```

### Ping

Keep connection alive:

```json
{
  "type": "ping",
  "data": {},
  "id": "ping_123"
}
```

## Server-to-Client Events

### Connection Established

Sent when WebSocket connection is successfully established:

```json
{
  "type": "connection_established",
  "data": {
    "user_id": "admin",
    "session_id": "sess_789012",
    "server_time": "2024-07-20T12:00:00Z",
    "features": ["sync_progress", "ai_chat", "notifications"]
  },
  "timestamp": "2024-07-20T12:00:00Z"
}
```

### Pong

Response to ping:

```json
{
  "type": "pong",
  "data": {
    "client_id": "ping_123"
  },
  "timestamp": "2024-07-20T12:00:00Z"
}
```

## Sync Operation Events

### Sync Started

```json
{
  "type": "sync_started",
  "data": {
    "operation_id": "456e7890-e89b-12d3-a456-426614174001",
    "library_id": "123e4567-e89b-12d3-a456-426614174000",
    "library_name": "My Steam Library",
    "operation_type": "incremental_sync",
    "estimated_duration_minutes": 5,
    "total_games_to_process": 198
  },
  "timestamp": "2024-07-20T12:00:00Z"
}
```

### Sync Progress

Real-time progress updates during sync:

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
    "games_added": 3,
    "games_updated": 12,
    "current_game": {
      "title": "The Witcher 3: Wild Hunt",
      "platform_game_id": "292030"
    },
    "rate_per_minute": 18,
    "estimated_completion": "2024-07-20T12:03:00Z",
    "errors_count": 0
  },
  "timestamp": "2024-07-20T12:01:30Z"
}
```

### Sync Completed

```json
{
  "type": "sync_completed",
  "data": {
    "operation_id": "456e7890-e89b-12d3-a456-426614174001",
    "library_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "completed",
    "duration_minutes": 4.5,
    "games_processed": 198,
    "games_added": 5,
    "games_updated": 23,
    "games_removed": 1,
    "errors_count": 0,
    "summary": {
      "new_games": [
        {
          "title": "Baldur's Gate 3",
          "game_id": "new_game_123"
        }
      ],
      "updated_games": [
        {
          "title": "Cyberpunk 2077", 
          "changes": ["playtime_updated", "achievement_unlocked"]
        }
      ]
    }
  },
  "timestamp": "2024-07-20T12:04:30Z"
}
```

### Sync Failed

```json
{
  "type": "sync_failed",
  "data": {
    "operation_id": "456e7890-e89b-12d3-a456-426614174001",
    "library_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "failed",
    "error_code": "PLATFORM_API_ERROR",
    "error_message": "Steam API returned 503 Service Unavailable",
    "games_processed": 45,
    "games_total": 198,
    "can_retry": true,
    "retry_after_seconds": 300,
    "recovery_suggestions": [
      "Check Steam API status",
      "Verify API credentials",
      "Try again in 5 minutes"
    ]
  },
  "timestamp": "2024-07-20T12:02:15Z"
}
```

### Sync Rate Limited

```json
{
  "type": "sync_rate_limited",
  "data": {
    "operation_id": "456e7890-e89b-12d3-a456-426614174001",
    "library_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "rate_limited",
    "platform": "steam",
    "retry_after_seconds": 120,
    "requests_remaining": 0,
    "window_reset_at": "2024-07-20T12:05:00Z",
    "auto_resume": true
  },
  "timestamp": "2024-07-20T12:03:00Z"
}
```

## AI Chat Events

### AI Response Streaming

Streaming AI responses for real-time chat experience:

```json
{
  "type": "ai_chat_response_chunk",
  "data": {
    "conversation_id": "conv_456789",
    "message_id": "msg_123456",
    "chunk": "Based on your library, here are some great unplayed RPG games:",
    "is_final": false,
    "chunk_index": 0
  },
  "timestamp": "2024-07-20T12:00:00Z"
}
```

### AI Response Complete

```json
{
  "type": "ai_chat_response_complete",
  "data": {
    "conversation_id": "conv_456789",
    "message_id": "msg_123456",
    "full_message": "Based on your library, here are some great unplayed RPG games:\n\n1. Baldur's Gate 3 - 95 Metacritic\n2. Disco Elysium - 91 Metacritic\n3. Divinity: Original Sin 2 - 93 Metacritic",
    "tools_used": ["search_games"],
    "response_time_ms": 1250,
    "token_count": 156
  },
  "timestamp": "2024-07-20T12:00:01Z"
}
```

### AI Thinking

Show AI is processing a complex request:

```json
{
  "type": "ai_thinking",
  "data": {
    "conversation_id": "conv_456789",
    "message_id": "msg_123456",
    "status": "thinking",
    "activity": "Analyzing your gaming patterns...",
    "estimated_seconds": 5
  },
  "timestamp": "2024-07-20T12:00:00Z"
}
```

### AI Tool Execution

Show when AI is using MCP tools:

```json
{
  "type": "ai_tool_execution",
  "data": {
    "conversation_id": "conv_456789",
    "message_id": "msg_123456",
    "tool_name": "search_games",
    "tool_parameters": {
      "query": "RPG",
      "status_filter": ["unplayed"],
      "rating_filter": {"min_metacritic": 80}
    },
    "status": "executing"
  },
  "timestamp": "2024-07-20T12:00:00Z"
}
```

### AI Error

```json
{
  "type": "ai_error",
  "data": {
    "conversation_id": "conv_456789",
    "message_id": "msg_123456",
    "error_code": "TOOL_EXECUTION_FAILED",
    "error_message": "Unable to search games: Database connection timeout",
    "is_recoverable": true,
    "suggested_action": "Please try your request again"
  },
  "timestamp": "2024-07-20T12:00:00Z"
}
```

## Game Library Events

### Game Added

```json
{
  "type": "game_added",
  "data": {
    "library_id": "123e4567-e89b-12d3-a456-426614174000",
    "game": {
      "game_id": "new_game_123",
      "title": "Baldur's Gate 3",
      "developer": "Larian Studios",
      "cover_image_url": "https://example.com/bg3.jpg"
    },
    "source": "sync_operation",
    "operation_id": "456e7890-e89b-12d3-a456-426614174001"
  },
  "timestamp": "2024-07-20T12:02:00Z"
}
```

### Game Updated

```json
{
  "type": "game_updated",
  "data": {
    "library_id": "123e4567-e89b-12d3-a456-426614174000",
    "game_id": "789e0123-e89b-12d3-a456-426614174002",
    "changes": {
      "total_playtime_minutes": {
        "old": 7620,
        "new": 7680
      },
      "last_played_at": {
        "old": "2024-07-19T20:00:00Z",
        "new": "2024-07-20T21:00:00Z"
      }
    },
    "source": "sync_operation"
  },
  "timestamp": "2024-07-20T12:02:30Z"
}
```

### Achievement Unlocked

```json
{
  "type": "achievement_unlocked",
  "data": {
    "library_id": "123e4567-e89b-12d3-a456-426614174000",
    "game_id": "789e0123-e89b-12d3-a456-426614174002",
    "game_title": "The Witcher 3: Wild Hunt",
    "achievement": {
      "achievement_id": "ach_12345",
      "title": "Geralt: The Professional",
      "description": "Complete 10 Witcher contracts",
      "icon_url": "https://example.com/ach_icon.jpg",
      "rarity_percentage": 23.4,
      "points": 15
    },
    "unlocked_at": "2024-07-20T21:15:00Z"
  },
  "timestamp": "2024-07-20T21:15:00Z"
}
```

## System Events

### System Notification

```json
{
  "type": "system_notification",
  "data": {
    "level": "info",
    "title": "Platform API Update",
    "message": "Steam Web API is experiencing intermittent issues. Sync operations may be delayed.",
    "action": {
      "type": "url",
      "label": "View Status",
      "url": "https://steamstat.us/"
    },
    "dismissible": true,
    "expires_at": "2024-07-20T18:00:00Z"
  },
  "timestamp": "2024-07-20T12:00:00Z"
}
```

### System Status Update

```json
{
  "type": "system_status_update",
  "data": {
    "component": "steam_api",
    "status": "degraded",
    "message": "Steam API response times elevated",
    "impact": "Sync operations may take longer than usual",
    "estimated_resolution": "2024-07-20T14:00:00Z"
  },
  "timestamp": "2024-07-20T12:00:00Z"
}
```

### Maintenance Mode

```json
{
  "type": "maintenance_mode",
  "data": {
    "status": "starting",
    "message": "System maintenance starting in 5 minutes",
    "duration_minutes": 30,
    "scheduled_start": "2024-07-20T13:00:00Z",
    "scheduled_end": "2024-07-20T13:30:00Z",
    "affected_services": ["sync", "ai_chat"]
  },
  "timestamp": "2024-07-20T12:55:00Z"
}
```

## Error Events

### Connection Error

```json
{
  "type": "connection_error",
  "data": {
    "error_code": "AUTH_EXPIRED",
    "message": "Authentication token has expired",
    "reconnect_required": true,
    "action_required": "refresh_token"
  },
  "timestamp": "2024-07-20T12:00:00Z"
}
```

### Rate Limit Warning

```json
{
  "type": "rate_limit_warning",
  "data": {
    "requests_remaining": 10,
    "window_reset_seconds": 45,
    "warning_threshold": 20
  },
  "timestamp": "2024-07-20T12:00:00Z"
}
```

## Event Filtering

Clients can filter events based on various criteria:

### Subscribe with Filters

```json
{
  "type": "subscribe",
  "data": {
    "events": ["sync_progress", "game_added", "achievement_unlocked"],
    "filters": {
      "library_id": "123e4567-e89b-12d3-a456-426614174000",
      "game_genres": ["RPG", "Strategy"],
      "notification_level": ["info", "warning", "error"]
    }
  }
}
```

## Client Implementation Examples

### JavaScript WebSocket Client

```javascript
class GameDjinnWebSocket {
  constructor(token) {
    this.token = token;
    this.ws = null;
    this.eventHandlers = new Map();
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:8000/ws?token=${this.token}`);
    
    this.ws.onopen = () => {
      console.log('Connected to Game Djinn');
      this.subscribe(['sync_progress', 'ai_chat', 'notifications']);
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleEvent(message);
    };
    
    this.ws.onclose = () => {
      console.log('Disconnected from Game Djinn');
      // Implement reconnection logic
    };
  }

  subscribe(events, filters = {}) {
    this.send({
      type: 'subscribe',
      data: { events, filters }
    });
  }

  sendAIMessage(message, context = {}) {
    this.send({
      type: 'ai_chat_message',
      data: { message, context },
      id: `msg_${Date.now()}`
    });
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        ...data,
        timestamp: new Date().toISOString()
      }));
    }
  }

  on(eventType, handler) {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType).push(handler);
  }

  handleEvent(message) {
    const handlers = this.eventHandlers.get(message.type) || [];
    handlers.forEach(handler => handler(message.data));
  }
}

// Usage
const ws = new GameDjinnWebSocket('your-jwt-token');
ws.connect();

ws.on('sync_progress', (data) => {
  updateProgressBar(data.progress_percentage);
  displayCurrentGame(data.current_game);
});

ws.on('ai_chat_response_chunk', (data) => {
  appendToChatMessage(data.chunk);
});
```

### React Hook

```javascript
import { useEffect, useRef, useState } from 'react';

export function useGameDjinnWebSocket(token) {
  const ws = useRef(null);
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    if (!token) return;

    ws.current = new WebSocket(`ws://localhost:8000/ws?token=${token}`);
    
    ws.current.onopen = () => setConnected(true);
    ws.current.onclose = () => setConnected(false);
    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setEvents(prev => [...prev.slice(-99), message]); // Keep last 100 events
    };

    return () => {
      ws.current?.close();
    };
  }, [token]);

  const sendMessage = (data) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    }
  };

  return { connected, events, sendMessage };
}
```

This WebSocket specification enables real-time, interactive experiences in Game Djinn, supporting live sync updates, streaming AI conversations, and immediate system notifications.