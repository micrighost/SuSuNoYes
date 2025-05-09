import google_search   # 匯入自訂的 Google 搜尋模組，負責搜尋與網頁內容擷取
import google_ai       # 匯入 Google AI 聊天模組（例如 Gemini、ChatGPT API 包裝）
import local_ai        # 匯入本地 AI 聊天模組（例如本地 LLM）

# 這裡可以切換使用 Google AI 或本地 AI 作為語言模型
model = google_ai.ai_chat
# model = local_ai.ai_chat  # 若要切換為本地 AI，將上方註解，這行取消註解

def rag_ai_chat(query="你好", adjective="可愛的", role="妹妹", reset_input="r", user_id=None):
    """
    智能聊天與網路檢索（RAG）整合主流程
    1. 先用語言模型嘗試直接回答問題
    2. 若模型判斷需查證（如專業、時事、數據等），回傳 'search' 觸發檢索
    3. 進入自動搜尋、摘要、再生成答案的流程

    參數說明：
        query (str): 使用者的提問
        adjective (str): AI 角色形容詞（如「可愛的」）
        role (str): AI 角色（如「妹妹」）
        reset_input (str): 對話歷史重置控制（'r'重置，其他值不重置）
        user_id (str): 用戶唯一識別ID
    回傳：
        str: AI 回覆內容
    """
    # 先用語言模型嘗試直接回答
    response = model(
        f"""你是{adjective}{role}，平常會用輕鬆自然的語氣聊天。
        如果遇到以下情況請只回search：
        1. 需要查證的專業問題（如健康/科技數據/天氣/日期）
        2. 不確定答案是否正確
        3. 問題涉及近期新聞或時事

        現在請回答：{query}
        """,
        f"你是{adjective}{role}，喜歡跟我聊天",
        f"{reset_input}",
        user_id=user_id
    )
    
    # 若模型回覆 "search"，進入檢索增強流程
    if "search" in response.lower():
        print(f"\n{role}：等我查一下資料喔～")
        search_term = query
        answer = search_and_answer(search_term, adjective=adjective, role=role, user_id=user_id)
        return answer
    else:
        # 若能直接回答，直接輸出
        print(f"\n{role}回答:")
        print(response)
        return response

def search_and_answer(search_term, max_retries=5, adjective="可愛的", role="妹妹", user_id=None):
    """
    搜尋並根據檢索內容生成答案
    1. 自動生成適合的搜尋關鍵詞
    2. 執行網路搜尋，取得多個網址
    3. 擷取每個網頁的主要內容
    4. 判斷是否有足夠資訊可回答
    5. 若可回答，生成口語化摘要；否則換關鍵詞重試

    參數說明：
        search_term (str): 搜尋主題
        max_retries (int): 最大重試次數（換不同關鍵詞）
        adjective (str): AI 角色形容詞
        role (str): AI 角色
        user_id (str): 用戶唯一識別ID
    回傳：
        str: AI 回覆內容（若多次失敗則回傳預設訊息）
    """
    retry_count = 0       # 初始化重試次數為0
    answer_found = False  # 標記是否已成功獲得答案
    
    # 只要還沒找到答案，且重試次數未超過最大上限，就持續進行搜尋
    while retry_count < max_retries and not answer_found:
        # 如果已經重試過，要求模型產生「不一樣」的搜尋關鍵詞，避免每次都用同一組詞
        uniqueness = "，不可以一樣" if retry_count > 0 else ""
        # 請語言模型根據搜尋主題生成適合的搜尋關鍵詞，只能回覆可直接用於瀏覽器搜尋的詞句
        kearch_keywords = model( 
            f"幫我下搜尋{search_term}的關鍵詞{uniqueness}，你只能回覆要在瀏覽器上輸入的搜尋詞",
            f"你是{adjective}{role}",
            "1",
            user_id=user_id
        )
        print(f"\n{role}正在用這些關鍵詞找資料: {kearch_keywords}")

        # 執行搜尋，取得網址列表
        urls = google_search.web_search(kearch_keywords)

        # 如果沒有找到任何網址，代表這組關鍵詞效果不好，進入下一輪重試
        if not urls:
            print("暫時找不到相關資料...")
            retry_count += 1  # 累加重試次數
            continue  # 跳回while開頭，重新生成新關鍵詞

        # 擷取所有搜尋結果網頁的主要文字內容
        combined_text = []
        for idx, url in enumerate(urls, 1):
            print(f"\n==== 資料來源 {idx} ====")
            text = google_search.extract_all_text(url)  # 擷取網頁主體文字
            combined_text.append(text)  # 加入彙整清單
            print(text[:300] + "...")  # 預覽前300字，方便人工檢查

        # 將所有網頁內容合併成一大段文字，供後續判斷與摘要
        full_text = "\n\n".join(combined_text)

        # 請語言模型根據這些資料判斷：是否足夠回答原始問題
        # 僅允許回覆 "yes" 或 "no"，避免產生多餘內容
        can_answer = model(
            f"這些資料：\n{full_text[:2000]}...能回答'{search_term}'嗎？只能回答yes或no",
            "嚴謹的資料審查員",
            "1",
            user_id=user_id
        )

        # 若模型判斷「可以回答」
        if str(can_answer).strip().lower() == "yes":
            # 若可回答，請模型根據資料摘要生成口語化答案
            answer = model(
                f"""你是{adjective}{role}，請根據以下資料用輕鬆口語回答：
                資料：{full_text[:2000]}...
                問題：{search_term}
                回答時請：
                1. 用「我查到...」「網路資料說...」開頭
                2. 保持聊天語氣，不要像機器人
                3. 如果資料不完整就直接說不知道
                """,
                f"你是{adjective}{role}，喜歡跟我聊天",
                "1",
                user_id=user_id
            )
            print(f"\n{role}找到答案了：")
            print(answer)
            answer_found = True # 標記已找到答案，while 迴圈會結束
            return answer       # 回傳最終答案
        
        # 若模型判斷「無法回答」，則重試（換關鍵詞、換資料來源）
        else:                   
            retry_count += 1    
            print(f"\n{role}第{retry_count}次嘗試沒成功...")

    # 若多次重試後仍無法找到答案，回覆預設訊息
    print(f"\n{role}：我試了好幾次都找不到確切答案耶...")
    return "找不到確切資訊，我們聊點別的吧～"




