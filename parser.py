import cloudscraper
from bs4 import BeautifulSoup
import re

class TernopilLightParser:
    def __init__(self):
        # Используем cloudscraper для обхода блокировок
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://www.toe.com.ua/index.php/pohodynni-vidkliuchennia"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.toe.com.ua/'
        }

    def get_group_by_street(self, street_name):
        """Находит группу для конкретной улицы через внутренний поиск сайта"""
        try:
            # Отправляем POST запрос, как это делает форма на сайте
            payload = {'search': street_name}
            response = self.scraper.post(self.base_url, data=payload, headers=self.headers)
            
            if response.status_code != 200:
                return "Ошибка связи с сайтом"

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем текст, где упоминается номер группы
            # Обычно результат поиска выводится в блоке с определенным классом или просто текстом
            results_text = soup.get_text()
            
            # Ищем регулярным выражением формат "1.1 група", "Група 2.2" и т.д.
            match = re.search(r'(\d\.\d)\s*група', results_text, re.IGNORECASE)
            if not match:
                match = re.search(r'група\s*(\d\.\d)', results_text, re.IGNORECASE)

            if match:
                return match.group(1)
            else:
                return "Группа не найдена (проверьте название улицы)"

        except Exception as e:
            return f"Ошибка парсинга: {str(e)}"

    def get_full_schedule(self):
        """Получает текущие часы отключений (если они есть текстом)"""
        try:
            response = self.scraper.get("https://www.toe.com.ua/news/71", headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # На сайте ТОЕ график часто идет картинкой, 
            # но под ней бывает текстовое описание периодов.
            content = soup.find('div', {'class': 'item-page'})
            if content:
                return content.get_text(separator='\n', strip=True)
            return "Не удалось получить текстовый график"
            
        except Exception as e:
            return f"Ошибка: {str(e)}"

# --- ПРИМЕР ИСПОЛЬЗОВАНИЯ ---
if __name__ == "__main__":
    parser = TernopilLightParser()
    
    # Замените на улицу из вашего списка
    street = "Тарнавського" 
    group = parser.get_group_by_street(street)
    
    print(f"Результат для '{street}': {group}")
