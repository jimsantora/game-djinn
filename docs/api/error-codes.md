# Error Code Standardization

Game Djinn uses standardized error codes across all services to provide consistent error handling and debugging capabilities.

## Error Response Format

All services return errors in this standardized format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "details": {
      "field": "additional context",
      "suggestion": "what user can do"
    },
    "timestamp": "2024-07-20T12:00:00Z",
    "trace_id": "optional-trace-id-for-debugging"
  }
}
```

## HTTP Status Code Mapping

| HTTP Status | Category | Usage |
|-------------|----------|-------|
| 400 | Bad Request | Invalid input, malformed requests |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource state conflict |
| 422 | Unprocessable Entity | Valid format but business logic error |
| 429 | Too Many Requests | Rate limiting |
| 500 | Internal Server Error | Unexpected server errors |
| 502 | Bad Gateway | External service errors |
| 503 | Service Unavailable | Temporary service issues |

## Error Code Categories

### Authentication & Authorization (AUTH_*)

#### AUTH_REQUIRED
- **HTTP Status**: 401
- **Description**: Authentication is required but not provided
- **Example**:
```json
{
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Authentication required to access this resource",
    "details": {
      "endpoint": "/libraries",
      "required_auth": "JWT Bearer token"
    }
  }
}
```

#### AUTH_INVALID_TOKEN
- **HTTP Status**: 401
- **Description**: Provided authentication token is invalid
- **Example**:
```json
{
  "error": {
    "code": "AUTH_INVALID_TOKEN",
    "message": "Authentication token is invalid or malformed",
    "details": {
      "token_type": "JWT",
      "issue": "signature_invalid"
    }
  }
}
```

#### AUTH_TOKEN_EXPIRED
- **HTTP Status**: 401
- **Description**: Authentication token has expired
- **Example**:
```json
{
  "error": {
    "code": "AUTH_TOKEN_EXPIRED",
    "message": "Authentication token has expired",
    "details": {
      "expired_at": "2024-07-20T11:00:00Z",
      "action": "refresh_token"
    }
  }
}
```

#### AUTH_INVALID_API_KEY
- **HTTP Status**: 401
- **Description**: Invalid MCP API key
- **Example**:
```json
{
  "error": {
    "code": "AUTH_INVALID_API_KEY",
    "message": "Invalid API key provided",
    "details": {
      "header": "X-API-Key",
      "suggestion": "Check your MCP_API_KEY environment variable"
    }
  }
}
```

#### AUTH_INSUFFICIENT_PERMISSIONS
- **HTTP Status**: 403
- **Description**: Valid authentication but insufficient permissions
- **Example**:
```json
{
  "error": {
    "code": "AUTH_INSUFFICIENT_PERMISSIONS",
    "message": "Insufficient permissions to perform this action",
    "details": {
      "required_permission": "library:write",
      "user_permissions": ["library:read"]
    }
  }
}
```

### Validation & Input (VALIDATION_*)

#### VALIDATION_FAILED
- **HTTP Status**: 400
- **Description**: Request validation failed
- **Example**:
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": {
      "errors": [
        {
          "field": "email",
          "message": "Invalid email format"
        },
        {
          "field": "platform_code",
          "message": "Must be one of: steam, xbox, gog"
        }
      ]
    }
  }
}
```

#### VALIDATION_MISSING_FIELD
- **HTTP Status**: 400
- **Description**: Required field is missing
- **Example**:
```json
{
  "error": {
    "code": "VALIDATION_MISSING_FIELD",
    "message": "Required field 'user_identifier' is missing",
    "details": {
      "field": "user_identifier",
      "location": "request_body",
      "example": "76561198000000000"
    }
  }
}
```

#### VALIDATION_INVALID_FORMAT
- **HTTP Status**: 400
- **Description**: Field format is invalid
- **Example**:
```json
{
  "error": {
    "code": "VALIDATION_INVALID_FORMAT",
    "message": "Invalid UUID format for library_id",
    "details": {
      "field": "library_id",
      "provided": "invalid-uuid",
      "expected_format": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
  }
}
```

#### VALIDATION_VALUE_OUT_OF_RANGE
- **HTTP Status**: 400
- **Description**: Numeric value is outside valid range
- **Example**:
```json
{
  "error": {
    "code": "VALIDATION_VALUE_OUT_OF_RANGE",
    "message": "User rating must be between 1 and 5",
    "details": {
      "field": "user_rating",
      "provided": 6,
      "min": 1,
      "max": 5
    }
  }
}
```

