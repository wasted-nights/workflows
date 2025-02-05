import requests
from bs4 import BeautifulSoup
import os

# 從 GitHub Secrets 取得 LINE Notify Token
token = os.getenv('LINE_NOTIFY_TOKEN')
headers = {'Authorization': f'Bearer {token}'}

# PTT 看板的 URL
url = 'https://www.ptt.cc/bbs/Drama-Ticket/index.html'  # 替換為您要爬的看板 URL

# 發送 LINE 通知的函式
def send_line_notify(message):
    payload = {'message': message}
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=payload)
    return response.status_code

# 抓取 PTT 看板的文章標題
def fetch_ptt_titles():
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})  # 模擬瀏覽器請求
    soup = BeautifulSoup(response.text, 'html.parser')

    titles = soup.find_all('div', class_='title')  # 找到所有文章標題
    keywords = ['倉木', '角野']  # 這裡放上您要檢查的關鍵字

    for title in titles:
        if title.a:  # 檢查文章是否有有效的連結
            article_title = title.a.text.strip()  # 提取文章標題
            if any(keyword in article_title for keyword in keywords):  # 檢查標題中是否有關鍵字
                # 發送 LINE 通知
                send_line_notify(f"新文章：{article_title}")
                print(f"已發送通知：{article_title}")  # 顯示發送的標題

# 執行抓取函式
fetch_ptt_titles()
