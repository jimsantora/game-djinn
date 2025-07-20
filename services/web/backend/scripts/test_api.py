#!/usr/bin/env python3
"""Test script to verify backend API functionality."""

import asyncio
import httpx
import os
from typing import Dict, Any


async def test_api_endpoints():
    """Test the backend API endpoints."""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("Testing Game Djinn Backend API")
        print("=" * 40)
        
        # Test health endpoint
        try:
            response = await client.get(f"{base_url}/health")
            print(f"✓ Health: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"✗ Health: Failed - {e}")
            return
        
        # Test auth config
        try:
            response = await client.get(f"{base_url}/api/auth/config")
            print(f"✓ Auth config: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"✗ Auth config: Failed - {e}")
        
        # Test platforms (should work now)
        try:
            response = await client.get(f"{base_url}/api/platforms?enabled_only=false")
            print(f"✓ Platforms: {response.status_code}")
            if response.status_code == 200:
                platforms = response.json()
                print(f"  Found {len(platforms)} platforms:")
                for platform in platforms:
                    print(f"    - {platform['platform_name']} ({platform['platform_code']}) - Enabled: {platform['is_enabled']}")
            else:
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"✗ Platforms: Failed - {e}")
        
        # Test games endpoint
        try:
            response = await client.get(f"{base_url}/api/games")
            print(f"✓ Games: {response.status_code}")
            if response.status_code == 200:
                games = response.json()
                print(f"  Found {games.get('total', 0)} games")
            else:
                print(f"  Response: {response.text}")
        except Exception as e:
            print(f"✗ Games: Failed - {e}")
        
        # Test libraries endpoint  
        try:
            response = await client.get(f"{base_url}/api/libraries")
            print(f"✓ Libraries: {response.status_code}")
            if response.status_code == 200:
                libraries = response.json()
                print(f"  Found {libraries.get('total', 0)} libraries")
            else:
                print(f"  Response: {response.text}")
        except Exception as e:
            print(f"✗ Libraries: Failed - {e}")


if __name__ == "__main__":
    print("Make sure the backend server is running:")
    print("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    
    asyncio.run(test_api_endpoints())