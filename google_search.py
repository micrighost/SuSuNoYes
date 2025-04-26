# 導入必要套件
import requests  # 用於發送HTTP請求，獲取網頁原始碼
from bs4 import BeautifulSoup  # 用於解析HTML結構，提取所需資料
from fake_useragent import UserAgent  # 產生隨機User-Agent，降低被反爬蟲封鎖的機率

def web_search(query, num_results=5, start_page=1, end_page=1):
    """
    Bing搜尋引擎爬蟲（支援多分頁）
    
    參數說明：
        query (str): 搜尋關鍵字
        num_results (int): 每頁擷取的搜尋結果數量
        start_page (int): 起始分頁（預設第1頁）
        end_page (int): 結束分頁（預設第1頁）
    
    回傳：
        url_list (list): 擷取到的搜尋結果網址列表
    """
    try:
        ua = UserAgent()  # 隨機產生User-Agent字串
        headers = {
            'User-Agent': ua.random,  # 模擬不同瀏覽器
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',  # 偏好語言
            'Referer': 'https://www.bing.com/'  # 來源網址（降低被判斷為機器人）
        }
        
        url_list = []  # 用於儲存所有擷取到的網址
        
        # 分頁處理：逐頁爬取指定範圍
        for page in range(start_page, end_page + 1):
            # 計算本頁第一筆結果的索引（Bing參數first）
            first = 1 + (page - 1) * num_results
            url = f"https://www.bing.com/search?q={query}&first={first}"
            
            # 發送GET請求，取得搜尋結果頁面
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()  # 若狀態碼非200則拋出例外
            
            # 解析HTML內容
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 依據Bing的HTML結構，搜尋每一筆結果（li.b_algo）
            # Bing 的 HTML 結構中，每個搜尋結果通常包裹在 <li class="b_algo"> 元素內
            for item in soup.select('.b_algo')[:num_results]:
                # 先嘗試從h2 a標籤取得網址
                title_tag = item.select_one('h2 a, h2 > a')
                link = title_tag.get('href') if title_tag else None
                
                # 若找不到，則嘗試其他a標籤
                if not link:
                    link_tag = item.select_one('a[href^="http"]')
                    link = link_tag.get('href') if link_tag else '無連結'
                
                # 過濾無效連結，只收集有效網址
                if link != '無連結':
                    url_list.append(link)

        # 整理輸出格式：列出所有結果
        output_lines = []
        for idx, url in enumerate(url_list, 1):
            output_lines.append(f"結果 {idx}:\n連結: {url}\n")
        print('\n'.join(output_lines) if output_lines else "沒有找到搜尋結果。")
        
        return url_list  # 回傳網址列表

    except Exception as e:
        print(f"搜尋失敗: {str(e)}")
        return []
    

def extract_all_text(url):
    """
    網頁內容提取器
    
    參數說明：
        url (str): 欲擷取內容的網頁網址
    
    回傳：
        text (str): 清理後的網頁主要文字內容（若內容過短則回傳提示字串）
    """
    ua = UserAgent()  # 產生隨機User-Agent
    headers = {
        'User-Agent': ua.random,  # 偽裝不同瀏覽器
        'Accept': 'text/html,application/xhtml+xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/',  # 偽裝從Google跳轉而來
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'DNT': '1',  # 禁止追蹤
        'Connection': 'keep-alive'
    }

    try:
        # 發送GET請求取得網頁內容
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # 若HTTP錯誤則拋出例外
        
        # 若網頁內容包含驗證字樣，判斷為反爬蟲
        if "請驗證您是人類" in response.text:
            raise Exception('觸發反爬蟲驗證')

        # 解析HTML內容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除常見無用元素，避免干擾主體內容
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
            element.decompose()  # 從DOM樹中移除
        
        # 進階文本清理：逐行去除空白與短行
        text = '\n'.join([
            line.strip() for line in soup.get_text().splitlines() 
            if line.strip() and len(line.strip()) > 20  # 只保留長度大於20的行
        ])
        
        # 若內容過短，回傳提示
        return text if len(text) > 200 else "內容過短，可能解析錯誤"
        
    except requests.exceptions.HTTPError as http_err:
        # 處理HTTP錯誤（如404、403等）
        return f"HTTP錯誤 {http_err.response.status_code}"
    except Exception as e:
        # 處理其他異常（如連線逾時、反爬蟲等）
        return f"提取失敗: {str(e)}"


# # =========================
# # 測試搜尋功能範例
# search_term = "台積電今日股價"
# urls = web_search(search_term)  # 執行搜尋並獲取網址列表

# print("\n純網址列表:")
# print(urls)

# if urls:
#     for idx, url in enumerate(urls, 1):
#         print(f"\n========== 內容 {idx} ==========")
#         text = extract_all_text(url)
#         print(text)  # 完整輸出內容
# else:
#     print("無有效網址可提取內容")