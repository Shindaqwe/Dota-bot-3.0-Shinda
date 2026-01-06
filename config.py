import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    STEAM_API_KEY = os.getenv("STEAM_API_KEY")
    
    # OpenDota API
    OPENDOTA_URL = "https://api.opendota.com/api"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///database.db")