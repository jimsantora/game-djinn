# Platform Sync Service Implementation Plan

## Overview

The platform-sync service is a background worker service that handles the actual synchronization of game libraries from external platforms (initially Steam). It manages rate limiting, progress tracking, and resilient sync operations that can survive service restarts.

## Architecture

### Service Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Service   │────▶│      Redis      │◀────│ Platform Sync   │
│                 │     │   Job Queue     │     │    Worker       │
└─────────────────┘     │   + Pub/Sub     │     └─────────────────┘
         │              └─────────────────┘              │
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PostgreSQL    │     │  Redis Cache    │     │   Steam API     │
│   Game Data     │     │  Sync State     │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Data Flow

1. Web service enqueues sync job to Redis Queue (rq)
2. Platform-sync worker picks up job
3. Worker fetches games from Steam API with rate limiting
4. Progress updates published to Redis pub/sub
5. Web service receives updates and emits Socket.IO events
6. Sync state persisted to Redis for resumption

## Implementation Details

### 1. Core Service Structure

```
services/platform-sync/
├── src/
│   ├── __init__.py
│   ├── main.py                 # RQ worker entry point
│   ├── config.py               # Service configuration
│   ├── models.py               # Sync state models
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── sync_library.py    # Main sync job
│   │   └── enrich_games.py    # Enrichment job
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── base.py            # Abstract platform interface
│   │   ├── steam.py           # Steam implementation
│   │   └── rate_limiter.py    # Platform rate limiting
│   ├── sync/
│   │   ├── __init__.py
│   │   ├── manager.py         # Sync orchestration
│   │   ├── state.py           # State persistence
│   │   └── progress.py        # Progress tracking
│   └── utils/
│       ├── __init__.py
│       ├── redis_client.py    # Redis connections
│       └── db.py              # Database helpers
├── requirements.txt
├── Dockerfile
└── tests/
```

### 2. Redis Queue Setup

```python
# src/main.py
import redis
from rq import Worker, Queue, Connection
from rq.job import Job
import structlog

from config import settings
from utils.redis_client import get_redis_connection

logger = structlog.get_logger()

def main():
    """Main worker entry point."""
    redis_conn = get_redis_connection()
    
    # Listen to high, default, and low priority queues
    queues = [
        Queue('high', connection=redis_conn),    # Manual syncs
        Queue('default', connection=redis_conn), # Auto syncs
        Queue('low', connection=redis_conn)      # Enrichment
    ]
    
    with Connection(redis_conn):
        worker = Worker(
            queues,
            max_jobs=1,  # One sync at a time
            default_result_ttl=86400,  # Keep results for 24h
            log_level='INFO'
        )
        logger.info("Platform sync worker started", queues=[q.name for q in queues])
        worker.work()

if __name__ == '__main__':
    main()
```

### 3. Sync Job Implementation

