#!/usr/bin/env python3
"""
Game Djinn MCP Server

Standalone MCP server providing gaming library tools for AI agents.
"""

import asyncio
import os
from typing import Any

import structlog
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool

from database import init_database, close_engine
from tools import (
    get_supported_platforms, add_platform_library, sync_platform_library,
    search_games, get_game_details, analyze_gaming_patterns,
    filter_by_content_rating, recommend_games
)

# Configure logging
logger = structlog.get_logger(__name__)

# Server instance
server = Server("game-djinn-mcp")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="get_supported_platforms",
            description="Get list of supported gaming platforms with their availability status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="add_platform_library", 
            description="Add a new user library for a gaming platform",
            inputSchema={
                "type": "object",
                "properties": {
                    "platform_code": {"type": "string", "description": "Platform identifier (steam, xbox, gog, etc.)"},
                    "user_identifier": {"type": "string", "description": "Platform-specific user ID"},
                    "display_name": {"type": "string", "description": "Friendly name for the library"},
                    "credentials": {"type": "object", "description": "Optional platform-specific credentials"}
                },
                "required": ["platform_code", "user_identifier", "display_name"]
            }
        ),
        Tool(
            name="sync_platform_library",
            description="Trigger synchronization for a platform library",
            inputSchema={
                "type": "object",
                "properties": {
                    "library_id": {"type": "string", "description": "UUID of the library to sync"},
                    "force": {"type": "boolean", "description": "Force sync even if recently synced", "default": False},
                    "sync_type": {"type": "string", "description": "Type of sync", "enum": ["full_sync", "incremental_sync", "manual_sync"], "default": "incremental_sync"}
                },
                "required": ["library_id"]
            }
        ),
        Tool(
            name="search_games",
            description="Search for games across all platforms and libraries",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "platform_filter": {"type": "array", "items": {"type": "string"}, "description": "Filter by platforms"},
                    "status_filter": {"type": "array", "items": {"type": "string"}, "description": "Filter by game status"},
                    "rating_filter": {"type": "object", "description": "Filter by ratings"},
                    "genre_filter": {"type": "array", "items": {"type": "string"}, "description": "Filter by genres"},
                    "owned_only": {"type": "boolean", "description": "Show only owned games", "default": False},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_game_details",
            description="Get comprehensive information about a specific game",
            inputSchema={
                "type": "object",
                "properties": {
                    "game_id": {"type": "string", "description": "UUID of the game"},
                    "library_id": {"type": "string", "description": "Optional library ID to include user-specific data"}
                },
                "required": ["game_id"]
            }
        ),
        Tool(
            name="analyze_gaming_patterns",
            description="Analyze gaming patterns and provide insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "library_id": {"type": "string", "description": "Optional specific library to analyze"},
                    "time_period": {"type": "string", "enum": ["week", "month", "quarter", "year", "all"], "default": "month"},
                    "include_predictions": {"type": "boolean", "description": "Include ML-based predictions", "default": True}
                },
                "required": []
            }
        ),
        Tool(
            name="filter_by_content_rating",
            description="Filter games by ESRB content ratings for family-friendly viewing",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_rating": {"type": "string", "enum": ["E", "E10+", "T", "M"], "description": "Maximum ESRB rating"},
                    "library_id": {"type": "string", "description": "Optional specific library to filter"},
                    "exclude_descriptors": {"type": "array", "items": {"type": "string"}, "description": "Exclude games with specific content descriptors"},
                    "include_unrated": {"type": "boolean", "description": "Include unrated games", "default": True}
                },
                "required": ["max_rating"]
            }
        ),
        Tool(
            name="recommend_games",
            description="Get personalized game recommendations",
            inputSchema={
                "type": "object",
                "properties": {
                    "library_id": {"type": "string", "description": "Optional library to base recommendations on"},
                    "criteria": {"type": "object", "description": "Recommendation criteria"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
                    "include_owned": {"type": "boolean", "description": "Include already owned games", "default": False}
                },
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[Any]:
    """Handle tool execution."""
    args = arguments or {}
    
    try:
        if name == "get_supported_platforms":
            result = await get_supported_platforms()
            return [result]
        
        elif name == "add_platform_library":
            result = await add_platform_library(
                platform_code=args["platform_code"],
                user_identifier=args["user_identifier"], 
                display_name=args["display_name"],
                credentials=args.get("credentials")
            )
            return [result]
        
        elif name == "sync_platform_library":
            result = await sync_platform_library(
                library_id=args["library_id"],
                force=args.get("force", False),
                sync_type=args.get("sync_type", "incremental_sync")
            )
            return [result]
        
        elif name == "search_games":
            result = await search_games(
                query=args["query"],
                platform_filter=args.get("platform_filter"),
                status_filter=args.get("status_filter"),
                rating_filter=args.get("rating_filter"),
                genre_filter=args.get("genre_filter"),
                owned_only=args.get("owned_only", False),
                limit=args.get("limit", 20)
            )
            return [result]
        
        elif name == "get_game_details":
            result = await get_game_details(
                game_id=args["game_id"],
                library_id=args.get("library_id")
            )
            return [result]
        
        elif name == "analyze_gaming_patterns":
            result = await analyze_gaming_patterns(
                library_id=args.get("library_id"),
                time_period=args.get("time_period", "month"),
                include_predictions=args.get("include_predictions", True)
            )
            return [result]
        
        elif name == "filter_by_content_rating":
            result = await filter_by_content_rating(
                max_rating=args["max_rating"],
                library_id=args.get("library_id"),
                exclude_descriptors=args.get("exclude_descriptors"),
                include_unrated=args.get("include_unrated", True)
            )
            return [result]
        
        elif name == "recommend_games":
            result = await recommend_games(
                library_id=args.get("library_id"),
                criteria=args.get("criteria"),
                limit=args.get("limit", 10),
                include_owned=args.get("include_owned", False)
            )
            return [result]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [{
            "error": f"Tool execution failed: {str(e)}",
            "tool": name,
            "arguments": arguments
        }]

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources."""
    return []

async def main():
    """Main entry point."""
    logger.info("Starting Game Djinn MCP Server")
    
    # Initialize database connection
    db_initialized = await init_database()
    if not db_initialized:
        logger.error("Failed to initialize database connection")
        return
    
    try:
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="game-djinn-mcp",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    )
                )
            )
    finally:
        # Cleanup
        await close_engine()
        logger.info("Game Djinn MCP Server stopped")

if __name__ == "__main__":
    asyncio.run(main())