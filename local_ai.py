import requests
import json
from dotenv import load_dotenv

# 初始化環境變數（用於管理API金鑰等敏感資訊）
load_dotenv()

# API端點配置說明
# url = os.getenv('open_url') + "/api/chat"  # 外部API端點範例（需配合ngrok等反向代理工具）
url = "http://localhost:11434/api/chat"  # 本地Ollama API端點（需保持ollama的草尼馬在右下角出現持續運行）

class ChatLimiter:
    """對話歷史狀態管理類別
    
    主要功能：
    - 管理多用戶的對話歷史重置狀態
    - 維護每個用戶的對話歷史記錄
    - 提供檢查及設定用戶是否需要重置對話歷史的接口
    - 以 user_id 為鍵值，確保多用戶狀態獨立互不干擾
    """

    def __init__(self):
        # 用字典管理多用戶狀態，key 是 user_id，value 是該用戶的狀態字典
        # 狀態字典包含：
        #   'history_restore' (bool): 是否需要重置對話歷史，True 表示需要重置
        #   'chat_history' (list): 該用戶的對話歷史記錄，為一個訊息字典列表
        self.user_states = {}

    def _init_user_state(self, user_id):
        """
        初始化指定用戶的狀態字典
        如果 user_id 尚未存在於 user_states 中，則建立預設狀態：
            - history_restore 設為 True，表示預設需要重置對話歷史
            - chat_history 設為空列表，表示尚無歷史訊息
        參數：
            user_id (str): 用戶唯一識別ID
        """
        if user_id not in self.user_states:
            self.user_states[user_id] = {
                'history_restore': True,
                'chat_history': []
            }

    def is_history_restore(self, user_id) -> bool:
        """
        檢查指定用戶是否需要重置對話歷史
        
        參數：
            user_id (str): 用戶唯一識別ID
        
        回傳：
            bool: True 表示該用戶的對話歷史需要重置，False 表示保持現有歷史
        """
        self._init_user_state(user_id)
        return self.user_states[user_id]['history_restore']

    def set_history_restore(self, user_id, value: bool):
        """
        設定指定用戶是否需要重置對話歷史
        
        參數：
            user_id (str): 用戶唯一識別ID
            value (bool): True 表示需要重置，False 表示不需重置
        """
        self._init_user_state(user_id)
        self.user_states[user_id]['history_restore'] = value

    def get_chat_history(self, user_id):
        """
        取得指定用戶的對話歷史記錄
        
        參數：
            user_id (str): 用戶唯一識別ID
        
        回傳：
            list: 該用戶的對話歷史訊息列表，每筆訊息為字典（如 {"role": "user", "content": "..."}）
        """
        self._init_user_state(user_id)
        return self.user_states[user_id]['chat_history']

    def set_chat_history(self, user_id, history):
        """
        設定指定用戶的對話歷史記錄
        
        參數：
            user_id (str): 用戶唯一識別ID
            history (list): 新的對話歷史訊息列表，通常為字典列表
        """
        self._init_user_state(user_id)
        self.user_states[user_id]['chat_history'] = history

# 全局狀態管理實例（單例模式）
chat_limiter = ChatLimiter()

def ai_chat(user_input="你好", system="妳是妹妹", reset_input="r", user_id=None):
    """
    使用本地模型生成對話回應，具備對話歷史重置功能
    
    參數：
        user_input (str): 用戶輸入文本（預設為"你好"）
        system (str): 系統角色設定（預設為"妳是妹妹"）
        reset_input (str): 重置指令（'r'=重置歷史，其他值保持歷史）
        user_id (str): 用戶唯一識別ID
    
    返回：
        str: AI生成的回應文本
    
    工作流程：
    1. 處理重置指令
    2. 初始化/載入對話歷史
    3. 組裝對話上下文
    4. 發送API請求
    5. 處理回應並更新歷史
    """
    
    if user_id is None:
        raise ValueError("必須提供 user_id 以支援多用戶狀態管理")

    # 重置邏輯處理
    if reset_input == 'r':  # 當收到重置指令時
        chat_limiter.set_history_restore(user_id, True)  # 激活重置標記

    # 歷史記錄初始化
    if chat_limiter.is_history_restore(user_id):  # 雙重檢查確保狀態正確
        chat_limiter.set_chat_history(user_id, [])  # 清空歷史記錄
        chat_limiter.set_history_restore(user_id, False)  # 關閉重置標記

    chat_history = chat_limiter.get_chat_history(user_id)

    # 消息結構組裝（OpenAI API兼容格式）
    messages = [
        {"role": "system", "content": system},  # 系統角色設定
        # 歷史對話記錄（展開運算符） 例如:chat_history = [A, B]會變成[系統訊息, A, B, 用戶輸入]
        *chat_history,  
        {"role": "user", "content": user_input}  # 當前用戶輸入
    ]
    
    # API請求構造
    response = requests.post(
        url,
        json={
            "model": "gemma3:1b",  # 模型選擇 llama2-uncensored:latest, gemma3:1b （可選）
            "messages": messages,  # 完整對話上下文
            "stream": False,  # 禁用流式響應，禁用一個字一個字回復（簡化處理邏輯）
            "options": {  # 生成參數
                "temperature": 0.7,  # 創造性控制（0=嚴謹，1=創意）
                "max_tokens": 100  # 最大輸出長度（約70-100漢字）
            }
        }
    )
    
    # 響應處理
    try:
        ai_reply = json.loads(response.text)['message']['content']
    except KeyError as e:
        print(f"API響應解析錯誤：{e}")
        ai_reply = "發生錯誤，請稍後再試"

    # 歷史記錄更新（保存完整對話輪次）
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": ai_reply})
    chat_limiter.set_chat_history(user_id, chat_history)
    
    print("AI:", ai_reply)
    return ai_reply


# 使用範例說明
# ai_chat("你的工作是護士", "你是女生，妳使用中文", reset_input="1", user_id="user123")
# ai_chat("你的工作是甚麼？", reset_input="1", user_id="user123")
# ai_chat("你的工作是甚麼？", reset_input="r", user_id="user123")