### Resource Not Found (NOT_FOUND_*)

#### LIBRARY_NOT_FOUND
- **HTTP Status**: 404
- **Description**: Specified library doesn't exist
- **Example**:
```json
{
  "error": {
    "code": "LIBRARY_NOT_FOUND",
    "message": "Library with ID 'invalid-id' not found",
    "details": {
      "library_id": "invalid-id",
      "suggestion": "Check library ID or ensure library exists"
    }
  }
}
```

#### GAME_NOT_FOUND
- **HTTP Status**: 404
- **Description**: Specified game doesn't exist
- **Example**:
```json
{
  "error": {
    "code": "GAME_NOT_FOUND",
    "message": "Game with ID 'invalid-game-id' not found",
    "details": {
      "game_id": "invalid-game-id",
      "search_scope": "all_platforms"
    }
  }
}
```

#### PLATFORM_NOT_FOUND
- **HTTP Status**: 404
- **Description**: Specified platform doesn't exist
- **Example**:
```json
{
  "error": {
    "code": "PLATFORM_NOT_FOUND",
    "message": "Platform 'invalidplatform' not found",
    "details": {
      "platform_code": "invalidplatform",
      "supported_platforms": ["steam", "xbox", "gog", "manual"]
    }
  }
}
```

#### COLLECTION_NOT_FOUND
- **HTTP Status**: 404
- **Description**: Specified collection doesn't exist
- **Example**:
```json
{
  "error": {
    "code": "COLLECTION_NOT_FOUND",
    "message": "Collection with ID 'invalid-collection-id' not found",
    "details": {
      "collection_id": "invalid-collection-id",
      "library_id": "123e4567-e89b-12d3-a456-426614174000"
    }
  }
}
```

### Business Logic (BUSINESS_*)

#### SYNC_ALREADY_IN_PROGRESS
- **HTTP Status**: 409
- **Description**: Sync operation is already running for this library
- **Example**:
```json
{
  "error": {
    "code": "SYNC_ALREADY_IN_PROGRESS",
    "message": "Library sync is already in progress",
    "details": {
      "library_id": "123e4567-e89b-12d3-a456-426614174000",
      "current_operation_id": "456e7890-e89b-12d3-a456-426614174001",
      "started_at": "2024-07-20T11:55:00Z",
      "estimated_completion": "2024-07-20T12:00:00Z",
      "force_option": "Use force=true to cancel current sync"
    }
  }
}
```

#### LIBRARY_ALREADY_EXISTS
- **HTTP Status**: 409
- **Description**: Library for this platform and user already exists
- **Example**:
```json
{
  "error": {
    "code": "LIBRARY_ALREADY_EXISTS",
    "message": "Library for this platform and user already exists",
    "details": {
      "platform_code": "steam",
      "user_identifier": "76561198000000000",
      "existing_library_id": "123e4567-e89b-12d3-a456-426614174000",
      "action": "Use existing library or delete it first"
    }
  }
}
```

#### COLLECTION_NAME_CONFLICT
- **HTTP Status**: 409
- **Description**: Collection with this name already exists in library
- **Example**:
```json
{
  "error": {
    "code": "COLLECTION_NAME_CONFLICT",
    "message": "Collection 'Favorites' already exists in this library",
    "details": {
      "collection_name": "Favorites",
      "library_id": "123e4567-e89b-12d3-a456-426614174000",
      "existing_collection_id": "collection_123",
      "suggestion": "Choose a different name or update existing collection"
    }
  }
}
```

#### INVALID_GAME_STATUS_TRANSITION
- **HTTP Status**: 422
- **Description**: Cannot transition game to specified status
- **Example**:
```json
{
  "error": {
    "code": "INVALID_GAME_STATUS_TRANSITION",
    "message": "Cannot mark unowned game as 'completed'",
    "details": {
      "current_status": "wishlist",
      "requested_status": "completed",
      "valid_transitions": ["unplayed"],
      "reason": "Game must be owned before marking as completed"
    }
  }
}
```

### Rate Limiting (RATE_LIMIT_*)

