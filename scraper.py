import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time
import random

# 更多 User-Agent 選項
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
]

# 讀取 LINE Notify Token
token = os.getenv('LINE_NOTIFY_TOKEN')

# 隨機選擇 User-Agent
headers = {
    'User-Agent': random.choice(USER_AGENTS),
    'Referer': 'https://www.ptt.cc/bbs/Drama-Ticket/index.html',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*',
    'Accept-Encoding': 'gzip, deflate, br',  # 添加接受編碼
    'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',  # 保持連接
    'Cookie': 'over18=1'  # 設置過18歲的cookie
}

# PTT 看板 URL
url = 'https://www.ptt.cc/bbs/Drama-Ticket/index.html'

# 設定關鍵字
keywords = ['倉木', '角野']

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
            return set(file.read().splitlines())
    return set()

# 更新已處理過的標題
def save_processed_title(title):
    with open(processed_titles_file, 'a', encoding='utf-8') as file:
        file.write(title + '\n')

# 抓取 PTT 看板的文章標題
def fetch_ptt_titles(max_retries=3):
    print("===== 開始爬取 PTT =====")
    
    for attempt in range(max_retries):
        try:
            # 直接使用 requests.get()
            response = requests.get(url, headers=headers, timeout=15)  # 延長 timeout
            
            print(f"HTTP 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('div', class_='r-ent')
                
                print(f"🔍 找到 {len(articles)} 篇文章")
                
                found_match = False
                processed_titles = read_processed_titles()
                
                for article in articles:
                    title_div = article.find('div', class_='title')
                    date_div = article.find('div', class_='meta').find('div', class_='date')
                    
                    if title_div.a and date_div:
                        article_title = title_div.a.text.strip()
                        article_date = date_div.text.strip()
                        article_datetime = datetime.strptime(f"2025/{article_date}", "%Y/%m/%d")
                        
                        print(f"📌 抓取到的標題: {article_title} ({article_date})")
                        
                        if article_datetime >= start_date:
                            if article_title not in processed_titles:
                                if any(keyword in article_title for keyword in keywords):
                                    print(f"✅ 關鍵字匹配成功: {article_title}")
                                    send_line_notify(f"新文章：{article_title}")
                                    save_processed_title(article_title)
                                    found_match = True
                            else:
                                print(f"📌 已處理過的標題: {article_title}")
                
                if not found_match:
                    print("❌ 沒有符合的關鍵字，這次沒有發送通知")
                
                break  # 成功後跳出重試迴圈
            
            time.sleep(random.uniform(3, 6))  # 隨機延遲 3 到 6 秒，避免過快的請求
        
        except Exception as e:
            print(f"❌ 第 {attempt+1} 次嘗試失敗: {e}")
    
    print("===== 爬取 PTT 結束 =====")

# 執行爬取函式
fetch_ptt_titles()
