import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# 讀取 LINE Notify Token
token = os.getenv('LINE_NOTIFY_TOKEN')
headers = {'Authorization': f'Bearer {token}'}

# PTT 看板 URL
url = 'https://www.ptt.cc/bbs/Drama-Ticket/index.html'

# 設定關鍵字
keywords = ['倉木', '角野']  # 這裡放上你要檢查的關鍵字

# 設定日期篩選，僅處理 2025/02/06 之後的文章
start_date = datetime(2025, 2, 6)

# 保存已處理過的標題
processed_titles_file = 'processed_titles.txt'

# 發送 LINE 通知的函式
def send_line_notify(message):
    payload = {'message': message}
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=payload)
    return response.status_code

# 讀取已處理過的標題
def read_processed_titles():
    if os.path.exists(processed_titles_file):
        with open(processed_titles_file, 'r', encoding='utf-8') as file:
            return set(file.read().splitlines())  # 返回已處理標題的集合
    return set()

# 更新已處理過的標題
def save_processed_title(title):
    with open(processed_titles_file, 'a', encoding='utf-8') as file:
        file.write(title + '\n')  # 保存處理過的標題

# 抓取 PTT 看板的文章標題
def fetch_ptt_titles():
    print("===== 開始爬取 PTT =====")

    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    print(f"HTTP 狀態碼: {response.status_code}")

    if response.status_code != 200:
        print("❌ 爬取失敗，請檢查 URL 或 PTT 是否有變更")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('div', class_='r-ent')  # 找到所有文章區塊

    print(f"🔍 找到 {len(articles)} 篇文章")

    found_match = False  # 用來標記是否有符合關鍵字的文章
    processed_titles = read_processed_titles()  # 讀取已處理的標題

    for article in articles:
        title_div = article.find('div', class_='title')
        date_div = article.find('div', class_='meta').find('div', class_='date')

        if title_div.a and date_div:
            article_title = title_div.a.text.strip()
            article_date = date_div.text.strip()  # 取得日期（格式: 2/06）

            # 轉換日期格式，讓它變成 datetime 格式來比較
            article_datetime = datetime.strptime(f"2025/{article_date}", "%Y/%m/%d")

            print(f"📌 抓取到的標題: {article_title} ({article_date})")

            # 只處理 2025/02/06 之後的文章
            if article_datetime >= start_date:
                # 檢查標題是否已經處理過
                if article_title not in processed_titles:
                    if any(keyword in article_title for keyword in keywords):
                        print(f"✅ 關鍵字匹配成功: {article_title}")
                        send_line_notify(f"新文章：{article_title}")
                        save_processed_title(article_title)  # 保存已處理過的標題
                        found_match = True
                else:
                    print(f"📌 已處理過的標題: {article_title}")

    if not found_match:
        print("❌ 沒有符合的關鍵字，這次沒有發送通知")

    print("===== 爬取 PTT 結束 =====")

# 執行爬取函式
fetch_ptt_titles()
