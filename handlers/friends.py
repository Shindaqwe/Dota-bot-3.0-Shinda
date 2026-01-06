from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class FriendsStates(StatesGroup):
    adding_friend = State()
    comparing = State()

@router.message(F.text == "👥 Друзья")
async def friends_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📋 Список друзей")],
            [types.KeyboardButton(text="➕ Добавить друга")],
            [types.KeyboardButton(text="📊 Сравнить с другом")],
            [types.KeyboardButton(text="🗑 Удалить друга")],
            [types.KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    
    await message.answer("Меню друзей:", reply_markup=keyboard)
