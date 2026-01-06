from aiogram import Router, types
from services.opendota_api import OpenDotaAPI

router = Router()

@router.message(F.text == "📈 Мета герои")
async def show_meta_heroes(message: types.Message):
    await message.answer("Получаю актуальную мету...")
    
    opendota = OpenDotaAPI()
    hero_stats = await opendota.get_hero_meta()
    
    if hero_stats:
        # Фильтруем героев с >500 матчей и сортируем по винрейту
        popular_heroes = [
            hero for hero in hero_stats 
            if hero.get("pick_rate", 0) > 0.5  # Пример фильтрации
        ]
        
        # Сортируем по винрейту
        sorted_heroes = sorted(popular_heroes, key=lambda x: x.get("win_rate", 0), reverse=True)
        
        # Формируем сообщение
        text = "🏆 Топ мета-героев:\n\n"
        for i, hero in enumerate(sorted_heroes[:10], 1):
            text += f"{i}. {hero['localized_name']}\n"
            text += f"   📊 Винрейт: {hero['win_rate']:.1f}%\n"
            text += f"   🎮 Пиков: {hero['pick_rate']:.1f}%\n\n"
        
        await message.answer(text)
    else:
        await message.answer("Не удалось получить данные о мете")
