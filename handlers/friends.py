from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.opendota_api import OpenDotaAPI
from services.steam_api import SteamAPI
from utils.steam_resolver import SteamIDResolver
from database import async_session
from database import Friend
from sqlalchemy import select, delete
from config import Config

router = Router()

class FriendsStates(StatesGroup):
    adding_friend = State()
    comparing = State()

@router.message(F.text == "👥 Друзья")
async def friends_menu(message: types.Message):
    """Главное меню друзей"""
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📋 Список друзей")],
            [types.KeyboardButton(text="➕ Добавить друга")],
            [types.KeyboardButton(text="⚔️ Сравнить с другом")],
            [types.KeyboardButton(text="🗑 Удалить друга")],
            [types.KeyboardButton(text="🔄 Синхронизировать со Steam")],
            [types.KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    
    await message.answer("👥 Управление друзьями:", reply_markup=keyboard)

@router.message(F.text == "📋 Список друзей")
async def list_friends(message: types.Message):
    """Показывает список сохраненных друзей"""
    async with async_session() as session:
        result = await session.execute(
            select(Friend).where(Friend.user_id == message.from_user.id)
        )
        friends = result.scalars().all()
        
        if not friends:
            await message.answer("У вас пока нет добавленных друзей.")
            return
        
        text = "📋 Ваши друзья:\n\n"
        for i, friend in enumerate(friends, 1):
            text += f"{i}. {friend.friend_name}\n"
            text += f"   Steam ID: {friend.friend_steam_id}\n"
            text += f"   Добавлен: {friend.added_at.strftime('%d.%m.%Y')}\n\n"
        
        # Кнопки для быстрого просмотра статистики друзей
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        for friend in friends[:5]:  # Ограничиваем 5 кнопками
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"📊 {friend.friend_name}",
                    callback_data=f"friend_stats_{friend.friend_steam_id}"
                )
            ])
        
        await message.answer(text, reply_markup=keyboard)

@router.message(F.text == "➕ Добавить друга")
async def add_friend_start(message: types.Message, state: FSMContext):
    """Начинает процесс добавления друга"""
    await message.answer(
        "Введите SteamID или ссылку на профиль друга:\n\n"
        "Форматы:\n"
        "• https://steamcommunity.com/id/username\n"
        "• https://steamcommunity.com/profiles/7656119xxxxxxxx\n"
        "• SteamID64: 76561198012345678\n"
        "• Account ID: 12345678\n\n"
        "Нажмите /cancel для отмены",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(FriendsStates.adding_friend)

@router.message(FriendsStates.adding_friend, F.text.lower() == "/cancel")
async def cancel_add_friend(message: types.Message, state: FSMContext):
    """Отменяет добавление друга"""
    await state.clear()
    await message.answer("Добавление друга отменено", reply_markup=get_main_menu())

@router.message(FriendsStates.adding_friend)
async def process_add_friend(message: types.Message, state: FSMContext):
    """Обрабатывает добавление друга"""
    if not SteamIDResolver.is_valid_steam_format(message.text):
        await message.answer(
            "Неверный формат. Введите SteamID или ссылку в правильном формате:"
        )
        return
    
    await message.answer("🔍 Проверяю профиль...")
    
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
    
    # Сохраняем друга в БД
    async with async_session() as session:
        # Проверяем, не добавлен ли уже
        result = await session.execute(
            select(Friend).where(
                Friend.user_id == message.from_user.id,
                Friend.friend_steam_id == steam_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            await message.answer(
                f"❌ {player_summary.get('personaname')} уже есть в вашем списке друзей.",
                reply_markup=get_main_menu()
            )
        else:
            friend = Friend(
                user_id=message.from_user.id,
                friend_steam_id=steam_id,
                friend_name=player_summary.get('personaname', 'Unknown')
            )
            session.add(friend)
            await session.commit()
            
            await message.answer(
                f"✅ {player_summary.get('personaname')} успешно добавлен в список друзей!",
                reply_markup=get_main_menu()
            )
    
    await state.clear()

@router.callback_query(F.data.startswith("friend_stats_"))
async def show_friend_stats(callback: types.CallbackQuery):
    """Показывает статистику друга"""
    steam_id = callback.data.split("_")[2]
    
    await callback.message.answer("⏳ Загружаю статистику друга...")
    
    opendota = OpenDotaAPI()
    player_data = await opendota.get_player_stats(steam_id)
    
    if player_data:
        # Используем существующий форматтер
        from services.formatters import format_player_stats
        formatted_stats = format_player_stats(player_data)
        
        await callback.message.answer(
            f"📊 Статистика друга:\n\n{formatted_stats}"
        )
    else:
        await callback.message.answer(
            "Не удалось загрузить статистику друга. "
            "Возможно, профиль скрыт или нет данных на OpenDota."
        )
    
    await callback.answer()
