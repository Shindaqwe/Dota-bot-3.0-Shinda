import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import Update
from aiohttp import web

from config import Config
from handlers import start, profile, friends, meta, support, quick_search
from database import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot, dispatcher: Dispatcher):
    # Установка вебхука
    webhook_url = f"https://{Config.RENDER_DOMAIN}/webhook"
    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

async def handle_webhook(request: web.Request):
    bot: Bot = request.app['bot']
    dispatcher: Dispatcher = request.app['dispatcher']
    try:
        update = Update.model_validate(await request.json(), context={"bot": bot})
        await dispatcher.feed_update(bot, update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    return web.Response()

async def ping_handler(request: web.Request):
    return web.Response(text="pong")

async def main():
    # Инициализация бота
    bot = Bot(token=Config.BOT_TOKEN)
    
    # Инициализация диспетчера
    dispatcher = Dispatcher(
        storage=MemoryStorage(),
        fsm_strategy=FSMStrategy.USER_IN_CHAT
    )
    
    # Регистрация роутеров
    dispatcher.include_router(start.router)
    dispatcher.include_router(profile.router)
    dispatcher.include_router(friends.router)
    dispatcher.include_router(meta.router)
    dispatcher.include_router(support.router)
    dispatcher.include_router(quick_search.router)
    
    # Инициализация базы данных
    await init_db()
    
    # Создание aiohttp приложения
    app = web.Application()
    app['bot'] = bot
    app['dispatcher'] = dispatcher
    
    # Регистрация обработчиков
    app.router.add_post('/webhook', handle_webhook)
    app.router.add_get('/ping', ping_handler)
    
    # Запуск приложения
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', Config.PORT)
    await site.start()
    
    logger.info(f"Server started on port {Config.PORT}")
    
    # Установка вебхука при старте
    await on_startup(bot, dispatcher)
    
    # Бесконечный цикл
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
