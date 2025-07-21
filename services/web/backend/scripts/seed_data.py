"""Seed initial data into the database."""

import asyncio
import logging
from sqlalchemy import select
from app.database.connection import async_session
from app.models import Platform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial platform data
INITIAL_PLATFORMS = [
    {
        "platform_code": "steam",
        "platform_name": "Steam",
        "api_available": True,
        "icon_url": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/steamworks_docs/english/SteamLogo_200px.png",
        "base_url": "https://steamcommunity.com",
    },
    {
        "platform_code": "xbox",
        "platform_name": "Xbox Game Pass",
        "api_available": True,  # Steam integration working, Xbox demo enabled for testing
        "icon_url": None,
        "base_url": "https://xbox.com",
    },
    {
        "platform_code": "gog",
        "platform_name": "GOG",
        "api_available": False,
        "icon_url": None,
        "base_url": "https://gog.com",
    },
    {
        "platform_code": "epic",
        "platform_name": "Epic Games Store",
        "api_available": False,
        "icon_url": None,
        "base_url": "https://store.epicgames.com",
    },
    {
        "platform_code": "playstation",
        "platform_name": "PlayStation Network",
        "api_available": False,  # Will be enabled in future phases
        "icon_url": None,
        "base_url": "https://playstation.com",
    },
    {
        "platform_code": "nintendo",
        "platform_name": "Nintendo eShop",
        "api_available": False,  # Will be enabled in future phases
        "icon_url": None,
        "base_url": "https://nintendo.com",
    },
    {
        "platform_code": "manual",
        "platform_name": "Manual Entry",
        "api_available": False,
        "icon_url": None,
        "base_url": None,
    },
]


async def seed_platforms():
    """Seed initial platform data."""
    logger.info("Seeding platform data...")
    
    async with async_session() as session:
        try:
            # Check existing platforms
            result = await session.execute(select(Platform))
            existing_platforms = result.scalars().all()
            existing_codes = {p.platform_code for p in existing_platforms}
            
            platforms_added = 0
            for platform_data in INITIAL_PLATFORMS:
                if platform_data["platform_code"] not in existing_codes:
                    platform = Platform(**platform_data)
                    session.add(platform)
                    platforms_added += 1
                    logger.info(f"Adding platform: {platform_data['platform_name']}")
                else:
                    logger.info(f"Platform already exists: {platform_data['platform_name']}")
            
            if platforms_added > 0:
                await session.commit()
                logger.info(f"Successfully added {platforms_added} platforms")
            else:
                logger.info("No new platforms to add")
                
        except Exception as e:
            await session.rollback()
            logger.error(f"Error seeding platforms: {e}")
            raise


async def seed_test_data():
    """Seed test data for development."""
    logger.info("Seeding test data...")
    
    # For now, just seed platforms
    # In the future, we can add test games, users, etc.
    await seed_platforms()
    
    logger.info("Test data seeding completed")


async def main():
    """Main seeding function."""
    try:
        await seed_test_data()
        logger.info("Database seeding completed successfully")
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())