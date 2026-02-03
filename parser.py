import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

ADDRESSES = {
    "1.1": {"city": "Чортків", "street": "вул. Ринок", "house": "1"},
    "1.2": {"city": "Тернопіль", "street": "вул. Володимира Лучаковського", "house": "1"},
    "2.1": {"city": "Кременець", "street": "вул. Андрія Пушкаря", "house": "3"},
    "2.2": {"city": "Іванчани", "street": "вул. Центральна", "house": "1"},
    "3.1": {"city": "Лисичинці", "street": "вул. Лесі Українки", "house": "1"},
    "3.2": {"city": "Тернопіль", "street": "вул. Михайла Вербицького", "house": "4"},
    "4.1": {"city": "Тернопіль", "street": "вул. Миколи Пирогова", "house": "1"},
    "4.2": {"city": "Рублин", "street": "вул. Центральна", "house": "1"},
    "5.1": {"city": "Йосипівка", "street": "вул. Лесі Українки", "house": "18"},
    "5.2": {"city": "Тернопіль", "street": "вул. Дмитра Вишневецького", "house": "1"},
    "6.1": {"city": "Данилівці", "street": "вул. Молодіжна", "house": "292"},
    "6.2": {"city": "Борщів", "street": "вул. Романа Шухевича", "house": "1"}
}

def get_schedule(group, addr):
    scraper = cloudscraper.create_scraper()
    url = "https://www.toe.com.ua/index.php/pohodynni-vidkliuchennia"
    payload = {'city': addr['city'], 'street': addr['street'], 'house': addr['house'], 'action': 'search'}
    
    try:
        response = scraper.post(url, data=payload, timeout=25)
        soup = BeautifulSoup(response.text, 'html.parser')
        hours_data = []
        
        # Шукаємо абсолютно ВСІ елементи, які мають колір фону
        elements = soup.find_all(True, style=True)
        
        for el in elements:
            style = el.get('style', '').lower()
            text = el.get_text(strip=True)
            
            # Якщо в елементі або його батькові є час (напр. 08:00)
            if (len(text) == 5 and text[2] == ':') or ("background-color" in style):
                # СИНІЙ (Немає світла) - перевіряємо різні формати запису
                if '0, 0, 51' in style or '#000033' in style:
                    hours_data.append(0)
                # СІРИЙ (Можливо)
                elif '80, 80, 80' in style or '#808080' in style or 'gray' in style or 'gradient' in style:
                    hours_data.append(2)
                # БІЛИЙ (Є світло)
                elif '255, 255, 255' in style or '#ffffff' in style or 'transparent' in style:
                    # Додаємо тільки якщо це схоже на комірку графіка
                    if len(hours_data) < 24:
                        hours_data.append(1)

        if len(hours_data) >= 24:
            # Беремо останні 24, щоб не вхопити шапку таблиці
            return hours_data[-24:]
        
        print(f"⚠️ Група {group}: знайдено лише {len(hours_data)} комірок. Ставлю заглушку.")
        return [1] * 24 
    except Exception as e:
        print(f"❌ Помилка {group}: {e}")
        return [1] * 24

# Збір даних
results = {}
for g, a in ADDRESSES.items():
    print(f"🚀 Парсинг {g}...")
    results[g] = get_schedule(g, a)
    time.sleep(1)

output = {
    "last_update": datetime.now().strftime("%d.%m.%Y %H:%M"),
    "groups": results
}

with open('schedule.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)
