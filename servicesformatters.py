def format_player_stats(data: dict) -> str:
    """Форматирует статистику игрока в красивый текст"""
    profile = data.get("profile", {})
    matches = data.get("recent_matches", [])
    winrate = data.get("winrate", {})
    
    # Расчет винрейта
    total_wins = winrate.get("win", 0)
    total_matches = total_wins + winrate.get("lose", 0)
    wr_percentage = (total_wins / total_matches * 100) if total_matches > 0 else 0
    
    # Формируем текст
    text = f"👤 {profile.get('profile', {}).get('personaname', 'Unknown')}\n"
    text += f"🎯 MMR: ~{profile.get('mmr_estimate', {}).get('estimate', 'N/A')}\n\n"
    text += f"📊 Статистика за последние {len(matches)} игр:\n"
    text += f"🔥 Винрейт: {wr_percentage:.1f}% ({total_wins}W - {total_matches-total_wins}L)\n"
    text += f"🎭 Роль: Универсал\n\n"
    text += "Последние 5 игр детально:\n"
    
    # Последние 5 матчей
    for match in matches[:5]:
        result = "✅" if match.get("player_slot", 0) < 128 == match.get("radiant_win", False) else "❌"
        hero = match.get("hero_name", "Unknown")
        kda = f"{match.get('kills', 0)}/{match.get('deaths', 0)}/{match.get('assists', 0)}"
        duration = match.get("duration", 0)
        
        text += f"{result} | {hero}\n"
        text += f"📊 KDA: {kda} | 🕒 {duration//60}:{duration%60:02d}\n"
        text += "----------------------------\n"
    
    return text