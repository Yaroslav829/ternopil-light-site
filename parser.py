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
    if g > 150 and r < 150: return 1 # Зелений
    if r > 180 and g < 100: return 0 # Червоний
    if r > 200 and g > 180: return 2 # Жовтий
    return 1

def run_parser():
    img_url = get_actual_image_url()
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content)).convert('RGB')
    x_start, y_start = 110, 125
    step_x, step_y = 38.5, 33 
    results = {}
    subgroups = ["1.1", "1.2", "2.1", "2.2", "3.1", "3.2", "4.1", "4.2", "5.1", "5.2", "6.1", "6.2"]
    for i, name in enumerate(subgroups):
        y = int(y_start + (i * step_y))
        row_status = []
        for hour in range(24):
            x = int(x_start + (hour * step_x))
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
