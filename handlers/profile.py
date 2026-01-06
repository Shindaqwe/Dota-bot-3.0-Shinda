from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from services.opendota_api import OpenDotaAPI
from services.steam_api import SteamAPI
from services.formatters import format_player_stats
from utils.steam_resolver import SteamIDResolver
from keyboards.main_menu import get_main_menu
from database import async_session
from database import User
from sqlalchemy import select
from datetime import datetime
from config import Config

router = Router()

class ProfileStates(StatesGroup):
    waiting_for_steam_link = State()

@router.message(F.text == "📊 Моя статистика")
async def show_my_stats(message: types.Message):
    """Показывает статистику текущего пользователя"""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if user and user.steam_id:
            # Показываем статистику
            opendota = OpenDotaAPI()
            player_data = await opendota.get_player_stats(user.steam_id)
            
            if player_data:
                formatted_stats = format_player_stats(player_data)
                await message.answer(formatted_stats, reply_markup=get_main_menu())
            else:
                await message.answer(
                    "Не удалось получить статистику. Проверьте правильность Steam ID.",
                    reply_markup=get_main_menu()
                )
        else:
            # Просим привязать профиль
            await message.answer(
                "Сначала привяжите свой Steam профиль. Отправьте ссылку или SteamID:",
                reply_markup=ReplyKeyboardRemove()
            )
            # Можно установить состояние, но для простоты просто отправляем сообщение

@router.message(F.text.regexp(r'.*(steam|steamcommunity|7656119|\d{17,}|\d{7,10}).*'))
async def process_steam_link(message: types.Message):
    """Обрабатывает Steam ссылку от пользователя"""
    if not SteamIDResolver.is_valid_steam_format(message.text):
        await message.answer(
            "Неверный формат. Отправьте один из следующих форматов:\n"
            "• https://steamcommunity.com/id/username\n"
            "• https://steamcommunity.com/profiles/7656119xxxxxxxx\n"
            "• SteamID64: 76561198012345678\n"
            "• Account ID: 12345678"
        )
        return
    
    await message.answer("🔍 Обрабатываю запрос...")
    
    # Конвертируем в SteamID64
    steam_api = SteamAPI(Config.STEAM_API_KEY)
    steam_id = await SteamIDResolver.resolve_to_steamid64(
        message.text, 
        Config.STEAM_API_KEY
    )
    
    if not steam_id:
        await message.answer(
            "Не удалось определить Steam ID. Проверьте правильность ссылки.",
            reply_markup=get_main_menu()
        )
        return
    
    # Проверяем существование профиля через Steam API
    player_summary = await steam_api.get_player_summaries(steam_id)
    if not player_summary:
        await message.answer(
            "Профиль не найден. Проверьте правильность Steam ID.",
            reply_markup=get_main_menu()
        )
        return
    
    # Сохраняем/обновляем пользователя в БД
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.steam_id = steam_id
            user.profile_data = player_summary
            user.created_at = datetime.utcnow()
        else:
            user = User(
                telegram_id=message.from_user.id,
                steam_id=steam_id,
                profile_data=player_summary
            )
            session.add(user)
        
        await session.commit()
    
    # Получаем статистику
    opendota = OpenDotaAPI()
    player_data = await opendota.get_player_stats(steam_id)
    
    if player_data:
        formatted_stats = format_player_stats(player_data)
        await message.answer(
            f"✅ Профиль успешно привязан!\n\n"
            f"👤 {player_summary.get('personaname', 'Unknown')}\n"
            f"📊 Статистика загружена\n\n"
            f"{formatted_stats}",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            f"✅ Профиль успешно привязан!\n"
            f"👤 {player_summary.get('personaname', 'Unknown')}\n\n"
            "Но не удалось загрузить статистику матчей. "
            "Попробуйте позже или проверьте настройки приватности профиля.",
            reply_markup=get_main_menu()
        )
