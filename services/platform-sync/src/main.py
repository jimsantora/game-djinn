#!/usr/bin/env python3
"""
Game Djinn Platform Sync Service

Background service for syncing game data from various platforms.
"""

import os
import asyncio
from fastapi import FastAPI
import structlog

# Configure logging
logger = structlog.get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Game Djinn Platform Sync Service",
    description="Background sync service for gaming platforms",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "game-djinn-platform-sync"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Game Djinn Platform Sync Service", "status": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)