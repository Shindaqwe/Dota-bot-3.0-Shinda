from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, JSON, DateTime
from datetime import datetime

from config import Config

Base = declarative_base()
engine = create_async_engine(Config.DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    steam_id = Column(String, unique=True)
    profile_data = Column(JSON)  # Кэшированные данные профиля
    created_at = Column(DateTime, default=datetime.utcnow)

class Friend(Base):
    __tablename__ = "friends"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    friend_steam_id = Column(String)
    friend_name = Column(String)
    added_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)