```python
# src/jobs/sync_library.py
import time
from typing import Dict, Any
from uuid import UUID
import structlog

from integrations.steam import SteamIntegration
from sync.manager import SyncManager
from sync.state import SyncState
from sync.progress import ProgressTracker
from utils.redis_client import get_redis_pubsub

logger = structlog.get_logger()

async def sync_library_job(library_id: str, force: bool = False, sync_type: str = "manual") -> Dict[str, Any]:
    """
    Main sync job that runs in RQ worker.
    
    Args:
        library_id: UUID of the library to sync
        force: Whether to force full resync
        sync_type: Type of sync (manual, scheduled, auto)
    
    Returns:
        Sync result summary
    """
    logger.info("Starting library sync", library_id=library_id, sync_type=sync_type)
    
    # Initialize components
    sync_state = SyncState(library_id)
    progress = ProgressTracker(library_id)
    manager = SyncManager(library_id)
    
    try:
        # Check if already syncing
        if not force and await sync_state.is_syncing():
            return {"status": "already_syncing", "library_id": library_id}
        
        # Load or initialize sync state
        state = await sync_state.load() if not force else None
        if not state:
            state = await sync_state.initialize()
        
        # Mark as syncing
        await sync_state.set_status("syncing")
        await progress.start()
        
        # Get platform integration
        integration = await manager.get_platform_integration()
        
        # Perform sync
        result = await _perform_sync(
            integration=integration,
            state=state,
            progress=progress,
            manager=manager
        )
        
        # Mark as completed
        await sync_state.set_status("completed")
        await progress.complete(result)
        
        return result
        
    except Exception as e:
        logger.error("Sync failed", library_id=library_id, error=str(e))
        await sync_state.set_status("failed", error=str(e))
        await progress.error(str(e))
        raise

async def _perform_sync(integration, state, progress, manager):
    """Perform the actual sync with progress tracking."""
    # Get total games count
    total_games = await integration.get_games_count(state.get("user_id"))
    await progress.set_total(total_games)
    
    # Resume from last position
    start_offset = state.get("last_offset", 0)
    batch_size = 100  # Steam API allows 100 games per request
    
    games_synced = start_offset
    games_batch = []
    
    # Sync in batches
    for offset in range(start_offset, total_games, batch_size):
        # Fetch batch from API
        batch = await integration.fetch_games_batch(
            user_id=state.get("user_id"),
            offset=offset,
            limit=batch_size
        )
        
        # Process each game
        for game_data in batch:
            # Add to batch
            games_batch.append(game_data)
            games_synced += 1
            
            # Update progress every 10 games
            if games_synced % 10 == 0:
                await progress.update(
                    games_processed=games_synced,
                    current_game=game_data.get("name"),
                    progress_percentage=(games_synced / total_games) * 100
                )
                
                # Save batch to database
                await manager.save_games_batch(games_batch)
                games_batch = []
                
                # Update sync state
                await state.update_offset(offset + len(batch))
        
        # Check for pause/cancel
        if await state.should_pause():
            logger.info("Sync paused", library_id=state.library_id, offset=offset)
            break
    
    # Save any remaining games
    if games_batch:
        await manager.save_games_batch(games_batch)
    
    return {
        "status": "completed",
        "total_games": total_games,
        "games_synced": games_synced,
        "new_games": manager.stats.get("new_games", 0),
        "updated_games": manager.stats.get("updated_games", 0)
    }
```

### 4. Rate Limiting Implementation

```python
# src/integrations/rate_limiter.py
import time
import asyncio
from typing import Dict, Optional
import structlog

logger = structlog.get_logger()

class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that slows down before hitting limits.
    Tracks rate limits per platform globally.
    """
    
    # Platform rate limits
    LIMITS = {
        "steam": {
            "calls_per_window": 100,
            "window_seconds": 300,  # 5 minutes
            "daily_limit": 100000,
            "buffer_percentage": 0.8  # Slow down at 80% of limit
        }
    }
    
    def __init__(self, platform: str, redis_client):
        self.platform = platform
        self.redis = redis_client
        self.limits = self.LIMITS.get(platform, {})
        self.key_prefix = f"ratelimit:{platform}"
        
    async def acquire(self, weight: int = 1) -> None:
        """
        Acquire permission to make API call(s).
        Will pause if necessary to stay within limits.
        
        Args:
            weight: Number of API calls this request represents
        """
        while True:
            current_usage = await self._get_current_usage()
            
            # Check if we're approaching the limit
            usage_ratio = current_usage / self.limits["calls_per_window"]
            
            if usage_ratio >= 1.0:
                # At limit, must wait
                wait_time = await self._get_wait_time()
                logger.warning(
                    "Rate limit reached, pausing",
                    platform=self.platform,
                    wait_seconds=wait_time
                )
                await asyncio.sleep(wait_time)
                continue
                
            elif usage_ratio >= self.limits["buffer_percentage"]:
                # Approaching limit, slow down
                delay = self._calculate_adaptive_delay(usage_ratio)
                logger.debug(
                    "Approaching rate limit, slowing down",
                    platform=self.platform,
                    delay_seconds=delay
                )
                await asyncio.sleep(delay)
            
            # Record the API call
            await self._record_call(weight)
            break
    
    async def _get_current_usage(self) -> int:
        """Get current API usage in the time window."""
        window_start = time.time() - self.limits["window_seconds"]
        
        # Count calls in current window
        calls = await self.redis.zcount(
            f"{self.key_prefix}:calls",
            window_start,
            "+inf"
        )
        
        # Clean up old entries
        await self.redis.zremrangebyscore(
            f"{self.key_prefix}:calls",
            "-inf",
            window_start
        )
        
        return calls
    
    async def _record_call(self, weight: int) -> None:
        """Record API call(s) with timestamp."""
        timestamp = time.time()
        
        # Add entries for each call (weight)
        pipeline = self.redis.pipeline()
        for _ in range(weight):
            pipeline.zadd(f"{self.key_prefix}:calls", {timestamp: timestamp})
        
        # Update daily counter
        daily_key = f"{self.key_prefix}:daily:{time.strftime('%Y%m%d')}"
        pipeline.incrby(daily_key, weight)
        pipeline.expire(daily_key, 86400)  # Expire after 24 hours
        
        await pipeline.execute()
    
    async def _get_wait_time(self) -> float:
        """Calculate how long to wait before next call is allowed."""
        # Get oldest call in window
        oldest_call = await self.redis.zrange(
            f"{self.key_prefix}:calls",
            0, 0,
            withscores=True
        )
        
        if not oldest_call:
            return 0
        
        oldest_timestamp = oldest_call[0][1]
        window_end = oldest_timestamp + self.limits["window_seconds"]
        wait_time = max(0, window_end - time.time())
        
        return wait_time + 1  # Add 1 second buffer
    
    def _calculate_adaptive_delay(self, usage_ratio: float) -> float:
        """
        Calculate adaptive delay based on usage ratio.
        Exponentially increases delay as we approach the limit.
        """
        # usage_ratio is between 0.8 and 1.0
        # Map to delay between 0.1 and 5 seconds
        normalized = (usage_ratio - self.limits["buffer_percentage"]) / (1.0 - self.limits["buffer_percentage"])
        delay = 0.1 + (normalized ** 2) * 4.9
        return delay
```

