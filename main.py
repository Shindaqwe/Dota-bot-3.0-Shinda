import os
import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получаем токены из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN не установлен!")
    exit(1)

if not STEAM_API_KEY:
    logger.warning("⚠️ STEAM_API_KEY не установлен, некоторые функции будут недоступны")

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Клавиатура с кнопками
def get_main_keyboard():
    keyboard = [
        [types.KeyboardButton(text="📊 Моя статистика")],
        [types.KeyboardButton(text="🔍 Найти игрока")],
        [types.KeyboardButton(text="📈 Мета герои")],
        [types.KeyboardButton(text="🛠 Поддержка")]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
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
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.message(F.text == "📊 Моя статистика")
async def my_stats(message: types.Message):
    await message.answer(
        "📊 Для просмотра статистики отправьте ваш Steam ID или ссылку на профиль.\n\n"
        "Пример:\n"
        "• https://steamcommunity.com/id/username\n"
        "• 76561198012345678"
    )

@dp.message(F.text == "🔍 Найти игрока")
async def find_player(message: types.Message):
    await message.answer(
        "🔍 Введите Steam ID или ссылку на профиль любого игрока:\n\n"
        "Форматы:\n"
        "• https://steamcommunity.com/id/username\n"
        "• https://steamcommunity.com/profiles/7656119xxxxxxxx\n"
        "• 76561198012345678"
    )

@dp.message(F.text == "📈 Мета герои")
async def meta_heroes(message: types.Message):
    await message.answer("🔄 Получаю информацию о мета-героях...")
    
    # Простой пример работы с OpenDota API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.opendota.com/api/heroStats") as response:
                if response.status == 200:
                    heroes = await response.json()
                    # Берем топ-5 героев по популярности
                    top_heroes = sorted(heroes, key=lambda x: x.get("pick_rate", 0), reverse=True)[:5]
                    
                    text = "🏆 Топ-5 популярных героев:\n\n"
                    for hero in top_heroes:
                        text += f"• {hero['localized_name']}\n"
                        text += f"  📊 Пиков: {hero.get('pick_rate', 0):.1f}%\n"
                        text += f"  🏆 Винрейт: {hero.get('win_rate', 0):.1f}%\n\n"
                    
                    await message.answer(text)
                else:
                    await message.answer("❌ Не удалось получить данные о героях")
    except Exception as e:
        logger.error(f"Ошибка при получении меты: {e}")
        await message.answer("⚠️ Произошла ошибка при получении данных")

@dp.message(F.text == "🛠 Поддержка")
async def support(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💰 Поддержать проект", url="https://www.donationalerts.com/r/shindaqwe")],
        [types.InlineKeyboardButton(text="🤖 Помощник", url="https://t.me/DotaShindaHelper_bot")]
    ])
    
    text = (
        "💖 Поддержка проекта:\n\n"
        "Если тебе нравится бот и ты хочешь помочь в его развитии:\n\n"
        "💰 Финансовая помощь - помогает оплачивать сервера и дальнейшую разработку\n"
        "🤖 Помощник - бот для быстрых ответов на вопросы"
    )
    
    await message.answer(text, reply_markup=keyboard)

@dp.message(F.text.contains("steamcommunity.com") | F.text.regexp(r'^\d{17}$'))
async def handle_steam_link(message: types.Message):
    """Обработка Steam ссылок"""
    steam_id = message.text
    
    await message.answer(f"🔍 Обрабатываю Steam ID: {steam_id}\n\n"
                        "⏳ Получаю данные с OpenDota...")
    
    try:
        # Получаем базовую информацию об игроке
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.opendota.com/api/players/{steam_id}") as response:
                if response.status == 200:
                    player_data = await response.json()
                    
                    # Получаем последние матчи
                    async with session.get(f"https://api.opendota.com/api/players/{steam_id}/recentMatches") as matches_resp:
                        matches = await matches_resp.json() if matches_resp.status == 200 else []
                    
                    # Формируем ответ
                    persona_name = player_data.get("profile", {}).get("personaname", "Неизвестно")
                    mmr_estimate = player_data.get("mmr_estimate", {}).get("estimate", "Неизвестно")
                    
                    text = f"👤 Игрок: {persona_name}\n"
                    text += f"🎯 Примерный MMR: {mmr_estimate}\n\n"
                    
                    if matches:
                        text += f"📊 Последние {min(3, len(matches))} матча:\n"
                        for match in matches[:3]:
                            win = "✅" if match.get("player_slot", 0) < 128 == match.get("radiant_win", False) else "❌"
                            hero_id = match.get("hero_id", 0)
                            kills = match.get("kills", 0)
                            deaths = match.get("deaths", 0)
                            assists = match.get("assists", 0)
                            
                            # Получаем имя героя
                            async with session.get(f"https://api.opendota.com/api/heroes/{hero_id}") as hero_resp:
                                hero_name = "Неизвестно"
                                if hero_resp.status == 200:
                                    hero_data = await hero_resp.json()
                                    hero_name = hero_data.get("localized_name", "Неизвестно")
                            
                            text += f"{win} {hero_name} - {kills}/{deaths}/{assists}\n"
                    
                    text += "\n📈 Для более детальной статистики используйте OpenDota или Dotabuff"
                    
                    await message.answer(text)
                else:
                    await message.answer("❌ Не удалось найти игрока. Проверьте правильность Steam ID.")
    except Exception as e:
        logger.error(f"Ошибка при обработке Steam ID: {e}")
        await message.answer("⚠️ Произошла ошибка при обработке запроса")

@dp.message()
async def handle_other_messages(message: types.Message):
    """Обработка остальных сообщений"""
    await message.answer(
        "🤖 Используйте кнопки меню или отправьте Steam ID для получения статистики.\n\n"
        "Примеры Steam ID:\n"
        "• https://steamcommunity.com/id/username\n"
        "• https://steamcommunity.com/profiles/76561198012345678\n"
        "• 76561198012345678"
    )

async def main():
    logger.info("🚀 Запуск DotaStats бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
