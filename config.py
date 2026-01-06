import os

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    STEAM_API_KEY = os.getenv("STEAM_API_KEY", "")
    
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен!")
        if not cls.STEAM_API_KEY:
            raise ValueError("STEAM_API_KEY не установлен!")
        
        print("✅ Конфигурация загружена успешно")