### 5. Progress Tracking and Events

```python
# src/sync/progress.py
import json
from typing import Dict, Any, Optional
from datetime import datetime
import structlog

from utils.redis_client import get_redis_pubsub

logger = structlog.get_logger()

class ProgressTracker:
    """Tracks and publishes sync progress."""
    
    def __init__(self, library_id: str):
        self.library_id = library_id
        self.redis = get_redis_pubsub()
        self.channel = "sync:progress"
        self.state_key = f"sync:progress:{library_id}"
        
    async def start(self) -> None:
        """Mark sync as started."""
        await self._publish({
            "library_id": self.library_id,
            "status": "starting",
            "progress": 0,
            "message": "Starting sync process...",
            "started_at": datetime.utcnow().isoformat()
        })
        
    async def update(
        self,
        games_processed: int,
        current_game: Optional[str] = None,
        progress_percentage: float = 0
    ) -> None:
        """Update sync progress."""
        data = {
            "library_id": self.library_id,
            "status": "syncing",
            "progress": round(progress_percentage, 2),
            "games_processed": games_processed,
            "message": f"Processing games... ({games_processed} done)"
        }
        
        if current_game:
            data["current_game"] = current_game
            
        await self._publish(data)
        
        # Also save to Redis for status checks
        await self.redis.setex(
            self.state_key,
            3600,  # 1 hour TTL
            json.dumps(data)
        )
    
    async def complete(self, result: Dict[str, Any]) -> None:
        """Mark sync as completed."""
        await self._publish({
            "library_id": self.library_id,
            "status": "completed",
            "progress": 100,
            "message": "Sync completed successfully",
            "games_processed": result.get("games_synced", 0),
            "new_games": result.get("new_games", 0),
            "updated_games": result.get("updated_games", 0),
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # Clear progress state
        await self.redis.delete(self.state_key)
    
    async def error(self, error_message: str) -> None:
        """Mark sync as failed."""
        await self._publish({
            "library_id": self.library_id,
            "status": "failed",
            "error": error_message,
            "message": f"Sync failed: {error_message}"
        })
    
    async def _publish(self, data: Dict[str, Any]) -> None:
        """Publish progress update to Redis pub/sub."""
        try:
            await self.redis.publish(
                self.channel,
                json.dumps(data)
            )
            logger.debug("Published progress update", data=data)
        except Exception as e:
            logger.error("Failed to publish progress", error=str(e))
```

### 6. Steam Integration

