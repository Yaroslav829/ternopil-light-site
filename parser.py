import requests
from bs4 import BeautifulSoup
import json
import datetime

def parse_schedule():
    # Посилання на сторінку з ГПВ
    url = "https://www.toe.com.ua/index.php/gpv"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    # Тут зазвичай парситься або картинка, або таблиця. 
    # Для прикладу створимо структуру, яку заповнимо логікою:
    
    new_data = {
        "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "groups": {
            "1": [1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,1,1], # 24 години
            "2": [0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1],
            # ... заповнити для інших груп
        }
    }
    
    with open('schedule.json', 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parse_schedule()
