#!/usr/bin/env python3
"""
Game Djinn Web API

FastAPI application providing REST API and WebSocket endpoints.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import structlog

from app.database import close_engine, check_database_health

# Configure logging
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting Game Djinn Web API")
    
    # Check database connectivity
    try:
        health = await check_database_health()
        if health["status"] == "healthy":
            logger.info("Database connection verified")
        else:
            logger.warning(f"Database health check warning: {health}")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Game Djinn Web API")
    await close_engine()

# Create FastAPI app
app = FastAPI(
    title="Game Djinn API",
    description="AI-powered gaming library management system",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    health_info = {
        "status": "healthy",
        "service": "game-djinn-web",
        "version": "0.1.0"
    }
    
    # Check database health
    try:
        db_health = await check_database_health()
        health_info["database"] = db_health
        
        if db_health["status"] != "healthy":
            health_info["status"] = "unhealthy"
            
    except Exception as e:
        health_info["status"] = "unhealthy"
        health_info["database"] = {"status": "error", "error": str(e)}
    
    return health_info

# API routes will be added here

# Serve static files (built React app)
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)