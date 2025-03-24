# import requests
# from bs4 import BeautifulSoup
# from time import sleep
# import csv


# from fake_useragent import UserAgent
# ua = UserAgent(platforms='desktop', os=["Windows", "Linux", "Ubuntu", "Chrome OS", "Mac OS X"], browsers=["Google", "Chrome", "Firefox", "Edge", "Opera", "Safari", "Yandex Browser"])

# count = 0
# headers = {
#     "User-Agent": ua.random,
#     "Accept-Language": "en-US,en;q=0.9",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
# }

# with open('fatsecret.csv', 'a+', newline='', encoding='utf-8') as f:
#     writer = csv.writer(f)
#     writer.writerow(["Name", "Serving", "Calories", "Fat", "Carbs", "Proteins"])

#     for page in range(0,309):
#         """
#         Получение названий блюд из главной страницы 
#         """
#         URL = f"https://www.fatsecret.com/Default.aspx?pa=toc&pg={page}&f=a&s=0"

#         response = requests.get(URL, headers=headers)
#         soup = BeautifulSoup(response.text, "html.parser")

#         left_cell_content = soup.find("div", class_ = "leftCellContent")
#         food = left_cell_content.find_all("a", style = "color:#028CC4;")

#         for item in food:
#             sleep(1)
#             """
#             Получение характиристик блюда из страницы блюда
#             """
#             food_url = item.get("href")
#             FOOD_URL = f"https://www.fatsecret.com{food_url}"

#             food_response = requests.get(FOOD_URL, headers=headers)
#             food_soup = BeautifulSoup(food_response.text, "html.parser")
            
#             try:
#                 serving = food_soup.find("td", class_="serving_size black us serving_size_value").text.strip()
                
#                 nutrition = [value.text.strip() for value in food_soup.find_all("div", class_ = "factValue")]
                
#                 if len(nutrition) >= 4:
#                     calories = nutrition[0]
#                     fat = nutrition[1]
#                     carbs = nutrition[2]
#                     protein = nutrition[3]
#                 else:
#                     continue
                
#                 name = str(item.text.strip())
#                 row = [name, serving, calories, fat, carbs, protein]

#                 # with open('fatsecret.csv', 'a+', newline='', encoding='utf-8') as f:
#                 #     writer = csv.writer(f)
#                 writer.writerow(row)
#                 count +=1 
#                 print(count)
#             except AttributeError:
#                 continue 



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
    "http://185.17.153.178:8080",
    "http://37.204.144.240:8080",
    "http://62.33.207.201:80",
    "http://45.131.4.14:80",
    "http://57.128.201.50:3128",
    "http://217.76.79.86:80",
    "http://85.206.13.20:80",
    "http://77.46.138.49:8080",

] if False else [None]

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
    await asyncio.sleep(random.uniform(2, 5))
    try:
        async with session.get(url, headers=get_headers(), proxy=proxy) as response:
            if response.status == 429:
                print(f"Ошибка 429 на {url}, ждем 30 секунд...")
                await asyncio.sleep(15)
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
    with open('fatsecret.csv', 'a+', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(["Name", "Serving", "Calories", "Fat", "Carbs", "Proteins"])

        async with aiohttp.ClientSession() as session:
            tasks = []
            semaphore = asyncio.Semaphore(4)

            async def limited_fetch(session, food_url, writer, proxy):
                async with semaphore:
                    await parse_food(session, food_url, writer, proxy)

            for page in range(0, 34):
                url = f"https://www.fatsecret.com/Default.aspx?pa=toc&pg={page}&f=y&s=0"
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

                if len(tasks) >= 8:
                    await asyncio.gather(*tasks)
                    tasks = []

            if tasks:
                await asyncio.gather(*tasks)

# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())