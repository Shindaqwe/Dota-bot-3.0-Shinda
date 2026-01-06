import re

def parse_steam_input(input_text: str) -> dict:
    """Парсит различные форматы Steam ссылок/ID"""
    
    # SteamID64 (17 цифр)
    if re.match(r'^\d{17}$', input_text):
        return {'steam_id': input_text, 'type': 'steamid64'}
    
    # Account ID
    elif re.match(r'^\d{1,10}$', input_text):
        # Конвертируем в SteamID64
        steam_id = int(input_text) + 76561197960265728
        return {'steam_id': str(steam_id), 'type': 'account_id'}
    
    # URL профиля
    elif 'steamcommunity.com' in input_text:
        if '/profiles/' in input_text:
            steam_id = re.search(r'/profiles/(\d+)', input_text)
            if steam_id:
                return {'steam_id': steam_id.group(1), 'type': 'profile_url'}
        elif '/id/' in input_text:
            # Нужен Steam API для получения SteamID по кастомному URL
            return {'vanity_url': input_text, 'type': 'vanity_url'}
    
    return None