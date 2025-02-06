import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import time
import urllib3

# 禁用不安全請求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 讀取 LINE Notify Token
token = os.getenv('LINE_NOTIFY_TOKEN')

# 更新 headers 以模擬瀏覽器並繞過驗證
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.ptt.cc/bbs/Drama-Ticket/index.html',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'over18=1'  # 繞過 18 歲限制
}

# 建立一個 session 來保持會話
session = requests.Session()
session.headers.update(headers)

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
            # 使用 verify=False 忽略 SSL 驗證
            response = session.get(url, verify=False, timeout=10)
            
            print(f"HTTP 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                # 檢查是否有驗證碼
                if '驗證碼' in response.text:
                    print("❌ 遇到驗證碼，需要手動處理")
                    return
                
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
            
            time.sleep(2)  # 等待重試
        
        except Exception as e:
            print(f"❌ 第 {attempt+1} 次嘗試失敗: {e}")
    
    print("===== 爬取 PTT 結束 =====")

# 執行爬取函式
fetch_ptt_titles()
