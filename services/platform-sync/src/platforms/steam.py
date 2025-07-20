"""Steam platform integration."""

import asyncio
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, AsyncGenerator
import httpx
from urllib.parse import urlencode

from .base import (
    BasePlatform, PlatformError, RateLimitError,
    GameData, UserGameData, AchievementData, UserAchievementData, UserProfileData
)


class SteamPlatform(BasePlatform):
    """Steam Web API integration."""
    
    BASE_URL = "https://api.steampowered.com"
    STORE_URL = "https://store.steampowered.com"
    COMMUNITY_URL = "https://steamcommunity.com"
    
    # Rate limiting: Steam allows 100,000 requests per day
    REQUESTS_PER_SECOND = 2
    REQUESTS_PER_MINUTE = 100
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__("steam", credentials)
        self.api_key = credentials.get("steam_api_key")
        if not self.api_key:
            raise ValueError("Steam API key is required")
        
        # HTTP client with rate limiting
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )
        
        # Simple rate limiter (in production, use Redis-based limiter)
        self._last_request_time = 0
        self._request_semaphore = asyncio.Semaphore(self.REQUESTS_PER_SECOND)
    
    @property
    def platform_name(self) -> str:
        return "Steam"
    
    @property
    def requires_auth(self) -> bool:
        return True
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make rate-limited request to Steam API."""
        async with self._request_semaphore:
            # Basic rate limiting
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < (1.0 / self.REQUESTS_PER_SECOND):
                await asyncio.sleep((1.0 / self.REQUESTS_PER_SECOND) - time_since_last)
            
            params["key"] = self.api_key
            params["format"] = "json"
            
            url = f"{self.BASE_URL}/{endpoint}"
            
            self.logger.debug(f"Making Steam API request: {endpoint}")
            
            try:
                response = await self.client.get(url, params=params)
                self._last_request_time = asyncio.get_event_loop().time()
                
                if response.status_code == 429:
                    raise RateLimitError("Steam API rate limit exceeded", retry_after=60)
                elif response.status_code == 403:
                    raise PlatformError("Steam API access forbidden - check API key")
                elif response.status_code != 200:
                    raise PlatformError(f"Steam API error: {response.status_code}")
                
                data = response.json()
                return data
                
            except httpx.TimeoutException:
                raise PlatformError("Steam API request timed out")
            except httpx.RequestError as e:
                raise PlatformError(f"Steam API request failed: {e}")
    
    async def validate_credentials(self) -> bool:
        """Validate Steam API key."""
        try:
            # Try to get Steam app list (minimal request)
            data = await self._make_request(
                "ISteamApps/GetAppList/v2",
                {}
            )
            return "applist" in data
        except Exception:
            return False
    
    async def get_user_profile(self, user_identifier: str) -> UserProfileData:
        """Get Steam user profile information."""
        steamid = await self._resolve_vanity_url(user_identifier)
        
        data = await self._make_request(
            "ISteamUser/GetPlayerSummaries/v2",
            {"steamids": steamid}
        )
        
        if not data.get("response", {}).get("players"):
            raise PlatformError(f"Steam user not found: {user_identifier}")
        
        player = data["response"]["players"][0]
        
        # Get additional profile data
        games_data = await self._make_request(
            "IPlayerService/GetOwnedGames/v1",
            {"steamid": steamid, "include_appinfo": 1, "include_played_free_games": 1}
        )
        
        games_info = games_data.get("response", {})
        total_games = games_info.get("game_count", 0)
        
        # Calculate total playtime
        total_playtime_minutes = sum(
            game.get("playtime_forever", 0) 
            for game in games_info.get("games", [])
        )
        
        return UserProfileData(
            user_identifier=steamid,
            display_name=player.get("personaname", "Unknown"),
            avatar_url=player.get("avatarfull"),
            profile_url=player.get("profileurl"),
            profile_visibility=self._parse_profile_visibility(player.get("communityvisibilitystate", 1)),
            member_since=datetime.fromtimestamp(player.get("timecreated", 0), tz=timezone.utc) if player.get("timecreated") else None,
            total_games=total_games,
            total_playtime_minutes=total_playtime_minutes,
            platform_data={
                "personastate": player.get("personastate"),
                "realname": player.get("realname"),
                "countrycode": player.get("loccountrycode"),
                "statecode": player.get("locstatecode"),
                "lastlogoff": player.get("lastlogoff")
            }
        )
    
    async def get_user_games(
        self, 
        user_identifier: str,
        include_free_games: bool = True,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> AsyncGenerator[UserGameData, None]:
        """Get user's Steam game library."""
        steamid = await self._resolve_vanity_url(user_identifier)
        
        # Get owned games
        data = await self._make_request(
            "IPlayerService/GetOwnedGames/v1",
            {
                "steamid": steamid,
                "include_appinfo": 1,
                "include_played_free_games": 1 if include_free_games else 0
            }
        )
        
        games = data.get("response", {}).get("games", [])
        
        # Apply pagination
        if offset:
            games = games[offset:]
        if limit:
            games = games[:limit]
        
        for game in games:
            try:
                # Get additional game details
                game_details = await self.get_game_details(str(game["appid"]))
                
                # Convert playtime to minutes
                total_playtime_minutes = game.get("playtime_forever", 0)
                last_played_timestamp = game.get("rtime_last_played")
                
                user_game_data = UserGameData(
                    game_data=game_details,
                    owned=True,
                    total_playtime_minutes=total_playtime_minutes,
                    last_played_at=datetime.fromtimestamp(last_played_timestamp, tz=timezone.utc) if last_played_timestamp else None,
                    platform_data={
                        "playtime_2weeks": game.get("playtime_2weeks", 0),
                        "playtime_windows_forever": game.get("playtime_windows_forever", 0),
                        "playtime_mac_forever": game.get("playtime_mac_forever", 0),
                        "playtime_linux_forever": game.get("playtime_linux_forever", 0),
                        "has_community_visible_stats": game.get("has_community_visible_stats", False)
                    }
                )
                
                yield user_game_data
                
            except Exception as e:
                self.logger.warning(f"Error processing Steam game {game.get('appid')}: {e}")
                continue
    
    async def get_game_details(self, platform_game_id: str) -> GameData:
        """Get detailed Steam game information."""
        appid = int(platform_game_id)
        
        # Get app details from Steam store API
        store_url = f"{self.STORE_URL}/api/appdetails"
        params = {"appids": appid, "cc": "us", "l": "en"}
        
        try:
            response = await self.client.get(store_url, params=params)
            if response.status_code != 200:
                raise PlatformError(f"Steam store API error: {response.status_code}")
            
            data = response.json()
            app_data = data.get(str(appid), {})
            
            if not app_data.get("success"):
                raise PlatformError(f"Steam app not found: {appid}")
            
            details = app_data["data"]
            
            # Parse release date
            release_date = None
            if details.get("release_date", {}).get("date"):
                try:
                    date_str = details["release_date"]["date"]
                    # Steam dates can be in various formats
                    for fmt in ["%b %d, %Y", "%Y", "%b %Y"]:
                        try:
                            release_date = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass
            
            # Parse screenshots
            screenshots = []
            for screenshot in details.get("screenshots", []):
                screenshots.append(screenshot.get("path_full"))
            
            # Parse genres and categories
            genres = [genre["description"] for genre in details.get("genres", [])]
            categories = [cat["description"] for cat in details.get("categories", [])]
            
            return GameData(
                title=details.get("name", "Unknown"),
                platform_game_id=str(appid),
                developer=", ".join(details.get("developers", [])) if details.get("developers") else None,
                publisher=", ".join(details.get("publishers", [])) if details.get("publishers") else None,
                release_date=release_date,
                description=details.get("detailed_description"),
                short_description=details.get("short_description"),
                genres=genres,
                tags=categories,  # Steam categories serve as tags
                cover_image_url=details.get("header_image"),
                background_image_url=details.get("background"),
                screenshots=screenshots,
                metacritic_score=details.get("metacritic", {}).get("score"),
                website_url=details.get("website"),
                external_ids={"steam_appid": appid},
                esrb_rating=self._parse_esrb_rating(details.get("content_descriptors", {})),
                platform_data={
                    "type": details.get("type"),
                    "is_free": details.get("is_free", False),
                    "required_age": details.get("required_age", 0),
                    "price_overview": details.get("price_overview"),
                    "platforms": details.get("platforms"),
                    "recommendations": details.get("recommendations"),
                    "achievements": details.get("achievements"),
                    "support_info": details.get("support_info")
                }
            )
            
        except httpx.RequestError as e:
            raise PlatformError(f"Steam store request failed: {e}")
    
    async def get_game_achievements(self, platform_game_id: str) -> List[AchievementData]:
        """Get Steam game achievements."""
        appid = int(platform_game_id)
        
        try:
            data = await self._make_request(
                "ISteamUserStats/GetSchemaForGame/v2",
                {"appid": appid}
            )
            
            achievements = []
            game_data = data.get("game", {})
            available_achievements = game_data.get("availableGameStats", {}).get("achievements", [])
            
            for ach in available_achievements:
                achievements.append(AchievementData(
                    platform_achievement_id=ach.get("name", ""),
                    title=ach.get("displayName", ""),
                    description=ach.get("description", ""),
                    icon_url=ach.get("icon"),
                    is_hidden=ach.get("hidden", 0) == 1
                ))
            
            return achievements
            
        except Exception as e:
            self.logger.warning(f"Could not get achievements for Steam app {appid}: {e}")
            return []
    
    async def get_user_achievements(
        self, 
        user_identifier: str, 
        platform_game_id: str
    ) -> List[UserAchievementData]:
        """Get user's Steam achievements for a specific game."""
        steamid = await self._resolve_vanity_url(user_identifier)
        appid = int(platform_game_id)
        
        try:
            data = await self._make_request(
                "ISteamUserStats/GetPlayerAchievements/v1",
                {"steamid": steamid, "appid": appid}
            )
            
            user_achievements = []
            player_stats = data.get("playerstats", {})
            achievements = player_stats.get("achievements", [])
            
            for ach in achievements:
                if ach.get("achieved") == 1:
                    unlock_time = ach.get("unlocktime", 0)
                    
                    # Get achievement details
                    achievement_data = AchievementData(
                        platform_achievement_id=ach.get("apiname", ""),
                        title=ach.get("name", ""),
                        description=ach.get("description", "")
                    )
                    
                    user_achievements.append(UserAchievementData(
                        achievement_data=achievement_data,
                        unlocked_at=datetime.fromtimestamp(unlock_time, tz=timezone.utc) if unlock_time else datetime.utcnow(),
                        progress_percentage=100
                    ))
            
            return user_achievements
            
        except Exception as e:
            self.logger.warning(f"Could not get user achievements for Steam app {appid}: {e}")
            return []
    
    async def _resolve_vanity_url(self, user_identifier: str) -> str:
        """Resolve Steam vanity URL to SteamID64."""
        # If already a SteamID64, return as-is
        if user_identifier.isdigit() and len(user_identifier) == 17:
            return user_identifier
        
        # Try to resolve vanity URL
        try:
            data = await self._make_request(
                "ISteamUser/ResolveVanityURL/v1",
                {"vanityurl": user_identifier}
            )
            
            response = data.get("response", {})
            if response.get("success") == 1:
                return response["steamid"]
            else:
                raise PlatformError(f"Could not resolve Steam user: {user_identifier}")
                
        except Exception:
            raise PlatformError(f"Invalid Steam user identifier: {user_identifier}")
    
    def _parse_profile_visibility(self, visibility_state: int) -> str:
        """Parse Steam profile visibility state."""
        visibility_map = {
            1: "private",
            2: "friends_only", 
            3: "public"
        }
        return visibility_map.get(visibility_state, "private")
    
    def _parse_esrb_rating(self, content_descriptors: Dict[str, Any]) -> Optional[str]:
        """Parse ESRB rating from Steam content descriptors."""
        # This is a simplified parser - Steam doesn't always provide ESRB ratings
        # In a real implementation, you might cross-reference with external data
        descriptors = content_descriptors.get("notes", "").lower()
        
        if "mature" in descriptors or "blood" in descriptors or "violence" in descriptors:
            return "M"
        elif "teen" in descriptors or "mild" in descriptors:
            return "T"
        elif any(word in descriptors for word in ["everyone", "all ages", "family"]):
            return "E"
        
        return None
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()