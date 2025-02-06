import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# 從 GitHub Secrets 取得 LINE Notify Token
token = os.getenv('LINE_NOTIFY_TOKEN')
headers = {'Authorization': f'Bearer {token}'}

# PTT 看板的 URL
url = 'https://www.ptt.cc/bbs/Drama-Ticket/index.html'

# 設定要過濾的關鍵字
keywords = ['倉木', '角野']

# 設定要過濾的日期（只抓 2025/02/06 之後的文章）
start_date = datetime(2025, 2, 6)

# 發送 LINE 通知的函式
def send_line_notify(message):
    payload = {'message': message}
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=payload)
    return response.status_code

# 抓取 PTT 看板的文章標題
def fetch_ptt_titles():
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})  # 模擬瀏覽器請求
    soup = BeautifulSoup(response.text, 'html.parser')

    titles = soup.find_all('div', class_='r-ent')  # 找到所有文章區塊

    print("=== 抓取到的文章列表 ===")  # Debug 訊息
    for entry in titles:
        # 抓取標題
        title_div = entry.find('div', class_='title')
        if not title_div or not title_div.a:
            continue  # 跳過無效文章
        
        article_title = title_div.a.text.strip()
        article_link = 'https://www.ptt.cc' + title_div.a['href']  # 組合完整網址

        # 抓取日期
        date_div = entry.find('div', class_='date')
        if not date_div:
            continue  # 沒有日期的文章跳過

        # 解析日期（格式：2/06）
        article_date_str = date_div.text.strip()
        article_date = datetime.strptime(f"2025/{article_date_str}", "%Y/%m/%d")  # 假設年份為 2025

        # 記錄日誌
        print(f"日期: {article_date.strftime('%Y-%m-%d')} | 標題: {article_title}")

        # 只處理 2025/02/06 之後的文章
        if article_date < start_date:
            continue

        # 檢查標題是否包含關鍵字
        if any(keyword in article_title for keyword in keywords):
            message = f"📢 新文章通知！\n標題: {article_title}\n日期: {article_date.strftime('%Y-%m-%d')}\n🔗 {article_link}"
            send_line_notify(message)
            print(f"✅ 已發送通知: {article_title}")

# 執行抓取函式
fetch_ptt_titles()
