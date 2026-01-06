import aiohttp
from typing import Dict, Any, Optional

class OpenDotaAPI:
    def __init__(self):
        self.base_url = "https://api.opendota.com/api"
    
    async def get_player_stats(self, steam_id: str) -> Optional[Dict[str, Any]]:
        """Получает статистику игрока"""
        async with aiohttp.ClientSession() as session:
            try:
                # Получаем основную информацию
                async with session.get(f"{self.base_url}/players/{steam_id}") as resp:
                    if resp.status == 200:
                        player_info = await resp.json()
                
                # Получаем последние матчи
                async with session.get(f"{self.base_url}/players/{steam_id}/recentMatches") as resp:
                    if resp.status == 200:
                        recent_matches = await resp.json()
                
                # Получаем винрейт
                async with session.get(f"{self.base_url}/players/{steam_id}/wl") as resp:
                    if resp.status == 200:
                        winrate = await resp.json()
                
                return {
                    "profile": player_info,
                    "recent_matches": recent_matches[:20],  # Последние 20 игр
                    "winrate": winrate
                }
            except Exception as e:
                print(f"Error fetching data: {e}")
                return None
    
    async def get_hero_meta(self) -> Dict[str, Any]:
        """Получает мету героев"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/heroStats") as resp:
                return await resp.json()
