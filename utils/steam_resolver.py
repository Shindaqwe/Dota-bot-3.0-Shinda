import re
import aiohttp
from typing import Optional

class SteamIDResolver:
    @staticmethod
    async def resolve_to_steamid64(input_text: str, steam_api_key: str = None) -> Optional[str]:
        """Конвертирует любой формат Steam в SteamID64"""
        
        # Удаляем пробелы
        input_text = input_text.strip()
        
        # Если это уже SteamID64 (17 цифр)
        if re.match(r'^\d{17}$', input_text):
            return input_text
        
        # Если это Account ID (32-битный)
        if re.match(r'^\d+$', input_text):
            account_id = int(input_text)
            # Конвертируем в SteamID64
            return str(account_id + 76561197960265728)
        
        # Если это URL профиля
        if 'steamcommunity.com' in input_text:
            # Профиль по цифровому ID
            match = re.search(r'steamcommunity\.com/profiles/(\d+)', input_text)
            if match:
                return match.group(1)
            
            # Кастомный URL
            match = re.search(r'steamcommunity\.com/id/([\w-]+)', input_text)
            if match and steam_api_key:
                return await SteamIDResolver.resolve_vanity_url(match.group(1), steam_api_key)
        
        return None
    
    @staticmethod
    async def resolve_vanity_url(vanity_url: str, steam_api_key: str) -> Optional[str]:
        """Разрешает кастомный URL в SteamID64 через Steam API"""
        url = f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
        
        async with aiohttp.ClientSession() as session:
            params = {
                'key': steam_api_key,
                'vanityurl': vanity_url
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['response']['success'] == 1:
                            return data['response']['steamid']
            except Exception as e:
                print(f"Error resolving vanity URL: {e}")
        
        return None
    
    @staticmethod
    def is_valid_steam_format(text: str) -> bool:
        """Проверяет, является ли текст валидным Steam идентификатором"""
        patterns = [
            r'^https?://steamcommunity\.com/(id|profiles)/[\w-]+',
            r'^\d{17}$',
            r'^\d+$'  # Account ID
        ]
        
        return any(re.match(pattern, text.strip()) for pattern in patterns)
