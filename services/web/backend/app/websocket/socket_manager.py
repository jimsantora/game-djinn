"""Socket.IO server management."""

import socketio
import structlog
from typing import Dict, Any, Optional
from uuid import UUID

from app.auth.config import auth_config
from app.auth.jwt import decode_token


logger = structlog.get_logger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:3000", "http://localhost:5173"],
    logger=True,
    engineio_logger=True
)

# Create ASGI app  
socket_app = socketio.ASGIApp(sio)


@sio.event
async def connect(sid: str, environ: Dict[str, Any], auth: Optional[Dict[str, Any]] = None):
    """Handle client connection."""
    logger.info(f"Client {sid} attempting to connect")
    logger.info(f"Auth data received: {auth}")
    logger.info(f"Auth enabled: {auth_config.auth_enabled}")
    
    # Authentication check
    if auth_config.auth_enabled:
        token = None
        
        # Try to get token from auth data
        if auth and "token" in auth:
            token = auth["token"]
            logger.info(f"Token from auth data: {token[:20]}...")
        
        # Try to get token from query parameters
        if not token and "QUERY_STRING" in environ:
            query_string = environ["QUERY_STRING"].decode()
            logger.info(f"Query string: {query_string}")
            if "token=" in query_string:
                token = query_string.split("token=")[1].split("&")[0]
                logger.info(f"Token from query: {token[:20]}...")
        
        # Verify token
        if not token:
            logger.warning(f"Client {sid} rejected: No authentication token")
            return False
        
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                logger.warning(f"Client {sid} rejected: Invalid token type")
                return False
            
            # Store user info in session
            await sio.save_session(sid, {
                "user_email": payload.get("sub"),
                "authenticated": True
            })
            
        except Exception as e:
            logger.warning(f"Client {sid} rejected: Token verification failed: {e}")
            return False
    else:
        # Auth disabled - allow connection
        await sio.save_session(sid, {
            "user_email": "admin@localhost",
            "authenticated": False
        })
    
    logger.info(f"Client {sid} connected successfully")
    
    # Join general room
    await sio.enter_room(sid, "general")
    
    # Send welcome message
    await sio.emit("connected", {
        "message": "Connected to Game Djinn",
        "auth_enabled": auth_config.auth_enabled
    }, room=sid)
    
    return True


@sio.event
async def disconnect(sid: str):
    """Handle client disconnection."""
    session = await sio.get_session(sid)
    user_email = session.get("user_email", "unknown")
    logger.info(f"Client {sid} ({user_email}) disconnected")


@sio.event
async def join_library(sid: str, data: Dict[str, Any]):
    """Join a library-specific room for updates."""
    try:
        library_id = data.get("library_id")
        if not library_id:
            await sio.emit("error", {"message": "Missing library_id"}, room=sid)
            return
        
        # Validate UUID format
        UUID(library_id)
        
        room_name = f"library:{library_id}"
        await sio.enter_room(sid, room_name)
        
        logger.info(f"Client {sid} joined library room {room_name}")
        
        await sio.emit("joined_library", {
            "library_id": library_id,
            "room": room_name
        }, room=sid)
        
    except ValueError:
        await sio.emit("error", {"message": "Invalid library_id format"}, room=sid)
    except Exception as e:
        logger.error(f"Error joining library room: {e}")
        await sio.emit("error", {"message": "Failed to join library room"}, room=sid)


@sio.event
async def leave_library(sid: str, data: Dict[str, Any]):
    """Leave a library-specific room."""
    try:
        library_id = data.get("library_id")
        if not library_id:
            await sio.emit("error", {"message": "Missing library_id"}, room=sid)
            return
        
        room_name = f"library:{library_id}"
        await sio.leave_room(sid, room_name)
        
        logger.info(f"Client {sid} left library room {room_name}")
        
        await sio.emit("left_library", {
            "library_id": library_id,
            "room": room_name
        }, room=sid)
        
    except Exception as e:
        logger.error(f"Error leaving library room: {e}")
        await sio.emit("error", {"message": "Failed to leave library room"}, room=sid)


# Utility functions for emitting events from other parts of the application

async def emit_sync_progress(library_id: str, progress_data: Dict[str, Any]):
    """Emit sync progress to library room and general room."""
    data = {
        "library_id": library_id,
        **progress_data
    }
    
    logger.info(f"[SOCKET] Emitting sync:progress for library {library_id}")
    logger.info(f"[SOCKET] Progress data: {data}")
    
    # Emit to library-specific room
    room_name = f"library:{library_id}"
    await sio.emit("sync:progress", data, room=room_name)
    logger.info(f"[SOCKET] Emitted to room {room_name}")
    
    # Also emit to general room for app-wide indicators
    await sio.emit("sync:progress", data, room="general")
    logger.info(f"[SOCKET] Emitted to general room")


async def emit_sync_complete(library_id: str, result_data: Dict[str, Any]):
    """Emit sync completion to library room and general room."""
    data = {
        "library_id": library_id,
        **result_data
    }
    
    # Emit to library-specific room
    room_name = f"library:{library_id}"
    await sio.emit("sync:complete", data, room=room_name)
    
    # Also emit to general room for app-wide indicators
    await sio.emit("sync:complete", data, room="general")


async def emit_sync_error(library_id: str, error_data: Dict[str, Any]):
    """Emit sync error to library room and general room."""
    data = {
        "library_id": library_id,
        **error_data
    }
    
    # Emit to library-specific room
    room_name = f"library:{library_id}"
    await sio.emit("sync:error", data, room=room_name)
    
    # Also emit to general room for app-wide indicators
    await sio.emit("sync:error", data, room="general")


async def emit_library_updated(library_id: str, library_data: Dict[str, Any]):
    """Emit library update to library room."""
    room_name = f"library:{library_id}"
    await sio.emit("library:updated", {
        "library_id": library_id,
        **library_data
    }, room=room_name)


async def emit_game_updated(library_id: str, game_data: Dict[str, Any]):
    """Emit game update to library room."""
    room_name = f"library:{library_id}"
    await sio.emit("game:updated", {
        "library_id": library_id,
        **game_data
    }, room=room_name)


async def broadcast_notification(notification_data: Dict[str, Any]):
    """Broadcast notification to all connected clients."""
    await sio.emit("notification", notification_data, room="general")