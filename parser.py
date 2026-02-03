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
        
        # Шукаємо блоки з часом та кольором (плитки)
        for el in soup.find_all(True, style=True):
            txt = el.get_text(strip=True)
            if len(txt) == 5 and txt[2] == ':':
                style = el.get('style', '').lower()
                # 0 - НЕМАЄ (Синій), 2 - МОЖЛИВО (Сірий), 1 - Є (Білий)
                if '0, 0, 51' in style or '#000033' in style: hours_data.append(0)
                elif 'gray' in style or 'gradient' in style or '80, 80, 80' in style: hours_data.append(2)
                else: hours_data.append(1)
        
        if len(hours_data) >= 24: return hours_data[-24:]
        return [1] * 24
    except:
        return [1] * 24

results = {g: get_schedule(g, a) for g, a in ADDRESSES.items()}
output = {"last_update": datetime.now().strftime("%d.%m.%Y %H:%M"), "groups": results}

with open('schedule.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

