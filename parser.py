import cloudscraper
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Наші перевірені адреси
ADDRESSES = {
    "1.1": {"city": "Чортків", "street": "Гоголя", "house": "1"},
    "1.2": {"city": "Тернопіль", "street": "Миру", "house": "2"},
    "2.1": {"city": "Кременець", "street": "Вишнівецька", "house": "1"},
    "2.2": {"city": "Тернопіль", "street": "Руська", "house": "10"},
    "3.1": {"city": "Скалат", "street": "Грушевського", "house": "1"},
    "3.2": {"city": "Тернопіль", "street": "Київська", "house": "8"},
    "4.1": {"city": "Тернопіль", "street": "Збаразька", "house": "5"},
    "4.2": {"city": "Тернопіль", "street": "Галицька", "house": "5"},
    "5.1": {"city": "Йосипівка", "street": "Центральна", "house": "1"},
    "5.2": {"city": "Тернопіль", "street": "Стуса", "house": "1"},
    "6.1": {"city": "Данилівці", "street": "Головна", "house": "1"},
    "6.2": {"city": "Борщів", "street": "Мазепи", "house": "1"}
}

def get_schedule(addr):
    scraper = cloudscraper.create_scraper()
    url = "https://www.toe.com.ua/index.php/pohodynni-vidkliuchennia"
    payload = {
        'city': addr['city'],
        'street': addr['street'],
        'house': addr['house'],
        'submit': 'Пошук'
    }
    
    try:
        response = scraper.post(url, data=payload, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Шукаємо всі блоки годин (зазвичай це div-и з певними стилями)
        hours = []
        # На сайті ТОЕ колір зазвичай у стилі background-color
        cells = soup.find_all('div', style=True)
        
        # Фільтруємо лише ті блоки, що схожі на комірки графіка (00:00, 01:00...)
        # Логіка: шукаємо колір #000033 (вимкнено) або сірий (можливо)
        for cell in cells:
            if "00:00" in cell.text or "01:00" in cell.text: # Перевірка, що це комірка часу
                style = cell['style'].lower()
                if "#000033" in style: # Темно-синій
                    hours.append(2)
                elif "gray" in style or "linear-gradient" in style: # Сірий/Штриховка
                    hours.append(1)
                else:
                    hours.append(0)
        
        # Якщо знайшли 24 години — повертаємо, інакше — заглушка
        return hours[:24] if len(hours) >= 24 else [0]*24
    except Exception as e:
        print(f"Помилка при запиті: {e}")
        return [0]*24

# Збір даних
final_data = {}
for group, addr in ADDRESSES.items():
    print(f"Парсинг групи {group}...")
    final_data[group] = get_schedule(addr)

# Запис у файл
output = {
    "last_update": datetime.now().strftime("%d.%m.%Y %H:%M"),
    "groups": final_data
}

with open('schedule.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

print("Готово! schedule.json оновлено.")
