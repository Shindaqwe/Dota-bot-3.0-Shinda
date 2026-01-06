from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.opendota_api import OpenDotaAPI
from services.steam_api import SteamAPI
from services.formatters import format_player_stats
from utils.steam_resolver import SteamIDResolver
from keyboards.main_menu import get_main_menu
from config import Config

router = Router()

class QuickSearchStates(StatesGroup):
    waiting_for_steam_id = State()

@router.message(F.text == "🔍 Найти игрока")
async def quick_search_start(message: types.Message, state: FSMContext):
    """Начинает быстрый поиск профиля"""
    await message.answer(
        "Введите SteamID или ссылку на профиль любого игрока:\n\n"
        "Доступные форматы:\n"
        "• https://steamcommunity.com/id/username\n"
        "• https://steamcommunity.com/profiles/7656119xxxxxxxx\n"
        "• SteamID64: 76561198012345678\n"
        "• Account ID: 12345678\n\n"
        "Нажмите /cancel для отмены",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(QuickSearchStates.waiting_for_steam_id)

@router.message(QuickSearchStates.waiting_for_steam_id, F.text.lower() == "/cancel")
async def cancel_quick_search(message: types.Message, state: FSMContext):
    """Отменяет быстрый поиск"""
    await state.clear()
    await message.answer("Поиск отменен", reply_markup=get_main_menu())

@router.message(QuickSearchStates.waiting_for_steam_id)
async def process_quick_search(message: types.Message, state: FSMContext):
    """Обрабатывает быстрый поиск профиля"""
    if not SteamIDResolver.is_valid_steam_format(message.text):
        await message.answer(
            "Неверный формат. Введите SteamID или ссылку в правильном формате:"
        )
        return
    
    await message.answer("🔍 Ищу игрока...")
    
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
        await state.clear()
        return
    
    # Проверяем существование профиля
    player_summary = await steam_api.get_player_summaries(steam_id)
    if not player_summary:
        await message.answer(
            "Профиль не найден. Проверьте правильность Steam ID.",
            reply_markup=get_main_menu()
        )
        await state.clear()
        return
    
    # Получаем статистику
    opendota = OpenDotaAPI()
    player_data = await opendota.get_player_stats(steam_id)
    
    if player_data:
        formatted_stats = format_player_stats(player_data)
        # Добавляем информацию о том, что это быстрый поиск
        result_text = (
            f"🔍 Результаты поиска:\n\n"
            f"👤 {player_summary.get('personaname', 'Unknown')}\n"
            f"{formatted_stats}\n"
            f"📌 Это быстрый поиск. Чтобы сохранить профиль, привяжите его через '📊 Моя статистика'"
        )
        await message.answer(result_text, reply_markup=get_main_menu())
    else:
        await message.answer(
            f"🔍 Профиль найден:\n"
            f"👤 {player_summary.get('personaname', 'Unknown')}\n\n"
            "Но не удалось загрузить статистику матчей. "
            "Возможно, профиль скрыт или нет данных на OpenDota.",
            reply_markup=get_main_menu()
        )
    
    await state.clear()
