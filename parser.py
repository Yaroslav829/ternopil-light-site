import PIL.Image as Image
import requests
from io import BytesIO
import json

def get_status_by_color(pixel):
    # Логіка визначення статусу за кольором (RGB)
    r, g, b = pixel[:3]
    if r > 200 and g < 100: return 0 # Червоний
    if r > 200 and g > 200: return 2 # Жовтий
    if g > 150: return 1             # Зелений
    return 1 # За замовчуванням

def parse_ternopil_image():
    url = "https://www.toe.com.ua/images/GPV/today.jpg"
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    
    # Координати клітинок на картинці треба підібрати один раз
    # Це приклад того, як скрипт "проходить" по рядку групи
    group_1_schedule = []
    for hour in range(24):
        # x, y - координати центру клітинки для кожної години
        pixel = img.getpixel((100 + hour*30, 150)) 
        group_1_schedule.append(get_status_by_color(pixel))
    
    return group_1_schedule

# Далі зберігаємо в schedule.json, як ми робили раніше
