import aiohttp
from typing import Optional, Dict, Any

class SteamAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.steampowered.com"
    
    async def get_player_summaries(self, steamids: str) -> Optional[Dict[str, Any]]:
        """Получает информацию о игроках"""
        url = f"{self.base_url}/ISteamUser/GetPlayerSummaries/v0002/"
        
        async with aiohttp.ClientSession() as session:
            params = {
                'key': self.api_key,
                'steamids': steamids
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['response']['players'][0] if data['response']['players'] else None
            except Exception as e:
                print(f"Error getting player summaries: {e}")
        
        return None
    
    async def get_friend_list(self, steamid: str) -> Optional[Dict[str, Any]]:
        """Получает список друзей игрока"""
        url = f"{self.base_url}/ISteamUser/GetFriendList/v0001/"
        
        async with aiohttp.ClientSession() as session:
            params = {
                'key': self.api_key,
                'steamid': steamid,
                'relationship': 'friend'
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
            except Exception as e:
                print(f"Error getting friend list: {e}")
        
        return None
