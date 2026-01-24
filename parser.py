import json
import datetime
from PIL import Image

def get_status_by_color(rgb):
    r, g, b = rgb[:3]
    if r > 180 and g < 100: return 0  # Червоний - немає світла
    if g > 160 and r < 160: return 1  # Зелений - є світло
    return 2 # Жовтий або інше

def run_parser():
    try:
        img = Image.open("graph.png").convert('RGB')
        # Координати центрів клітинок (підберіть один раз точно)
        x_start, y_start = 108, 122
        step_x, step_y = 38.65, 33.25
        
        results = {}
        groups = ["1.1", "1.2", "2.1", "2.2", "3.1", "3.2", "4.1", "4.2", "5.1", "5.2", "6.1", "6.2"]
        
        for i, name in enumerate(groups):
            y = int(y_start + (i * step_y))
            row = []
            for hour in range(24):
                x = int(x_start + (hour * step_x))
                row.append(get_status_by_color(img.getpixel((x, y))))
            results[name] = row

        data = {
            "last_update": datetime.datetime.now().strftime("%d.%m %H:%M"),
            "groups": results
        }
        with open('schedule.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Помилка: {e}. Перевірте, чи файл названо graph.png")

if __name__ == "__main__":
    run_parser()