```python
# src/integrations/steam.py
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode
import structlog

from .base import PlatformIntegration
from .rate_limiter import AdaptiveRateLimiter

logger = structlog.get_logger()

class SteamIntegration(PlatformIntegration):
    """Steam Web API integration with rate limiting."""
    
    BASE_URL = "https://api.steampowered.com"
    
    def __init__(self, api_key: str, redis_client):
        self.api_key = api_key
        self.rate_limiter = AdaptiveRateLimiter("steam", redis_client)
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_games_count(self, steam_id: str) -> int:
        """Get total number of games in user's library."""
        # Steam API returns all games in one call, so we fetch and count
        games = await self._get_owned_games(steam_id, include_details=False)
        return len(games)
    
    async def fetch_games_batch(
        self,
        user_id: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch a batch of games. Steam returns all games at once,
        so we simulate batching for consistent interface.
        """
        if offset == 0:
            # First batch - fetch all games and cache
            games = await self._get_owned_games(user_id, include_details=True)
            
            # Cache the full list for subsequent batches
            cache_key = f"steam:games:{user_id}"
            await self.redis.setex(cache_key, 3600, json.dumps(games))
            
            # Return first batch
            return games[:limit]
        else:
            # Get from cache and return appropriate batch
            cache_key = f"steam:games:{user_id}"
            cached = await self.redis.get(cache_key)
            
            if cached:
                games = json.loads(cached)
                return games[offset:offset + limit]
            else:
                # Cache miss, refetch
                games = await self._get_owned_games(user_id, include_details=True)
                return games[offset:offset + limit]
    
    async def _get_owned_games(
        self,
        steam_id: str,
        include_details: bool = True
    ) -> List[Dict[str, Any]]:
        """Get user's owned games from Steam API."""
        await self.rate_limiter.acquire()
        
        params = {
            "key": self.api_key,
            "steamid": steam_id,
            "format": "json",
            "include_appinfo": "1" if include_details else "0",
            "include_played_free_games": "1"
        }
        
        url = f"{self.BASE_URL}/IPlayerService/GetOwnedGames/v1/?{urlencode(params)}"
        
        async with self.session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            
            games = data.get("response", {}).get("games", [])
            
            # Transform to our format
            return [self._transform_game(game) for game in games]
    
    def _transform_game(self, steam_game: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Steam game data to our universal format."""
        app_id = steam_game.get("appid")
        
        return {
            "platform_game_id": str(app_id),
            "title": steam_game.get("name", f"Unknown Game {app_id}"),
            "platform": "steam",
            "playtime_minutes": steam_game.get("playtime_forever", 0),
            "last_played": steam_game.get("rtime_last_played"),
            "icon_url": f"https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/{app_id}/{steam_game.get('img_icon_url', '')}.jpg",
            "logo_url": f"https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/{app_id}/{steam_game.get('img_logo_url', '')}.jpg",
            "raw_data": steam_game
        }
    
    async def get_game_details(self, app_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific game."""
        # This would be used in the enrichment phase
        await self.rate_limiter.acquire()
        
        url = f"https://store.steampowered.com/api/appdetails"
        params = {"appids": app_id}
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            
            if str(app_id) in data and data[str(app_id)]["success"]:
                return data[str(app_id)]["data"]
            
            return {}
```

### 7. Sync State Management

