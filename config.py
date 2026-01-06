import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Токен бота
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не установлен в переменных окружения")
    
    # Steam API Key
    STEAM_API_KEY = os.getenv("STEAM_API_KEY")
    if not STEAM_API_KEY:
        raise ValueError("STEAM_API_KEY не установлен в переменных окружения")
    
    # OpenDota API
    OPENDOTA_URL = "https://api.opendota.com/api"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///database.db")
    
    # Настройки кэширования
    CACHE_TTL = 300  # 5 минут
    
    @classmethod
    def validate(cls):
        """Проверяет наличие всех необходимых переменных"""
        required = ['BOT_TOKEN', 'STEAM_API_KEY']
        missing = [var for var in required if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Отсутствуют переменные окружения: {', '.join(missing)}")
        
        print("✅ Конфигурация загружена успешно")
        print(f"🤖 Bot token: {'*' * 10}{cls.BOT_TOKEN[-5:]}")
        print(f"🎮 Steam API key: {'*' * 10}{cls.STEAM_API_KEY[-5:]}")

# Проверяем конфигурацию при импорте
Config.validate()
