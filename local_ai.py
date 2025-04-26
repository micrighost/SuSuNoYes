import requests
import json
from dotenv import load_dotenv

# 初始化環境變數（用於管理API金鑰等敏感資訊）
load_dotenv()

# API端點配置說明
# url = os.getenv('open_url') + "/api/chat"  # 外部API端點範例（需配合ngrok等反向代理工具）
url = "http://localhost:11434/api/chat"  # 本地Ollama API端點（需保持ollama serve持續運行）

class TrueLimiter:
    """對話歷史狀態管理類別
    
    主要功能：
    - 管理對話歷史重置狀態
    - 維護對話歷史記錄
    - 提供歷史重置狀態檢查接口
    """
    def __init__(self):
        # 初始化時強制重置歷史記錄（確保新對話獨立性）
        self.history_restore = True  # 歷史重置標記（True=需要重置）
        self.chat_history = None  # 對話歷史存儲（初始化為空）
    
    def is_history_restore(self) -> bool:
        """歷史重置狀態檢查
        
        返回：
            bool: True表示需要重置對話歷史，False表示保持當前歷史
        """
        return self.history_restore

# 全局狀態管理實例（單例模式）
true_limiter = TrueLimiter()

def ai_chat(user_input="你好", system="妳是妹妹", reset_input="r"):
    """
    使用本地模型生成對話回應，具備對話歷史重置功能
    
    參數：
        user_input (str): 用戶輸入文本（預設為"你好"）
        system (str): 系統角色設定（預設為"妳是妹妹"）
        reset_input (str): 重置指令（'r'=重置歷史，其他值保持歷史）
    
    返回：
        str: AI生成的回應文本
    
    工作流程：
    1. 處理重置指令
    2. 初始化/載入對話歷史
    3. 組裝對話上下文
    4. 發送API請求
    5. 處理回應並更新歷史
    """
    
    # 重置邏輯處理
    if reset_input == 'r':  # 當收到重置指令時
        true_limiter.history_restore = True  # 激活重置標記

    # 歷史記錄初始化
    if true_limiter.is_history_restore():  # 雙重檢查確保狀態正確
        true_limiter.chat_history = []  # 清空歷史記錄
        true_limiter.history_restore = False  # 關閉重置標記

    # 消息結構組裝（OpenAI API兼容格式）
    messages = [
        {"role": "system", "content": system},  # 系統角色設定
        # 歷史對話記錄（展開運算符） 例如:chat_history = [A, B]會變成[系統訊息, A, B, 用戶輸入]
        *true_limiter.chat_history,  
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
        # 獲取原始 JSON 字串轉換為 Python 字典，提取 message 欄位，最終獲取 content 值
        ai_reply = json.loads(response.text)['message']['content']
    except KeyError as e:
        print(f"API響應解析錯誤：{e}")
        ai_reply = "發生錯誤，請稍後再試"

    # 歷史記錄更新（保存完整對話輪次）
    true_limiter.chat_history.append({"role": "user", "content": user_input})
    true_limiter.chat_history.append({"role": "assistant", "content": ai_reply})
    
    print("AI:", ai_reply)
    return ai_reply


# 使用範例說明

# # 初始化對話
# ai_chat("你的工作是護士", "你是女生，妳使用中文", reset_input="1")

# # 延續對話
# ai_chat("你的工作是甚麼？", reset_input="1")

# # 測試重置
# ai_chat("你的工作是甚麼？", reset_input="r")
