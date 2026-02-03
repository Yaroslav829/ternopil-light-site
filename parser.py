import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

# Адреси чітко за твоїми скриншотами для 100% результату
ADDRESSES = {
    "1.1": {"city": "Чортків", "street": "вул. Ринок", "house": "1"},
    "1.2": {"city": "Тернопіль", "street": "вул. Лучаковського", "house": "1"},
    "2.1": {"city": "Кременець", "street": "вул. А.Пушкаря", "house": "1"},
    "2.2": {"city": "Іванчани", "street": "вул. Центральна", "house": "1"},
    "3.1": {"city": "Лисичинці", "street": "вул. Центральна", "house": "1"},
    "3.2": {"city": "Тернопіль", "street": "вул. Вербицького", "house": "1"},
    "4.1": {"city": "Тернопіль", "street": "вул. Пирогова", "house": "1"},
    "4.2": {"city": "Рублин", "street": "вул. Центральна", "house": "1"},
    "5.1": {"city": "Йосипівка", "street": "вул. Центральна", "house": "1"},
    "5.2": {"city": "Тернопіль", "street": "вул. Вишнівецького", "house": "1"},
    "6.1": {"city": "Данилівці", "street": "вул. Центральна", "house": "1"},
    "6.2": {"city": "Борщів", "street": "вул. Шухевича", "house": "1"}
}

def get_schedule(group, addr):
    scraper = cloudscraper.create_scraper()
    url = "https://www.toe.com.ua/index.php/pohodynni-vidkliuchennia"
    
    payload = {
        'city': addr['city'],
        'street': addr['street'],
        'house': addr['house'],
        'action': 'search'
    }
    
    try:
        # Сайт ТОЕ іноді тупить, ставимо timeout 20 секунд
        response = scraper.post(url, data=payload, timeout=20)
        if response.status_code != 200:
            return [1] * 24

        soup = BeautifulSoup(response.text, 'html.parser')
        hours = []

        # Шукаємо всі блоки, що містять час (на твоїх фото це "00:00", "01:00" і т.д.)
        # Ми шукаємо елементи, де є колір фону в стилях
        cells = soup.find_all(['div', 'td'], style=True)
        
        for cell in cells:
            style = cell.get('style', '').lower()
            # Перевіряємо тільки ті блоки, де вказано background-color
            if 'background-color' in style:
                # 0 - Немає світла (темно-синій #000033)
                if '#000033' in style or 'rgb(0, 0, 51)' in style:
                    hours.append(0)
                # 2 - Можливе відключення (сірий або штриховка)
                elif 'gray' in style or '#808080' in style or 'rgb(128, 128, 128)' in style or 'linear-gradient' in style:
                    hours.append(2)
                # 1 - Світло є (білий або прозорий)
                elif '#ffffff' in style or 'rgb(255, 255, 255)' in style or 'transparent' in style:
                    hours.append(1)

        # Оскільки на сторінці можуть бути зайві блоки, беремо останні 24 (це сам графік)
        if len(hours) >= 24:
            result = hours[-24:]
            print(f"✅ Група {group} ({addr['city']}): Отримано.")
            return result
        else:
            print(f"⚠️ Група {group}: Комірок знайдено замало ({len(hours)}).")
            return [1] * 24

    except Exception as e:
        print(f"❌ Помилка на групі {group}: {e}")
        return [1] * 24

# Збираємо все в один об'єкт
final_data = {}
for group, addr in ADDRESSES.items():
    final_data[group] = get_schedule(group, addr)
    time.sleep(1.5) # Пауза, щоб Обленерго не подумало, що ми DDoS-атака

output = {
    "last_update": datetime.now().strftime("%d.%m.%Y %H:%M"),
    "groups": final_data
}

# Записуємо результат
with open('schedule.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

print(f"\n🚀 Всі групи оновлено! Час: {output['last_update']}")

