import json
import datetime
from PIL import Image

def get_status_by_color(rgb):
    r, g, b = rgb[:3]
    if r > 180 and g < 100: return 0  # Червоний
    if g > 160 and r < 160: return 1  # Зелений
    if r > 200 and g > 180: return 2  # Жовтий
    return 1

def run_parser():
    try:
        # Відкриваємо файл, який ти завантажив вручну
        img = Image.open("graph.png").convert('RGB')
        
        # Ті самі координати, що ми обговорили
        x_start, y_start = 108, 122
        step_x, step_y = 38.65, 33.25
        
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
        print("Графік успішно оновлено з файлу graph.png")
    except Exception as e:
        print(f"Помилка: {e}. Переконайтеся, що файл graph.png завантажено.")

if __name__ == "__main__":
    run_parser()
