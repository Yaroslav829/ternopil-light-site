const axios = require('axios');
const cheerio = require('cheerio');

async function getTernopilLightData() {
    const url = "https://www.toe.com.ua/news/71";
    
    try {
        // 1. Загружаем страницу
        const { data } = await axios.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        });

        const $ = cheerio.load(data);
        const result = {
            lastUpdate: new Date().toISOString(),
            groups: {}
        };

        // 2. Ищем контейнер с текстом
        const content = $('.item-page');
        let currentGroup = null;

        // 3. Логика сбора групп и улиц
        // Проходим по всем элементам внутри контента
        content.find('p, span, strong').each((i, el) => {
            const text = $(el).text().trim();
            
            // Регулярное выражение для поиска заголовка группы (н-р: "1.1. група" или "Група 2.1")
            const groupMatch = text.match(/(\d\.\d)\.?\s*група/i);
            
            if (groupMatch) {
                currentGroup = groupMatch[1]; // Получаем "1.1", "2.1" и т.д.
                result.groups[currentGroup] = [];
            } else if (currentGroup && text.length > 5) {
                // Если мы внутри группы, добавляем текст (список улиц)
                // Очищаем текст от лишних переносов строк
                const cleanText = text.replace(/\s+/g, ' ');
                result.groups[currentGroup].push(cleanText);
            }
        });

        // Конвертируем массивы строк в одну строку для каждой группы
        for (let group in result.groups) {
            result.groups[group] = result.groups[group].join(' ');
        }

        return result;

    } catch (error) {
        console.error("Ошибка при парсинге сайта ТОЕ:", error.message);
        return null;
    }
}

// Пример функции поиска улицы в группах
async function findGroupByStreet(streetName) {
    const data = await getTernopilLightData();
    if (!data) return "Ошибка получения данных";

    const searchName = streetName.toLowerCase();
    for (let [group, streets] of Object.entries(data.groups)) {
        if (streets.toLowerCase().includes(searchName)) {
            return `Улица найденна в группе: ${group}`;
        }
    }
    return "Группа для данной улицы не найдена";
}

// Запуск для проверки
getTernopilLightData().then(res => console.log(JSON.stringify(res, null, 2)));

