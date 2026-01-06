from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="📊 Моя статистика"))
    builder.add(KeyboardButton(text="👥 Друзья"))
    builder.add(KeyboardButton(text="📈 Мета герои"))
    builder.add(KeyboardButton(text="🔍 Найти игрока"))
    builder.add(KeyboardButton(text="🛠 Поддержка"))
    builder.add(KeyboardButton(text="⚙️ Настройки"))
    
    return builder.as_markup(resize_keyboard=True)