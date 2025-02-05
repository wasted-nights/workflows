import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# 從 GitHub Secrets 取得 LINE Notify Token
token = os.getenv('LINE_NOTIFY_TOKEN')
headers = {'Authorization': f'Bearer {token}'}

# PTT 看板的 URL
url = 'https://www.ptt.cc/bbs/Drama-Ticket/index.html'  # 替換為您要爬的看板 URL

# 目標日期：2025年2月6日
target_date = datetime(2025, 2, 6)

# 發送 LINE 通知的函式
def send_line_notify(message):
    payload = {'message': message}
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=payload)
    return response.status_code

# 解析第二行的日期
def parse_date_from_title(title):
    try:
        # 提取文章的第二行（日期部分）
        # 假設日期在標題的第二行並且格式為 "2/06"
        author_and_date = title.split('\n')[-1].strip()  # 取得標題的第二行並去除前後空白
        title_date_str = author_and_date.split()[-1]  # 日期應該在第二行的最後一部分
        return datetime.strptime(title_date_str, '%m/%d')  # 轉換為 datetime 物件
    except Exception as e:
        print(f"日期解析錯誤：{e}")
        return None

# 抓取 PTT 看板的文章標題
def fetch_ptt_titles():
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})  # 模擬瀏覽器請求
    soup = BeautifulSoup(response.text, 'html.parser')

    titles = soup.find_all('div', class_='title')  # 找到所有文章標題
    keywords = ['倉木', '角野']  # 這裡放上您要檢查的關鍵字

    for title in titles:
        if title.a:  # 檢查文章是否有有效的連結
            article_title = title.a.text.strip()  # 提取文章標題

            # 解析標題中的日期（從第二行獲取）
            article_date = parse_date_from_title(article_title)
            
            if article_date and article_date >= target_date:  # 如果日期大於或等於目標日期
                if any(keyword in article_title for keyword in keywords):  # 檢查標題中是否有關鍵字
                    # 發送 LINE 通知
                    message = f"新文章標題：{article_title}"
                    send_line_notify(message)
                    print(f"已發送通知：{article_title}")
                else:
                    print(f"標題符合關鍵字條件，但日期不符合：{article_title}")
            else:
                print(f"日期不符合：{article_title}")

# 執行抓取函式
fetch_ptt_titles()
