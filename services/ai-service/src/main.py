#!/usr/bin/env python3
"""
Game Djinn AI Service

LangChain-based AI agent service that connects to the MCP server.
"""

import os
import asyncio
from fastapi import FastAPI
import structlog

# Configure logging
logger = structlog.get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Game Djinn AI Service",
    description="AI agent service for gaming library management",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "game-djinn-ai"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Game Djinn AI Service", "status": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)