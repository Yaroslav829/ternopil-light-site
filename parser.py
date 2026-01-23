import requests
from PIL import Image
from io import BytesIO
import json
import datetime

def get_status_by_color(rgb):
    r, g, b = rgb[:3]
    if g > 150 and r < 150: return 1  # Зелений - Є світло
    elif r > 180 and g < 100: return 0  # Червоний - Немає
    elif r > 200 and g > 180: return 2  # Жовтий - Можливо
    return 1

def update_ternopil_schedule():
    img_url = "https://api-toe-poweron.inneti.net/media/2026/01/6973c03093be6_GPV.png"
    
    try:
        response = requests.get(img_url, timeout=15)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        
        # Точні координати під вашу картинку
        x_start = 110  # Початок годин (00:00)
        y_first_subgroup = 125 # Рядок підгрупи 1.1
        step_x = 38.5 
        step_y_subgroup = 33 # Відстань між підгрупами (1.1 та 1.2)
        step_y_group = 66    # Відстань між основними групами (1 та 2)

        schedule_data = {}

        for group in range(1, 7):
            for sub in [1, 2]:
                subgroup_key = f"{group}.{sub}"
                group_hours = []
                
                # Обчислюємо Y для конкретної підгрупи
                y = int(y_first_subgroup + ((group - 1) * step_y_group) + ((sub - 1) * step_y_subgroup))
                
                for hour in range(24):
                    x = int(x_start + (hour * step_x))
                    pixel = img.getpixel((x, y))
                    group_hours.append(get_status_by_color(pixel))
                
                schedule_data[subgroup_key] = group_hours

        output = {
            "last_update": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            "groups": schedule_data
        }

        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        
        print("Графік з підгрупами успішно оновлено!")

    except Exception as e:
        print(f"Помилка: {e}")

if __name__ == "__main__":
    update_ternopil_schedule()
