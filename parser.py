import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

# Адреси без змін
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

def get_schedule(scraper, group, addr):
    url = "https://www.toe.com.ua/index.php/pohodynni-vidkliuchennia"
    payload = {'city': addr['city'], 'street': addr['street'], 'house': addr['house'], 'action': 'search'}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Origin': 'https://www.toe.com.ua',
        'Referer': 'https://www.toe.com.ua/index.php/pohodynni-vidkliuchennia'
    }
    
    try:
        response = scraper.post(url, data=payload, headers=headers, timeout=45)
        if "cloudflare" in response.text.lower() or response.status_code == 403:
            print(f"🛑 {group}: Блокування Cloudflare")
            return [1] * 24

        soup = BeautifulSoup(response.text, 'html.parser')
        hours_data = []
        
        # Пошук кольорів плиток
        for el in soup.find_all(True, style=True):
            txt = el.get_text(strip=True)
            if len(txt) == 5 and txt[2] == ':':
                style = el.get('style', '').lower()
                if '0, 0, 51' in style or '#000033' in style: hours_data.append(0)
                elif 'gray' in style or 'gradient' in style or '80, 80, 80' in style: hours_data.append(2)
                else: hours_data.append(1)
        
        return hours_data[-24:] if len(hours_data) >= 24 else [1] * 24
    except Exception as e:
        print(f"❌ {group}: {e}")
        return [1] * 24

# Створюємо сесію
scraper = cloudscraper.create_scraper(delay=10)

print("⏳ Заходимо на сайт...")
try:
    scraper.get("https://www.toe.com.ua/index.php/pohodynni-vidkliuchennia")
    time.sleep(35) # Чекаємо, поки Cloudflare "перевірить" нас
except: pass

results = {}
for g, a in ADDRESSES.items():
    print(f"📡 Збір {g}...")
    results[g] = get_schedule(scraper, g, a)
    time.sleep(5) 

output = {"last_update": datetime.now().strftime("%d.%m.%Y %H:%M"), "groups": results}
with open('schedule.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)
