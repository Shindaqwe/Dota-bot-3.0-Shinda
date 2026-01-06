from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re

from services.opendota_api import OpenDotaAPI
from services.formatters import format_player_stats
from keyboards.main_menu import get_main_menu

router = Router()

class ProfileStates(StatesGroup):
    waiting_for_steam_link = State()

@router.message(F.text == "📊 Моя статистика")
async def show_my_stats(message: types.Message):
    # Проверка, привязан ли профиль
    # Если нет - запрашиваем ссылку
    await message.answer(
        "Сначала привяжи свой Steam профиль. Отправь ссылку или SteamID:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    # Устанавливаем состояние ожидания ссылки
    # Реализация через FSM

@router.message(F.text.regexp(r'(steamcommunity\.com|steamid|7656119|^\d+$)'))
async def process_steam_link(message: types.Message):
    # Извлекаем Steam ID из различных форматов
    steam_id = extract_steam_id(message.text)
    
    if steam_id:
        # Получаем данные с OpenDota
        opendota = OpenDotaAPI()
        player_data = await opendota.get_player_stats(steam_id)
        
        if player_data:
            # Форматируем статистику
            formatted_stats = format_player_stats(player_data)
            await message.answer(formatted_stats, reply_markup=get_main_menu())
        else:
            await message.answer("Не удалось получить данные. Проверь правильность ссылки.")
    else:
        await message.answer("Неверный формат. Отправь ссылку или SteamID:")

def extract_steam_id(text: str) -> str:
    """Извлекает Steam ID из различных форматов"""
    patterns = [
        r'steamcommunity\.com/profiles/(\d+)',
        r'steamcommunity\.com/id/(\w+)',
        r'(\d{17})',  # 17-значный SteamID64
        r'(\d{1,10})'  # Account ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None