#### RATE_LIMIT_EXCEEDED
- **HTTP Status**: 429
- **Description**: Rate limit exceeded
- **Example**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "details": {
      "limit": 100,
      "window_seconds": 60,
      "requests_made": 100,
      "retry_after": 60,
      "reset_at": "2024-07-20T12:01:00Z"
    }
  }
}
```

#### PLATFORM_RATE_LIMITED
- **HTTP Status**: 502
- **Description**: External platform API rate limited us
- **Example**:
```json
{
  "error": {
    "code": "PLATFORM_RATE_LIMITED",
    "message": "Steam API rate limit exceeded",
    "details": {
      "platform": "steam",
      "retry_after": 300,
      "limit_type": "requests_per_hour",
      "auto_retry": true,
      "next_attempt": "2024-07-20T12:05:00Z"
    }
  }
}
```

### External Service Errors (EXTERNAL_*)

#### PLATFORM_API_ERROR
- **HTTP Status**: 502
- **Description**: External platform API returned an error
- **Example**:
```json
{
  "error": {
    "code": "PLATFORM_API_ERROR",
    "message": "Steam API returned error: Service Unavailable",
    "details": {
      "platform": "steam",
      "api_error_code": "503",
      "api_error_message": "Service Unavailable",
      "endpoint": "/ISteamUser/GetOwnedGames/v0001/",
      "retry_suggested": true,
      "status_page": "https://steamstat.us/"
    }
  }
}
```

#### PLATFORM_API_TIMEOUT
- **HTTP Status**: 504
- **Description**: External platform API request timed out
- **Example**:
```json
{
  "error": {
    "code": "PLATFORM_API_TIMEOUT",
    "message": "Timeout while communicating with Steam API",
    "details": {
      "platform": "steam",
      "timeout_seconds": 30,
      "endpoint": "/ISteamUser/GetOwnedGames/v0001/",
      "suggestion": "Steam API may be experiencing issues"
    }
  }
}
```

#### EXTERNAL_SERVICE_UNAVAILABLE
- **HTTP Status**: 503
- **Description**: External service is unavailable
- **Example**:
```json
{
  "error": {
    "code": "EXTERNAL_SERVICE_UNAVAILABLE",
    "message": "Steam API is currently unavailable",
    "details": {
      "service": "steam",
      "status": "maintenance",
      "estimated_restoration": "2024-07-20T14:00:00Z",
      "impact": "Game metadata enrichment disabled"
    }
  }
}
```

### Internal System Errors (INTERNAL_*)

#### INTERNAL_ERROR
- **HTTP Status**: 500
- **Description**: Unexpected internal server error
- **Example**:
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "details": {
      "trace_id": "trace_123456789",
      "suggestion": "Please try again. If the error persists, contact support.",
      "incident_id": "inc_20240720_001"
    }
  }
}
```

#### DATABASE_ERROR
- **HTTP Status**: 500
- **Description**: Database operation failed
- **Example**:
```json
{
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Database operation failed",
    "details": {
      "operation": "SELECT",
      "table": "games",
      "error_type": "connection_timeout",
      "trace_id": "trace_123456789"
    }
  }
}
```

#### CACHE_ERROR
- **HTTP Status**: 500
- **Description**: Cache operation failed
- **Example**:
```json
{
  "error": {
    "code": "CACHE_ERROR",
    "message": "Cache operation failed",
    "details": {
      "cache_type": "redis",
      "operation": "GET",
      "key": "user_session_123",
      "fallback": "Proceeding without cache"
    }
  }
}
```

### MCP Tool Errors (MCP_*)

#### MCP_TOOL_NOT_FOUND
- **HTTP Status**: 404
- **Description**: Requested MCP tool doesn't exist
- **Example**:
```json
{
  "error": {
    "code": "MCP_TOOL_NOT_FOUND",
    "message": "MCP tool 'invalid_tool' not found",
    "details": {
      "tool_name": "invalid_tool",
      "available_tools": [
        "get_supported_platforms",
        "search_games",
        "sync_platform_library"
      ]
    }
  }
}
```

#### MCP_INVALID_PARAMETERS
- **HTTP Status**: 400
- **Description**: Invalid parameters for MCP tool
- **Example**:
```json
{
  "error": {
    "code": "MCP_INVALID_PARAMETERS",
    "message": "Invalid parameters for tool 'search_games'",
    "details": {
      "tool_name": "search_games",
      "parameter_errors": [
        {
          "parameter": "limit",
          "error": "Must be between 1 and 100",
          "provided": 150
        }
      ]
    }
  }
}
```

