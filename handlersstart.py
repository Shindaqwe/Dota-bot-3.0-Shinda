from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import get_main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    welcome_text = (
        "Привет!👋\n"
        "Я бот анализатор матчей DotaStats\n"
        "Мой создатель @shindaqwe\n\n"
        "Отправь ссылку на свой Steam профиль для статистики.\n\n"
        "Форматы ссылок:\n"
        "• https://steamcommunity.com/id/username\n"
        "• https://steamcommunity.com/profiles/7656119xxxxxxxx\n"
        "• Просто SteamID (например: 76561198012345678)\n"
        "• Или Account ID (например: 12345678)"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_menu())