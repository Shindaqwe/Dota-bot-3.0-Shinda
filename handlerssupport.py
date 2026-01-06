from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.message(F.text == "🛠 Поддержка")
async def show_support(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Поддержать проект", url="https://www.donationalerts.com/r/shindaqwe")],
        [InlineKeyboardButton(text="🤖 Помощник", url="https://t.me/DotaShindaHelper_bot")]
    ])
    
    text = (
        "💖 Поддержка проекта:\n\n"
        "Если тебе нравится бот и ты хочешь помочь в его развитии:\n\n"
        "💰 Финансовая помощь - помогает оплачивать сервера и дальнейшую разработку\n"
        "🤖 Помощник - бот для быстрых ответов на вопросы"
    )
    
    await message.answer(text, reply_markup=keyboard)