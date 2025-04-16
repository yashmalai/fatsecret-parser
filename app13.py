

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv
from fake_useragent import UserAgent
import random

# Инициализация User-Agent
ua = UserAgent(platforms='desktop', os=["Windows", "Linux", "Ubuntu", "Chrome OS", "Mac OS X"], 
               browsers=["Google", "Chrome", "Firefox", "Edge", "Opera", "Safari", "Yandex Browser"])

# Список прокси (добавьте свои)
proxies = [
    "http://6d3h52:hYOxIxJRvC@185.181.246.237:1050",
    "http://6d3h52:hYOxIxJRvC@2.59.50.55:1050",
    "http://6d3h52:hYOxIxJRvC@109.248.13.38:1050",
    "http://6d3h52:hYOxIxJRvC@45.15.73.59:1050",
    "http://6d3h52:hYOxIxJRvC@46.8.155.230:1050",

    "http://6d3h52:hYOxIxJRvC@109.248.15.180:1050",
    "http://6d3h52:hYOxIxJRvC@109.248.142.244:1050",
    "http://6d3h52:hYOxIxJRvC@46.8.222.214:1050",
    "http://6d3h52:hYOxIxJRvC@46.8.223.170:1050",
    "http://6d3h52:hYOxIxJRvC@188.130.143.179:1050",

    "http://6d3h52:hYOxIxJRvC@45.90.196.139:1050",
    "http://6d3h52:hYOxIxJRvC@188.130.187.166:1050",
    "http://6d3h52:hYOxIxJRvC@45.81.136.72:1050",
    "http://6d3h52:hYOxIxJRvC@188.130.218.204:1050",
    "http://6d3h52:hYOxIxJRvC@109.248.129.172:1050",

    "http://6d3h52:hYOxIxJRvC@109.248.167.101:1050",
    "http://6d3h52:hYOxIxJRvC@188.130.128.105:1050",
    "http://6d3h52:hYOxIxJRvC@45.86.1.93:1050",
    "http://6d3h52:hYOxIxJRvC@46.8.156.139:1050",
    "http://6d3h52:hYOxIxJRvC@45.15.73.245:1050",

]

count = 0

# Заголовки
def get_headers():
    return {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

# Асинхронная функция для получения страницы
async def fetch_page(session: aiohttp.ClientSession, url: str, proxy: str = None):
    print(f"Обрабатывается страница: {url}")
    await asyncio.sleep(random.uniform(1, 2))
    try:
        async with session.get(url, headers=get_headers(), proxy=proxy) as response:
            if response.status == 429:
                print(f"Ошибка 429 на {url}, ждем 30 секунд...")
                await asyncio.sleep(10)
                return await fetch_page(session, url, proxy)
            return await response.text()
    except Exception as e:
        print(f"Ошибка при запросе {url}: {e}")
        return None

# Парсинг данных блюда
async def parse_food(session: aiohttp.ClientSession, food_url: str, writer, proxy: str = None):
    global count
    full_url = f"https://www.fatsecret.com{food_url}"
    html = await fetch_page(session, full_url, proxy)
    if not html:
        return

    food_soup = BeautifulSoup(html, "html.parser")
    try:
        name_elem = food_soup.find("h1")
        if not name_elem:
            return
        name = name_elem.text.strip()

        serving_elem = food_soup.find("td", class_="serving_size black us serving_size_value")
        if not serving_elem:
            return
        serving = serving_elem.text.strip()

        nutrition = [value.text.strip() for value in food_soup.find_all("div", class_="factValue")]
        if len(nutrition) >= 4:
            calories = nutrition[0]
            fat = nutrition[1]
            carbs = nutrition[2]
            protein = nutrition[3]
        else:
            return

        row = [name, serving, calories, fat, carbs, protein]
        writer.writerow(row)
        count += 1
        print(f"Сохранено: {count} - {name}")
    except AttributeError:
        return

# Основная функция для парсинга страниц
async def main():
    with open('fat.csv', 'a+', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["Name", "Serving", "Calories", "Fat", "Carbs", "Proteins"])

        async with aiohttp.ClientSession() as session:
            tasks = []
            semaphore = asyncio.Semaphore(8)

            async def limited_fetch(session, food_url, writer, proxy):
                async with semaphore:
                    await parse_food(session, food_url, writer, proxy)

            for page in range(132, 176):
                url = f"https://www.fatsecret.com/Default.aspx?pa=toc&pg={page}&f=i&s=0"
                html = await fetch_page(session, url, random.choice(proxies))
                if not html:
                    continue
 
                soup = BeautifulSoup(html, "html.parser")
                left_cell_content = soup.find("div", class_="leftCellContent")
                food_items = left_cell_content.find_all("a", style="color:#028CC4;")

                for item in food_items:
                    food_url = item.get("href")
                    proxy = random.choice(proxies) if proxies else None
                    tasks.append(limited_fetch(session, food_url, writer, proxy))

                if len(tasks) >= 10:
                    await asyncio.gather(*tasks)
                    tasks = []

            if tasks:
                await asyncio.gather(*tasks)

# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())