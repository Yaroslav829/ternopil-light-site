import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import ssl

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
    # Налаштовуємо скрейпер для обходу Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    url = "https://www.toe.com.ua/index.php/pohodynni-vidkliuchennia"
    payload = {'city': addr['city'], 'street': addr['street'], 'house': addr['house'], 'action': 'search'}
    
    try:
        # Робимо запит з імітацією реального браузера
        response = scraper.post(url, data=payload, timeout=30, verify=False)
        
        # Якщо нас заблокував Cloudflare (код 403), повертаємо 1
        if response.status_code != 200:
            print(f"⚠️ Група {group}: Сайт повернув статус {response.status_code}")
            return [1] * 24

        soup = BeautifulSoup(response.text, 'html.parser')
        hours_data = []
        
        # Шукаємо елементи з кольором фону (твої плитки на фото)
        cells = soup.find_all(True, style=True)
        for cell in cells:
            txt = cell.get_text(strip=True)
            if len(txt) == 5 and txt[2] == ':':
                style = cell.get('style', '').lower()
                # 0 - НЕМАЄ (темно-синій), 2 - МОЖЛИВО (сірий/градієнт), 1 - Є (білий)
                if '0, 0, 51' in style or '#000033' in style:
                    hours_data.append(0)
                elif '80, 80, 80' in style or '#808080' in style or 'linear-gradient' in style:
                    hours_data.append(2)
                else:
                    hours_data.append(1)

        if len(hours_data) >= 24:
            return hours_data[-24:]
            
        return [1] * 24
    except Exception as e:
        print(f"❌ Помилка {group}: {e}")
        return [1] * 24

# Збір даних для всіх груп
results = {}
for g, a in ADDRESSES.items():
    print(f"🚀 Спроба отримати дані для черги {g}...")
    results[g] = get_schedule(g, a)
    time.sleep(2) # Збільшуємо паузу, щоб не викликати підозру у Cloudflare

output = {
    "last_update": datetime.now().strftime("%d.%m.%Y %H:%M"),
    "groups": results
}

with open('schedule.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)
print(f"✅ Готово! Оновлено о {output['last_update']}")