#### MCP_TOOL_EXECUTION_FAILED
- **HTTP Status**: 500
- **Description**: MCP tool execution failed
- **Example**:
```json
{
  "error": {
    "code": "MCP_TOOL_EXECUTION_FAILED",
    "message": "Tool execution failed: search_games",
    "details": {
      "tool_name": "search_games",
      "execution_error": "Database query timeout",
      "parameters": {
        "query": "witcher",
        "limit": 10
      },
      "trace_id": "trace_123456789"
    }
  }
}
```

### AI Service Errors (AI_*)

#### AI_SERVICE_UNAVAILABLE
- **HTTP Status**: 503
- **Description**: AI service is not available
- **Example**:
```json
{
  "error": {
    "code": "AI_SERVICE_UNAVAILABLE",
    "message": "AI service is currently unavailable",
    "details": {
      "service": "ollama",
      "status": "starting",
      "estimated_available": "2024-07-20T12:05:00Z"
    }
  }
}
```

#### AI_MODEL_ERROR
- **HTTP Status**: 500
- **Description**: AI model returned an error
- **Example**:
```json
{
  "error": {
    "code": "AI_MODEL_ERROR",
    "message": "AI model failed to generate response",
    "details": {
      "model": "llama2:7b",
      "error_type": "context_length_exceeded",
      "max_tokens": 4096,
      "suggestion": "Try a shorter conversation or clear context"
    }
  }
}
```

#### AI_TIMEOUT
- **HTTP Status**: 504
- **Description**: AI request timed out
- **Example**:
```json
{
  "error": {
    "code": "AI_TIMEOUT",
    "message": "AI request timed out",
    "details": {
      "timeout_seconds": 60,
      "model": "llama2:7b",
      "suggestion": "Try a simpler request or try again later"
    }
  }
}
```

## Error Handling Best Practices

### Client Implementation

```javascript
class GameDjinnAPIError extends Error {
  constructor(errorResponse) {
    super(errorResponse.error.message);
    this.code = errorResponse.error.code;
    this.details = errorResponse.error.details;
    this.timestamp = errorResponse.error.timestamp;
    this.traceId = errorResponse.error.trace_id;
  }

  isRetryable() {
    const retryableCodes = [
      'RATE_LIMIT_EXCEEDED',
      'PLATFORM_API_TIMEOUT',
      'INTERNAL_ERROR',
      'DATABASE_ERROR'
    ];
    return retryableCodes.includes(this.code);
  }

  getRetryAfter() {
    if (this.code === 'RATE_LIMIT_EXCEEDED') {
      return this.details.retry_after || 60;
    }
    return null;
  }
}

// Usage
try {
  const response = await fetch('/api/libraries/sync', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new GameDjinnAPIError(errorData);
  }
} catch (error) {
  if (error instanceof GameDjinnAPIError) {
    console.error(`API Error [${error.code}]: ${error.message}`);
    
    if (error.isRetryable()) {
      const retryAfter = error.getRetryAfter();
      if (retryAfter) {
        setTimeout(() => retryRequest(), retryAfter * 1000);
      }
    }
  }
}
```

### Error Logging

```javascript
function logError(error, context = {}) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    error_code: error.code,
    message: error.message,
    details: error.details,
    trace_id: error.traceId,
    context: context,
    user_agent: navigator.userAgent,
    url: window.location.href
  };
  
  // Send to logging service
  console.error('Game Djinn API Error:', logEntry);
}
```

### User-Friendly Error Messages

```javascript
function getUserFriendlyMessage(errorCode) {
  const messages = {
    'RATE_LIMIT_EXCEEDED': 'Too many requests. Please wait a moment and try again.',
    'LIBRARY_NOT_FOUND': 'The requested library could not be found.',
    'SYNC_ALREADY_IN_PROGRESS': 'A sync is already running. Please wait for it to complete.',
    'PLATFORM_API_ERROR': 'There was an issue connecting to the gaming platform. Please try again later.',
    'AUTH_TOKEN_EXPIRED': 'Your session has expired. Please log in again.',
    'VALIDATION_FAILED': 'Please check your input and try again.',
    'INTERNAL_ERROR': 'Something went wrong on our end. Please try again later.'
  };
  
  return messages[errorCode] || 'An unexpected error occurred. Please try again.';
}
```

This standardized error system ensures consistent error handling across all Game Djinn services and provides clear guidance for both developers and end users.