import cloudscraper
from bs4 import BeautifulSoup
import json
import re

class TernopilParser:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.url_news = "https://www.toe.com.ua/news/71"
        self.url_search = "https://www.toe.com.ua/index.php/pohodynni-vidkliuchennia"

    def get_actual_data(self):
        print("Подключение к сайту ТОЕ...")
        response = self.scraper.get(self.url_news)
        if response.status_code != 200:
            print("Ошибка доступа к сайту")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Пытаемся найти ссылку на актуальный график (картинку)
        img_tag = soup.find('img', src=re.compile(r'grafik', re.I))
        if img_tag:
            img_url = "https://www.toe.com.ua" + img_tag['src']
            print(f"Найдена ссылка на новый график: {img_url}")
            # Здесь можно добавить код для скачивания в graph.png

        # 2. Собираем группы и улицы (теперь это большой текстовый блок)
        content = soup.find('div', {'class': 'item-page'})
        schedule_dict = {}
        
        if content:
            text = content.get_text(separator="\n")
            # Разбиваем текст по группам (1.1, 1.2 и т.д.)
            groups = re.split(r'(\d\.\d)\s*група/підгрупа', text)
            
            for i in range(1, len(groups), 2):
                group_num = groups[i].strip()
                streets = groups[i+1].strip() if i+1 < len(groups) else ""
                schedule_dict[group_num] = streets

        return schedule_dict

    def save_to_json(self, data):
        if data:
            with open('schedule.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("Файл schedule.json успешно обновлен!")

if __name__ == "__main__":
    parser = TernopilParser()
    new_data = parser.get_actual_data()
    if new_data:
        parser.save_to_json(new_data)
    else:
        print("Не удалось получить новые данные.")