```python
# src/sync/state.py
import json
from typing import Dict, Any, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()

class SyncState:
    """Manages persistent sync state for resumption."""
    
    def __init__(self, library_id: str, redis_client):
        self.library_id = library_id
        self.redis = redis_client
        self.key = f"sync:state:{library_id}"
        self.lock_key = f"sync:lock:{library_id}"
        
    async def is_syncing(self) -> bool:
        """Check if library is currently syncing."""
        lock = await self.redis.get(self.lock_key)
        return lock is not None
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize new sync state."""
        # Get library details from database
        library = await self._get_library()
        
        state = {
            "library_id": self.library_id,
            "platform": library["platform_code"],
            "user_id": library["user_identifier"],
            "started_at": datetime.utcnow().isoformat(),
            "last_offset": 0,
            "games_synced": 0,
            "status": "initializing"
        }
        
        await self.save(state)
        return state
    
    async def load(self) -> Optional[Dict[str, Any]]:
        """Load existing sync state."""
        data = await self.redis.get(self.key)
        if data:
            return json.loads(data)
        return None
    
    async def save(self, state: Dict[str, Any]) -> None:
        """Save sync state."""
        # Update timestamp
        state["updated_at"] = datetime.utcnow().isoformat()
        
        # Save with TTL (keep for 7 days)
        await self.redis.setex(
            self.key,
            604800,  # 7 days
            json.dumps(state)
        )
    
    async def update_offset(self, offset: int) -> None:
        """Update the sync offset for resumption."""
        state = await self.load()
        if state:
            state["last_offset"] = offset
            state["games_synced"] = offset
            await self.save(state)
    
    async def set_status(self, status: str, error: Optional[str] = None) -> None:
        """Update sync status."""
        # Set/clear sync lock based on status
        if status == "syncing":
            await self.redis.setex(self.lock_key, 86400, "1")  # 24h lock
        elif status in ["completed", "failed", "cancelled"]:
            await self.redis.delete(self.lock_key)
        
        # Update state
        state = await self.load() or {}
        state["status"] = status
        
        if error:
            state["error"] = error
            state["failed_at"] = datetime.utcnow().isoformat()
        elif status == "completed":
            state["completed_at"] = datetime.utcnow().isoformat()
            
        await self.save(state)
    
    async def should_pause(self) -> bool:
        """Check if sync should pause (for cancellation)."""
        # Check if lock still exists (not cancelled)
        return await self.redis.get(self.lock_key) is None
    
    async def _get_library(self) -> Dict[str, Any]:
        """Get library details from database."""
        # This would query the actual database
        # Simplified for example
        from utils.db import get_db_connection
        
        async with get_db_connection() as conn:
            result = await conn.fetchrow(
                "SELECT * FROM user_libraries WHERE library_id = $1",
                self.library_id
            )
            return dict(result)
```

### 8. Web Service Integration

```python
# Updates to web service to integrate with platform-sync

# services/web/backend/app/routers/sync.py
import json
from rq import Queue
from redis import Redis
import structlog

from app.websocket.socket_manager import sio

logger = structlog.get_logger()

# Redis connection for RQ
redis_conn = Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))
sync_queue = Queue("high", connection=redis_conn)

# Redis pub/sub listener for progress updates
async def listen_for_sync_progress():
    """Background task to listen for sync progress and emit Socket.IO events."""
    redis = await aioredis.create_redis_pool('redis://redis:6379')
    channel = (await redis.subscribe('sync:progress'))[0]
    
    while True:
        try:
            message = await channel.get()
            if message:
                data = json.loads(message.decode())
                library_id = data.get("library_id")
                
                # Emit to Socket.IO
                await emit_sync_progress(library_id, data)
                
        except Exception as e:
            logger.error("Error in progress listener", error=str(e))
            await asyncio.sleep(1)

# Start listener on app startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(listen_for_sync_progress())

@router.post("/{library_id}")
async def trigger_sync(
    library_id: UUID,
    sync_request: SyncRequest,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
) -> SyncResponse:
    """Trigger synchronization for a library."""
    
    # Enqueue job to RQ
    job = sync_queue.enqueue(
        'jobs.sync_library.sync_library_job',
        args=[str(library_id)],
        kwargs={
            'force': sync_request.force,
            'sync_type': sync_request.sync_type
        },
        job_timeout='2h',  # 2 hour timeout for large libraries
        result_ttl=86400,   # Keep result for 24 hours
        failure_ttl=86400   # Keep failure info for 24 hours
    )
    
    # Update library status
    library.sync_status = "queued"
    library.last_sync_at = datetime.utcnow()
    await session.commit()
    
    return SyncResponse(
        library_id=library_id,
        status="queued",
        message=f"Sync queued for {library.display_name}",
        started_at=library.last_sync_at,
        job_id=job.id
    )

@router.get("/{library_id}/status")
async def get_sync_status(
    library_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session)
) -> SyncStatus:
    """Get real-time sync status from Redis."""
    
    # Get progress from Redis
    redis = await aioredis.create_redis_pool('redis://redis:6379')
    progress_key = f"sync:progress:{library_id}"
    progress_data = await redis.get(progress_key)
    
    if progress_data:
        data = json.loads(progress_data)
        return SyncStatus(
            library_id=library_id,
            status=data.get("status", "unknown"),
            progress_percentage=data.get("progress", 0),
            current_step=data.get("message", ""),
            games_processed=data.get("games_processed", 0),
            total_games=data.get("total_games", 0),
            error_message=data.get("error"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at")
        )
    
    # Fall back to database status
    library = await session.get(UserLibrary, library_id)
    return SyncStatus(
        library_id=library_id,
        status=library.sync_status or "idle",
        progress_percentage=0,
        current_step="No active sync",
        games_processed=library.total_games or 0,
        total_games=library.total_games or 0,
        error_message=None,
        started_at=library.last_sync_at,
        completed_at=library.last_sync_at
    )

@router.post("/{library_id}/cancel")
async def cancel_sync(
    library_id: UUID,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    """Cancel ongoing sync by removing the sync lock."""
    
    redis = await aioredis.create_redis_pool('redis://redis:6379')
    lock_key = f"sync:lock:{library_id}"
    
    # Remove lock to signal cancellation
    await redis.delete(lock_key)
    
    # Update library status
    library = await session.get(UserLibrary, library_id)
    library.sync_status = "cancelled"
    await session.commit()
    
    return {"message": "Sync cancellation requested"}
```

