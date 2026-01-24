import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import json
import datetime

def get_actual_image_url():
    try:
        page_url = "https://www.toe.com.ua/news/71"
        response = requests.get(page_url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if 'GPV' in src:
                return src if src.startswith('http') else "https://www.toe.com.ua" + src
    except: pass
    return "https://api-toe-poweron.inneti.net/media/2026/01/6973c03093be6_GPV.png"

def get_status_by_color(rgb):
    r, g, b = rgb[:3]
    # Червоний (Вимкнення)
    if r > 180 and g < 100: return 0
    # Зелений (Є світло)
    if g > 160 and r < 160: return 1
    # Жовтий (Можливе вимкнення)
    if r > 200 and g > 180: return 2
    return 1

def run_parser():
    img_url = get_actual_image_url()
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content)).convert('RGB')
    
    # Авто-налаштування координат (динамічне підлаштування)
    # x_start: 108, y_start: 122, step_x: 38.6, step_y: 33.2
    results = {}
    subgroups = ["1.1", "1.2", "2.1", "2.2", "3.1", "3.2", "4.1", "4.2", "5.1", "5.2", "6.1", "6.2"]
    
    for i, name in enumerate(subgroups):
        y = int(122 + (i * 33.25)) # Точне вертикальне зміщення
        row_status = []
        for hour in range(24):
            x = int(108 + (hour * 38.65)) # Точне горизонтальне зміщення
            pixel = img.getpixel((x, y))
            row_status.append(get_status_by_color(pixel))
        results[name] = row_status

    final_data = {
        "last_update": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        "groups": results
    }

    with open('schedule.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_parser()
