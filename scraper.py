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
    print(f"LINE Notify 回應碼: {response.status_code}")  # 確認 API 是否成功
    return response.status_code

# 抓取 PTT 看板的文章標題
def fetch_ptt_titles():
    print("===== 開始爬取 PTT =====")
    
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})  # 模擬瀏覽器請求
    print(f"HTTP 狀態碼: {response.status_code}")  # 顯示 HTTP 狀態碼

    if response.status_code != 200:
        print("⚠️ 無法抓取 PTT 內容，請檢查是否被封鎖")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.find_all('div', class_='title')  # 找到所有文章標題

    print(f"🔍 找到 {len(titles)} 篇文章")  # 顯示找到的文章數量

    keywords = ['倉木', '角野']  # 這裡放上您要檢查的關鍵字
    found_match = False  # 用來記錄是否有符合的標題

    for title in titles:
        if title.a:  # 檢查文章是否有有效的連結
            article_title = title.a.text.strip()  # 提取文章標題
            print(f"📌 抓取到的標題: {article_title}")  # 顯示標題

            if any(keyword in article_title for keyword in keywords):  # 檢查標題中是否有關鍵字
                print(f"✅ 關鍵字匹配成功: {article_title}")  # 顯示匹配到的標題
                send_line_notify(f"新文章：{article_title}")
                found_match = True  # 有找到符合的標題

    if not found_match:
        print("❌ 沒有符合的關鍵字，這次沒有發送通知")

    print("===== 爬取 PTT 結束 =====")

# 執行抓取函式
fetch_ptt_titles()