### 9. Docker Configuration

```dockerfile
# services/platform-sync/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app

# Run RQ worker
CMD ["python", "-m", "src.main"]
```

```yaml
# docker-compose.yml addition
platform-sync:
  build: ./services/platform-sync
  depends_on:
    - db
    - redis
  environment:
    - DATABASE_URL=${DATABASE_URL}
    - REDIS_URL=redis://redis:6379
    - STEAM_API_KEY=${STEAM_API_KEY}
    - LOG_LEVEL=${LOG_LEVEL:-INFO}
  volumes:
    - ./services/platform-sync/src:/app/src
  restart: unless-stopped
  deploy:
    resources:
      limits:
        memory: 256M
```

### 10. Testing Strategy

```python
# tests/test_rate_limiter.py
import pytest
import asyncio
from integrations.rate_limiter import AdaptiveRateLimiter

@pytest.mark.asyncio
async def test_rate_limiter_respects_limits():
    """Test that rate limiter enforces limits."""
    limiter = AdaptiveRateLimiter("steam", mock_redis)
    
    # Make calls up to limit
    for _ in range(100):
        await limiter.acquire()
    
    # Next call should delay
    start = time.time()
    await limiter.acquire()
    duration = time.time() - start
    
    assert duration > 1  # Should have waited

@pytest.mark.asyncio
async def test_adaptive_slowdown():
    """Test adaptive slowdown before hitting limit."""
    limiter = AdaptiveRateLimiter("steam", mock_redis)
    
    # Make 80 calls (80% of limit)
    for _ in range(80):
        await limiter.acquire()
    
    # Next calls should have delays
    delays = []
    for _ in range(10):
        start = time.time()
        await limiter.acquire()
        delays.append(time.time() - start)
    
    # Delays should increase
    assert delays[-1] > delays[0]
```

## Implementation Priority

1. **Core Structure** (Week 1)
   - Set up service skeleton
   - Redis Queue integration
   - Basic job structure

2. **Rate Limiting** (Week 1)
   - Implement adaptive rate limiter
   - Test with real Steam API

3. **Sync Logic** (Week 2)
   - Steam integration
   - Progress tracking
   - State persistence

4. **Error Handling** (Week 2)
   - Retry logic
   - Failure recovery
   - Cancellation support

5. **Testing & Optimization** (Week 3)
   - Load testing with large libraries
   - Memory optimization
   - Performance tuning

## Monitoring & Observability

- Structured logging with correlation IDs
- Metrics for sync duration, API calls, failures
- Health endpoint for monitoring
- Redis keys for real-time status inspection

## Future Enhancements

1. **Scheduled Syncs** - Cron-like scheduling for automatic updates
2. **Differential Sync** - Only sync changed games
3. **Multi-Platform** - Extend to Xbox, GOG, etc.
4. **Webhooks** - Steam API webhooks for real-time updates
5. **Batch Enrichment** - Parallel enrichment jobs