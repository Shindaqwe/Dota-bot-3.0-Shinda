import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class SimpleCache:
    def __init__(self, ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl  # Time To Live в секундах
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Получает значение из кэша"""
        if key in self.cache:
            item = self.cache[key]
            if datetime.now() < item['expires']:
                return item['data']
            else:
                del self.cache[key]
        return None
    
    async def set(self, key: str, data: Dict[str, Any]):
        """Сохраняет значение в кэш"""
        self.cache[key] = {
            'data': data,
            'expires': datetime.now() + timedelta(seconds=self.ttl)
        }
    
    async def clear(self):
        """Очищает кэш"""
        self.cache.clear()

# Глобальный экземпляр кэша
player_cache = SimpleCache()
