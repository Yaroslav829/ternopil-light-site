import requests
from PIL import Image
from io import BytesIO
import json
import datetime

def get_status_by_color(rgb):
    r, g, b = rgb[:3]
    # Визначаємо колір:
    if r > 200 and g < 100: return 0  # Червоний (Немає світла)
    if r > 200 and g > 200: return 2  # Жовтий (Можливе відключення)
    if g > 150: return 1             # Зелений (Є світло)
    return 1

def update_ternopil_schedule():
    # Посилання на картинку з вашої новини
    img_url = "https://api-toe-poweron.inneti.net/media/2026/01/6973c03093be6_GPV.png"
    
    try:
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        
        # Координати для Тернопільської таблиці (приблизні, треба підлаштувати під оригінал)
        # x_start - перша клітинка (00:00), y_start - перший рядок (Група 1)
        x_start, y_start = 115, 145 
        step_x, step_y = 35, 65 # Крок між годинами та групами
        
        schedule_data = {}
        
        for group in range(1, 7):
            group_hours = []
            for hour in range(24):
                # Беремо колір пікселя в центрі клітинки кожної години
                pixel = img.getpixel((x_start + (hour * step_x), y_start + ((group-1) * step_y)))
                group_hours.append(get_status_by_color(pixel))
            schedule_data[str(group)] = group_hours

        final_json = {
            "last_update": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            "groups": schedule_data
        }

        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(final_json, f, ensure_ascii=False, indent=4)
        
        print("Графік успішно оновлено з картинки!")

    except Exception as e:
        print(f"Помилка парсингу: {e}")

if __name__ == "__main__":
    update_ternopil_schedule()
